import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import date

from gui import theme
from gui.activity import log
from gui.skeleton import schedule_table_load, safe_grab

STATUS_COLORS = {
    "Pending": theme.c("warning"),
    "Approved": theme.c("success"),
    "Rejected": theme.c("danger"),
}


class AttendanceRequestsView(ctk.CTkFrame):
    """Student-facing request submission + admin/teacher review of requests."""

    def __init__(self, db, parent, user=None):
        super().__init__(parent, fg_color=theme.c("bg_dark"))
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)

        self.colors = theme.colors
        self.is_student = bool(user and user.get("role") == "student")

        self._build_header()
        self._build_filters()
        self._build_table()

    # -------------------------------------------------------------
    # Header
    # -------------------------------------------------------------
    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = "My Attendance Requests" if self.is_student else "Attendance Requests"
        ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(side="left")

        if self.is_student:
            ctk.CTkButton(
                header_frame,
                text="+ New Request",
                command=self._new_request_dialog,
                fg_color=self.colors["primary"],
                hover_color=self.colors["primary_hover"],
                height=36,
                corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="right", padx=4)
        else:
            ctk.CTkButton(
                header_frame,
                text="\u2705 Approve Selected",
                command=self._approve_selected,
                fg_color=self.colors["success"],
                hover_color=self.colors["success_hover"],
                height=36,
                corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="right", padx=4)

            ctk.CTkButton(
                header_frame,
                text="\u274C Reject Selected",
                command=self._reject_selected,
                fg_color=self.colors["danger"],
                hover_color=self.colors["danger_hover"],
                height=36,
                corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="right", padx=4)

    # -------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------
    def _build_filters(self):
        if self.is_student:
            return

        filter_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        filter_card.pack(fill="x", padx=30, pady=(5, 15))

        inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        inner.pack(padx=20, pady=15, fill="x")

        ctk.CTkLabel(inner, text="Status:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=self.colors["text_muted"]).pack(side="left", padx=(8, 4))

        self.status_combo = ctk.CTkComboBox(
            inner, width=140, height=36, corner_radius=8,
            values=["All", "Pending", "Approved", "Rejected"]
        )
        self.status_combo.set("Pending")
        self.status_combo.pack(side="left", padx=2)
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self.load_requests())

        ctk.CTkButton(
            inner,
            text="Reset",
            command=self.reset_filters,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=2)

    def reset_filters(self):
        self.status_combo.set("Pending")
        self.load_requests()

    # -------------------------------------------------------------
    # Table
    # -------------------------------------------------------------
    def _build_table(self):
        table_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self.table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(15, 15))

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Requests.Treeview",
            background=theme.c("table_bg"),
            foreground=theme.c("table_fg"),
            fieldbackground=theme.c("table_bg"),
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Requests.Treeview.Heading",
            background=theme.c("table_head_bg"),
            foreground=theme.c("table_head_fg"),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "Requests.Treeview",
            background=[("selected", theme.c("table_selected"))],
            foreground=[("selected", theme.c("table_selected_fg"))]
        )
        style.map(
            "Requests.Treeview.Heading",
            background=[("active", theme.c("table_head_active"))]
        )

        if self.is_student:
            columns = ("date", "course", "type", "reason", "status", "submitted")
        else:
            columns = ("date", "sid", "student", "course", "type", "reason", "status", "submitted")

        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings",
                                 style="Requests.Treeview", selectmode="browse")

        if self.is_student:
            headings = {
                "date": ("Date", 110),
                "course": ("Course", 150),
                "type": ("Type", 100),
                "reason": ("Reason", 260),
                "status": ("Status", 100),
                "submitted": ("Submitted", 150),
            }
        else:
            headings = {
                "date": ("Date", 100),
                "sid": ("Student ID", 100),
                "student": ("Student Name", 180),
                "course": ("Course", 140),
                "type": ("Type", 90),
                "reason": ("Reason", 220),
                "status": ("Status", 90),
                "submitted": ("Submitted", 140),
            }

        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, minwidth=width, stretch=True, anchor="w")

        scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("Pending", foreground=STATUS_COLORS.get("Pending", ""))
        self.tree.tag_configure("Approved", foreground=STATUS_COLORS.get("Approved", ""))
        self.tree.tag_configure("Rejected", foreground=STATUS_COLORS.get("Rejected", ""))

        schedule_table_load(self, self.table_frame, self.load_requests)

    # -------------------------------------------------------------
    # Data loading
    # -------------------------------------------------------------
    def _scope(self):
        if self.is_student:
            student = self.db.get_student_by_user_id(self.user["id"])
            return {"student_id": student["id"]} if student else {}
        if self.user and self.user.get("role") == "teacher":
            teacher = self.db.get_teacher_by_user_id(self.user["id"])
            if teacher:
                courses = self.db.get_courses(teacher_id=teacher["id"])
                if courses:
                    return {"course_ids": [c["id"] for c in courses]}
        return {}

    def load_requests(self):
        self.tree.delete(*self.tree.get_children())

        kwargs = self._scope()
        status = getattr(self, "status_combo", None)
        if status and status.get() and status.get() != "All":
            kwargs["status"] = status.get()

        records = self.db.get_attendance_requests(**kwargs)

        for r in records:
            status = r.get("status", "Pending")
            tag = status if status in STATUS_COLORS else ""
            course = r.get("course_code") or "\u2014"
            if self.is_student:
                values = (
                    r.get("request_date", ""),
                    course,
                    r.get("request_type", ""),
                    r.get("reason", "") or "\u2014",
                    status,
                    (r.get("created_at") or "")[:16],
                )
            else:
                values = (
                    r.get("request_date", ""),
                    r.get("sid", "") or "\u2014",
                    r.get("student_name", "") or "\u2014",
                    course,
                    r.get("request_type", ""),
                    r.get("reason", "") or "\u2014",
                    status,
                    (r.get("created_at") or "")[:16],
                )
            self.tree.insert("", "end", iid=str(r["id"]), values=values, tags=(tag,))

    # -------------------------------------------------------------
    # Student: new request
    # -------------------------------------------------------------
    def _get_student(self):
        return self.db.get_student_by_user_id(self.user["id"]) if self.is_student else None

    def _new_request_dialog(self):
        student = self._get_student()
        if not student:
            messagebox.showerror("Error", "Student profile not linked to this account. Contact the administrator.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Request Attendance")
        dialog.geometry("460x620")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        safe_grab(dialog)

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text="Request Attendance",
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(16, 4))

        ctk.CTkLabel(
            card,
            text="Submit a request if you attended a session that was not marked, "
                 "or for an excused absence.",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_muted"],
            wraplength=400,
            justify="center"
        ).pack(padx=20, pady=(0, 12))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=24)

        def add_lbl(text):
            ctk.CTkLabel(form, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=self.colors["text_muted"], anchor="w").pack(fill="x", pady=(8, 3))

        add_lbl("Course *")
        courses = self.db.get_courses(department_id=student.get("department_id"))
        if not courses:
            courses = self.db.get_courses()
        self._req_courses = courses
        course_combo = ctk.CTkComboBox(
            form, height=36, corner_radius=8,
            values=[f"{c['course_code']} - {c['course_name']}" for c in courses]
        )
        if courses:
            course_combo.set(f"{courses[0]['course_code']} - {courses[0]['course_name']}")
        course_combo.pack(fill="x")

        add_lbl("Date *")
        date_entry = ctk.CTkEntry(form, height=36, corner_radius=8,
                                  placeholder_text="YYYY-MM-DD")
        date_entry.insert(0, date.today().isoformat())
        date_entry.pack(fill="x")

        add_lbl("Request Type *")
        type_combo = ctk.CTkComboBox(
            form, height=36, corner_radius=8,
            values=["Correction", "Excused"]
        )
        type_combo.set("Correction")
        type_combo.pack(fill="x")

        add_lbl("Reason")
        reason_entry = ctk.CTkEntry(form, height=36, corner_radius=8,
                                    placeholder_text="e.g. I attended but was marked absent")
        reason_entry.pack(fill="x")

        def submit():
            course_str = course_combo.get()
            date_val = date_entry.get().strip()
            rtype = type_combo.get()
            reason = reason_entry.get().strip() or None

            if not course_str or course_str == "\u2014":
                messagebox.showerror("Validation Error", "Please select a course.")
                return
            if not date_val:
                messagebox.showerror("Validation Error", "Please enter a date (YYYY-MM-DD).")
                return

            course_id = None
            cc = course_str.split(" - ")[0]
            for c in self._req_courses:
                if c["course_code"] == cc:
                    course_id = c["id"]
                    break
            if not course_id:
                messagebox.showerror("Validation Error", "Could not resolve the selected course.")
                return

            req_id = self.db.add_attendance_request(
                student_id=student["id"],
                course_id=course_id,
                request_date=date_val,
                request_type=rtype,
                reason=reason,
            )
            if req_id:
                messagebox.showinfo("Success", "Attendance request submitted. Awaiting review by staff.")
                log(self.db, self.user, "CREATE", "Attendance Request",
                    f"Submitted request for {date_val} ({rtype}).")
                dialog.destroy()
                self.load_requests()
            else:
                messagebox.showerror("Error", "Failed to submit request.")

        ctk.CTkButton(
            card,
            text="Submit Request",
            command=submit,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=38,
            corner_radius=8
        ).pack(fill="x", padx=24, pady=(16, 18))

    # -------------------------------------------------------------
    # Admin / Teacher: review
    # -------------------------------------------------------------
    def _get_selected_req_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a request from the table.")
            return None
        return int(sel[0])

    def _approve_selected(self):
        req_id = self._get_selected_req_id()
        if req_id is None:
            return
        req = self.db.get_attendance_request(req_id)
        if req and req.get("status") != "Pending":
            messagebox.showinfo("Already Reviewed", "Only pending requests can be approved.")
            return
        if not messagebox.askyesno("Approve Request",
                                   "Approve this request?\nAttendance will be recorded as "
                                   "Present/Excused for the requested date."):
            return
        if self.db.apply_attendance_request(req_id, self.user["id"]):
            messagebox.showinfo("Success", "Request approved and attendance recorded.")
            log(self.db, self.user, "UPDATE", "Attendance Request",
                f"Approved request (ID {req_id}).")
            self.load_requests()
        else:
            messagebox.showerror("Error", "Could not approve the request.")

    def _reject_selected(self):
        req_id = self._get_selected_req_id()
        if req_id is None:
            return
        req = self.db.get_attendance_request(req_id)
        if req and req.get("status") != "Pending":
            messagebox.showinfo("Already Reviewed", "Only pending requests can be rejected.")
            return
        if not messagebox.askyesno("Reject Request", "Reject this attendance request?"):
            return
        self.db.review_attendance_request(req_id, "Rejected", self.user["id"])
        messagebox.showinfo("Success", "Request rejected.")
        log(self.db, self.user, "UPDATE", "Attendance Request",
            f"Rejected request (ID {req_id}).")
        self.load_requests()
