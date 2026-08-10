import os

import customtkinter as ctk
from PIL import Image
from tkinter import messagebox

from gui import theme


def _fmt(value):
    return str(value) if value not in (None, "") else "N/A"


def _initials(name):
    if not name:
        return "?"
    parts = [p for p in str(name).replace(".", " ").split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _load_photo(photo_path, size=88):
    if photo_path and os.path.exists(photo_path):
        try:
            img = Image.open(photo_path).convert("RGB")
            return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
        except Exception:
            return None
    return None


def _attendance_status(pct):
    if pct >= 85:
        return "Excellent", theme.c("success")
    if pct >= 75:
        return "Good", theme.c("success")
    if pct >= 60:
        return "Warning", theme.c("warning")
    return "At Risk", theme.c("danger")


class BaseProfileView(ctk.CTkFrame):
    def __init__(self, db, parent, user, dashboard):
        super().__init__(parent, fg_color=theme.c("bg_dark"), corner_radius=0)
        self.db = db
        self.user = user
        self.dashboard = dashboard
        self.pack(fill="both", expand=True)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=4)

        self._refresh()

    # ---- helpers ----------------------------------------------------------
    def _refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self._render()

    def _header_card(self, name, subtitle, photo_path=None, accent=None):
        accent = accent or theme.c("primary")
        card = ctk.CTkFrame(self.scroll, fg_color=theme.c("card_bg"),
                            corner_radius=16, border_width=1, border_color=theme.c("border"))
        card.pack(fill="x", padx=20, pady=(20, 16))

        # thin accent strip along the top of the card for a bit of identity
        ctk.CTkFrame(card, fg_color=accent, height=3, corner_radius=0
                     ).pack(fill="x", side="top")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=(20, 20))
        inner.grid_columnconfigure(1, weight=1)

        avatar = ctk.CTkFrame(inner, width=76, height=76, corner_radius=38,
                              fg_color=accent)
        avatar.grid(row=0, column=0, rowspan=2, padx=(0, 18))
        avatar.grid_propagate(False)
        photo = _load_photo(photo_path, 76)
        if photo:
            ctk.CTkLabel(avatar, text="", image=photo).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(avatar, text=_initials(name),
                         font=ctk.CTkFont(size=24, weight="bold"),
                         text_color=theme.c("text_bright")).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(inner, text=name, font=ctk.CTkFont(size=21, weight="bold"),
                     text_color=theme.c("text_bright"), anchor="w"
                     ).grid(row=0, column=1, sticky="w")
        if subtitle:
            ctk.CTkLabel(inner, text=subtitle, font=ctk.CTkFont(size=12),
                         text_color=theme.c("text_muted"), anchor="w"
                         ).grid(row=1, column=1, sticky="w", pady=(3, 0))

        return card

    def _header_buttons(self, card, show_edit=True, edit_cb=None):
        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(fill="x", padx=24, pady=(0, 20))

        if show_edit and edit_cb:
            ctk.CTkButton(btns, text="Edit Profile", width=136, height=34, corner_radius=8,
                          font=ctk.CTkFont(size=12, weight="bold"),
                          fg_color=theme.c("primary"), hover_color=theme.c("primary_hover"),
                          command=edit_cb).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btns, text="Change Password", width=150, height=34, corner_radius=8,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      fg_color="transparent", hover_color=theme.c("neutral_hover"),
                      border_width=1, border_color=theme.c("border"),
                      text_color=theme.c("text_bright"),
                      command=self.dashboard.change_password).pack(side="left")

    def _stat_row(self, stats):
        """stats: list of (label, value) tuples rendered as a row of compact stat tiles."""
        row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 16))
        for i, (label, value) in enumerate(stats):
            tile = ctk.CTkFrame(row, fg_color=theme.c("card_bg"), corner_radius=12,
                                border_width=1, border_color=theme.c("border"))
            tile.grid(row=0, column=i, sticky="nsew", padx=(0, 10) if i < len(stats) - 1 else 0)
            row.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(tile, text=str(value), font=ctk.CTkFont(size=20, weight="bold"),
                         text_color=theme.c("text_bright")).pack(anchor="w", padx=16, pady=(14, 0))
            ctk.CTkLabel(tile, text=label, font=ctk.CTkFont(size=11),
                         text_color=theme.c("text_muted")).pack(anchor="w", padx=16, pady=(1, 14))

    def _section_card(self, title, subtitle=None, accent=None):
        card = ctk.CTkFrame(self.scroll, fg_color=theme.c("card_bg"),
                            corner_radius=14, border_width=1, border_color=theme.c("border"))
        card.pack(fill="x", padx=20, pady=(0, 14))

        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=(16, 4))
        head.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(head, width=3, height=16, corner_radius=2,
                    fg_color=accent or theme.c("primary")).grid(row=0, column=0, rowspan=2,
                                                                  sticky="ns", padx=(0, 8))
        ctk.CTkLabel(head, text=title, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright"), anchor="w").grid(row=0, column=1, sticky="w")
        if subtitle:
            ctk.CTkLabel(head, text=subtitle, font=ctk.CTkFont(size=11),
                         text_color=theme.c("text_muted"), anchor="w").grid(row=1, column=1, sticky="w")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=20, pady=(6, 16))
        return body

    def _field(self, body, label, value, value_color=None, mono=False, last=False):
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12), width=175, anchor="w",
                     text_color=theme.c("text_muted")).grid(row=0, column=0, sticky="w", pady=8)
        ctk.CTkLabel(row, text=_fmt(value),
                     font=ctk.CTkFont(size=12, family="Consolas" if mono else None,
                                       weight="bold" if value_color else "normal"),
                     anchor="w", text_color=value_color or theme.c("text_bright")
                     ).grid(row=0, column=1, sticky="w", pady=8)
        if not last:
            ctk.CTkFrame(body, fg_color=theme.c("border"), height=1
                         ).pack(fill="x")

    def _status_pill(self, parent, text, color):
        pill = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=10,
                            border_width=1, border_color=color, height=24)
        ctk.CTkLabel(pill, text=text, font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=color).pack(padx=10, pady=2)
        return pill

    def _progress_field(self, body, label, pct, color, last=False):
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x", pady=8)
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12), width=175, anchor="w",
                     text_color=theme.c("text_muted")).grid(row=0, column=0, sticky="w")

        bar_wrap = ctk.CTkFrame(row, fg_color="transparent")
        bar_wrap.grid(row=0, column=1, sticky="ew")
        bar_wrap.grid_columnconfigure(0, weight=1)
        bar = ctk.CTkProgressBar(bar_wrap, height=8, corner_radius=4,
                                 fg_color=theme.c("bg_dark"), progress_color=color)
        bar.set(max(0, min(pct, 100)) / 100)
        bar.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ctk.CTkLabel(bar_wrap, text=f"{pct}%", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=color, width=40, anchor="e").grid(row=0, column=1, sticky="e")
        if not last:
            ctk.CTkFrame(body, fg_color=theme.c("border"), height=1).pack(fill="x")

    def _account_section(self, account):
        is_active = account.get("is_active", 1)
        status = "Active" if is_active in (1, "1", True) else "Inactive"
        body = self._section_card("Account", "Sign-in credentials and security")
        self._field(body, "Username", account.get("username"), mono=True)
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text="Account Status", font=ctk.CTkFont(size=12), width=175, anchor="w",
                     text_color=theme.c("text_muted")).grid(row=0, column=0, sticky="w", pady=8)
        pill = self._status_pill(row, status,
                                 theme.c("success") if status == "Active" else theme.c("danger"))
        pill.grid(row=0, column=1, sticky="w", pady=8)
        ctk.CTkFrame(body, fg_color=theme.c("border"), height=1).pack(fill="x")
        self._field(body, "Last Login", account.get("last_login"), last=True)

    def _edit_dialog(self, title, fields, on_save):
        dialog = ctk.CTkToplevel(self.winfo_toplevel())
        dialog.title(title)
        dialog.geometry("440x560")
        dialog.configure(fg_color=theme.c("bg_dark"))
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=title, font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=theme.c("text_bright")).pack(anchor="w", padx=22, pady=(18, 0))

        body = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=14)

        entries = {}
        for key, label, initial in fields:
            ctk.CTkLabel(body, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=theme.c("text_muted")).pack(anchor="w", pady=(10, 4))
            e = ctk.CTkEntry(body, height=36, corner_radius=8,
                             border_color=theme.c("border"))
            e.insert(0, str(initial) if initial not in (None, "") else "")
            e.pack(fill="x")
            entries[key] = e

        def save():
            values = {k: e.get().strip() for k, e in entries.items()}
            on_save(values, dialog)

        ctk.CTkButton(dialog, text="Save Changes", height=40, corner_radius=8,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      fg_color=theme.c("primary"), hover_color=theme.c("primary_hover"),
                      command=save).pack(fill="x", padx=18, pady=(0, 18))


class AdminProfileView(BaseProfileView):
    def __init__(self, db, parent, user, dashboard):
        super().__init__(db, parent, user, dashboard)

    def _render(self):
        account = self.db.get_user_by_username(self.user["username"]) or self.user
        accent = theme.c("primary")

        card = self._header_card(account.get("username", "Administrator"),
                                 "Administrator  \u2022  System Manager",
                                 photo_path=None, accent=accent)
        self._header_buttons(card, show_edit=True, edit_cb=self._edit_profile)

        # System Activity counts (pulled up front as quick stats)
        conn = self.db.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM students")
        student_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM teachers")
        teacher_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM courses")
        course_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM attendance")
        att_count = cur.fetchone()[0]
        conn.close()

        self._stat_row([
            ("Users", user_count),
            ("Students", student_count),
            ("Teachers", teacher_count),
            ("Courses", course_count),
        ])

        # Personal Information
        body = self._section_card("Personal Information", "Account holder details", accent)
        self._field(body, "Admin ID", "ADMIN-1", mono=True)
        self._field(body, "Full Name", account.get("username"))
        self._field(body, "Role", "Administrator")
        self._field(body, "Email Address", account.get("email"))
        self._field(body, "Phone Number", account.get("phone"), last=True)

        # Administration Information
        body = self._section_card("Administration Information", "Access and responsibility", accent)
        self._field(body, "Department", _fmt(self.db.get_setting("university_name")) or "System Administration")
        self._field(body, "Position", "System Administrator")
        self._field(body, "Permissions", "Users, students, teachers, courses, classes, attendance, reports, settings")
        is_active = account.get("is_active", 1)
        status = "Active" if is_active in (1, "1", True) else "Inactive"
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text="Account Status", font=ctk.CTkFont(size=12), width=175, anchor="w",
                     text_color=theme.c("text_muted")).grid(row=0, column=0, sticky="w", pady=8)
        self._status_pill(row, status,
                          theme.c("success") if status == "Active" else theme.c("danger")
                          ).grid(row=0, column=1, sticky="w", pady=8)

        # System Activity detail
        body = self._section_card("System Activity", "Platform usage overview", accent)
        self._field(body, "Last Login", account.get("last_login"))
        self._field(body, "Last Activity", account.get("last_login"))
        self._field(body, "Attendance Records", att_count, last=True)

        self._account_section(account)

    def _edit_profile(self):
        account = self.db.get_user_by_username(self.user["username"]) or self.user

        def on_save(values, dialog):
            email = values.get("email")
            phone = values.get("phone")
            conn = self.db.get_conn()
            cur = conn.cursor()
            cur.execute("UPDATE users SET email=?, phone=? WHERE id=?", (email or None, phone or None, self.user["id"]))
            conn.commit()
            conn.close()
            dialog.destroy()
            messagebox.showinfo("Success", "Profile updated successfully.")
            self._refresh()

        self._edit_dialog("Edit Admin Profile", [
            ("email", "Email Address", account.get("email")),
            ("phone", "Phone Number", account.get("phone")),
        ], on_save)


class TeacherProfileView(BaseProfileView):
    def __init__(self, db, parent, user, dashboard):
        super().__init__(db, parent, user, dashboard)

    def _render(self):
        account = self.db.get_user_by_username(self.user["username"]) or self.user
        teacher = self.db.get_teacher_by_user_id(self.user["id"])

        if not teacher:
            ctk.CTkLabel(self.scroll, text="Teacher profile not found. Please contact an administrator.",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=theme.c("danger")).pack(pady=60)
            return

        accent = theme.c("primary")
        card = self._header_card(teacher.get("full_name") or "Teacher",
                                 f"{teacher.get('teacher_id', '')}  \u2022  {_fmt(teacher.get('department_name'))}",
                                 photo_path=None, accent=accent)
        self._header_buttons(card, show_edit=True, edit_cb=self._edit_profile)

        courses = self.db.get_courses(teacher_id=teacher["id"])

        conn = self.db.get_conn()
        cur = conn.cursor()
        course_ids = [c["id"] for c in courses]
        my_classes = [c for c in self.db.get_classes() if c.get("teacher_id") == teacher["id"]]
        classes_conducted = records = students_managed = 0
        if course_ids:
            placeholders = ",".join("?" * len(course_ids))
            cur.execute(f"SELECT COUNT(DISTINCT attendance_date) FROM attendance WHERE course_id IN ({placeholders})", course_ids)
            classes_conducted = cur.fetchone()[0] or 0
            cur.execute(f"SELECT COUNT(*) FROM attendance WHERE course_id IN ({placeholders})", course_ids)
            records = cur.fetchone()[0] or 0
            cur.execute(f"SELECT COUNT(DISTINCT student_id) FROM attendance WHERE course_id IN ({placeholders})", course_ids)
            students_managed = cur.fetchone()[0] or 0
        conn.close()

        self._stat_row([
            ("Total Classes", len(my_classes)),
            ("Conducted", classes_conducted),
            ("Records", records),
            ("Students", students_managed),
        ])

        # Personal Information
        body = self._section_card("Personal Information", "Faculty contact details", accent)
        self._field(body, "Teacher ID", teacher.get("teacher_id"), mono=True)
        self._field(body, "Full Name", teacher.get("full_name"))
        self._field(body, "Gender", teacher.get("gender"))
        self._field(body, "Date of Birth", teacher.get("dob"))
        self._field(body, "Email Address", teacher.get("email"))
        self._field(body, "Phone Number", teacher.get("phone"))
        self._field(body, "Address", teacher.get("address"), last=True)

        # Professional Information
        body = self._section_card("Professional Information", "Teaching assignment", accent)
        self._field(body, "Department", teacher.get("department_name"))
        self._field(body, "Position", teacher.get("position"))
        self._field(body, "Courses Assigned", ", ".join(
            c["course_code"] for c in courses) or "None", last=True)

        self._account_section(account)

    def _edit_profile(self):
        teacher = self.db.get_teacher_by_user_id(self.user["id"])
        if not teacher:
            return

        def on_save(values, dialog):
            self.db.update_teacher(
                teacher["teacher_id"],
                full_name=values.get("full_name") or None,
                gender=values.get("gender") or None,
                email=values.get("email") or None,
                phone=values.get("phone") or None,
                address=values.get("address") or None,
                position=values.get("position") or None,
            )
            dialog.destroy()
            messagebox.showinfo("Success", "Profile updated successfully.")
            self._refresh()

        self._edit_dialog("Edit Teacher Profile", [
            ("full_name", "Full Name", teacher.get("full_name")),
            ("gender", "Gender", teacher.get("gender")),
            ("email", "Email Address", teacher.get("email")),
            ("phone", "Phone Number", teacher.get("phone")),
            ("address", "Address", teacher.get("address")),
            ("position", "Position", teacher.get("position")),
        ], on_save)


class StudentProfileView(BaseProfileView):
    def __init__(self, db, parent, user, dashboard):
        super().__init__(db, parent, user, dashboard)

    def _render(self):
        account = self.db.get_user_by_username(self.user["username"]) or self.user
        student = self.db.get_student_by_user_id(self.user["id"])

        if not student:
            ctk.CTkLabel(self.scroll, text="Student profile not found. Please contact an administrator.",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=theme.c("danger")).pack(pady=60)
            return

        summary = self.db.get_attendance_summary(student_id=student["id"])
        pct = summary.get("percentage", 0) or 0
        status_text, status_color = _attendance_status(pct)

        card = self._header_card(student.get("full_name") or "Student",
                                 f"{student.get('student_id', '')}  \u2022  {_fmt(student.get('department_name'))}",
                                 photo_path=student.get("photo_path"), accent=status_color)
        self._header_buttons(card, show_edit=True, edit_cb=self._edit_profile)

        self._stat_row([
            ("Total Classes", summary.get("total", 0)),
            ("Attended", summary.get("present_count", 0) + summary.get("late_count", 0)),
            ("Absent", summary.get("absent_count", 0)),
            ("Late", summary.get("late_count", 0)),
        ])

        # Personal Information
        body = self._section_card("Personal Information", "Contact and identity details", status_color)
        self._field(body, "Student ID", student.get("student_id"), mono=True)
        self._field(body, "Full Name", student.get("full_name"))
        self._field(body, "Gender", student.get("gender"))
        self._field(body, "Date of Birth", student.get("dob"))
        self._field(body, "Email Address", student.get("email"))
        self._field(body, "Phone Number", student.get("phone"))
        self._field(body, "Address", student.get("address"), last=True)

        # Academic Information
        body = self._section_card("Academic Information", "Enrolment details", status_color)
        self._field(body, "Department", student.get("department_name"))
        self._field(body, "Program", student.get("program"))
        self._field(body, "Year", student.get("year"))
        self._field(body, "Semester", student.get("semester"))
        self._field(body, "Class", student.get("class_name"))
        self._field(body, "Academic Year", self.db.get_setting("academic_year"))
        self._field(body, "Enrollment Date", student.get("created_at"), last=True)

        # Attendance Summary
        body = self._section_card("Attendance Summary", "Current participation overview", status_color)
        self._progress_field(body, "Attendance", pct, status_color)
        row = ctk.CTkFrame(body, fg_color="transparent")
        row.pack(fill="x")
        row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(row, text="Current Status", font=ctk.CTkFont(size=12), width=175, anchor="w",
                     text_color=theme.c("text_muted")).grid(row=0, column=0, sticky="w", pady=8)
        self._status_pill(row, status_text, status_color).grid(row=0, column=1, sticky="w", pady=8)
        ctk.CTkFrame(body, fg_color=theme.c("border"), height=1).pack(fill="x")
        self._field(body, "Classes Absent", summary.get("absent_count", 0))
        self._field(body, "Late Arrivals", summary.get("late_count", 0), last=True)

        self._account_section(account)

    def _edit_profile(self):
        student = self.db.get_student_by_user_id(self.user["id"])
        if not student:
            return

        def on_save(values, dialog):
            self.db.update_student(
                student["student_id"],
                full_name=values.get("full_name") or None,
                gender=values.get("gender") or None,
                email=values.get("email") or None,
                phone=values.get("phone") or None,
                address=values.get("address") or None,
                program=values.get("program") or None,
            )
            dialog.destroy()
            messagebox.showinfo("Success", "Profile updated successfully.")
            self._refresh()

        self._edit_dialog("Edit Student Profile", [
            ("full_name", "Full Name", student.get("full_name")),
            ("gender", "Gender", student.get("gender")),
            ("email", "Email Address", student.get("email")),
            ("phone", "Phone Number", student.get("phone")),
            ("address", "Address", student.get("address")),
            ("program", "Program", student.get("program")),
        ], on_save)