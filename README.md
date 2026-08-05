# University Attendance Management System (UAMS)

A desktop application for managing university attendance built with Python, CustomTkinter, and SQLite.

## Features

### User Authentication
- Login / Logout with role-based access
- Three roles: Admin, Teacher, Student
- Password encryption (bcrypt)

### Role-Based Access

**Admin:**
- Manage Users, Students, Teachers, Departments, Courses, Classes
- Take and view attendance
- Generate reports with export (Excel, CSV, PDF)
- Face recognition attendance
- Database backup & restore
- System settings

**Teacher:**
- Take attendance
- View attendance records
- Generate reports

**Student:**
- View personal attendance
- View profile

### Modules
- **Student Management** - Add, edit, delete, search students with photo upload
- **Teacher Management** - Add, edit, delete, assign to departments
- **Department Management** - Create, edit, delete departments
- **Course Management** - Add subjects, assign teachers, semester, credits
- **Class Management** - Create classes, assign/remove students
- **Attendance Management** - Take attendance with Present/Absent/Late/Permission status
- **Attendance Dashboard** - Real-time stats with progress bar
- **Reports** - Daily, monthly, student, teacher reports with PDF/Excel/CSV export
- **Face Recognition** - Register faces, auto-mark attendance via camera (optional)
- **Database Backup & Restore** - Manual and scheduled backups
- **System Settings** - University info, theme toggle, email SMTP config

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Installation

```bash
# Clone or navigate to the project directory
cd "School Attendence Management System"

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

For face recognition (optional):
```bash
pip install opencv-python face-recognition
```

## Usage

```bash
python main.py
```

Default login credentials:
- **Username:** `admin`
- **Password:** `admin123`

## Database

The application uses SQLite (`uams.db`). The database is created automatically on first run with all tables and a default admin user. Photos are stored in the `photos/` directory.

## Project Structure

```
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── database/
│   └── db_manager.py        # Database schema and CRUD operations
├── gui/
│   ├── login.py             # Login window
│   ├── dashboard.py         # Main navigation dashboard
│   ├── dashboard_view.py    # Attendance dashboard view
│   ├── student_management.py
│   ├── teacher_management.py
│   ├── department_management.py
│   ├── course_management.py
│   ├── class_management.py
│   ├── attendance_view.py   # Take and view attendance
│   ├── reports.py           # Report generation and export
│   ├── face_recognition_view.py
│   ├── backup_restore.py
│   └── settings_view.py
├── photos/                  # Student photos
└── backup/                  # Database backups
```

## Export Formats

Reports can be exported to:
- **Excel** (.xlsx) via openpyxl
- **CSV** via pandas
- **PDF** via reportlab

## Face Recognition

The face recognition module requires OpenCV and face_recognition libraries. When enabled:
1. Register a student's face via camera
2. Start face recognition attendance
3. The system automatically detects and marks recognized students as Present
