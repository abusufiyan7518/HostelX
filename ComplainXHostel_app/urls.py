from django.urls import path
from . import views

urlpatterns = [

    # ================= ROLE =================
    path('', views.role_select, name='role_select'),

    # ================= AUTH =================
    path('login/', views.login_view, name='student_login'),
    
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ================= STUDENT =================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('view-room/', views.view_room, name='view_room'),

    # ================= FEES =================
    path('fee-status/', views.fee_status, name='fee_status'),
    

    # ================= COMPLAINTS =================
    path('raise-complaint/', views.raise_complaint, name='raise_complaint'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),

    path('warden/complaints/', views.warden_complaints, name='warden_complaints'),
    
    # ================= VISITOR =================
    path('visitor/', views.visitor, name='visitor'),
    path('warden/visitors/', views.warden_visitors, name='warden_visitors'),
    path('approve-visitor/<int:id>/', views.approve_visitor, name='approve_visitor'),
    path('reject-visitor/<int:id>/', views.reject_visitor, name='reject_visitor'),

    # ================= TRANSFER =================
    path('request-transfer/', views.request_transfer, name='request_transfer'),
    path('warden/transfers/', views.warden_transfers, name='warden_transfers'),
    path('approve-transfer/<int:id>/', views.approve_transfer, name='approve_transfer'),
    path('reject-transfer/<int:id>/', views.reject_transfer, name='reject_transfer'),



    # ================= WARDEN =================
    path('warden/dashboard/', views.warden_dashboard, name='warden_dashboard'),

    # ================= API =================
    path('notifications/', views.notification_data, name='notifications'),

    path('warden/fees/', views.warden_fee_dashboard, name='warden_fee_dashboard'),

    # path('students/', views.warden_students, name='warden_students'),

   path('warden/rooms/', views.warden_rooms, name='warden_rooms'),

   path('warden/students/', views.all_students, name='warden_students'),

   path('check-room/', views.check_room, name='check_room'),


   path("api/rooms/status/", views.room_status_api, name="room_status_api"),

   path('warden/rooms/live/', views.room_live_dashboard, name='room_live'),

   path("room-details/<int:room_id>/", views.room_details, name="room_details"),

   path('profile/upload/', views.update_profile_pic, name='update_profile_pic'),

   path('warden/login/', views.warden_login, name='warden_login'),
   
   path("shift-student/", views.shift_student, name="shift_student"),

   path('subscription/', views.subscription_page, name='subscription_page'),
   path('upgrade-plan/', views.upgrade_plan, name='upgrade_plan'),
   path("apply-leave/", views.apply_leave, name="apply_leave"),
   path("my-leaves/", views.my_leave, name="my_leave"),

   path("warden/leaves/", views.manage_leaves, name="manage_leaves"),

   path("leave/approve/<int:id>/", views.approve_leave, name="approve_leave"),
   path("leave/reject/<int:id>/", views.reject_leave, name="reject_leave"),
   path("update-leave-status/", views.update_leave_status, name="update_leave_status"),

   path("update-complaint-status/", views.update_complaint_status, name="update_complaint_status"),

   path("remove-student/<int:id>/", views.remove_student, name="remove_student"),
   path("assign-room/<int:student_id>/", views.assign_room_manual, name="assign_room_manual"),
   

   path("removal-history/", views.removal_history, name="removal_history"),

   path("create-order/", views.create_order, name="create_order"),
   path("payment-success/", views.payment_success, name="payment_success"),
   path("payment-failed/", views.payment_failed, name="payment_failed"),

   path("invoice/<int:payment_id>/", views.download_invoice, name="download_invoice"),

]


