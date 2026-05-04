# ==========================================================
# 1. STANDARD LIBRARY IMPORTS
# ==========================================================
import json
import uuid
from collections import defaultdict

# ==========================================================
# 2. DJANGO CORE IMPORTS
# ==========================================================
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Sum, Case, When, IntegerField
from django.db.models.functions import TruncMonth, TruncDate
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

# ==========================================================
# 3. THIRD-PARTY IMPORTS (Channels, Razorpay, etc.)
# ==========================================================
import razorpay
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# ==========================================================
# 4. LOCAL APP IMPORTS
# ==========================================================
# Using absolute imports is more professional for hosting
from ComplainXHostel_app.models import (
    Student, 
    Complaint, 
    Visitor, 
    RoomTransfer, 
    Warden, 
    Payment, 
    Room, 
    StudentRemovalLog,
    LeaveApplication
)
from .utils import get_wing_from_warden

# ==========================================================
# 5. CONSTANTS & CONFIGURATION
# ==========================================================
PLAN_PRICING = {
    "BASIC": 20000,
    "PREMIUM": 50000,
    "VIP": 85000,
}

# Optional Realtime helper logic
try:
    from utils.realtime import send_realtime
except ImportError:
    send_realtime = None
def is_student(user):
    return not user.is_staff

def is_warden(user):
    return user.is_staff

def get_student(user):
    return Student.objects.filter(user=user).select_related('user').first()

def get_wing_from_warden(warden):
    return "boys" if warden.gender == "Male" else "girls"


# ================= AUTH =================

def role_select(request):
    return render(request, 'app/role_select.html')


def login_view(request):
    if request.method == "POST":

        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')

        user_obj = User.objects.filter(email__iexact=email).first()

        if not user_obj:
            return render(request, 'app/login.html', {
                'error': 'Email not registered'
            })

        user = authenticate(request, username=user_obj.username, password=password)

        if user:
            login(request, user)

            if user.is_staff:
                return redirect('warden_dashboard')
            return redirect('dashboard')

        return render(request, 'app/login.html', {
            'error': 'Wrong password'
        })

    return render(request, 'app/login.html')


def send_realtime(event_type, data):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        "hostel",
        {
            "type": "send_update",
            "data": {"event": event_type, "payload": data}
        }
    )



# optional realtime
try:
    from utils.realtime import send_realtime
except:
    send_realtime = None


def register(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        gender = request.POST.get("gender")
        wing = "boys" if gender == "Male" else "girls"

        prefers_ac = request.POST.get("prefers_ac") == "yes"

        course = request.POST.get("course", "").upper().strip()
        current_year = request.POST.get("current_year")
        contact = request.POST.get("contact", "").strip()

        # ================= VALIDATION =================
        if not current_year or not current_year.isdigit():
            messages.error(request, "Invalid year selection")
            return redirect("register")

        current_year = int(current_year)

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")

        course_duration_map = {
            "BCA": 3,
            "MCA": 2,
            "BTECH": 4,
            "BPharma":4,
            "MBA":2,
            "MTech":2,
            "BBA":3,
            "LLB":3,
        }

        course_duration = course_duration_map.get(course, 3)

        try:
            with transaction.atomic():

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                student = Student.objects.create(
                    user=user,
                    wing=wing,
                    gender=gender,
                    course=course,
                    course_duration=course_duration,
                    current_year=current_year,
                    contact=contact,
                    is_active=True,
                    prefers_ac=prefers_ac
                )

                # 🚀 ONLY ONE CALL (correct)
                result = assign_student_to_room(student)

        except Exception as e:
            print("REGISTER ERROR:", e)
            messages.error(request, f"Error: {str(e)}")
            return redirect("register")

        # ================= SAFE REALTIME =================
        if send_realtime:
            try:
                send_realtime("ROOM_ASSIGNED", {
                    "student": student.user.username,
                    "room": student.room.room_number if student.room else "Not Assigned"
                })
            except:
                pass

        # ================= CLEAN FEEDBACK =================
        if result["status"] == "waiting":
            messages.warning(request, "All rooms full. Added to waiting list.")

        elif result["status"] == "assigned":
            messages.success(request, f"Room assigned: {result['room']}")

        else:
            messages.info(request, "Registration completed")

        return redirect("student_login")

    return render(request, "app/register.html")


def logout_view(request):
    logout(request)
    return redirect('role_select')


# ================= STUDENT =================

@login_required
@user_passes_test(is_student)
def dashboard(request):

    student = get_student(request.user)

    complaints = Complaint.objects.filter(student=student)

    # ================= MONTHLY TREND =================
    monthly = complaints.annotate(month=TruncMonth('date')) \
        .values('month') \
        .annotate(total=Count('id')) \
        .order_by('month')

    months = []
    counts = []

    for m in monthly:
        if m['month']:
            months.append(m['month'].strftime("%b"))
            counts.append(m['total'])

    # ================= STATUS COUNTS =================
    total = complaints.count()
    pending = complaints.filter(status="Pending").count()
    resolved = complaints.filter(status="Approved").count()

    # ================= CATEGORY ANALYTICS (NEW FIX) =================
    category_data = complaints.values('category') \
        .annotate(total=Count('id')) \
        .order_by('-total')

    category_labels = [c['category'] or "Unknown" for c in category_data]
    category_counts = [c['total'] for c in category_data]

    # ================= PAYMENT =================
    payments = Payment.objects.filter(student=student)
    paid = payments.aggregate(total=Sum('amount'))['total'] or 0

    # ================= AI INSIGHT (SIMPLE LOGIC) =================
    insight_text = "No data available"

    if category_data:
        top_category = category_data[0]['category']
        top_count = category_data[0]['total']

        # fake simple logic for demo (you can improve later with ML)
        insight_text = f"Most complaints are from {top_category}. It has {top_count} entries."

    # ================= CONTEXT =================
    context = {
        "student": student,

        # KPIs
        "total_complaints": total,
        "pending_complaints": pending,
        "resolved_complaints": resolved,

        # CHARTS (IMPORTANT: safe JSON)
        "months": json.dumps(months),
        "counts": json.dumps(counts),

        "category_labels": json.dumps(category_labels),
        "category_counts": json.dumps(category_counts),

        # PAYMENT
        "paid_amount": paid,

        # INSIGHT (Netflix-style AI card)
        "insight_text": insight_text,
    }

    return render(request, "dashboard/student_dashboard.html", context)

# ================= PROFILE =================
@login_required
def profile(request):
    return render(request, 'app/profile.html', {
        'student': get_student(request.user)
    })

# ================= ROOMMATES Details =================
@login_required
@user_passes_test(is_student)
def view_room(request):
    student = get_student(request.user)

    # handle case if no room assigned
    if not student.room:
        return render(request, "room/view_room.html", {
            "student": student,
            "roommates": [],
            "total_in_room": 0,
            "percent": 0,
            "room_number": "Not Assigned"
        })

    roommates = Student.objects.filter(room=student.room)
    total_in_room = roommates.count()

    capacity = 3
    percent = (total_in_room / capacity) * 100

    return render(request, "room/view_room.html", {
        "student": student,
        "roommates": roommates,
        "total_in_room": total_in_room,
        "percent": percent,
        "room_number": student.room.room_number
    })
# ================= Student FEES =================  

client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, Payment

def fee_status(request):

    student = Student.objects.filter(user=request.user).first()

    # ✅ SAFETY CHECK (VERY IMPORTANT)
    if not student:
        messages.error(request, "Student profile not found. Contact admin.")
        return redirect("/")   # ya dashboard

    total_fee = student.get_total_fee()

    payments = Payment.objects.filter(student=student)

    paid_amount = sum(p.amount for p in payments if p.status == "SUCCESS")

    remaining = total_fee - paid_amount

    percent = int((paid_amount / total_fee) * 100) if total_fee > 0 else 0

    context = {
        "student": student,
        "total_fee": total_fee,
        "paid_amount": paid_amount,
        "remaining": remaining,
        "percent": percent,
        "payments": payments
    }

    return render(request, "fees/fee_status.html", context)

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Payment

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Payment


def download_invoice(request, payment_id):

    payment = get_object_or_404(Payment, id=payment_id)
    student = payment.student

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # ================= HEADER =================
    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=18,
        leading=22,
        alignment=1,  # center
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        name="SubTitle",
        fontSize=10,
        alignment=1,
        textColor=colors.grey
    )

    elements.append(Paragraph("🏨 HostelX Payment", title_style))
    elements.append(Paragraph("Official Payment Receipt", subtitle_style))
    elements.append(Spacer(1, 20))

    # ================= RECEIPT INFO =================
    receipt_data = [
        ["Receipt No:", f"HX-{payment.id:05d}"],
        ["Date:", payment.created_at.strftime("%d %b %Y")],
        ["Status:", payment.status],
    ]

    receipt_table = Table(receipt_data, colWidths=[120, 250])
    receipt_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
    ]))

    elements.append(receipt_table)
    elements.append(Spacer(1, 20))

    # ================= STUDENT DETAILS =================
    student_data = [
        ["Student Name", student.user.username],
        ["Student ID", student.id],
        ["Course", student.course if hasattr(student, "course") else "N/A"],
        ["Room", student.room.room_number if student.room else "N/A"],
        ["Room Type", "AC" if student.room and student.room.is_ac else "Non-AC"],
    ]

    student_table = Table(student_data, colWidths=[150, 250])
    student_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ]))

    elements.append(Paragraph("Student Details", styles["Heading3"]))
    elements.append(student_table)
    elements.append(Spacer(1, 20))

    # ================= PAYMENT DETAILS =================
    payment_data = [
        ["Amount Paid", f"₹{payment.amount}"],
        ["Payment Method", payment.method],
        ["Transaction Status", payment.status],
    ]

    payment_table = Table(payment_data, colWidths=[150, 250])
    payment_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ]))

    elements.append(Paragraph("Payment Details", styles["Heading3"]))
    elements.append(payment_table)
    elements.append(Spacer(1, 30))

    # ================= FOOTER =================
    footer_style = ParagraphStyle(
        name="Footer",
        fontSize=9,
        alignment=1,
        textColor=colors.grey
    )

    elements.append(Paragraph("This is a system generated receipt.", footer_style))
    elements.append(Paragraph("HostelX • Secure Digital Payment System", footer_style))

    doc.build(elements)

    return response

# ================= COMPLAINT =================
def raise_complaint(request):

    if request.method == "POST":

        student = request.user.student
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category")
        issue_type = request.POST.get("issue_type")
        image = request.FILES.get("image")

        Complaint.objects.create(
            student=student,
            title=title,
            description=description,
            category=category,
            issue_type=issue_type,
            image=image
        )

        return redirect("my_complaints")

    return render(request, "complaints/raise_complaint.html")


# ================= MY COMPLAINTS =================
@login_required
@user_passes_test(is_student)
def my_complaints(request):

    student = get_student(request.user)

    data = Complaint.objects.filter(student=student).order_by("-date")

    pending_count = data.filter(status="Pending").count()
    approved_count = data.filter(status="Approved").count()
    rejected_count = data.filter(status="Rejected").count()

    return render(request, "complaints/my_complaints.html", {
        "data": data,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count
    })

# ================= WARDEN COMPLAINTS =================
@login_required
@user_passes_test(is_warden)
def warden_complaints(request):

    # ✅ IMPORTANT FIX (joins student, user, room)
    data = Complaint.objects.select_related(
        "student",
        "student__user",
        "student__room"
    ).all().order_by("-date")

    # STATUS COUNTS
    pending_count = data.filter(status="Pending").count()
    approved_count = data.filter(status="Approved").count()
    rejected_count = data.filter(status="Rejected").count()

    # 📊 TREND CHART
    trend_data = (
        data
        .annotate(day=TruncDate("date"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    trend_labels = [str(i["day"]) for i in trend_data]
    trend_counts = [i["count"] for i in trend_data]

    # 📊 CATEGORY CHART
    category_data = (
        data
        .values("category")
        .annotate(count=Count("id"))
    )

    category_labels = [i["category"] for i in category_data]
    category_counts = [i["count"] for i in category_data]

    return render(request, "warden/complaint_requests.html", {
        "data": data,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,

        "trend_labels": trend_labels,
        "trend_counts": trend_counts,

        "category_labels": category_labels,
        "category_counts": category_counts,
    })
# ================= UPDATE COMPLAINT STATUS (AJAX) =================
@login_required
@user_passes_test(is_warden)
def update_complaint_status(request):
    if request.method == "POST":
        cid = request.POST.get("id")
        status = request.POST.get("status")

        try:
            complaint = Complaint.objects.get(id=cid)
            complaint.status = status
            complaint.save()

            return JsonResponse({
                "status": "success",
                "new_status": status
            })
        except Complaint.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Complaint not found"
            })

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method"
    })



# ================= VISITOR =================
@login_required
def visitor(request):
    student = Student.objects.filter(user=request.user).first()

    if request.method == "POST" and student:
        Visitor.objects.create(
            student=student,
            name=request.POST.get("name"),
            relation=request.POST.get("relation"),
            contact=request.POST.get("contact"),
            id_proof=request.FILES.get("id_proof"),
            status="Pending"
        )

        return redirect("visitor")

    data = Visitor.objects.filter(student=student).order_by("-id")

    pending_count = data.filter(status="Pending").count()
    approved_count = data.filter(status="Approved").count()

    return render(request, "visitor/visitor.html", {
        "student": student,
        "data": data,
        "pending_count": pending_count,
        "approved_count": approved_count,
    })
# ================= WARDEN VISITORS =================
@login_required
@user_passes_test(is_warden)
def warden_visitors(request):
    visitors = Visitor.objects.select_related("student", "student__user").all()

    context = {
        "visitors": visitors,
        "total": visitors.count(),
        "pending": visitors.filter(status="Pending").count(),
        "approved": visitors.filter(status="Approved").count(),
        "rejected": visitors.filter(status="Rejected").count(),
    }

    return render(request, "warden/visitor_requests.html", context)

# ================= Approve VISITOR STATUS (AJAX) =================
@login_required
@user_passes_test(is_warden)
def approve_visitor(request, id):
    v = Visitor.objects.get(id=id)
    v.status = "Approved"
    v.save()
    return redirect("warden_visitors")  # important


#================= REJECT VISITOR STATUS (AJAX) =================
@login_required
@user_passes_test(is_warden)
def reject_visitor(request, id):
    v = Visitor.objects.get(id=id)
    v.status = "Rejected"
    v.save()
    return redirect("warden_visitors")


# ================= ROOM TRANSFER =================
def get_student(user):
    try:
        return Student.objects.get(user=user)
    except Student.DoesNotExist:
        return None
    
@login_required
@user_passes_test(is_student)
def request_transfer(request):

    student = get_student(request.user)

    if not student:
        return render(request, "room/request_transfer.html", {
            "student": None
        })

    if request.method == "POST":
        requested_room = request.POST.get("requested_room")
        reason = request.POST.get("reason")

        # ❌ Validation
        if not requested_room or not reason:
            messages.error(request, "All fields are required")
            return redirect("request_transfer")

        # ❌ Same room check
        if student.room and requested_room == student.room.room_number:
            messages.warning(request, "You are already in this room")
            return redirect("request_transfer")

        # ❌ Duplicate pending request check
        exists = RoomTransfer.objects.filter(
            student=student,
            status="Pending"
        ).exists()

        if exists:
            messages.warning(request, "You already have a pending request")
            return redirect("request_transfer")

        # ✅ Create request
        RoomTransfer.objects.create(
            student=student,
            current_room=student.room.room_number if student.room else "N/A",
            requested_room=requested_room,
            reason=reason,
            status="Pending"
        )

        messages.success(request, "Transfer request submitted successfully")

        return redirect("request_transfer")   # ✅ correct

    data = RoomTransfer.objects.filter(student=student).order_by("-created_at")

    return render(request, "room/request_transfer.html", {
        "student": student,
        "data": data
    })

# ================= WARDEN TRANSFER REQUESTS =================
@login_required
@user_passes_test(is_warden)
def warden_transfers(request):
    data = RoomTransfer.objects.all().order_by("-created_at")

    return render(request, "warden/transfer_requests.html", {
        "data": data
    })

# ================= APPROVE TRANSFER REQUEST (AJAX) =================
@login_required
@user_passes_test(is_warden)
def approve_transfer(request, id):

    transfer = get_object_or_404(RoomTransfer, id=id)

    if transfer.status != "Pending":
        return redirect("warden_transfers")

    with transaction.atomic():

        student = transfer.student

        # safer lookup (NO crash if duplicates exist)
        room = Room.objects.filter(room_number=transfer.requested_room).first()

        if not room:
            return redirect("warden_transfers")

        # update student room
        student.room = room
        student.save()

        # update transfer status
        transfer.status = "Approved"
        transfer.save()

    return redirect("warden_transfers")

# ================= REJECT TRANSFER REQUEST (AJAX) =================
@login_required
@user_passes_test(is_warden)
def reject_transfer(request, id):
    t = get_object_or_404(RoomTransfer, id=id)

    t.status = "Rejected"
    t.save()

    return redirect("warden_transfers")   # ✅ correct


# ================= WARDEN DASHBOARD =================
@login_required
@user_passes_test(is_warden)
def warden_dashboard(request):

    warden = Warden.objects.get(user=request.user)
    wing = get_wing_from_warden(warden)

    # ================= STUDENTS =================
    students = Student.objects.filter(wing=wing, is_active=True)

    # 👉 IMPORTANT: unassigned students for drag-drop panel
    unassigned_students = students.filter(room__isnull=True)

    # ================= FEES =================
    total_paid = 0
    total_due = 0
    defaulters = []

    payments = Payment.objects.filter(student__in=students) \
        .values('student_id') \
        .annotate(total=Sum('amount'))

    payment_map = {p['student_id']: p['total'] for p in payments}

    top_defaulter = None
    max_due = 0

    for s in students:
        paid = payment_map.get(s.id, 0) or 0
        due = 85000 - paid

        total_paid += paid
        total_due += due

        if due > 0:
            defaulters.append({
                "student": s,
                "remaining": due
            })

        if due > max_due:
            max_due = due
            top_defaulter = {
                "name": s.user.username,
                "due": due
            }

    # ================= ROOMS =================
    rooms = Room.objects.filter(wing=wing).prefetch_related('students')

    floor_map = {}

    occupancy_data = Student.objects.filter(
        wing=wing,
        is_active=True,
        room__isnull=False
    ).values("room_id").annotate(count=Count("id"))

    occupancy_map = {
        item["room_id"]: item["count"]
        for item in occupancy_data
    }

    most_filled = None
    max_count = 0

    total_capacity = 0
    total_occupied = 0

    for room in rooms:

        occupied = occupancy_map.get(room.id, 0)

        total_capacity += room.capacity
        total_occupied += occupied

        if occupied > max_count:
            max_count = occupied
            most_filled = {
                "room": room.room_number,
                "count": occupied
            }

        room_data = {
            "id": room.id,
            "room_number": room.room_number,
            "capacity": room.capacity,
            "occupied": occupied,
            "students": room.students.filter(is_active=True)  # 🔥 IMPORTANT
        }

        floor_map.setdefault(room.floor, []).append(room_data)

    floors = [
        {"number": k, "rooms": v}
        for k, v in sorted(floor_map.items())
    ]

    occupancy_rate = int((total_occupied / total_capacity) * 100) if total_capacity else 0

    # ================= COMPLAINTS =================
    complaints = Complaint.objects.filter(student__wing=wing)

    monthly = complaints.annotate(month=TruncMonth('date')) \
        .values('month') \
        .annotate(count=Count('id'))

    months = [m['month'].strftime('%b') for m in monthly if m['month']]
    complaint_counts = [m['count'] for m in monthly]

    category_data = complaints.values('category').annotate(count=Count('id'))
    categories = [c['category'] for c in category_data]
    category_counts = [c['count'] for c in category_data]

    pending_complaints = complaints.filter(status="Pending").count()

    # ================= CONTEXT =================
    context = {
        "total_students": students.count(),
        "total_fee_collected": total_paid,
        "total_pending_fee": total_due,
        "defaulters": defaulters,

        "floors": floors,
        "unassigned_students": unassigned_students,  # 🔥 IMPORTANT

        "months": json.dumps(months),
        "complaint_counts": json.dumps(complaint_counts),
        "categories": json.dumps(categories),
        "category_counts": json.dumps(category_counts),

        "top_defaulter": top_defaulter,
        "occupancy_rate": occupancy_rate,
        "most_filled": most_filled,
        "pending_complaints": pending_complaints,
    }

    return render(request, "warden/dashboard.html", context)

# ================= NOTIFICATIONS =================
@login_required
def notification_data(request):

    student = get_student(request.user)

    total = Complaint.objects.filter(student=student, status="Pending").count()

    return JsonResponse({
        "total": total
    })


# ==========  warden_fee_dashboard =======from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import Student, Payment, Warden

@login_required
@user_passes_test(lambda u: hasattr(u, 'warden'))
def warden_fee_dashboard(request):

    warden = Warden.objects.get(user=request.user)
    wing = get_wing_from_warden(warden)

    students = Student.objects.filter(
        wing=wing,
        is_active=True
    ).select_related("room", "user")   # ⚡ performance boost

    # 🔍 FILTER (AC / NON-AC / ALL)
    room_filter = request.GET.get("type")  # ac / nonac / None

    if room_filter == "ac":
        students = students.filter(room__is_ac=True)
    elif room_filter == "nonac":
        students = students.filter(room__is_ac=False)

    total_students = students.count()
    total_collected = 0
    total_pending = 0

    fee_data = []

    for s in students:

        # ✅ REAL FEE LOGIC (MAIN FIX)
        total_fee = s.get_total_fee()

        payments = Payment.objects.filter(student=s).order_by('-created_at')

        paid = payments.filter(status="SUCCESS").aggregate(
            total=Sum("amount")
        )["total"] or 0

        remaining = total_fee - paid

        total_collected += paid
        total_pending += remaining

        percent = int((paid / total_fee) * 100) if total_fee else 0

        fee_data.append({
            "student": s,
            "paid": paid,
            "remaining": remaining,
            "total_fee": total_fee,
            "percent": percent,
            "payments": payments[:5],
        })

    recovery = int(
        (total_collected / (total_collected + total_pending)) * 100
    ) if (total_collected + total_pending) else 0

    return render(request, "warden/warden_fees.html", {
        "fee_data": fee_data,
        "total_students": total_students,
        "total_collected": total_collected,
        "total_pending": total_pending,
        "recovery": recovery,
        "selected_filter": room_filter
    })


# ================= WARDEN ROOMS =================
@login_required
@user_passes_test(is_warden)
def warden_rooms(request):

    warden = Warden.objects.get(user=request.user)
    wing = get_wing_from_warden(warden)

    
    rooms = Room.objects.filter(wing=wing).order_by("floor", "room_number")

    rooms_data = []

    for room in rooms:

        students = Student.objects.filter(
            room=room,
            is_active=True
        ).select_related("user")

        count = students.count()
        capacity = room.capacity

        rooms_data.append({
            "number": room.room_number,
            "floor": room.floor,
            "is_ac": getattr(room, "is_ac", False),  # safe fallback
            "count": count,
            "capacity": capacity,
            "percent": int((count / capacity) * 100) if capacity else 0,
            "students": students
        })

    return render(request, "warden/rooms.html", {
        "rooms": rooms_data
    })

























# ================= WARDEN STUDENTS =================
@login_required
@user_passes_test(is_warden)
def all_students(request):

    warden = get_object_or_404(Warden, user=request.user)
    wing = get_wing_from_warden(warden)

    # ✅ optimized query (avoid N+1)
    students = Student.objects.filter(wing=wing).select_related("user", "room")

    # ✅ FIXED (you used wrong variable before)
    total = students.count()
    active = students.filter(is_active=True).count()
    removed = students.filter(is_active=False).count()

    # ✅ payments aggregation (single query)
    payments = (
        Payment.objects
        .filter(student__in=students)
        .values('student_id')
        .annotate(total_paid=Sum('amount'))
    )

    payment_map = {p['student_id']: p['total_paid'] or 0 for p in payments}

    # ✅ attach calculated fields
    for s in students:
        paid = payment_map.get(s.id, 0)

        s.total_fee = 85000
        s.paid = paid
        s.due = s.total_fee - paid

        s.is_due = s.due > 0
        s.is_high_due = s.due > 30000

    return render(request, "warden/students.html", {
        "students": students,
        "total": total,
        "active": active,
        "removed": removed
    })

@login_required
@user_passes_test(is_warden)
def remove_student(request, id):

    if request.method != "POST":
        messages.error(request, "Invalid request")
        return redirect("warden_students")

    student = get_object_or_404(Student, id=id)

    student.is_active = False
    student.room = None   # ✅ IMPORTANT (free room)
    student.save()

    messages.success(request, "Student removed successfully")

    return redirect('warden_students')

from django.http import JsonResponse

def check_room(request):

    room_id = request.GET.get("room_id")

    if not room_id:
        return JsonResponse({"error": "Room ID required"}, status=400)

    room = get_object_or_404(Room, id=room_id)

    count = Student.objects.filter(
        room=room,
        is_active=True
    ).count()

    return JsonResponse({
        "count": count,
        "capacity": room.capacity,
        "full": count >= room.capacity   # ✅ dynamic
    })
from django.http import JsonResponse
from django.db.models import Count, Sum
from ComplainXHostel_app.models import Room, Student, Payment


@login_required
@user_passes_test(is_warden)
def room_status_api(request):

    warden = Warden.objects.get(user=request.user)
    wing = warden.gender

    rooms = Room.objects.filter(wing=wing)

    # 🔥 OPTIMIZED OCCUPANCY (single query)
    occupancy_data = Student.objects.filter(
        wing=wing,
        is_active=True,
        room__isnull=False
    ).values("room_id").annotate(count=Count("id"))

    occupancy_map = {
        item["room_id"]: item["count"]
        for item in occupancy_data
    }

    # 🔥 PREFETCH STUDENTS (single query)
    students = Student.objects.filter(
        wing=wing,
        is_active=True,
        room__isnull=False
    ).select_related("user")

    room_students_map = {}

    for s in students:
        room_students_map.setdefault(s.room_id, []).append({
            "id": s.id,
            "name": s.user.username
        })

    data = []

    for room in rooms:

        occupied = occupancy_map.get(room.id, 0)
        capacity = room.capacity
        percent = int((occupied / capacity) * 100) if capacity else 0

        data.append({
            "id": room.id,
            "room": room.room_number,
            "floor": room.floor,
            "capacity": capacity,
            "occupied": occupied,
            "available": capacity - occupied,
            "occupancy_percent": percent,

            # 🔥 CLEAN STATUS
            "status": (
                "Full" if occupied >= capacity else
                "Almost Full" if percent >= 70 else
                "Available"
            ),

            "is_ac": room.is_ac,

            "students": room_students_map.get(room.id, [])
        })

    return JsonResponse({"rooms": data})


from django.http import JsonResponse
from django.db.models import Sum
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Student, Room, Payment, Warden


# ================= ROOM LIVE DASHBOARD =================
@login_required
@user_passes_test(is_warden)
def room_live_dashboard(request):

    warden = Warden.objects.get(user=request.user)

    wing = "boys" if warden.gender == "Male" else "girls"

    if prefers_ac:
        rooms = Room.objects.filter(wing=wing, is_ac=True)
    else:
        rooms = Room.objects.filter(wing=wing).order_by("floor", "room_number")

    rooms_data = []

    for room in rooms:

        # 🔥 FIX: only active students + safe filter
        students = Student.objects.filter(
            room=room,
            is_active=True,
            wing=wing
        ).select_related("user")

        rooms_data.append({
            "id": room.id,
            "number": room.room_number,
            "count": students.count(),
            "capacity": room.capacity,
            "is_ac": room.is_ac,

            # 🔥 FIX: convert queryset → JSON-safe list
            "students": [
                {
                    "id": s.id,
                    "name": s.user.username,
                    "course": s.course,
                    "year": s.current_year
                }
                for s in students
            ]
        })

    return render(request, "warden/room_live_dashboard.html", {
        "rooms": rooms_data
    })





from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Room, Student, Payment
from django.db.models import Sum

@login_required
def room_details(request, room_id):
    try:
        room = Room.objects.get(id=room_id)

        students = Student.objects.filter(room=room)

        student_list = []

        for s in students:

            # ✅ SAFE PAYMENT CALCULATION
            paid = Payment.objects.filter(
                student=s,
                status="SUCCESS"
            ).aggregate(total=Sum("amount"))["total"] or 0

            total_fee = s.total_fee or 0
            due = total_fee - paid

            student_list.append({
                "id": s.id,
                "name": s.user.username if s.user else "Unknown",
                "room": room.room_number,
                "course": getattr(s, "course", ""),
                "year": getattr(s, "year", ""),
                "contact": getattr(s, "contact", ""),
                "paid": paid,
                "due": due,
                "profile_pic": s.profile_pic.url if getattr(s, "profile_pic", None) and s.profile_pic else None,
            })

        return JsonResponse({
            "students": student_list
        })

    except Room.DoesNotExist:
        return JsonResponse({"students": []})

    except Exception as e:
        print("ROOM DETAILS ERROR:", e)
        return JsonResponse({
            "students": [],
            "error": str(e)
        })


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Student, Room

@login_required
def shift_student(request):

    if request.method == "POST":
        try:
            student_id = request.POST.get("student_id")
            room_id = request.POST.get("room_id")

            print("SHIFT DATA:", student_id, room_id)

            student = Student.objects.get(id=student_id)
            new_room = Room.objects.get(id=room_id)

            # ✅ CHECK CAPACITY
            current_count = Student.objects.filter(room=new_room).count()

            if current_count >= new_room.capacity:
                return JsonResponse({
                    "status": "error",
                    "message": "Room is full"
                })

            # ✅ UPDATE ROOM
            student.room = new_room
            student.save()

            return JsonResponse({
                "status": "success"
            })

        except Student.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Student not found"
            })

        except Room.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Room not found"
            })

        except Exception as e:
            print("SHIFT ERROR:", e)
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })

    return JsonResponse({"status": "error", "message": "Invalid request"})

@login_required
@user_passes_test(is_student)
def update_profile_pic(request):

    student = get_student(request.user)

    if request.method == "POST" and request.FILES.get("profile_pic"):

        student.profile_pic = request.FILES["profile_pic"]
        student.save()

        return redirect("profile")

    return redirect("profile")


def warden_login(request):

    if request.method == "POST":

        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(email=email).first()

        if not user_obj:
            return render(request, 'app/warden_login.html', {
                'error': 'Email not registered'
            })

        user = authenticate(request, username=user_obj.username, password=password)

        if user and user.is_staff:
            login(request, user)
            return redirect('warden_dashboard')

        return render(request, 'app/warden_login.html', {
            'error': 'Invalid warden credentials'
        })

    return render(request, 'app/warden_login.html')


import razorpay
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Payment


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def create_order(request):
    if request.method == "POST":
        try:
            print("\n" + "="*50)
            print("🔔 CREATE ORDER REQUEST RECEIVED")
            print("="*50)
            
            amount_str = request.POST.get("amount", "").strip()
            print(f"📦 Amount string: {amount_str}")
            
            if not amount_str:
                return JsonResponse({"error": "Amount is required"}, status=400)
            
            try:
                amount = int(float(amount_str)) * 100
            except ValueError:
                return JsonResponse({"error": "Invalid amount format"}, status=400)

            if amount <= 0:
                return JsonResponse({"error": "Amount must be greater than 0"}, status=400)

            # Check if user is authenticated and has a student profile
            if not hasattr(request.user, 'student') or not request.user.student:
                print(f"❌ Student profile not found for user: {request.user}")
                return JsonResponse({"error": "Student profile not found. Contact admin."}, status=403)

            print(f"👤 User: {request.user}")
            print(f"📚 Student: {request.user.student}")
            print(f"💰 Amount (paise): {amount}")

            client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )

            print("🔗 Creating Razorpay order...")
            order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })
            print(f"✅ Order created: {order['id']}")

            payment = Payment.objects.create(
                student=request.user.student,
                amount=amount // 100,
                razorpay_order_id=order["id"],
                status="PENDING"
            )
            print(f"✅ Payment record created: {payment.id}")
            print("="*50)

            return JsonResponse({
                "order_id": order["id"],
                "amount": amount,
                "key": settings.RAZORPAY_KEY_ID
            })
        except Exception as e:
            print(f"❌ Order creation error: {str(e)}")
            print("="*50)
            return JsonResponse({"error": f"Order creation failed: {str(e)}"}, status=500)

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        # Razorpay sends standard Form Data on redirect, not JSON body
        payment_id = request.POST.get("razorpay_payment_id", "")
        order_id = request.POST.get("razorpay_order_id", "")
        signature = request.POST.get("razorpay_signature", "")

        print(f"DEBUG: Received Payment ID: {payment_id}")

        try:
            # 1. Verify Signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params_dict)

            # 2. Update Database
            payment = Payment.objects.get(razorpay_order_id=order_id)
            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            payment.status = "SUCCESS"
            payment.save()

            messages.success(request, "Payment Successful! 🎉")
            return redirect('fee_status')

        except Exception as e:
            print(f"ERROR: Payment Verification Failed: {e}")
            messages.error(request, "Payment failed or verification error.")
            return redirect('fee_status')

    return redirect('fee_status')

@csrf_exempt
def payment_failed(request):
    if request.method == "POST":
        print("FAILED PAYMENT:", request.body)
        return JsonResponse({"status": "failed"})


@login_required
def finance_dashboard(request):

    student = get_student(request.user)

    payments = Payment.objects.filter(student=student).order_by("-created_at")

    total_fee = student.total_fee

    paid_amount = payments.filter(status="SUCCESS").aggregate(
        total=Sum("amount")
    )["total"] or 0

    pending_amount = payments.filter(status="PENDING").aggregate(
        total=Sum("amount")
    )["total"] or 0

    remaining = total_fee - paid_amount
    percent = round((paid_amount / total_fee) * 100, 2) if total_fee else 0

    return render(request, "finance/dashboard.html", {
        "payments": payments,
        "total_fee": total_fee,
        "paid_amount": paid_amount,
        "pending_amount": pending_amount,
        "remaining": remaining,
        "percent": percent
    })


@login_required
def subscription_page(request):

    student = get_student(request.user)

    subscription, created = Subscription.objects.get_or_create(student=student)

    plan_price = PLAN_PRICING.get(subscription.plan, 0)

    paid_amount = subscription.amount_paid

    remaining = plan_price - paid_amount

    percent = (paid_amount / plan_price) * 100 if plan_price else 0

    return render(request, "subscription.html", {
        "subscription": subscription,
        "plan_price": plan_price,
        "paid_amount": paid_amount,
        "remaining": remaining,
        "percent": percent
    })


@login_required
def upgrade_plan(request):

    student = get_student(request.user)
    subscription = Subscription.objects.get(student=student)

    new_plan = request.POST.get("plan")

    subscription.plan = new_plan
    subscription.amount_paid = 0
    subscription.save()

    return redirect("subscription_page")


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import LeaveApplication, Student


@login_required
def apply_leave(request):

    if request.method == "POST":

        student = Student.objects.get(user=request.user)

        LeaveApplication.objects.create(
            student=student,
            from_date=request.POST.get("from_date"),
            to_date=request.POST.get("to_date"),
            student_contact=request.POST.get("student_contact"),
            parent_contact=request.POST.get("parent_contact"),
            reason=request.POST.get("reason"),
        )

        return redirect("my_leave")

    return render(request, "app/apply_leave.html")

@login_required
def my_leave(request):

    student = Student.objects.get(user=request.user)

    leaves = LeaveApplication.objects.filter(
        student=student
    ).order_by("-applied_at")

    total = leaves.count()
    approved = leaves.filter(status="Approved").count()
    rejected = leaves.filter(status="Rejected").count()
    pending = leaves.filter(status="Pending").count()

    approval_rate = int((approved / total) * 100) if total else 0

    context = {
        "leaves": leaves,
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "pending": pending,
        "approval_rate": approval_rate
    }

    return render(request, "app/my_leave.html", context)


from django.views.decorators.http import require_POST
from django.db.models import Case, When, IntegerField

@login_required
@user_passes_test(is_warden)
def manage_leaves(request):

    leaves = LeaveApplication.objects.select_related(
        "student",
        "student__user",
        "student__room"
    ).all().order_by("-applied_at")

    return render(request, "warden/manage_leaves.html", {
        "leaves": leaves
    })


from django.shortcuts import get_object_or_404, redirect

def approve_leave(request, id):
    if request.method == "POST":
        leave = get_object_or_404(LeaveApplication, id=id)
        leave.status = "Approved"
        leave.save()
    return redirect("manage_leaves")


def reject_leave(request, id):
    if request.method == "POST":
        leave = get_object_or_404(LeaveApplication, id=id)
        leave.status = "Rejected"
        leave.save()
    return redirect("manage_leaves")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
@user_passes_test(is_warden)
@csrf_exempt
def update_leave_status(request):

    if request.method == "POST":

        leave_id = request.POST.get("leave_id")
        status = request.POST.get("status")

        try:
            leave = LeaveApplication.objects.get(id=leave_id)

            leave.status = status
            leave.save()

            return JsonResponse({"status": "success"})

        except LeaveApplication.DoesNotExist:
            return JsonResponse({"status": "error"})

    return JsonResponse({"status": "invalid"})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count

from .models import Student, Room, StudentRemovalLog
from .services.room_engine import assign_student_to_room


# ================= REMOVE STUDENT =================
def remove_student(request, id):
    if request.method == "POST":

        student = get_object_or_404(Student, id=id)
        freed_room = student.room

        # ✅ Create removal log
        StudentRemovalLog.objects.create(
            student=student,
            removed_by=request.user,
            reason="Removed by warden"
        )

        # ✅ Remove student
        student.room = None
        student.is_active = False
        student.save()

        # ✅ Smart reassignment (FIFO)
        if freed_room:
            waiting_students = Student.objects.filter(
                wing=student.wing,
                room__isnull=True,
                is_active=True
            ).order_by("id")

            for ws in waiting_students:
                result = assign_student_to_room(ws)
                if result.get("status") == "assigned":
                    break

        messages.success(request, "Student removed and room reassigned")
        return redirect("warden_students")

    return redirect("warden_students")


# ================= MANUAL ASSIGN =================
def assign_room_manual(request, student_id):   # ✅ FIXED PARAM NAME

    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":
        room_id = request.POST.get("room_id")

        if not room_id:
            messages.error(request, "Please select a room")
            return redirect(request.path)

        room = get_object_or_404(Room, id=room_id)

        # ✅ Capacity check (IMPORTANT)
        current_count = Student.objects.filter(room=room, is_active=True).count()

        if current_count >= room.capacity:
            messages.error(request, "Room is already full")
            return redirect(request.path)

        # ✅ Assign room
        student.room = room
        student.is_active = True
        student.save()

        messages.success(request, "Room assigned successfully")
        return redirect("warden_students")

    # ✅ Only rooms with available space
    # rooms = Room.objects.annotate(
    #     student_count=Count('students',distinct=True)
    # ).filter(student_count__lt=Count('capacity'))  # optional filter
    rooms = []

    all_rooms = Room.objects.filter(wing=student.wing)

    for room in all_rooms:
        occupied = Student.objects.filter(
            room=room,
            is_active=True
        ).count()

        if occupied < room.capacity:
            room.occupants = occupied   # 👈 template ke liye
            rooms.append(room)

    return render(request, "warden/manual_assign.html", {
        "student": student,
        "rooms": rooms
    })


# ================= REMOVAL HISTORY =================
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import StudentRemovalLog, Warden
from .utils import get_wing_from_warden

@login_required
def removal_history(request):

    warden = Warden.objects.get(user=request.user)
    wing = get_wing_from_warden(warden)

    logs = StudentRemovalLog.objects.filter(
        student__wing=wing,          # ✅ MAIN FIX
        student__is_active=False
    ).order_by('-removed_at')

    return render(request, "warden/removal_history.html", {
        "logs": logs
    })


