# 🏨 HostelX – Smart Hostel Management System

HostelX is a modern Django-based hostel management platform designed to simplify and automate hostel operations.

The system provides dedicated dashboards for students and wardens, enabling efficient handling of complaints, room allocation, leave requests, and hostel administration through a structured workflow system.

---

# 🚀 Key Highlights

* Role-Based Access Control
* ERP-Inspired Workflow System
* Complaint & Leave Management
* Student & Warden Dashboards
* Secure Authentication System
* Room Allocation & Transfer Handling
* CRUD Operations & Data Management
* Responsive User Interface

---

# 🔐 Role-Based Access Control

HostelX implements structured access control to ensure privacy and secure data management.

## 👮 Warden Access Rules

* Male wardens can manage male students only
* Female wardens can manage female students only

## 🎯 Data Segregation

* Student records are filtered according to hostel wings
* Prevents unauthorized cross-access between hostel sections

## 🛡 Security & Integrity

* Controlled dashboard access
* Secure authentication workflow
* Structured data visibility and handling

---

# 🧩 System Workflow

## 👨‍🎓 Student Workflow

1. Student Registration & Login
2. Dashboard Access
3. Complaint Submission
4. Leave Application
5. Room & Roommate Details
6. Complaint Tracking & Updates

## 👨‍💼 Warden Workflow

1. Secure Warden Login
2. Student Monitoring
3. Complaint Resolution
4. Leave Approval / Rejection
5. Room Transfer Management
6. Hostel Activity Monitoring

---

# 🏗 System Architecture

The application follows Django's MVT (Model-View-Template) architecture:

* **Models** → Database structure and relationships
* **Views** → Business logic and request handling
* **Templates** → Frontend UI rendering

The project uses:

* Authentication & Session Management
* Role-Based Access Logic
* Database Operations (CRUD)
* Structured URL Routing
* Dynamic Dashboard Rendering

---

# 🗄 Database Design

The system manages multiple entities including:

* Students
* Wardens
* Complaints
* Leave Applications
* Room Allocation
* Visitor Requests

SQLite is currently used for development purposes, with future scalability support for MySQL/MariaDB integration.

---

# 🚀 Features

## 👨‍🎓 Student Panel

* Student Registration & Login
* Dashboard Overview
* Roommate Details
* Raise & Track Complaints
* Leave Application System
* Fee Management

## 👨‍💼 Warden Panel

* Secure Warden Login
* Student Management
* Complaint Resolution
* Room Transfer Requests
* Visitor Request Handling
* Leave Approval System

---

# 🛠 Tech Stack

| Technology   | Usage                 |
| ------------ | --------------------- |
| Python       | Backend Logic         |
| Django       | Web Framework         |
| HTML/CSS     | Frontend UI           |
| JavaScript   | Dynamic Functionality |
| SQLite       | Database              |
| Git & GitHub | Version Control       |

---

# 📸 Screenshots

## 🔐 Authentication Module

![Role Preview](ComplainXHostel_app/static/images/screenshots/auth/role.jpeg)
![Student Login](ComplainXHostel_app/static/images/screenshots/auth/student-login.jpeg)
![Student Register](ComplainXHostel_app/static/images/screenshots/auth/student-register.jpeg)
![Warden Login](ComplainXHostel_app/static/images/screenshots/auth/warden-login.jpeg)

---

## 🎓 Student Dashboard

![Dashboard](ComplainXHostel_app/static/images/screenshots/student/student-dashboard.jpg)
![Roommate](ComplainXHostel_app/static/images/screenshots/student/roommate-details.jpg)
![Complaint](ComplainXHostel_app/static/images/screenshots/student/raise-complaint.jpg)
![Leave](ComplainXHostel_app/static/images/screenshots/student/leave-application.jpg)

---

## 🛠 Warden Dashboard

![Warden Dashboard](ComplainXHostel_app/static/images/screenshots/warden/warden-dashboard.jpg)
![Students](ComplainXHostel_app/static/images/screenshots/warden/student-management.jpg)
![Complaints](ComplainXHostel_app/static/images/screenshots/warden/complaint-management.jpg)

---

# 📂 Project Structure

```bash
HostelX/
│
├── myproject/                     # Django settings & configuration
├── ComplainXHostel_app/          # Main application
│   ├── templates/
│   ├── static/
│   │   └── images/screenshots/
│
├── media/                        # Uploaded media files
├── manage.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Installation & Setup

```bash
# Clone Repository
git clone https://github.com/your-username/HostelX.git

# Open Project
cd HostelX

# Create Virtual Environment
python -m venv myenv

# Activate Environment (Windows)
myenv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Apply Migrations
python manage.py migrate

# Run Development Server
python manage.py runserver
```

---

# 🔮 Future Improvements

* 💳 Payment Gateway Integration
* 📧 Email Notifications
* 📊 Advanced Admin Analytics Dashboard
* 📱 Improved Mobile Responsiveness
* 🌐 REST API Integration
* 🗃 MySQL/MariaDB Migration Support

---

# 👨‍💻 Author

## Abusufiyan

Aspiring Python & Frappe Developer

* GitHub: https://github.com/abusufiyan7518
* LinkedIn: https://www.linkedin.com/in/abu-sufiyan-822b9827b/

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.
