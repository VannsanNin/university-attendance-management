from datetime import date
import customtkinter as ctk

from gui import theme


class DashboardView(ctk.CTkFrame):

    def __init__(self, user, db, parent):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self.db = db
        self.pack(fill="both", expand=True, padx=30, pady=20)

        self._build_header()
        self._build_stat_row()
        self._build_today_attendance()
        self._build_charts_section()
        self._build_recent_activity()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        title_label = ctk.CTkLabel(
            header_frame,
            text="Dashboard",
            font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
            text_color=theme.c("text_bright"),
        )
        title_label.pack(side="left")

        date_badge = ctk.CTkFrame(
            header_frame, fg_color=theme.c("card_alt"), corner_radius=8, border_width=1, border_color=theme.c("border_alt")
        )
        date_badge.pack(side="right")

        date_text = date.today().strftime("%A, %b %d, %Y")
        ctk.CTkLabel(
            date_badge,
            text=f"\U0001F4C5  {date_text}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=theme.c("text_subtle"),
        ).pack(padx=14, pady=6)

    def _build_stat_row(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))

        for i in range(5):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="stat_card")

        total_students = self.db.get_student_count()
        total_teachers = self.db.get_teacher_count()
        total_departments = len(self.db.get_departments())
        total_courses = len(self.db.get_courses())
        total_classes = len(self.db.get_classes())

        card_data = [
            ("\U0001F9D2", str(total_students), "Total Students", theme.c("chart_1")),
            ("\U0001F468\u200D\U0001F3EB", str(total_teachers), "Total Teachers", theme.c("chart_2")),
            ("\U0001F3DB\uFE0F", str(total_departments), "Total Departments", theme.c("chart_3")),
            ("\U0001F4DA", str(total_courses), "Total Courses", theme.c("chart_4")),
            ("\U0001F3EB", str(total_classes), "Total Classes", theme.c("chart_5")),
        ]

        for idx, (icon, count, label, accent_color) in enumerate(card_data):
            card = ctk.CTkFrame(
                cards_frame,
                fg_color=theme.c("card_alt"),
                corner_radius=12,
                border_width=1,
                border_color=theme.c("border_alt"),
            )
            card.grid(row=0, column=idx, padx=6, sticky="nsew")

            accent = ctk.CTkFrame(card, fg_color=accent_color, height=4, corner_radius=0)
            accent.pack(fill="x", side="top")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=16, pady=14, fill="both", expand=True)

            ctk.CTkLabel(inner, text=icon, font=ctk.CTkFont(size=22)).pack(anchor="w")

            ctk.CTkLabel(
                inner, text=count,
                font=ctk.CTkFont(family="Inter", size=30, weight="bold"),
                text_color=theme.c("text_bright")
            ).pack(anchor="w", pady=(4, 0))

            ctk.CTkLabel(
                inner, text=label,
                font=ctk.CTkFont(size=12),
                text_color=theme.c("text_table")
            ).pack(anchor="w")

    def _build_today_attendance(self):
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            section, text="Today's Attendance",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(anchor="w", pady=(0, 10))

        stats = self.db.get_today_attendance_stats()
        total = stats.get("total") or 0
        present = stats.get("present") or 0
        absent = stats.get("absent") or 0
        late = stats.get("late") or 0
        permission = stats.get("permission") or 0
        excused = total - (present + absent + late + permission)

        cards_frame = ctk.CTkFrame(section, fg_color="transparent")
        cards_frame.pack(fill="x")

        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="today_card")

        today_data = [
            ("Present", str(present), theme.c("chart_2"), "\u2705"),
            ("Absent", str(absent), theme.c("danger"), "\u274C"),
            ("Late", str(late), theme.c("chart_3"), "\u23F3"),
            ("Excused", str(excused), theme.c("chart_1"), "\U0001F4CB"),
        ]

        for idx, (label, count, accent_color, icon) in enumerate(today_data):
            card = ctk.CTkFrame(
                cards_frame,
                fg_color=theme.c("card_alt"),
                corner_radius=12,
                border_width=1,
                border_color=theme.c("border_alt"),
            )
            card.grid(row=0, column=idx, padx=6, sticky="nsew")

            accent = ctk.CTkFrame(card, fg_color=accent_color, height=4, corner_radius=0)
            accent.pack(fill="x", side="top")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(padx=16, pady=14, fill="both", expand=True)

            top_row = ctk.CTkFrame(inner, fg_color="transparent")
            top_row.pack(fill="x")
            ctk.CTkLabel(top_row, text=icon, font=ctk.CTkFont(size=18)).pack(side="left")
            ctk.CTkLabel(
                top_row, text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=theme.c("text_table")
            ).pack(side="right")

            ctk.CTkLabel(
                inner, text=count,
                font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
                text_color=theme.c("text_bright")
            ).pack(anchor="w", pady=(4, 0))

    def _build_charts_section(self):
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            section, text="Charts",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(anchor="w", pady=(0, 10))

        charts_frame = ctk.CTkFrame(section, fg_color="transparent")
        charts_frame.pack(fill="x")

        for i in range(3):
            charts_frame.grid_columnconfigure(i, weight=1, uniform="chart")

        attendance_card = ctk.CTkFrame(
            charts_frame, fg_color=theme.c("card_alt"), corner_radius=12,
            border_width=1, border_color=theme.c("border_alt")
        )
        attendance_card.grid(row=0, column=0, padx=6, sticky="nsew")

        ctk.CTkLabel(
            attendance_card, text="Attendance %",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(padx=16, pady=(14, 10), anchor="w")

        stats = self.db.get_today_attendance_stats()
        total = stats.get("total") or 0
        present = stats.get("present") or 0
        if total > 0:
            pct = round((present / total) * 100, 1)
        else:
            pct = 0.0

        bar_bg = ctk.CTkFrame(attendance_card, fg_color=theme.c("border_alt"), height=20, corner_radius=6)
        bar_bg.pack(padx=16, fill="x")

        fill_width = max(2, int(pct))
        bar_fill = ctk.CTkFrame(bar_bg, fg_color=theme.c("chart_2"), height=20, corner_radius=6)
        bar_fill.pack(side="left", fill="y")
        bar_fill.configure(width=int(180 * pct / 100))

        ctk.CTkLabel(
            attendance_card, text=f"{pct}% Present",
            font=ctk.CTkFont(size=13),
            text_color=theme.c("text_body")
        ).pack(padx=16, pady=(6, 14), anchor="w")

        dept_card = ctk.CTkFrame(
            charts_frame, fg_color=theme.c("card_alt"), corner_radius=12,
            border_width=1, border_color=theme.c("border_alt")
        )
        dept_card.grid(row=0, column=1, padx=6, sticky="nsew")

        ctk.CTkLabel(
            dept_card, text="Students by Department",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(padx=16, pady=(14, 10), anchor="w")

        departments = self.db.get_departments()
        for dept in departments[:6]:
            dept_frame = ctk.CTkFrame(dept_card, fg_color="transparent")
            dept_frame.pack(fill="x", padx=16, pady=2)

            ctk.CTkLabel(
                dept_frame, text=dept["name"],
                font=ctk.CTkFont(size=12),
                text_color=theme.c("text_body"),
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

            dept_students = self.db.get_students(department_id=dept["id"])
            ctk.CTkLabel(
                dept_frame, text=str(len(dept_students)),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=theme.c("text_bright")
            ).pack(side="right")

        monthly_card = ctk.CTkFrame(
            charts_frame, fg_color=theme.c("card_alt"), corner_radius=12,
            border_width=1, border_color=theme.c("border_alt")
        )
        monthly_card.grid(row=0, column=2, padx=6, sticky="nsew")

        ctk.CTkLabel(
            monthly_card, text="Monthly Breakdown",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(padx=16, pady=(14, 10), anchor="w")

        today = date.today()
        month = today.month
        year = today.year
        start = f"{year}-{month:02d}-01"
        if month == 12:
            end = f"{year+1}-01-01"
        else:
            end = f"{year}-{month+1:02d}-01"
        records = self.db.get_attendance(start_date=start, end_date=end)
        total_rec = len(records)
        present_rec = sum(1 for r in records if r["status"] == "Present")
        absent_rec = sum(1 for r in records if r["status"] == "Absent")
        late_rec = sum(1 for r in records if r["status"] == "Late")

        monthly_data = [
            ("Present", str(present_rec), theme.c("chart_2")),
            ("Absent", str(absent_rec), theme.c("danger")),
            ("Late", str(late_rec), theme.c("chart_3")),
        ]
        for m_label, m_count, m_color in monthly_data:
            m_row = ctk.CTkFrame(monthly_card, fg_color="transparent")
            m_row.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(
                m_row, text=m_label,
                font=ctk.CTkFont(size=12),
                text_color=theme.c("text_body")
            ).pack(side="left")
            ctk.CTkLabel(
                m_row, text=m_count,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=m_color
            ).pack(side="right")

        if total_rec > 0:
            month_pct = round((present_rec / total_rec) * 100, 1)
        else:
            month_pct = 0.0
        ctk.CTkLabel(
            monthly_card, text=f"{month_pct}% attendance rate",
            font=ctk.CTkFont(size=12),
            text_color=theme.c("text_table")
        ).pack(padx=16, pady=(6, 14), anchor="w")

    def _build_recent_activity(self):
        section = ctk.CTkFrame(self, fg_color="transparent")
        section.pack(fill="both", expand=True)

        ctk.CTkLabel(
            section, text="Recent Activity",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(anchor="w", pady=(0, 10))

        activity_frame = ctk.CTkFrame(section, fg_color="transparent")
        activity_frame.pack(fill="both", expand=True)

        for i in range(2):
            activity_frame.grid_columnconfigure(i, weight=1, uniform="recent")

        recent_students_card = ctk.CTkFrame(
            activity_frame, fg_color=theme.c("card_alt"), corner_radius=12,
            border_width=1, border_color=theme.c("border_alt")
        )
        recent_students_card.grid(row=0, column=0, padx=6, sticky="nsew")

        ctk.CTkLabel(
            recent_students_card, text="Recently Added Students",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(padx=16, pady=(14, 8), anchor="w")

        students = self.db.get_students()
        recent_students = students[-5:] if len(students) > 5 else students

        scroll_frame = ctk.CTkScrollableFrame(
            recent_students_card, fg_color="transparent",
            height=200
        )
        scroll_frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        for s in reversed(recent_students):
            s_card = ctk.CTkFrame(
                scroll_frame, fg_color=theme.c("border_alt"), corner_radius=6
            )
            s_card.pack(fill="x", pady=2)

            name_label = ctk.CTkLabel(
                s_card, text=s.get("full_name", "?"),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=theme.c("text_bright")
            )
            name_label.pack(side="left", padx=10, pady=4)

            id_label = ctk.CTkLabel(
                s_card, text=s.get("student_id", ""),
                font=ctk.CTkFont(size=11),
                text_color=theme.c("text_table")
            )
            id_label.pack(side="right", padx=10, pady=4)

        recent_attendance_card = ctk.CTkFrame(
            activity_frame, fg_color=theme.c("card_alt"), corner_radius=12,
            border_width=1, border_color=theme.c("border_alt")
        )
        recent_attendance_card.grid(row=0, column=1, padx=6, sticky="nsew")

        ctk.CTkLabel(
            recent_attendance_card, text="Recent Attendance Records",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(padx=16, pady=(14, 8), anchor="w")

        records = self.db.get_attendance(limit=5)

        scroll_frame2 = ctk.CTkScrollableFrame(
            recent_attendance_card, fg_color="transparent",
            height=200
        )
        scroll_frame2.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        status_colors = {
            "Present": theme.c("chart_2"),
            "Absent": theme.c("danger"),
            "Late": theme.c("chart_3"),
            "Permission": theme.c("chart_1"),
            "Excused": theme.c("chart_1"),
        }

        for r in records:
            r_card = ctk.CTkFrame(
                scroll_frame2, fg_color=theme.c("border_alt"), corner_radius=6
            )
            r_card.pack(fill="x", pady=2)

            name_text = r.get("student_name", r.get("sid", "?"))
            date_text = r.get("attendance_date", "")
            status_text = r.get("status", "")
            status_color = status_colors.get(status_text, theme.c("text_bright"))

            ctk.CTkLabel(
                r_card, text=name_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=theme.c("text_bright")
            ).pack(side="left", padx=10, pady=4)

            ctk.CTkLabel(
                r_card, text=date_text,
                font=ctk.CTkFont(size=11),
                text_color=theme.c("text_table")
            ).pack(side="left", padx=10, pady=4)

            ctk.CTkLabel(
                r_card, text=status_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=status_color
            ).pack(side="right", padx=10, pady=4)
