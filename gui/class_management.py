import customtkinter as ctk
from tkinter import messagebox, ttk


class ClassManagementView(ctk.CTkFrame):
    def __init__(self, db, parent):
        super().__init__(parent, fg_color="#0F172A")  # Slate 900 background
        self.db = db
        self.selected_class_id = None
        self.pack(fill="both", expand=True)

        # Unified Color Palette Tokens
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

        self.build_ui()
        self.load_combo_data()
        self.after(50, self.load_classes)

    def build_ui(self):
        # -------------------------------------------------------------
        # Header Section
        # -------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Class Management",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Manage class sections, room allocations, advisors, and student enrollments",
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
        add_field_label("Class Name *", 0, 0)
        self.name_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8, placeholder_text="e.g. CS-Year2-A")
        self.name_entry.grid(row=0, column=1, padx=(5, 15), pady=6, sticky="ew")

        add_field_label("Department", 0, 2)
        self.dept_combo = ctk.CTkComboBox(form_grid, values=[""], height=36, corner_radius=8)
        self.dept_combo.grid(row=0, column=3, padx=(5, 15), pady=6, sticky="ew")

        # Row 1
        add_field_label("Advisor", 1, 0)
        self.advisor_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8, placeholder_text="e.g. Prof. Smith")
        self.advisor_entry.grid(row=1, column=1, padx=(5, 15), pady=6, sticky="ew")

        add_field_label("Room", 1, 2)
        self.room_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8, placeholder_text="e.g. Lab 302")
        self.room_entry.grid(row=1, column=3, padx=(5, 15), pady=6, sticky="ew")

        # Row 2
        add_field_label("Schedule", 2, 0)
        self.schedule_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8,
                                           placeholder_text="e.g. Mon/Wed 08:00-10:00")
        self.schedule_entry.grid(row=2, column=1, padx=(5, 15), pady=6, sticky="ew")

        add_field_label("Academic Year", 2, 2)
        self.acad_year_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8)
        self.acad_year_entry.grid(row=2, column=3, padx=(5, 15), pady=6, sticky="ew")
        self.acad_year_entry.insert(0, "2024/2025")

        # Row 3
        add_field_label("Semester", 3, 0)
        self.sem_entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8, placeholder_text="e.g. 1")
        self.sem_entry.grid(row=3, column=1, padx=(5, 15), pady=6, sticky="ew")

        # Toolbar Actions Inside Form Card
        btn_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(5, 15))

        actions = [
            ("+ Create Class", self.create_class, self.colors["primary"], self.colors["primary_hover"]),
            ("Assign Students", self.assign_students, self.colors["neutral_btn"], self.colors["neutral_hover"]),
            ("Assign Teacher", self.assign_teacher, self.colors["neutral_btn"], self.colors["neutral_hover"]),
            ("View Student List", self.view_student_list, self.colors["neutral_btn"], self.colors["neutral_hover"]),
            ("Delete Selected", self.delete_class, self.colors["danger"], self.colors["danger_hover"]),
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
            placeholder_text="🔍 Search class name...",
            width=320,
            height=38,
            corner_radius=8
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self.load_classes())

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=90,
            height=38,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self.load_classes
        ).pack(side="left", padx=8)

        # Table Wrapper
        self.table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Custom Styled Treeview Table
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Class.Treeview",
            background="#1E293B",
            foreground="#F8FAFC",
            fieldbackground="#1E293B",
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Class.Treeview.Heading",
            background="#0F172A",
            foreground="#94A3B8",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "Class.Treeview",
            background=[("selected", "#334155")],
            foreground=[("selected", "#FFFFFF")]
        )
        style.map(
            "Class.Treeview.Heading",
            background=[("active", "#1E293B")]
        )

        columns = ("name", "department", "advisor", "room", "schedule", "total_students")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", style="Class.Treeview",
                                 selectmode="browse")

        headings = {
            "name": ("Class Name", 160),
            "department": ("Department", 160),
            "advisor": ("Advisor", 140),
            "room": ("Room", 100),
            "schedule": ("Schedule", 160),
            "total_students": ("Total Students", 110)
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
        depts = self.db.get_departments()
        self.dept_combo.configure(values=[""] + [d["name"] for d in depts])

    def create_class(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Class name is required.")
            return

        dept_id = None
        dn = self.dept_combo.get()
        for d in self.db.get_departments():
            if d["name"] == dn:
                dept_id = d["id"]
                break

        advisor = self.advisor_entry.get().strip() or None
        room = self.room_entry.get().strip() or None
        schedule = self.schedule_entry.get().strip() or None
        acad_year = self.acad_year_entry.get().strip() or None
        sem_str = self.sem_entry.get().strip()
        sem = int(sem_str) if sem_str.isdigit() else None

        result = self.db.add_class(name, dept_id, None, advisor, room, schedule, acad_year, sem)
        if result:
            messagebox.showinfo("Success", f"Class '{name}' created successfully.")
            self.clear_form()
            self.load_classes()
        else:
            messagebox.showerror("Error", "Failed to create class.")

    def assign_students(self):
        if not self.selected_class_id:
            messagebox.showinfo("Selection Required", "Please select a class from the table first.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Assign Students to Class")
        dialog.geometry("520x450")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        dialog.after(100, dialog.grab_set)

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text="Enroll Students",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(15, 5))

        search_f = ctk.CTkFrame(card, fg_color="transparent")
        search_f.pack(fill="x", padx=15, pady=5)

        search_e = ctk.CTkEntry(search_f, placeholder_text="Search students...", height=36, corner_radius=8)
        search_e.pack(side="left", padx=(0, 5), fill="x", expand=True)

        scroll = ctk.CTkScrollableFrame(card, fg_color="#0F172A", corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        enrolled = {s["id"] for s in self.db.get_class_students(self.selected_class_id)}

        def refresh(search_text=""):
            for w in scroll.winfo_children():
                w.destroy()
            students = self.db.get_students(search=search_text or None)
            for s in students:
                if s["id"] in enrolled:
                    continue
                row = ctk.CTkFrame(scroll, fg_color=self.colors["card_bg"], corner_radius=6)
                row.pack(fill="x", pady=2, padx=2)
                ctk.CTkLabel(
                    row,
                    text=f"{s['student_id']} - {s['full_name']}",
                    anchor="w",
                    text_color=self.colors["text_main"]
                ).pack(side="left", fill="x", expand=True, padx=10, pady=5)

                ctk.CTkButton(
                    row,
                    text="Add",
                    width=60,
                    height=28,
                    corner_radius=6,
                    fg_color=self.colors["primary"],
                    hover_color=self.colors["primary_hover"],
                    command=lambda sid=s["id"]: self.do_assign_student(sid, dialog)
                ).pack(side="right", padx=5, pady=5)

        def on_search():
            refresh(search_e.get().strip())

        ctk.CTkButton(
            search_f,
            text="Search",
            width=80,
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=on_search
        ).pack(side="left")

        search_e.bind("<Return>", lambda e: on_search())
        refresh()

    def do_assign_student(self, student_id, dialog):
        self.db.add_student_to_class(self.selected_class_id, student_id)
        dialog.destroy()
        self.load_classes()

    def assign_teacher(self):
        if not self.selected_class_id:
            messagebox.showinfo("Selection Required", "Please select a class from the table first.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Assign Class Teacher")
        dialog.geometry("380x220")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        dialog.after(100, dialog.grab_set)

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
            self.db.update_class(self.selected_class_id, teacher_id=teacher_id)
            messagebox.showinfo("Success", "Teacher assigned successfully.")
            dialog.destroy()
            self.load_classes()

        ctk.CTkButton(
            card,
            text="Confirm Assignment",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=38,
            command=save
        ).pack(fill="x", padx=20, pady=(15, 10))

    def view_student_list(self):
        if not self.selected_class_id:
            messagebox.showinfo("Selection Required", "Please select a class from the table first.")
            return

        students = self.db.get_class_students(self.selected_class_id)
        dialog = ctk.CTkToplevel(self)
        dialog.title("Class Student Roster")
        dialog.geometry("520x450")
        dialog.configure(fg_color=self.colors["bg_dark"])

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text="Enrolled Students",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(15, 5))

        if not students:
            ctk.CTkLabel(card, text="No students enrolled in this class.", text_color=self.colors["text_muted"]).pack(
                pady=30)
            return

        scroll = ctk.CTkScrollableFrame(card, fg_color="#0F172A", corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        for s in students:
            row = ctk.CTkFrame(scroll, fg_color=self.colors["card_bg"], corner_radius=6)
            row.pack(fill="x", pady=2, padx=2)

            ctk.CTkLabel(
                row,
                text=f"{s['student_id']} - {s['full_name']}",
                anchor="w",
                text_color=self.colors["text_main"]
            ).pack(side="left", fill="x", expand=True, padx=10, pady=5)

            ctk.CTkButton(
                row,
                text="Remove",
                width=70,
                height=28,
                corner_radius=6,
                fg_color=self.colors["danger"],
                hover_color=self.colors["danger_hover"],
                command=lambda sid=s["id"]: self.do_remove_student(sid, dialog)
            ).pack(side="right", padx=5, pady=5)

    def do_remove_student(self, student_id, dialog):
        if self.selected_class_id and messagebox.askyesno("Confirm Action", "Remove student from this class?"):
            self.db.remove_student_from_class(self.selected_class_id, student_id)
            dialog.destroy()
            self.load_classes()

    def delete_class(self):
        if not self.selected_class_id:
            messagebox.showinfo("Selection Required", "Please select a class from the table first.")
            return

        cls = next((c for c in self.db.get_classes() if c["id"] == self.selected_class_id), None)
        if cls and messagebox.askyesno("Confirm Deletion",
                                       f"Are you sure you want to delete class '{cls['class_name']}'?"):
            self.db.delete_class(self.selected_class_id)
            self.selected_class_id = None
            self.clear_form()
            self.load_classes()

    def clear_form(self):
        self.name_entry.delete(0, "end")
        self.advisor_entry.delete(0, "end")
        self.room_entry.delete(0, "end")
        self.schedule_entry.delete(0, "end")
        self.sem_entry.delete(0, "end")
        self.dept_combo.set("")
        self.selected_class_id = None

    def load_classes(self):
        self.tree.delete(*self.tree.get_children())

        search = self.search_entry.get().strip().lower()
        classes = self.db.get_classes()
        if search:
            classes = [c for c in classes if search in c["class_name"].lower()]

        for cl in classes:
            total = len(self.db.get_class_students(cl["id"]))
            self.tree.insert("", "end", iid=str(cl["id"]), values=(
                cl["class_name"],
                cl.get("department_name", "") or "—",
                cl.get("advisor", "") or "—",
                cl.get("room", "") or "—",
                cl.get("schedule", "") or "—",
                str(total)
            ))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if sel:
            cid = int(sel[0])
            self.select_class(cid)

    def select_class(self, cid):
        self.selected_class_id = cid
        cl = next((c for c in self.db.get_classes() if c["id"] == cid), None)
        if cl:
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, cl["class_name"])
            self.dept_combo.set(cl.get("department_name", "") or "")
            self.advisor_entry.delete(0, "end")
            self.advisor_entry.insert(0, cl.get("advisor", "") or "")
            self.room_entry.delete(0, "end")
            self.room_entry.insert(0, cl.get("room", "") or "")
            self.schedule_entry.delete(0, "end")
            self.schedule_entry.insert(0, cl.get("schedule", "") or "")
            self.acad_year_entry.delete(0, "end")
            self.acad_year_entry.insert(0, cl.get("academic_year", "") or "")
            self.sem_entry.delete(0, "end")
            self.sem_entry.insert(0, str(cl.get("semester", "") or ""))