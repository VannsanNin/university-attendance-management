import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from datetime import date
from gui import theme
from gui.sidebar import Sidebar
from gui.activity import log

class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.db = DatabaseManager()
        self.title("UAMS - Dashboard")
        self.attributes("-zoomed", True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.sidebar = Sidebar(
            self,
            user=self.user,
            on_navigate=self.show_frame,
            on_change_password=self.change_password,
            on_logout=self.logout,
        )

        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=theme.c("bg_dark"))
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.frames = {}
        self.current_view = "dashboard"
        self.show_frame("dashboard")

    def apply_theme(self):
        """Rebuild sidebar + current view after the theme mode changes."""
        self.sidebar.apply_theme()
        self.content_frame.configure(fg_color=theme.c("bg_dark"))
        self.show_frame(self.current_view)

    def show_frame(self, name):
        self.current_view = name
        self.sidebar.set_active(name)

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        from gui.dashboard_view import DashboardView
        from gui.student_management import StudentManagementView
        from gui.teacher_management import TeacherManagementView
        from gui.department_management import DepartmentManagementView
        from gui.course_management import CourseManagementView
        from gui.class_management import ClassManagementView
        from gui.attendance_view import AttendanceView, AttendanceTakeView
        from gui.attendance_requests_view import AttendanceRequestsView
        from gui.activity_log_view import ActivityLogView
        from gui.reports import ReportsView
        from gui.settings_view import SettingsView
        from gui.user_management import UserManagementView
        from gui.academic_year_view import AcademicYearView
        from gui.profile import AdminProfileView, TeacherProfileView, StudentProfileView
        from gui.teacher_classes_view import TeacherClassesView
        from gui.student_subjects_view import StudentSubjectsView
        from gui.student_report_view import StudentReportView

        views = {
            "dashboard": (DashboardView, [self.user, self.db, self.content_frame, self.show_frame]),
            "users": (UserManagementView, [self.db, self.content_frame, self.user]),
            "students": (StudentManagementView, [self.db, self.content_frame, self.user]),
            "teachers": (TeacherManagementView, [self.db, self.content_frame, self.user]),
            "departments": (DepartmentManagementView, [self.db, self.content_frame, self.user]),
            "courses": (CourseManagementView, [self.db, self.content_frame, self.user]),
            "classes": (ClassManagementView, [self.db, self.content_frame, self.user]),
            "attendance": (AttendanceTakeView, [self.user, self.db, self.content_frame]),
            "reports": (ReportsView, [self.db, self.content_frame]),
            "academic_year": (AcademicYearView, [self.db, self.content_frame, self.user]),
            "settings": (SettingsView, [self.db, self.content_frame, self]),
            "take_attendance": (AttendanceTakeView, [self.user, self.db, self.content_frame]),
            "attendance_view": (AttendanceView, [self.db, self.content_frame]),
            "attendance_requests": (AttendanceRequestsView, [self.db, self.content_frame, self.user]),
            "activity_logs": (ActivityLogView, [self.db, self.content_frame, self.user]),
            "attendance_report": (StudentReportView, [self.db, self.content_frame, self.user]),
            "my_attendance": (AttendanceView, [self.db, self.content_frame, self.user]),
            "my_subjects": (StudentSubjectsView, [self.db, self.content_frame, self.user]),
            "my_classes": (TeacherClassesView, [self.db, self.content_frame, self.user]),
            "admin_profile": (AdminProfileView, [self.db, self.content_frame, self.user, self]),
            "teacher_profile": (TeacherProfileView, [self.db, self.content_frame, self.user, self]),
            "student_profile": (StudentProfileView, [self.db, self.content_frame, self.user, self]),
            "my_courses": (MyCoursesView, [self.db, self.content_frame, self.user]),
        }

        if name in views:
            cls, args = views[name]
            frame = cls(*args)
            if hasattr(frame, 'pack'):
                frame.pack(fill="both", expand=True)
            self.frames[name] = frame

    def change_password(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Change Password")
        dialog.geometry("350x250")

        ctk.CTkLabel(dialog, text="Change Password", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        ctk.CTkLabel(dialog, text="Current Password:").pack()
        old_e = ctk.CTkEntry(dialog, width=250, show="*")
        old_e.pack(pady=5)

        ctk.CTkLabel(dialog, text="New Password:").pack()
        new_e = ctk.CTkEntry(dialog, width=250, show="*")
        new_e.pack(pady=5)

        ctk.CTkLabel(dialog, text="Confirm New Password:").pack()
        confirm_e = ctk.CTkEntry(dialog, width=250, show="*")
        confirm_e.pack(pady=5)

        def save():
            old = old_e.get()
            new = new_e.get()
            confirm = confirm_e.get()
            if not old or not new:
                messagebox.showerror("Error", "Fill all fields")
                return
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match")
                return
            if len(new) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return
            if self.db.change_password(self.user["id"], old, new):
                log(self.db, self.user, "CHANGE_PASSWORD", "Auth",
                    f"User '{self.user['username']}' changed their password.")
                messagebox.showinfo("Success", "Password changed successfully")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Current password is incorrect")

        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=10)

    def logout(self):
        from utils.session import clear_session

        log(self.db, self.user, "LOGOUT", "Auth", f"User '{self.user['username']}' logged out.")
        clear_session()
        self.destroy()
        self.parent.apply_theme()
        self.parent.deiconify()

    def on_close(self):
        log(self.db, self.user, "LOGOUT", "Auth", f"User '{self.user['username']}' closed the session.")
        self.destroy()
        self.parent.apply_theme()
        self.parent.deiconify()


class MyCoursesView(ctk.CTkFrame):
    def __init__(self, db, parent, user):
        super().__init__(parent, fg_color=theme.c("bg_dark"))
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="My Courses",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        conn = db.get_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT t.id FROM teachers t WHERE t.user_id=?""", (user["id"],))
        teacher = cursor.fetchone()
        conn.close()

        if not teacher:
            ctk.CTkLabel(self, text="Teacher profile not linked to this account.",
                         font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        courses = db.get_courses(teacher_id=teacher["id"])
        if not courses:
            ctk.CTkLabel(self, text="No courses assigned to you.",
                         font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        for c in courses:
            card = ctk.CTkFrame(self, fg_color=theme.c("card_alt"), corner_radius=8,
                                border_width=1, border_color=theme.c("border_alt"))
            card.pack(fill="x", padx=40, pady=5)

            info = f"{c['course_code']} - {c['course_name']}"
            if c.get("semester"):
                info += f" | Semester: {c['semester']}"
            if c.get("credit"):
                info += f" | Credit: {c['credit']}"

            ctk.CTkLabel(card, text=info, font=ctk.CTkFont(size=14),
                         anchor="w").pack(side="left", padx=15, pady=10)
