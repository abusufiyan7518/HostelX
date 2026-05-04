from django.db import models
from django.contrib.auth.models import User

# ================= WARDEN =================
class Warden(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    gender = models.CharField(max_length=10)  # Male / Female
    contact = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    profile_pic = models.ImageField(
        upload_to='warden_profiles/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


# ================= STUDENT =================
from django.db import models
from django.contrib.auth.models import User
from datetime import date

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female')
]

WING_CHOICES = [
    ('boys', 'Boys'),
    ('girls', 'Girls')
]
ROOM_TYPES=(
    ("AC", "AC"),
    ("NON_AC", "Non AC")
)


class Student(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, related_name="students")
    # room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default="NON_AC")
    prefers_ac = models.BooleanField(default=False)
   
    total_fee = models.IntegerField(default=85000)

    wing = models.CharField(max_length=10, choices=WING_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    contact = models.CharField(max_length=15)
    removed_at = models.DateTimeField(null=True, blank=True)
    removed_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="removed_students"
    )

    course = models.CharField(max_length=100, blank=True, null=True)

    course_duration = models.IntegerField(default=3)
    current_year = models.IntegerField(default=1)

    admission_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # ================= SMART LOGIC =================
    def get_total_fee(self):

        if self.room and self.room.is_ac:
            return 100000
        return 85000

    @property
    def is_graduating(self):
        return self.current_year >= self.course_duration

    @property
    def years_left(self):
        return self.course_duration - self.current_year

    @property
    def stay_duration(self):
        return (date.today() - self.admission_date).days

    def __str__(self):
        room_no = self.room.room_number if self.room else "Not Assigned"
        return f"{self.user.username} (Room {room_no})"


# ================= COMPLAINT =================
class Complaint(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)

    issue_type = models.CharField(max_length=100, null=True, blank=True)

    # ✅ ADD THIS
    image = models.ImageField(upload_to="complaints/", null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("Approved", "Approved"),
            ("Rejected", "Rejected")
        ],
        default="Pending"
    )

    date = models.DateTimeField(auto_now_add=True)

# ================= VISITOR =================
from django.utils import timezone

class Visitor(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relation = models.CharField(max_length=50)
    contact = models.CharField(max_length=15)
    id_proof = models.FileField(upload_to="visitors/")

    status = models.CharField(max_length=20, default="Pending")

    # FIX HERE 👇
    visit_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



# ================= LEAVE =================
from django.db import models
from django.contrib.auth.models import User

class LeaveApplication(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    
    from_date = models.DateField()
    to_date = models.DateField()

    student_contact = models.CharField(max_length=15)
    parent_contact = models.CharField(max_length=15)
    
    reason = models.TextField()
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.status}"




# ================= FEE PLAN =================
class FeePlan(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)

    total_fee = models.IntegerField(default=85000)
    academic_year = models.CharField(max_length=20, default="2025-26")

    def __str__(self):
        return f"{self.student.user.username} FeePlan"


# ================= PAYMENT =================
class Payment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    amount = models.IntegerField()

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)

    method = models.CharField(max_length=20, default="Razorpay")

    status = models.CharField(
        max_length=20,
        default="PENDING",
        choices=[
            ("PENDING", "PENDING"),
            ("SUCCESS", "SUCCESS"),
            ("FAILED", "FAILED"),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.amount} - {self.status}"


# ================= NOTIFICATION =================
class Notification(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    message = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} Notification"

    
class Room(models.Model):
    room_number = models.CharField(max_length=10)
    floor = models.IntegerField()
    wing = models.CharField(max_length=10)
    capacity = models.IntegerField(default=3)

    is_ac = models.BooleanField(default=False)  # ✅ THIS LINE MUST BE HERE

    def __str__(self):
        return self.room_number

class RoomWaitingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10)
    wing = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)



class Subscription(models.Model):

    PLAN_CHOICES = [
        ('BASIC', 'Basic'),
        ('PREMIUM', 'Premium'),
        ('VIP', 'VIP'),
    ]

    student = models.OneToOneField(Student, on_delete=models.CASCADE)

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='BASIC')

    amount_paid = models.IntegerField(default=0)

    start_date = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.plan}"


class RoomTransfer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    current_room = models.CharField(max_length=10)
    requested_room = models.CharField(max_length=10)
    reason = models.TextField()

    status = models.CharField(max_length=20, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.status}"
    
# models.py

class StudentRemovalLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    removed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True)
    removed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} removed on {self.removed_at}"