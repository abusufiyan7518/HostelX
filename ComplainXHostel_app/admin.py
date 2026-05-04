from django.contrib import admin
from .models import Student, Complaint, Visitor, Payment, Warden

# ================= STUDENT =================
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'get_room',
        'wing',
        'contact',
        'is_active'
    )

    def get_room(self, obj):
        return obj.room.room_number if obj.room else "Not Assigned"

    get_room.short_description = "Room"


# ================= COMPLAINT =================
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'category', 'status', 'date')
    list_filter = ('status', 'category')
    search_fields = ('title',)


# ================= VISITOR =================
@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'student', 'relation', 'contact', 'status', 'visit_date')
    list_filter = ('status', 'relation')


# ================= PAYMENT =================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'method', 'status', 'created_at')


# ================= WARDEN =================
@admin.register(Warden)
class WardenAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'contact')


from django.contrib import admin
from .models import Room
from .services.room_generator import generate_hostel_rooms
from django.http import HttpResponseRedirect
from django.urls import path

from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages

from .models import Room

class RoomAdmin(admin.ModelAdmin):
    change_list_template = "admin/room_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("generate-rooms/", self.generate_rooms),
        ]
        return custom_urls + urls

    def generate_rooms(self, request):
        from .services.room_engine import generate_rooms_bulk

        try:
            generate_rooms_bulk()
            self.message_user(request, "Rooms generated successfully ✅", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error: {str(e)}", messages.ERROR)

        return redirect("../")

admin.site.register(Room, RoomAdmin)