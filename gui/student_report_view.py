import customtkinter as ctk
from gui import theme
from datetime import date

class StudentReportView(ctk.CTkFrame):
    def __init__(self, db, parent, user):
        super().__init__(parent, fg_color=theme.c("bg_dark"))
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="Attendance Report",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        conn = db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM students WHERE user_id=?", (user["id"],))
        student = cursor.fetchone()
        conn.close()

        if not student:
            ctk.CTkLabel(self, text="Student profile not found.",
                         font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        summary = db.get_attendance_summary(student_id=student["id"])

        stats = ctk.CTkFrame(self)
        stats.pack(pady=20, padx=40, fill="x")

        total = summary.get("total", 0) or 1
        present_pct = round(summary.get("present_count", 0) / total * 100, 1)
        absent_pct = round(summary.get("absent_count", 0) / total * 100, 1)
        late_pct = round(summary.get("late_count", 0) / total * 100, 1)
        perm_pct = round(summary.get("permission_count", 0) / total * 100, 1)

        labels = [
            ("Total Classes", str(summary.get("total", 0)), theme.c("text_bright")),
            ("Present", f"{present_pct}%", theme.c("green")),
            ("Absent", f"{absent_pct}%", theme.c("lightcoral")),
            ("Late", f"{late_pct}%", theme.c("gold")),
            ("Permission", f"{perm_pct}%", theme.c("steelblue")),
            ("Overall", f"{summary.get('percentage', 0)}%", theme.c("success") if summary.get('percentage', 0) >= 75 else theme.c("warning")),
        ]

        for i, (label, value, color) in enumerate(labels):
            f = ctk.CTkFrame(stats)
            f.grid(row=i, column=0, sticky="ew", pady=2, padx=20)
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=14, weight="bold"),
                         width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=value, font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=color).pack(side="left", padx=10)

        records = db.get_attendance(student_id=student["id"], limit=50)

        if records:
            ctk.CTkLabel(self, text="Recent Records",
                         font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 5))

            scroll = ctk.CTkScrollableFrame(self)
            scroll.pack(fill="both", expand=True, padx=40, pady=10)

            for r in records:
                row = ctk.CTkFrame(scroll)
                row.pack(fill="x", pady=1)

                status_colors = {"Present": theme.c("green"), "Absent": theme.c("lightcoral"),
                                 "Late": theme.c("gold"), "Permission": theme.c("steelblue")}
                color = status_colors.get(r["status"], theme.c("text_bright"))

                ctk.CTkLabel(row, text=r.get("attendance_date", ""), width=120).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=r.get("course_code", ""), width=100).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=r.get("course_name", ""), width=200).pack(side="left", padx=5)
                ctk.CTkLabel(row, text=r["status"], width=100, text_color=color,
                             font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
