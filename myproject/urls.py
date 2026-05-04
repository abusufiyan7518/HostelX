# """
# URL configuration for myproject project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/6.0/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path
# from . import views
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', views.RoleBased, name='RoleBased'),
#     path('Student_login/', views.Student_login, name='Student_login'),
#     path('Student_register/', views.Student_register, name='Student_register'),
#     path('home/', views.home, name='home'),

#     # Sidenav routes
#     path('dashboard/', views.dashboard, name='dashboard'),
#     path('view-room/', views.view_room, name='view_room'),
#     path('request-transfer/', views.request_transfer, name='request_transfer'),
#     path('fee-status/', views.fee_status, name='fee_status'),
#     path('pay-fees/', views.pay_fees, name='pay_fees'),
#     path('download-receipt/', views.download_receipt, name='download_receipt'),
#     path('raise-complaint/', views.raise_complaint, name='raise_complaint'),
#     path('my-complaints/', views.my_complaints, name='my_complaints'),
#     path('visitor-entry/', views.visitor_entry, name='visitor_entry'),
#     path('notifications/', views.notifications, name='notifications'),
#     path('profile/', views.profile, name='profile'),
#     path('logout/', views.logout_view, name='logout'),
# ]


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # ✅ admin working
    path('', include('ComplainXHostel_app.urls')),  # ✅ app routing
]

# media files (for Aadhaar upload)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
