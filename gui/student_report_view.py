import customtkinter as ctk
from gui import theme
from datetime import date


class StudentReportView(ctk.CTkFrame):
    def __init__(self, db, parent, user):
        super().__init__(parent, fg_color=theme.c("bg_dark"), corner_radius=0)
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)

        self._build_ui()

    def _build_ui(self):
        # Top Header Bar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="Attendance Report",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Personal course participation and log history",
            font=ctk.CTkFont(size=12),
            text_color=theme.c("text_muted")
        ).pack(anchor="w", pady=(2, 0))

        # Refresh Action Button
        ctk.CTkButton(
            header,
            text="Refresh",
            width=90,
            height=32,
            corner_radius=8,
            fg_color=theme.c("card_bg"),
            hover_color=theme.c("border"),
            text_color=theme.c("text_bright"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._load_data
        ).pack(side="right")

        # Main Content Container
        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=30, pady=10)

        self._load_data()

    def _load_data(self):
        # Clear existing children in content area
        for widget in self.content_area.winfo_children():
            widget.destroy()

        # Query Student Profile ID
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM students WHERE user_id=?", (self.user["id"],))
        student = cursor.fetchone()
        conn.close()

        if not student:
            empty_box = ctk.CTkFrame(self.content_area, fg_color=theme.c("card_bg"), corner_radius=12)
            empty_box.pack(fill="x", pady=40, padx=20)
            ctk.CTkLabel(
                empty_box,
                text="Student profile record not found.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=theme.c("lightcoral")
            ).pack(pady=30)
            return

        student_id = student["id"]
        summary = self.db.get_attendance_summary(student_id=student_id)
        records = self.db.get_attendance(student_id=student_id, limit=50)

        # Build Analytics Stat Cards Grid
        self._render_summary_cards(summary)

        # Build Recent Logs Table
        self._render_records_table(records)

    def _render_summary_cards(self, summary):
        stats_grid = ctk.CTkFrame(self.content_area, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 20))
        stats_grid.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="stat_card")

        total = summary.get("total", 0) or 1
        present_pct = round(summary.get("present_count", 0) / total * 100, 1)
        absent_pct = round(summary.get("absent_count", 0) / total * 100, 1)
        late_pct = round(summary.get("late_count", 0) / total * 100, 1)
        perm_pct = round(summary.get("permission_count", 0) / total * 100, 1)
        overall_pct = summary.get("percentage", 0)

        overall_color = theme.c("success") if overall_pct >= 75 else theme.c("warning")

        cards = [
            ("Total Classes", str(summary.get("total", 0)), theme.c("text_bright")),
            ("Present", f"{present_pct}%", theme.c("green")),
            ("Absent", f"{absent_pct}%", theme.c("lightcoral")),
            ("Late", f"{late_pct}%", theme.c("gold")),
            ("Permission", f"{perm_pct}%", theme.c("steelblue")),
            ("Overall Rate", f"{overall_pct}%", overall_color),
        ]

        for col, (label, val, color) in enumerate(cards):
            card = ctk.CTkFrame(stats_grid, fg_color=theme.c("card_bg"), corner_radius=10)
            card.grid(row=0, column=col, padx=4, sticky="ew")

            ctk.CTkLabel(
                card,
                text=label.upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=theme.c("text_muted")
            ).pack(anchor="w", padx=12, pady=(12, 2))

            ctk.CTkLabel(
                card,
                text=val,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color
            ).pack(anchor="w", padx=12, pady=(0, 12))

    def _render_records_table(self, records):
        table_box = ctk.CTkFrame(self.content_area, fg_color=theme.c("card_bg"), corner_radius=12)
        table_box.pack(fill="both", expand=True)

        # Table Section Header
        tbl_header = ctk.CTkFrame(table_box, fg_color="transparent")
        tbl_header.pack(fill="x", padx=16, pady=(14, 10))

        ctk.CTkLabel(
            tbl_header,
            text="Recent Attendance Logs",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(side="left")

        if not records:
            ctk.CTkLabel(
                table_box,
                text="No attendance records registered yet.",
                font=ctk.CTkFont(size=13),
                text_color=theme.c("text_muted")
            ).pack(pady=40)
            return

        # Column Header Row
        col_bar = ctk.CTkFrame(table_box, fg_color=theme.c("bg_dark"), height=32, corner_radius=6)
        col_bar.pack(fill="x", padx=16, pady=(0, 6))

        headers = [
            ("Date", 120),
            ("Code", 100),
            ("Course Name", 240),
            ("Status", 100)
        ]

        for text, width in headers:
            ctk.CTkLabel(
                col_bar,
                text=text.upper(),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=theme.c("text_muted"),
                width=width,
                anchor="w"
            ).pack(side="left", padx=8, pady=4)

        # Scrollable Records List
        scroll = ctk.CTkScrollableFrame(table_box, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        status_colors = {
            "Present": theme.c("green"),
            "Absent": theme.c("lightcoral"),
            "Late": theme.c("gold"),
            "Permission": theme.c("steelblue")
        }

        for r in records:
            row = ctk.CTkFrame(scroll, fg_color=theme.c("card_bg"), height=36, corner_radius=6)
            row.pack(fill="x", pady=2)

            color = status_colors.get(r.get("status"), theme.c("text_bright"))

            ctk.CTkLabel(
                row,
                text=r.get("attendance_date", "—"),
                width=120,
                anchor="w",
                font=ctk.CTkFont(size=12),
                text_color=theme.c("text_bright")
            ).pack(side="left", padx=8)

            ctk.CTkLabel(
                row,
                text=r.get("course_code", "—"),
                width=100,
                anchor="w",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=theme.c("text_bright")
            ).pack(side="left", padx=8)

            ctk.CTkLabel(
                row,
                text=r.get("course_name", "—"),
                width=240,
                anchor="w",
                font=ctk.CTkFont(size=12),
                text_color=theme.c("text_bright")
            ).pack(side="left", padx=8)

            # Status Badge Pill
            badge = ctk.CTkFrame(row, fg_color="transparent", width=100)
            badge.pack(side="left", padx=8)

            ctk.CTkLabel(
                badge,
                text=r.get("status", "Unknown"),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=color,
                anchor="w"
            ).pack(side="left")