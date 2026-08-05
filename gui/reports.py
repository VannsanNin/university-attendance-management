import customtkinter as ctk
from gui import theme
from tkinter import messagebox, filedialog, ttk
from datetime import date, datetime
import pandas as pd
import os


class ReportsView(ctk.CTkFrame):
    def __init__(self, db, parent):
        super().__init__(parent, fg_color=theme.c("bg_dark"))  # Slate 900 background
        self.db = db
        self.report_data = None
        self.current_report_type = "Daily"
        self.pack(fill="both", expand=True)

        # Unified Color Palette Tokens
        self.colors = theme.colors

        self._build_header()
        self._build_main()
        self._generate_report()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Attendance Reports & Analytics",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Generate detailed summary reports and export statistical attendance data",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_muted"]
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # -------------------------------------------------------------
        # Filter Configuration Card
        # -------------------------------------------------------------
        top_card = ctk.CTkFrame(
            main,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        top_card.pack(fill="x", pady=(0, 15))

        report_type_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        report_type_frame.pack(padx=20, pady=(15, 6), fill="x")

        ctk.CTkLabel(
            report_type_frame,
            text="Report Type:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(side="left", padx=(0, 10))

        self.report_types = ["Daily", "Weekly", "Monthly", "Semester", "Student", "Teacher", "Department"]
        self.report_type_var = ctk.StringVar(value="Daily")
        self.report_type_combo = ctk.CTkComboBox(
            report_type_frame,
            values=self.report_types,
            variable=self.report_type_var,
            width=200,
            height=36,
            corner_radius=8,
            command=self._on_report_type_change
        )
        self.report_type_combo.pack(side="left", padx=5)

        self.filter_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        self.filter_frame.pack(padx=20, pady=(6, 12), fill="x")

        self._build_filter_widgets()

        ctk.CTkButton(
            top_card,
            text="Generate Report",
            command=self._generate_report,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            width=180,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=(0, 15))

        # -------------------------------------------------------------
        # Results Section Card
        # -------------------------------------------------------------
        result_card = ctk.CTkFrame(
            main,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        result_card.pack(fill="both", expand=True)

        res_header = ctk.CTkFrame(result_card, fg_color="transparent")
        res_header.pack(fill="x", padx=20, pady=(15, 10))

        self.result_title_lbl = ctk.CTkLabel(
            res_header,
            text="Report Results",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        )
        self.result_title_lbl.pack(side="left")

        # Export Actions Bar
        export_bar = ctk.CTkFrame(res_header, fg_color="transparent")
        export_bar.pack(side="right")

        export_actions = [
            ("Print Report", self.print_report),
            ("Export PDF", self.export_pdf),
            ("Export Excel", self.export_excel),
            ("Export CSV", self.export_csv)
        ]

        for text, cmd in export_actions:
            ctk.CTkButton(
                export_bar,
                text=text,
                command=cmd,
                fg_color=self.colors["neutral_btn"],
                hover_color=self.colors["neutral_hover"],
                height=32,
                corner_radius=6,
                font=ctk.CTkFont(size=11, weight="bold")
            ).pack(side="left", padx=3)

        # Summary Stats Buffer Frame (used dynamically by Student Report)
        self.summary_stats_frame = ctk.CTkFrame(result_card, fg_color=theme.c("bg_dark"), corner_radius=8)
        self.summary_stats_frame.pack_forget()

        # Table Wrapper Frame
        self.table_wrapper = ctk.CTkFrame(result_card, fg_color="transparent")
        self.table_wrapper.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Configure Custom Treeview Style
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Report.Treeview",
            background=theme.c("table_bg"),
            foreground=theme.c("table_fg"),
            fieldbackground=theme.c("table_bg"),
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Report.Treeview.Heading",
            background=theme.c("table_head_bg"),
            foreground=theme.c("table_head_fg"),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "Report.Treeview",
            background=[("selected", theme.c("table_selected"))],
            foreground=[("selected", theme.c("table_selected_fg"))]
        )
        style.map(
            "Report.Treeview.Heading",
            background=[("active", theme.c("table_head_active"))]
        )

        self.tree = ttk.Treeview(self.table_wrapper, show="headings", style="Report.Treeview", selectmode="browse")
        self.scrollbar = ctk.CTkScrollbar(self.table_wrapper, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_report_type_change(self, choice):
        self.current_report_type = choice
        self._build_filter_widgets()

    def _build_filter_widgets(self):
        for w in self.filter_frame.winfo_children():
            w.destroy()

        self.filter_widgets = {}

        def add_label(text, col=None):
            lbl = ctk.CTkLabel(self.filter_frame, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                               text_color=self.colors["text_muted"])
            lbl.pack(side="left", padx=(10 if col else 0, 5))

        if self.current_report_type == "Daily":
            add_label("Date:")
            self.date_entry = ctk.CTkEntry(self.filter_frame, width=140, height=36, corner_radius=8)
            self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
            self.date_entry.pack(side="left", padx=5)
            self.filter_widgets["date"] = self.date_entry

        elif self.current_report_type == "Weekly":
            add_label("Week (YYYY-WW):")
            self.week_entry = ctk.CTkEntry(self.filter_frame, width=140, height=36, corner_radius=8)
            today = date.today()
            week_num = today.isocalendar()[1]
            self.week_entry.insert(0, f"{today.year}-W{week_num:02d}")
            self.week_entry.pack(side="left", padx=5)

        elif self.current_report_type == "Monthly":
            add_label("Year:")
            self.month_year_entry = ctk.CTkEntry(self.filter_frame, width=100, height=36, corner_radius=8)
            self.month_year_entry.insert(0, str(date.today().year))
            self.month_year_entry.pack(side="left", padx=5)

            add_label("Month (1-12):", col=True)
            self.month_entry = ctk.CTkEntry(self.filter_frame, width=80, height=36, corner_radius=8)
            self.month_entry.insert(0, str(date.today().month))
            self.month_entry.pack(side="left", padx=5)

        elif self.current_report_type == "Semester":
            add_label("Semester:")
            self.semester_combo = ctk.CTkComboBox(self.filter_frame, values=["1", "2", "3"], width=90, height=36,
                                                  corner_radius=8)
            self.semester_combo.pack(side="left", padx=5)

            add_label("Year:", col=True)
            self.semester_year_entry = ctk.CTkEntry(self.filter_frame, width=100, height=36, corner_radius=8)
            self.semester_year_entry.insert(0, str(date.today().year))
            self.semester_year_entry.pack(side="left", padx=5)

        elif self.current_report_type == "Student":
            add_label("Search Student:")
            self.student_entry = ctk.CTkEntry(self.filter_frame, width=280, height=36, corner_radius=8,
                                              placeholder_text="Name or Student ID...")
            self.student_entry.pack(side="left", padx=5)

        elif self.current_report_type == "Teacher":
            add_label("Search Teacher:")
            self.teacher_entry = ctk.CTkEntry(self.filter_frame, width=280, height=36, corner_radius=8,
                                              placeholder_text="Name or Teacher ID...")
            self.teacher_entry.pack(side="left", padx=5)

        elif self.current_report_type == "Department":
            add_label("Department:")
            departments = self.db.get_departments()
            dept_values = [d["name"] for d in departments]
            self.dept_combo = ctk.CTkComboBox(self.filter_frame, values=dept_values, width=250, height=36,
                                              corner_radius=8)
            if dept_values:
                self.dept_combo.set(dept_values[0])
            self.dept_combo.pack(side="left", padx=5)

    def _generate_report(self):
        self.tree.delete(*self.tree.get_children())
        self.summary_stats_frame.pack_forget()
        for w in self.summary_stats_frame.winfo_children():
            w.destroy()

        self.report_data = None

        rtype = self.current_report_type
        if rtype == "Daily":
            self._generate_daily()
        elif rtype == "Weekly":
            self._generate_weekly()
        elif rtype == "Monthly":
            self._generate_monthly()
        elif rtype == "Semester":
            self._generate_semester()
        elif rtype == "Student":
            self._generate_student()
        elif rtype == "Teacher":
            self._generate_teacher()
        elif rtype == "Department":
            self._generate_department()

    def _display_table(self, headers, col_keys, widths, rows, title="Report Results"):
        self.result_title_lbl.configure(text=title)

        self.tree["columns"] = col_keys
        for key, text, width in zip(col_keys, headers, widths):
            self.tree.heading(key, text=text, anchor="w")
            self.tree.column(key, width=width, minwidth=width, stretch=True, anchor="w")

        for r_idx, row_data in enumerate(rows):
            vals = [str(val) if val is not None else "" for val in row_data]
            self.tree.insert("", "end", iid=str(r_idx), values=vals)

    def _generate_daily(self):
        d = self.date_entry.get().strip()
        if not d:
            messagebox.showinfo("Validation Error", "Please enter a valid date.")
            return
        records = self.db.get_attendance(attendance_date=d)
        if not records:
            self._show_no_data(f"No attendance data recorded for {d}")
            return

        self.report_data = records
        rows = []
        for r in records:
            rows.append([
                r.get("attendance_date", ""),
                r.get("sid", ""),
                r.get("student_name", ""),
                r.get("course_code", ""),
                r.get("status", "")
            ])

        self._display_table(
            ["Date", "Student ID", "Name", "Course", "Status"],
            ["date", "sid", "name", "course", "status"],
            [120, 120, 220, 160, 120],
            rows,
            title=f"Daily Attendance Report — {d}"
        )

    def _generate_weekly(self):
        week_str = self.week_entry.get().strip()
        if not week_str:
            messagebox.showinfo("Validation Error", "Please enter a week format (YYYY-WW).")
            return
        try:
            parts = week_str.split("-W")
            year = int(parts[0])
            week = int(parts[1])
            from datetime import timedelta
            d = date(year, 1, 4)
            d = d - timedelta(days=d.weekday())
            d = d + timedelta(weeks=week - 1)
            start = d.isoformat()
            end = (d + timedelta(days=6)).isoformat()
        except Exception:
            messagebox.showerror("Error", "Invalid week format. Use YYYY-WW (e.g. 2026-W31).")
            return

        records = self.db.get_attendance(start_date=start, end_date=end)
        if not records:
            self._show_no_data(f"No attendance data for week {week_str}")
            return

        self.report_data = records
        rows = []
        for r in records:
            rows.append([
                r.get("attendance_date", ""),
                r.get("sid", ""),
                r.get("student_name", ""),
                r.get("course_code", ""),
                r.get("status", "")
            ])

        self._display_table(
            ["Date", "Student ID", "Name", "Course", "Status"],
            ["date", "sid", "name", "course", "status"],
            [120, 120, 220, 160, 120],
            rows,
            title=f"Weekly Attendance Report — {week_str} ({start} to {end})"
        )

    def _generate_monthly(self):
        try:
            year = int(self.month_year_entry.get().strip())
            month = int(self.month_entry.get().strip())
        except Exception:
            messagebox.showerror("Error", "Invalid year or month value.")
            return

        start = f"{year}-{month:02d}-01"
        if month == 12:
            end = f"{year + 1}-01-01"
        else:
            end = f"{year}-{month + 1:02d}-01"

        records = self.db.get_attendance(start_date=start, end_date=end)
        if not records:
            self._show_no_data(f"No attendance data for {year}-{month:02d}")
            return

        self.report_data = records

        summary = {}
        for r in records:
            name = r.get("student_name", "?")
            if name not in summary:
                summary[name] = {"Present": 0, "Absent": 0, "Late": 0, "Permission": 0, "Excused": 0, "total": 0}
            status = r["status"]
            summary[name][status] = summary[name].get(status, 0) + 1
            summary[name]["total"] += 1

        rows = []
        for name, stats in sorted(summary.items()):
            pct = round(
                (stats["Present"] + stats["Late"] + stats["Permission"] + stats["Excused"]) / stats["total"] * 100, 1
            ) if stats["total"] else 0
            rows.append([
                name,
                stats["Present"],
                stats["Absent"],
                stats["Late"],
                stats["Excused"],
                f"{pct}%"
            ])

        self._display_table(
            ["Student Name", "Present", "Absent", "Late", "Excused", "Percentage"],
            ["student", "present", "absent", "late", "excused", "percentage"],
            [220, 100, 100, 100, 100, 120],
            rows,
            title=f"Monthly Attendance Summary — {year}-{month:02d}"
        )

    def _generate_semester(self):
        semester = self.semester_combo.get()
        year = self.semester_year_entry.get().strip()
        if not semester or not year:
            messagebox.showinfo("Validation Error", "Select a semester and enter a year.")
            return

        records = self.db.get_attendance()
        filtered = []
        for r in records:
            d = r.get("attendance_date", "")
            if d.startswith(year):
                filtered.append(r)

        if not filtered:
            self._show_no_data(f"No data found for Semester {semester} — {year}")
            return

        self.report_data = filtered

        summary = {}
        for r in filtered:
            name = r.get("student_name", "?")
            if name not in summary:
                summary[name] = {"Present": 0, "Absent": 0, "Late": 0, "Excused": 0, "total": 0}
            status = r["status"]
            summary[name][status] = summary[name].get(status, 0) + 1
            summary[name]["total"] += 1

        rows = []
        for name, stats in sorted(summary.items()):
            pct = round(
                (stats["Present"] + stats["Late"] + stats["Excused"]) / stats["total"] * 100, 1
            ) if stats["total"] else 0
            rows.append([
                name,
                stats["Present"],
                stats["Absent"],
                stats["Late"],
                stats["Excused"],
                f"{pct}%"
            ])

        self._display_table(
            ["Student Name", "Present", "Absent", "Late", "Excused", "Percentage"],
            ["student", "present", "absent", "late", "excused", "percentage"],
            [220, 100, 100, 100, 100, 120],
            rows,
            title=f"Semester {semester} — {year} Attendance Report"
        )

    def _generate_student(self):
        search = self.student_entry.get().strip()
        if not search:
            messagebox.showinfo("Validation Error", "Enter a student name or ID.")
            return
        students = self.db.get_students(search=search)
        if not students:
            self._show_no_data("Student not found.")
            return
        s = students[0]
        records = self.db.get_attendance(student_id=s["id"])
        if not records:
            self._show_no_data(f"No attendance records for {s['full_name']}")
            return

        self.report_data = records

        # Show summary metrics banner above table
        summary = self.db.get_attendance_summary(student_id=s["id"])
        self.summary_stats_frame.pack(fill="x", padx=20, pady=(0, 10))

        metrics = [
            ("Present", "present_count"),
            ("Absent", "absent_count"),
            ("Late", "late_count"),
            ("Excused", "excused_count"),
            ("Overall Score", "percentage"),
        ]

        for label, key in metrics:
            val = summary.get(key, 0)
            suffix = "%" if key == "percentage" else ""
            stat_box = ctk.CTkFrame(self.summary_stats_frame, fg_color=self.colors["card_bg"], corner_radius=6)
            stat_box.pack(side="left", padx=8, pady=8, expand=True, fill="x")

            ctk.CTkLabel(
                stat_box,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=self.colors["text_muted"]
            ).pack(pady=(4, 0))

            ctk.CTkLabel(
                stat_box,
                text=f"{val}{suffix}",
                font=ctk.CTkFont(size=15, weight="bold"),
                text_color=self.colors["primary"]
            ).pack(pady=(0, 4))

        rows = []
        for r in records:
            rows.append([
                r.get("attendance_date", ""),
                r.get("course_code", ""),
                r.get("course_name", ""),
                r.get("status", "")
            ])

        self._display_table(
            ["Date", "Course Code", "Course Name", "Status"],
            ["date", "code", "name", "status"],
            [120, 130, 250, 130],
            rows,
            title=f"Individual Student Report — {s['full_name']} ({s['student_id']})"
        )

    def _generate_teacher(self):
        search = self.teacher_entry.get().strip()
        if not search:
            teachers = self.db.get_teachers()
        else:
            teachers = self.db.get_teachers(search=search)

        if not teachers:
            self._show_no_data("No teachers found.")
            return

        self.report_data = teachers
        rows = []
        for t in teachers:
            rows.append([
                t["teacher_id"],
                t["full_name"],
                t.get("email", "") or "—",
                t.get("phone", "") or "—",
                t.get("department_name", "") or "—",
            ])

        self._display_table(
            ["Faculty ID", "Name", "Email", "Phone", "Department"],
            ["id", "name", "email", "phone", "department"],
            [120, 200, 200, 140, 160],
            rows,
            title="Faculty Teacher Directory Report"
        )

    def _generate_department(self):
        dept_name = self.dept_combo.get()
        if not dept_name:
            messagebox.showinfo("Validation Error", "Select a department.")
            return

        departments = self.db.get_departments()
        dept_id = None
        for d in departments:
            if d["name"] == dept_name:
                dept_id = d["id"]
                break

        if not dept_id:
            self._show_no_data("Department not found.")
            return

        students = self.db.get_students(department_id=dept_id)
        student_ids = [s["id"] for s in students]

        if not student_ids:
            self._show_no_data(f"No students enrolled in department: {dept_name}")
            return

        all_records = []
        for sid in student_ids:
            records = self.db.get_attendance(student_id=sid)
            all_records.extend(records)

        if not all_records:
            self._show_no_data(f"No attendance data recorded for {dept_name}")
            return

        self.report_data = all_records

        summary = {}
        for r in all_records:
            name = r.get("student_name", "?")
            if name not in summary:
                summary[name] = {"Present": 0, "Absent": 0, "Late": 0, "Excused": 0, "total": 0}
            status = r["status"]
            summary[name][status] = summary[name].get(status, 0) + 1
            summary[name]["total"] += 1

        rows = []
        for name, stats in sorted(summary.items()):
            pct = round(
                (stats["Present"] + stats["Late"] + stats["Excused"]) / stats["total"] * 100, 1
            ) if stats["total"] else 0
            rows.append([
                name,
                stats["Present"],
                stats["Absent"],
                stats["Late"],
                stats["Excused"],
                f"{pct}%"
            ])

        self._display_table(
            ["Student Name", "Present", "Absent", "Late", "Excused", "Percentage"],
            ["student", "present", "absent", "late", "excused", "percentage"],
            [220, 100, 100, 100, 100, 120],
            rows,
            title=f"Department Attendance Report — {dept_name}"
        )

    def _show_no_data(self, message):
        self.result_title_lbl.configure(text="Report Results")
        self.tree["columns"] = ("msg",)
        self.tree.heading("msg", text="Notice", anchor="center")
        self.tree.column("msg", width=600, anchor="center")
        self.tree.insert("", "end", values=(message,))

    # -------------------------------------------------------------
    # Document Printing and Export Helpers
    # -------------------------------------------------------------
    def print_report(self):
        if not self.report_data:
            messagebox.showinfo("Info", "Generate a report first.")
            return
        try:
            import tempfile
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet

            tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            doc = SimpleDocTemplate(tmp.name, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph(f"{self.current_report_type} Report", styles["Title"]))
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))

            if self.report_data:
                keys = list(self.report_data[0].keys())
                data = [keys]
                for r in self.report_data:
                    data.append([str(r.get(k, "")) for k in keys])
                table = Table(data)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
            doc.build(elements)
            os.startfile(tmp.name)
        except Exception as e:
            messagebox.showerror("Error", f"Print failed: {str(e)}")

    def export_pdf(self):
        if not self.report_data:
            messagebox.showinfo("Info", "Generate a report first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not path:
            return
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet

            doc = SimpleDocTemplate(path, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph(f"{self.current_report_type} Report", styles["Title"]))
            elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))

            if self.report_data:
                keys = list(self.report_data[0].keys())
                data = [keys]
                for r in self.report_data:
                    data.append([str(r.get(k, "")) for k in keys])
                table = Table(data)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
            doc.build(elements)
            messagebox.showinfo("Success", f"Exported report PDF to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")

    def export_excel(self):
        if not self.report_data:
            messagebox.showinfo("Info", "Generate a report first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if path:
            df = pd.DataFrame(self.report_data)
            df.to_excel(path, index=False)
            messagebox.showinfo("Success", f"Exported report to:\n{path}")

    def export_csv(self):
        if not self.report_data:
            messagebox.showinfo("Info", "Generate a report first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            df = pd.DataFrame(self.report_data)
            df.to_csv(path, index=False)
            messagebox.showinfo("Success", f"Exported report to:\n{path}")