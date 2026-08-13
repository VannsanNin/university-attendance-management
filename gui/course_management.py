import customtkinter as ctk
from gui import theme
from gui.skeleton import schedule_table_load, safe_grab
from gui.activity import log
from tkinter import messagebox, ttk


class CourseManagementView(ctk.CTkFrame):
    def __init__(self, db, parent, user=None):
        super().__init__(parent, fg_color=theme.c("bg_dark"))  # Slate 900 background
        self.db = db
        self.user = user
        self.selected_course_id = None
        self.pack(fill="both", expand=True)

        # Unified Color Palette Tokens
        self.colors = theme.colors

        self.build_ui()
        self.load_combo_data()
        schedule_table_load(self, self.table_frame, self.load_courses)

    def build_ui(self):
        # -------------------------------------------------------------
        # Header Section
        # -------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Course / Subject Management",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Manage curriculum courses, department links, credits, and faculty assignments",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_muted"]
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # -------------------------------------------------------------
        # Form Card Section
        # -------------------------------------------------------------
        form_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        form_card.pack(fill="x", padx=30, pady=(5, 15))

        form_grid = ctk.CTkFrame(form_card, fg_color="transparent")
        form_grid.pack(fill="x", padx=20, pady=15)

        for i in range(4):
            form_grid.grid_columnconfigure(i, weight=1)

        def add_field_label(text, row, col):
            lbl = ctk.CTkLabel(
                form_grid,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["text_muted"]
            )
            lbl.grid(row=row, column=col, padx=(10, 5), pady=6, sticky="e")

        # Row 0
        add_field_label("Course Code *", 0, 0)
        self.code_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8, placeholder_text="e.g. CS101")
        self.code_entry.grid(row=0, column=1, padx=(5, 15), pady=6, sticky="ew")

        add_field_label("Course Name *", 0, 2)
        self.name_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8,
                                       placeholder_text="e.g. Intro to Programming")
        self.name_entry.grid(row=0, column=3, padx=(5, 15), pady=6, sticky="ew")

        # Row 1
        add_field_label("Department", 1, 0)
        self.dept_combo = ctk.CTkComboBox(form_grid, values=[""], height=36, corner_radius=8)
        self.dept_combo.grid(row=1, column=1, padx=(5, 15), pady=6, sticky="ew")

        add_field_label("Teacher", 1, 2)
        self.teacher_combo = ctk.CTkComboBox(form_grid, values=[""], height=36, corner_radius=8)
        self.teacher_combo.grid(row=1, column=3, padx=(5, 15), pady=6, sticky="ew")

        # Row 2
        add_field_label("Credits", 2, 0)
        self.credit_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8, placeholder_text="e.g. 3")
        self.credit_entry.grid(row=2, column=1, padx=(5, 15), pady=6, sticky="ew")

        add_field_label("Semester", 2, 2)
        self.sem_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8, placeholder_text="e.g. 1")
        self.sem_entry.grid(row=2, column=3, padx=(5, 15), pady=6, sticky="ew")

        # Row 3
        add_field_label("Academic Year", 3, 0)
        self.acad_year_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8)
        self.acad_year_entry.grid(row=3, column=1, padx=(5, 15), pady=6, sticky="ew")
        self.acad_year_entry.insert(0, "2024/2025")

        # Toolbar Actions Inside Form Card
        btn_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(5, 15))

        actions = [
            ("+ Add Course", self.add_course, self.colors["primary"], self.colors["primary_hover"]),
            ("Edit Selected", self.edit_course, self.colors["neutral_btn"], self.colors["neutral_hover"]),
            ("Assign Teacher", self.assign_teacher, self.colors["neutral_btn"], self.colors["neutral_hover"]),
            ("Delete Selected", self.delete_course, self.colors["danger"], self.colors["danger_hover"]),
        ]

        for text, cmd, bg_col, hover_col in actions:
            ctk.CTkButton(
                btn_frame,
                text=text,
                height=36,
                corner_radius=8,
                fg_color=bg_col,
                hover_color=hover_col,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=cmd
            ).pack(side="left", padx=4)

        # -------------------------------------------------------------
        # Table Section (List Card & Search Bar)
        # -------------------------------------------------------------
        table_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Search Controls
        search_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(15, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search course code, name, or teacher...",
            width=320,
            height=38,
            corner_radius=8
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self.load_courses())

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=90,
            height=38,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self.load_courses
        ).pack(side="left", padx=8)

        # Table Wrapper
        self.table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Treeview Styling
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Course.Treeview",
            background=theme.c("table_bg"),
            foreground=theme.c("table_fg"),
            fieldbackground=theme.c("table_bg"),
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Course.Treeview.Heading",
            background=theme.c("table_head_bg"),
            foreground=theme.c("table_head_fg"),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "Course.Treeview",
            background=[("selected", theme.c("table_selected"))],
            foreground=[("selected", theme.c("table_selected_fg"))]
        )
        style.map(
            "Course.Treeview.Heading",
            background=[("active", theme.c("table_head_active"))]
        )

        columns = ("code", "name", "department", "teacher", "credit", "semester", "academic_year")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", style="Course.Treeview",
                                 selectmode="browse")

        headings = {
            "code": ("Code", 90),
            "name": ("Course Name", 200),
            "department": ("Department", 150),
            "teacher": ("Assigned Teacher", 160),
            "credit": ("Credits", 70),
            "semester": ("Semester", 80),
            "academic_year": ("Academic Year", 120)
        }

        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, minwidth=width, stretch=True, anchor="w")

        scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # -------------------------------------------------------------
    # Business Logic & Database Helpers
    # -------------------------------------------------------------
    def load_combo_data(self):
        teachers = self.db.get_teachers()
        self.teacher_combo.configure(values=[""] + [f"{t['teacher_id']} - {t['full_name']}" for t in teachers])
        depts = self.db.get_departments()
        self.dept_combo.configure(values=[""] + [d["name"] for d in depts])

    def add_course(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        if not code or not name:
            messagebox.showerror("Validation Error", "Course Code and Course Name are required.")
            return

        dept_id = None
        d_name = self.dept_combo.get()
        for d in self.db.get_departments():
            if d["name"] == d_name:
                dept_id = d["id"]
                break

        teacher_id = None
        t_str = self.teacher_combo.get()
        if t_str and " - " in t_str:
            tid = t_str.split(" - ")[0]
            for t in self.db.get_teachers():
                if t["teacher_id"] == tid:
                    teacher_id = t["id"]
                    break

        credit_str = self.credit_entry.get().strip()
        credit = int(credit_str) if credit_str.isdigit() else None
        sem_str = self.sem_entry.get().strip()
        sem = int(sem_str) if sem_str.isdigit() else None
        acad_year = self.acad_year_entry.get().strip() or None

        result = self.db.add_course(code, name, teacher_id, sem, credit, dept_id, acad_year)
        if result:
            messagebox.showinfo("Success", f"Course '{name}' added successfully.")
            log(self.db, self.user, "CREATE", "Course", f"Added course '{name}' ({code}).")
            self.clear_form()
            self.load_courses()
        else:
            messagebox.showerror("Error", "Course code already exists.")

    def edit_course(self):
        if not self.selected_course_id:
            messagebox.showinfo("Selection Required", "Please select a course from the table first.")
            return

        course = None
        for c in self.db.get_courses():
            if c["id"] == self.selected_course_id:
                course = c
                break
        if not course:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Course Details")
        dialog.geometry("420x420")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        safe_grab(dialog)

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text=f"Edit: {course.get('course_code', '')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(15, 10))

        form_f = ctk.CTkFrame(card, fg_color="transparent")
        form_f.pack(fill="both", expand=True, padx=15, pady=5)

        fields = [
            ("course_name", "Course Name"),
            ("semester", "Semester"),
            ("credit", "Credits"),
            ("academic_year", "Academic Year")
        ]
        entries = {}
        for i, (key, label) in enumerate(fields):
            ctk.CTkLabel(form_f, text=label + ":", text_color=self.colors["text_muted"]).grid(row=i, column=0, padx=10,
                                                                                              pady=4, sticky="e")
            e = ctk.CTkEntry(form_f, width=220, height=32)
            e.insert(0, str(course.get(key, "") or ""))
            e.grid(row=i, column=1, padx=10, pady=4, sticky="w")
            entries[key] = e

        row_idx = len(fields)
        ctk.CTkLabel(form_f, text="Department:", text_color=self.colors["text_muted"]).grid(row=row_idx, column=0,
                                                                                            padx=10, pady=4, sticky="e")
        dept_e = ctk.CTkComboBox(form_f, width=220, values=[""] + [d["name"] for d in self.db.get_departments()],
                                 height=32)
        dept_e.set(course.get("department_name", "") or "")
        dept_e.grid(row=row_idx, column=1, padx=10, pady=4, sticky="w")

        teachers = self.db.get_teachers()
        ctk.CTkLabel(form_f, text="Teacher:", text_color=self.colors["text_muted"]).grid(row=row_idx + 1, column=0,
                                                                                         padx=10, pady=4, sticky="e")
        teacher_e = ctk.CTkComboBox(form_f, width=220,
                                    values=[""] + [f"{t['teacher_id']} - {t['full_name']}" for t in teachers],
                                    height=32)

        if course.get("teacher_id"):
            for t in teachers:
                if t["id"] == course.get("teacher_id"):
                    teacher_e.set(f"{t['teacher_id']} - {t['full_name']}")
                    break
        teacher_e.grid(row=row_idx + 1, column=1, padx=10, pady=4, sticky="w")

        def save():
            kwargs = {}
            for key, w in entries.items():
                val = w.get().strip()
                if key in ["semester", "credit"]:
                    kwargs[key] = int(val) if val.isdigit() else None
                else:
                    kwargs[key] = val or None

            d_name = dept_e.get()
            for d in self.db.get_departments():
                if d["name"] == d_name:
                    kwargs["department_id"] = d["id"]
                    break

            t_str = teacher_e.get()
            if t_str and " - " in t_str:
                tid = t_str.split(" - ")[0]
                for t in self.db.get_teachers():
                    if t["teacher_id"] == tid:
                        kwargs["teacher_id"] = t["id"]
                        break
            elif not t_str:
                kwargs["teacher_id"] = None

            self.db.update_course(self.selected_course_id, **kwargs)
            messagebox.showinfo("Success", "Course updated successfully.")
            log(self.db, self.user, "UPDATE", "Course",
                f"Updated course '{course.get('course_name')}' ({course.get('course_code')}).")
            dialog.destroy()
            self.load_courses()

        ctk.CTkButton(
            card,
            text="Save Changes",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=38,
            command=save
        ).pack(fill="x", padx=20, pady=(10, 15))

    def delete_course(self):
        if not self.selected_course_id:
            messagebox.showinfo("Selection Required", "Please select a course from the table first.")
            return
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this course?"):
            self.db.delete_course(self.selected_course_id)
            log(self.db, self.user, "DELETE", "Course", f"Deleted course (ID {self.selected_course_id}).")
            self.selected_course_id = None
            self.load_courses()

    def assign_teacher(self):
        if not self.selected_course_id:
            messagebox.showinfo("Selection Required", "Please select a course from the table first.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Assign Faculty Member")
        dialog.geometry("380x220")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        safe_grab(dialog)

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text="Select Faculty Teacher:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(15, 10))

        teachers = self.db.get_teachers()
        combo = ctk.CTkComboBox(
            card,
            width=280,
            height=36,
            corner_radius=8,
            values=[""] + [f"{t['teacher_id']} - {t['full_name']}" for t in teachers]
        )
        combo.pack(pady=5)

        def save():
            t_str = combo.get()
            teacher_id = None
            if t_str and " - " in t_str:
                tid = t_str.split(" - ")[0]
                for t in self.db.get_teachers():
                    if t["teacher_id"] == tid:
                        teacher_id = t["id"]
                        break
            self.db.update_course(self.selected_course_id, teacher_id=teacher_id)
            messagebox.showinfo("Success", "Teacher assigned successfully.")
            log(self.db, self.user, "UPDATE", "Course",
                f"Assigned teacher to course (ID {self.selected_course_id}).")
            dialog.destroy()
            self.load_courses()

        ctk.CTkButton(
            card,
            text="Confirm Assignment",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=38,
            command=save
        ).pack(fill="x", padx=20, pady=(15, 10))

    def clear_form(self):
        self.code_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.credit_entry.delete(0, "end")
        self.sem_entry.delete(0, "end")
        self.dept_combo.set("")
        self.teacher_combo.set("")
        self.selected_course_id = None

    def load_courses(self):
        self.tree.delete(*self.tree.get_children())

        search = self.search_entry.get().strip() or None
        courses = self.db.get_courses(search=search)

        for c in courses:
            self.tree.insert("", "end", iid=str(c["id"]), values=(
                c["course_code"],
                c["course_name"],
                c.get("department_name", "") or "—",
                c.get("teacher_name", "") or "—",
                str(c.get("credit", "") or "—"),
                str(c.get("semester", "") or "—"),
                str(c.get("academic_year", "") or "—")
            ))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_course_id = int(sel[0])

    def select_course(self, cid):
        self.selected_course_id = cid