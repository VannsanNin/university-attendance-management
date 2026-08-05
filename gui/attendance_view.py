import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from datetime import date, datetime
import pandas as pd
import os


class AttendanceTakeView(ctk.CTkFrame):
    def __init__(self, user, db, parent):
        super().__init__(parent, fg_color="#0F172A")  # Slate 900 background
        self.user = user
        self.db = db
        self.current_students = []
        self.attendance_statuses = {}
        self.pack(fill="both", expand=True)

        # Unified Color Palette
        self.colors = {
            "bg_dark": "#0F172A",
            "card_bg": "#1E293B",
            "card_border": "#334155",
            "primary": "#0EA5E9",
            "primary_hover": "#0284C7",
            "success": "#10B981",
            "success_hover": "#059669",
            "danger": "#EF4444",
            "danger_hover": "#DC2626",
            "neutral_btn": "#334155",
            "neutral_hover": "#475569",
            "text_main": "#F8FAFC",
            "text_muted": "#94A3B8"
        }

        self._build_header()
        self._build_top_bar()
        self._build_student_list()
        self._build_bottom_bar()
        self._load_combo_data()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Take Attendance",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Record daily student session attendance and update class rosters",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_muted"]
        )
        subtitle.pack(anchor="w", pady=(2, 0))

    def _build_top_bar(self):
        top_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        top_card.pack(fill="x", padx=30, pady=(5, 15))

        inner = ctk.CTkFrame(top_card, fg_color="transparent")
        inner.pack(padx=20, pady=15, fill="x")

        def add_lbl(text):
            lbl = ctk.CTkLabel(inner, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                               text_color=self.colors["text_muted"])
            lbl.pack(side="left", padx=(10, 4))

        add_lbl("Date:")
        self.date_entry = ctk.CTkEntry(inner, width=120, height=36, corner_radius=8)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.pack(side="left", padx=2)

        add_lbl("Time:")
        self.time_entry = ctk.CTkEntry(inner, width=90, height=36, corner_radius=8)
        self.time_entry.insert(0, datetime.now().strftime("%H:%M"))
        self.time_entry.pack(side="left", padx=2)

        add_lbl("Course:")
        self.course_combo = ctk.CTkComboBox(inner, width=180, height=36, corner_radius=8, values=[""])
        self.course_combo.pack(side="left", padx=2)
        self.course_combo.configure(command=self._on_course_select)

        add_lbl("Class:")
        self.class_combo = ctk.CTkComboBox(inner, width=180, height=36, corner_radius=8, values=[""])
        self.class_combo.pack(side="left", padx=2)

        add_lbl("Subject:")
        self.subject_entry = ctk.CTkEntry(inner, width=180, height=36, corner_radius=8, state="readonly")
        self.subject_entry.pack(side="left", padx=2)

        ctk.CTkButton(
            inner,
            text="Load Roster",
            command=self.load_students,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(15, 0))

    def _on_course_select(self, choice):
        if not choice:
            return
        code = choice.split(" - ")[0]
        courses = self.db.get_courses()
        for c in courses:
            if c["course_code"] == code:
                self.subject_entry.configure(state="normal")
                self.subject_entry.delete(0, "end")
                self.subject_entry.insert(0, c["course_name"])
                self.subject_entry.configure(state="readonly")
                break

    def _load_combo_data(self):
        courses = self.db.get_courses()
        self.course_combo.configure(values=[f"{c['course_code']} - {c['course_name']}" for c in courses])
        classes = self.db.get_classes()
        if classes:
            self.class_combo.configure(values=[f"{c['class_name']} ({c['department_name']})" for c in classes])

    def _build_student_list(self):
        list_container = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        list_container.pack(fill="both", expand=True, padx=30, pady=(0, 15))

        header_frame = ctk.CTkFrame(list_container, fg_color="#0F172A", corner_radius=8)
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        for col, text, w in [
            ("sid_col", "Student ID", 140),
            ("name_col", "Student Name", 320),
            ("status_col", "Attendance Status", 220),
        ]:
            ctk.CTkLabel(
                header_frame,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["text_muted"],
                width=w,
                anchor="w"
            ).pack(side="left", padx=12, pady=8)

        self.students_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.students_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _build_bottom_bar(self):
        bottom_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        bottom_card.pack(fill="x", padx=30, pady=(0, 20))

        inner = ctk.CTkFrame(bottom_card, fg_color="transparent")
        inner.pack(padx=20, pady=12, fill="x")

        ctk.CTkButton(
            inner,
            text="Mark All Present",
            command=lambda: self.mark_all("Present"),
            fg_color=self.colors["success"],
            hover_color=self.colors["success_hover"],
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            inner,
            text="Mark All Absent",
            command=lambda: self.mark_all("Absent"),
            fg_color=self.colors["danger"],
            hover_color=self.colors["danger_hover"],
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            inner,
            text="Export CSV",
            command=self.export_csv,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            inner,
            text="Export Excel",
            command=self.export_excel,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            inner,
            text="Save Attendance",
            command=self.save_attendance,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="right", padx=4)

    def load_students(self):
        for w in self.students_frame.winfo_children():
            w.destroy()
        self.attendance_statuses = {}

        course_str = self.course_combo.get()
        class_str = self.class_combo.get()

        if not course_str:
            messagebox.showinfo("Selection Required", "Please select a course first.")
            return

        students = []
        if class_str:
            class_name = class_str.split(" (")[0]
            for cl in self.db.get_classes():
                if cl["class_name"] == class_name:
                    students = self.db.get_class_students(cl["id"])
                    break
            if not students:
                students = self.db.get_students(class_name=class_name)
        else:
            students = self.db.get_students()

        if not students:
            messagebox.showinfo("Info", "No students found for the selected class/course.")
            return

        self.current_students = students

        for s in students:
            row = ctk.CTkFrame(self.students_frame, fg_color="#0F172A", corner_radius=8)
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row,
                text=s["student_id"],
                width=140,
                anchor="w",
                font=ctk.CTkFont(size=12),
                text_color=self.colors["text_muted"]
            ).pack(side="left", padx=12, pady=8)

            ctk.CTkLabel(
                row,
                text=s["full_name"],
                width=320,
                anchor="w",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["text_main"]
            ).pack(side="left", padx=12, pady=8)

            status_var = ctk.StringVar(value="Present")
            self.attendance_statuses[s["id"]] = status_var
            status_menu = ctk.CTkOptionMenu(
                row,
                values=["Present", "Absent", "Late", "Excused"],
                variable=status_var,
                width=180,
                height=32,
                corner_radius=6
            )
            status_menu.pack(side="left", padx=12, pady=8)

    def mark_all(self, status):
        for var in self.attendance_statuses.values():
            var.set(status)

    def save_attendance(self):
        if not self.current_students:
            messagebox.showinfo("Info", "No students loaded.")
            return

        course_str = self.course_combo.get()
        if not course_str:
            messagebox.showerror("Validation Error", "Select a course.")
            return
        course_code = course_str.split(" - ")[0]
        course_id = None
        for c in self.db.get_courses():
            if c["course_code"] == course_code:
                course_id = c["id"]
                break
        if not course_id:
            messagebox.showerror("Error", "Course not found.")
            return

        attendance_date = self.date_entry.get().strip()
        class_str = self.class_combo.get()
        class_id = None
        if class_str:
            class_name = class_str.split(" (")[0]
            for cl in self.db.get_classes():
                if cl["class_name"] == class_name:
                    class_id = cl["id"]
                    break

        count = 0
        for sid, var in self.attendance_statuses.items():
            if self.db.take_attendance(
                    sid, course_id, attendance_date, var.get(),
                    taken_by=self.user["id"], class_id=class_id
            ):
                count += 1

        messagebox.showinfo("Success", f"Attendance successfully saved for {count} students.")
        self.load_students()

    def export_csv(self):
        if not self.current_students:
            messagebox.showinfo("Info", "No data to export. Load students first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        data = []
        for s in self.current_students:
            status = self.attendance_statuses.get(s["id"], ctk.StringVar(value="Present")).get()
            data.append({
                "Student ID": s["student_id"],
                "Name": s["full_name"],
                "Status": status,
                "Date": self.date_entry.get(),
                "Time": self.time_entry.get(),
                "Course": self.course_combo.get(),
            })
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)
        messagebox.showinfo("Success", f"Exported attendance to:\n{path}")

    def export_excel(self):
        if not self.current_students:
            messagebox.showinfo("Info", "No data to export. Load students first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
        data = []
        for s in self.current_students:
            status = self.attendance_statuses.get(s["id"], ctk.StringVar(value="Present")).get()
            data.append({
                "Student ID": s["student_id"],
                "Name": s["full_name"],
                "Status": status,
                "Date": self.date_entry.get(),
                "Time": self.time_entry.get(),
                "Course": self.course_combo.get(),
            })
        df = pd.DataFrame(data)
        df.to_excel(path, index=False)
        messagebox.showinfo("Success", f"Exported attendance to:\n{path}")


class AttendanceView(ctk.CTkFrame):
    def __init__(self, db, parent, user=None):
        super().__init__(parent, fg_color="#0F172A")  # Slate 900 background
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)

        self.colors = {
            "bg_dark": "#0F172A",
            "card_bg": "#1E293B",
            "card_border": "#334155",
            "primary": "#0EA5E9",
            "primary_hover": "#0284C7",
            "danger": "#EF4444",
            "danger_hover": "#DC2626",
            "neutral_btn": "#334155",
            "neutral_hover": "#475569",
            "text_main": "#F8FAFC",
            "text_muted": "#94A3B8"
        }

        self._build_header()
        self._build_filters()
        self._build_table()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = "My Attendance" if (self.user and self.user.get("role") == "student") else "Attendance History"

        ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(side="left")

        ctk.CTkButton(
            header_frame,
            text="Export Excel",
            command=self.export_excel,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            header_frame,
            text="Export CSV",
            command=self.export_csv,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right", padx=4)

    def _build_filters(self):
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

        def add_lbl(text):
            lbl = ctk.CTkLabel(inner, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                               text_color=self.colors["text_muted"])
            lbl.pack(side="left", padx=(8, 4))

        add_lbl("Student:")
        self.student_entry = ctk.CTkEntry(inner, width=150, height=36, corner_radius=8, placeholder_text="Search...")
        self.student_entry.pack(side="left", padx=2)

        add_lbl("Course:")
        self.course_combo = ctk.CTkComboBox(inner, width=160, height=36, corner_radius=8, values=["All"])
        self.course_combo.pack(side="left", padx=2)

        add_lbl("Date:")
        self.date_entry = ctk.CTkEntry(inner, width=110, height=36, corner_radius=8, placeholder_text="YYYY-MM-DD")
        self.date_entry.pack(side="left", padx=2)

        add_lbl("Status:")
        self.status_combo = ctk.CTkComboBox(
            inner, width=130, height=36, corner_radius=8,
            values=["All", "Present", "Absent", "Late", "Excused"]
        )
        self.status_combo.pack(side="left", padx=2)

        add_lbl("Class:")
        self.class_combo = ctk.CTkComboBox(inner, width=160, height=36, corner_radius=8, values=["All"])
        self.class_combo.pack(side="left", padx=2)

        ctk.CTkButton(
            inner,
            text="Filter",
            command=self.load_attendance,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(10, 2))

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

        courses = self.db.get_courses()
        self.course_combo.configure(values=["All"] + [f"{c['course_code']} - {c['course_name']}" for c in courses])

        classes = self.db.get_classes()
        self.class_combo.configure(
            values=["All"] + [f"{c['class_name']} ({c['department_name']})" for c in classes] if classes else ["All"]
        )

    def reset_filters(self):
        self.student_entry.delete(0, "end")
        self.course_combo.set("All")
        self.date_entry.delete(0, "end")
        self.status_combo.set("All")
        self.class_combo.set("All")
        self.load_attendance()

    def _build_table(self):
        table_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Action Buttons Header inside Table Card
        top_action_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        top_action_frame.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkButton(
            top_action_frame,
            text="Edit Status",
            width=90,
            height=34,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            command=self._edit_selected_row
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            top_action_frame,
            text="Delete",
            width=90,
            height=34,
            fg_color=self.colors["danger"],
            hover_color=self.colors["danger_hover"],
            command=self._delete_selected_row
        ).pack(side="left", padx=2)

        # Treeview Wrapper
        self.table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Custom Styled Treeview Table
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Attendance.Treeview",
            background="#1E293B",
            foreground="#F8FAFC",
            fieldbackground="#1E293B",
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Attendance.Treeview.Heading",
            background="#0F172A",
            foreground="#94A3B8",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "Attendance.Treeview",
            background=[("selected", "#334155")],
            foreground=[("selected", "#FFFFFF")]
        )
        style.map(
            "Attendance.Treeview.Heading",
            background=[("active", "#1E293B")]
        )

        columns = ("date", "time", "sid", "student_name", "course_code", "status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", style="Attendance.Treeview",
                                 selectmode="browse")

        headings = {
            "date": ("Date", 110),
            "time": ("Time", 80),
            "sid": ("Student ID", 110),
            "student_name": ("Student Name", 200),
            "course_code": ("Course", 130),
            "status": ("Status", 110)
        }

        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, minwidth=width, stretch=True, anchor="w")

        scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_attendance()

    def load_attendance(self):
        self.tree.delete(*self.tree.get_children())
        records = self._get_current_records()

        for r in records:
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                r.get("attendance_date", ""),
                r.get("attendance_time", "") or "—",
                r.get("sid", "") or "—",
                r.get("student_name", "") or "—",
                r.get("course_code", "") or "—",
                r.get("status", "")
            ))

    def _get_selected_rid(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select an attendance record from the table.")
            return None
        return int(sel[0])

    def _edit_selected_row(self):
        rid = self._get_selected_rid()
        if rid:
            item = self.tree.item(str(rid))
            current_status = item["values"][5]
            self.edit_status(rid, current_status)

    def _delete_selected_row(self):
        rid = self._get_selected_rid()
        if rid:
            self.delete_record(rid)

    def edit_status(self, rid, current):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Attendance Record")
        dialog.geometry("340x220")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        dialog.after(100, dialog.grab_set)

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text="Update Status",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(15, 10))

        status_var = ctk.StringVar(value=current)
        menu = ctk.CTkOptionMenu(
            card,
            values=["Present", "Absent", "Late", "Excused"],
            variable=status_var,
            width=220,
            height=36,
            corner_radius=8
        )
        menu.pack(pady=5)

        def save():
            self.db.update_attendance(rid, status_var.get())
            messagebox.showinfo("Success", "Attendance record updated successfully.")
            dialog.destroy()
            self.load_attendance()

        ctk.CTkButton(
            card,
            text="Save Changes",
            command=save,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=38,
            corner_radius=8
        ).pack(fill="x", padx=20, pady=(15, 10))

    def delete_record(self, rid):
        if messagebox.askyesno("Confirm Action", "Are you sure you want to delete this attendance record?"):
            self.db.delete_attendance(rid)
            self.load_attendance()

    def export_csv(self):
        records = self._get_current_records()
        if not records:
            messagebox.showinfo("Info", "No attendance records available to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        data = [
            {
                "Date": r.get("attendance_date", ""),
                "Time": r.get("attendance_time", ""),
                "Student ID": r.get("sid", ""),
                "Name": r.get("student_name", ""),
                "Course": r.get("course_code", ""),
                "Status": r.get("status", ""),
            }
            for r in records
        ]
        df = pd.DataFrame(data)
        df.to_csv(path, index=False)
        messagebox.showinfo("Success", f"Exported attendance history to:\n{path}")

    def export_excel(self):
        records = self._get_current_records()
        if not records:
            messagebox.showinfo("Info", "No attendance records available to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
        data = [
            {
                "Date": r.get("attendance_date", ""),
                "Time": r.get("attendance_time", ""),
                "Student ID": r.get("sid", ""),
                "Name": r.get("student_name", ""),
                "Course": r.get("course_code", ""),
                "Status": r.get("status", ""),
            }
            for r in records
        ]
        df = pd.DataFrame(data)
        df.to_excel(path, index=False)
        messagebox.showinfo("Success", f"Exported attendance history to:\n{path}")

    def _get_current_records(self):
        kwargs = {}
        search = self.student_entry.get().strip()
        if search:
            students = self.db.get_students(search=search)
            if students:
                kwargs["student_id"] = students[0]["id"]

        course_str = self.course_combo.get()
        if course_str and course_str != "All":
            cc = course_str.split(" - ")[0]
            for c in self.db.get_courses():
                if c["course_code"] == cc:
                    kwargs["course_id"] = c["id"]
                    break

        class_str = self.class_combo.get()
        if class_str and class_str != "All":
            cn = class_str.split(" (")[0]
            for cl in self.db.get_classes():
                if cl["class_name"] == cn:
                    kwargs["class_id"] = cl["id"]
                    break

        date_val = self.date_entry.get().strip()
        if date_val:
            kwargs["attendance_date"] = date_val

        status = self.status_combo.get()
        if status and status != "All":
            kwargs["status"] = status

        if self.user and self.user.get("role") == "student":
            students = self.db.get_students()
            for s in students:
                if s.get("user_id") == self.user.get("id") or s.get("email") == self.user.get("email"):
                    kwargs["student_id"] = s["id"]
                    break

        return self.db.get_attendance(**kwargs)