import customtkinter as ctk
from gui import theme
from gui.skeleton import schedule_table_load
from gui.activity import log
from tkinter import messagebox, filedialog, ttk
from PIL import Image
import os
import pandas as pd


class StudentManagementView(ctk.CTkFrame):
    def __init__(self, db, parent, user=None):
        super().__init__(parent, fg_color=theme.c("bg_dark"))  # Slate 900 background
        self.db = db
        self.user = user
        self.photo_path = None
        self.selected_student_id = None
        self.pack(fill="both", expand=True)

        # Color Palette Definition
        self.colors = theme.colors

        self.build_ui()
        schedule_table_load(self, self.table_frame, self.load_students)

    def build_ui(self):
        # -------------------------------------------------------------
        # Header Section
        # -------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Student Management",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Manage student records, academic information, and guardian details",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_muted"]
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # -------------------------------------------------------------
        # Top Form Section (Tabbed Inputs Card)
        # -------------------------------------------------------------
        form_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        form_card.pack(fill="x", padx=30, pady=(5, 15))

        self.tab_view = ctk.CTkTabview(
            form_card,
            height=230,
            fg_color="transparent",
            segmented_button_fg_color=theme.c("bg_dark"),
            segmented_button_selected_color=self.colors["primary"],
            segmented_button_selected_hover_color=self.colors["primary_hover"]
        )
        self.tab_view.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab_info = self.tab_view.add("Student Information")
        self.tab_acad = self.tab_view.add("Academic Information")
        self.tab_guard = self.tab_view.add("Guardian Information")

        self.build_student_info_tab()
        self.build_academic_info_tab()
        self.build_guardian_info_tab()

        # Action Buttons Toolbar
        btn_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Action buttons configuration
        actions = [
            ("+ Add Student", self.add_student, self.colors["primary"], self.colors["primary_hover"]),
            ("Edit Selected", self.edit_student, self.colors["neutral_btn"], self.colors["neutral_hover"]),
            ("Delete Selected", self.delete_student, self.colors["danger"], self.colors["danger_hover"]),
            ("Import Excel", self.import_excel, self.colors["success"], self.colors["success_hover"]),
            ("Export Excel", self.export_excel, self.colors["neutral_btn"], self.colors["neutral_hover"]),
            ("Print Report", self.print_students, self.colors["neutral_btn"], self.colors["neutral_hover"]),
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
        # Bottom Table Section (List Card & Search Bar)
        # -------------------------------------------------------------
        table_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Search Bar Header
        search_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(15, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search student name, ID, or email...",
            width=320,
            height=38,
            corner_radius=8
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self.load_students())

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=90,
            height=38,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self.load_students
        ).pack(side="left", padx=8)

        # Table Container
        self.table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Treeview Setup & Styling
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Student.Treeview",
            background=theme.c("table_bg"),
            foreground=theme.c("table_fg"),
            fieldbackground=theme.c("table_bg"),
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Student.Treeview.Heading",
            background=theme.c("table_head_bg"),
            foreground=theme.c("table_head_fg"),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "Student.Treeview",
            background=[("selected", theme.c("table_selected"))],
            foreground=[("selected", theme.c("table_selected_fg"))]
        )
        style.map(
            "Student.Treeview.Heading",
            background=[("active", theme.c("table_head_active"))]
        )

        columns = ("id", "name", "gender", "department", "year", "class", "phone", "email")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", style="Student.Treeview",
                                 selectmode="browse")

        headings = {
            "id": ("ID", 70),
            "name": ("Full Name", 170),
            "gender": ("Gender", 80),
            "department": ("Department", 150),
            "year": ("Year", 55),
            "class": ("Class", 110),
            "phone": ("Phone", 115),
            "email": ("Email Address", 190)
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
    # Form Tab Builders
    # -------------------------------------------------------------
    def build_student_info_tab(self):
        f = self.tab_info
        for i in range(4):
            f.grid_columnconfigure(i, weight=1)

        fields = [
            ("Student ID:", 0, 0), ("First Name:", 0, 2),
            ("Last Name:", 1, 0), ("Gender:", 1, 2),
            ("Date of Birth:", 2, 0), ("Nationality:", 2, 2),
            ("Email:", 3, 0), ("Phone Number:", 3, 2),
            ("Address:", 4, 0),
        ]
        self.entries = {}
        for label, row, col in fields:
            lbl = ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                               text_color=self.colors["text_muted"])
            lbl.grid(row=row, column=col, padx=(10, 5), pady=6, sticky="e")

            if label == "Gender:":
                entry = ctk.CTkComboBox(f, values=["Male", "Female", "Other"], height=34, corner_radius=8)
            else:
                entry = ctk.CTkEntry(f, height=34, corner_radius=8)

            entry.grid(row=row, column=col + 1, padx=(5, 15), pady=6, sticky="ew")
            self.entries[label] = entry

        self.address_entry = self.entries["Address:"]

        # Photo Field Row
        ctk.CTkLabel(f, text="Photo:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=self.colors["text_muted"]).grid(row=4, column=2, padx=(10, 5), pady=6, sticky="e")

        photo_box = ctk.CTkFrame(f, fg_color="transparent")
        photo_box.grid(row=4, column=3, padx=(5, 15), pady=6, sticky="w")

        self.photo_label = ctk.CTkLabel(photo_box, text="No file selected", text_color=self.colors["text_muted"],
                                        font=ctk.CTkFont(size=11))
        self.photo_label.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            photo_box,
            text="Browse...",
            width=80,
            height=30,
            corner_radius=6,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            command=self.browse_photo
        ).pack(side="left")

    def build_academic_info_tab(self):
        f = self.tab_acad
        for i in range(4):
            f.grid_columnconfigure(i, weight=1)

        def add_lbl(text, row, col):
            lbl = ctk.CTkLabel(f, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                               text_color=self.colors["text_muted"])
            lbl.grid(row=row, column=col, padx=(10, 5), pady=8, sticky="e")

        add_lbl("Department:", 0, 0)
        self.dept_combo = ctk.CTkComboBox(f, values=[""], height=34, corner_radius=8)
        self.dept_combo.grid(row=0, column=1, padx=(5, 15), pady=8, sticky="ew")

        add_lbl("Program:", 0, 2)
        self.program_entry = ctk.CTkEntry(f, height=34, corner_radius=8)
        self.program_entry.grid(row=0, column=3, padx=(5, 15), pady=8, sticky="ew")

        add_lbl("Year:", 1, 0)
        self.year_combo = ctk.CTkComboBox(f, values=[""] + [str(i) for i in range(1, 5)],
                                          height=34, corner_radius=8)
        self.year_combo.grid(row=1, column=1, padx=(5, 15), pady=8, sticky="ew")

        add_lbl("Semester:", 1, 2)
        self.semester_entry = ctk.CTkEntry(f, height=34, corner_radius=8)
        self.semester_entry.grid(row=1, column=3, padx=(5, 15), pady=8, sticky="ew")

        add_lbl("Class:", 2, 0)
        self.class_combo = ctk.CTkComboBox(f, values=[""], height=34, corner_radius=8)
        self.class_combo.grid(row=2, column=1, padx=(5, 15), pady=8, sticky="ew")

        self.load_departments()
        self.load_classes()

    def build_guardian_info_tab(self):
        f = self.tab_guard
        f.grid_columnconfigure(1, weight=1)

        def add_lbl(text, row):
            lbl = ctk.CTkLabel(f, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                               text_color=self.colors["text_muted"])
            lbl.grid(row=row, column=0, padx=(20, 10), pady=10, sticky="e")

        add_lbl("Guardian Name:", 0)
        self.guardian_name_entry = ctk.CTkEntry(f, width=300, height=34, corner_radius=8)
        self.guardian_name_entry.grid(row=0, column=1, padx=(0, 20), pady=10, sticky="w")

        add_lbl("Guardian Phone:", 1)
        self.guardian_phone_entry = ctk.CTkEntry(f, width=300, height=34, corner_radius=8)
        self.guardian_phone_entry.grid(row=1, column=1, padx=(0, 20), pady=10, sticky="w")

        add_lbl("Emergency Contact:", 2)
        self.emergency_entry = ctk.CTkEntry(f, width=300, height=34, corner_radius=8)
        self.emergency_entry.grid(row=2, column=1, padx=(0, 20), pady=10, sticky="w")

    # -------------------------------------------------------------
    # Data Helpers & Business Logic
    # -------------------------------------------------------------
    def load_departments(self):
        depts = self.db.get_departments()
        self.dept_combo.configure(values=[d["name"] for d in depts])

    def load_classes(self):
        classes = self.db.get_classes()
        names = sorted(set(c["class_name"] for c in classes))
        self.class_combo.configure(values=names if names else [""])

    def browse_photo(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if path:
            self.photo_path = path
            self.photo_label.configure(text=os.path.basename(path))

    def get_form_data(self):
        data = {}
        for k, w in self.entries.items():
            if isinstance(w, ctk.CTkComboBox):
                data[k] = w.get()
            else:
                data[k] = w.get().strip()
        return data

    def add_student(self):
        data = self.get_form_data()
        sid = data.get("Student ID:", "")
        first = data.get("First Name:", "")
        last = data.get("Last Name:", "")
        full = f"{first} {last}".strip()
        if not sid or not full:
            messagebox.showerror("Validation Error", "Student ID and Full Name are required.")
            return

        dept_name = self.dept_combo.get()
        dept_id = None
        for d in self.db.get_departments():
            if d["name"] == dept_name:
                dept_id = d["id"]
                break

        class_name = self.class_combo.get() or None

        photo_dest = None
        if self.photo_path:
            ext = os.path.splitext(self.photo_path)[1]
            photo_dest = os.path.join(os.path.dirname(self.db.db_path), "photos", f"{sid}{ext}")
            os.makedirs(os.path.dirname(photo_dest), exist_ok=True)
            try:
                img = Image.open(self.photo_path)
                img.save(photo_dest)
            except Exception:
                photo_dest = None

        year_str = self.year_combo.get().strip()
        year = int(year_str) if year_str.isdigit() else None
        sem_str = self.semester_entry.get().strip()
        sem = int(sem_str) if sem_str.isdigit() else None

        result = self.db.add_student(
            student_id=sid,
            full_name=full,
            first_name=first or None,
            last_name=last or None,
            gender=data.get("Gender:", ""),
            dob=data.get("Date of Birth:", ""),
            nationality=data.get("Nationality:", ""),
            email=data.get("Email:", ""),
            phone=data.get("Phone Number:", ""),
            address=data.get("Address:", ""),
            department_id=dept_id,
            program=self.program_entry.get().strip() or None,
            year=year,
            semester=sem,
            class_name=class_name,
            photo_path=photo_dest,
            guardian_name=self.guardian_name_entry.get().strip() or None,
            guardian_phone=self.guardian_phone_entry.get().strip() or None,
            emergency_contact=self.emergency_entry.get().strip() or None,
        )
        if result:
            username = sid
            password = data.get("Date of Birth:", "") or sid
            user_id = self.db.create_user(username, password, "student", data.get("Email:", "") or None)
            if user_id:
                self.db.link_student_user(result, user_id)
            messagebox.showinfo("Success", f"Student '{full}' added successfully.")
            log(self.db, self.user, "CREATE", "Student", f"Added student {sid} '{full}'.")
            self.clear_form()
            self.load_students()
        else:
            messagebox.showerror("Error", "Student ID already exists in the system.")

    def edit_student(self):
        if not self.selected_student_id:
            messagebox.showinfo("Selection Required", "Please select a student from the table first.")
            return
        student = self.db.get_student(self.selected_student_id)
        if not student:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Student Information")
        dialog.geometry("580x520")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        dialog.after(100, dialog.grab_set)

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text=f"Edit Record: {student.get('full_name', '')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(15, 5))

        tab_view = ctk.CTkTabview(card, height=360, fg_color="transparent")
        tab_view.pack(fill="both", expand=True, padx=10, pady=5)

        tab1 = tab_view.add("Student Info")
        tab2 = tab_view.add("Academic Info")
        tab3 = tab_view.add("Guardian Info")

        entries = {}
        info_fields = [
            ("student_id", "Student ID"), ("first_name", "First Name"),
            ("last_name", "Last Name"), ("gender", "Gender"),
            ("dob", "DOB"), ("nationality", "Nationality"),
            ("email", "Email"), ("phone", "Phone"),
            ("address", "Address"),
        ]
        for i, (key, label) in enumerate(info_fields):
            ctk.CTkLabel(tab1, text=label + ":", text_color=self.colors["text_muted"]).grid(row=i, column=0, padx=5,
                                                                                            pady=3, sticky="e")
            if key == "gender":
                e = ctk.CTkComboBox(tab1, width=220, values=["Male", "Female", "Other"], height=32)
                e.set(str(student.get(key, "") or ""))
            else:
                e = ctk.CTkEntry(tab1, width=220, height=32)
                e.insert(0, str(student.get(key, "") or ""))
            e.grid(row=i, column=1, padx=5, pady=3, sticky="w")
            entries[key] = e

        ctk.CTkLabel(tab2, text="Department:", text_color=self.colors["text_muted"]).grid(row=0, column=0, padx=5,
                                                                                          pady=5, sticky="e")
        dept_e = ctk.CTkComboBox(tab2, width=220, values=[d["name"] for d in self.db.get_departments()], height=32)
        dept_e.set(student.get("department_name", "") or "")
        dept_e.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        entries["department_name"] = dept_e

        acad_fields = [("program", "Program"), ("year", "Year"), ("semester", "Semester")]
        for i, (key, label) in enumerate(acad_fields, start=1):
            ctk.CTkLabel(tab2, text=label + ":", text_color=self.colors["text_muted"]).grid(row=i, column=0, padx=5,
                                                                                            pady=5, sticky="e")
            if key == "year":
                e = ctk.CTkComboBox(tab2, width=220, values=[""] + [str(v) for v in range(1, 5)], height=32)
            else:
                e = ctk.CTkEntry(tab2, width=220, height=32)
            e.insert(0, str(student.get(key, "") or ""))
            e.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            entries[key] = e

        ctk.CTkLabel(tab2, text="Class:", text_color=self.colors["text_muted"]).grid(row=4, column=0, padx=5, pady=5,
                                                                                     sticky="e")
        cls_e = ctk.CTkComboBox(tab2, width=220, values=[""], height=32)
        classes = self.db.get_classes()
        cls_names = sorted(set(c["class_name"] for c in classes))
        cls_e.configure(values=cls_names if cls_names else [""])
        cls_e.set(student.get("class_name", "") or "")
        cls_e.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        entries["class_name"] = cls_e

        guard_fields = [("guardian_name", "Guardian Name"), ("guardian_phone", "Guardian Phone"),
                        ("emergency_contact", "Emergency Contact")]
        for i, (key, label) in enumerate(guard_fields):
            ctk.CTkLabel(tab3, text=label + ":", text_color=self.colors["text_muted"]).grid(row=i, column=0, padx=5,
                                                                                            pady=5, sticky="e")
            e = ctk.CTkEntry(tab3, width=250, height=32)
            e.insert(0, str(student.get(key, "") or ""))
            e.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            entries[key] = e

        def save():
            kwargs = {}
            for key, w in entries.items():
                val = w.get().strip()
                if key in ["year", "semester"]:
                    kwargs[key] = int(val) if val.isdigit() else None
                elif key == "department_name":
                    for d in self.db.get_departments():
                        if d["name"] == val:
                            kwargs["department_id"] = d["id"]
                            break
                else:
                    kwargs[key] = val or None
            if "department_id" not in kwargs:
                kwargs["department_id"] = None

            self.db.update_student(self.selected_student_id, **kwargs)
            log(self.db, self.user, "UPDATE", "Student",
                f"Updated student '{student.get('full_name', student.get('student_id'))}'.")
            messagebox.showinfo("Success", "Student information updated successfully.")
            dialog.destroy()
            self.load_students()

        ctk.CTkButton(
            card,
            text="Save Changes",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=38,
            command=save
        ).pack(fill="x", padx=20, pady=(10, 15))

    def delete_student(self):
        if not self.selected_student_id:
            messagebox.showinfo("Selection Required", "Please select a student from the table first.")
            return
        student = self.db.get_student(self.selected_student_id)
        if student and messagebox.askyesno("Confirm Deletion",
                                           f"Permanently delete student record '{student['full_name']}'?"):
            self.db.delete_student(self.selected_student_id)
            log(self.db, self.user, "DELETE", "Student",
                f"Deleted student '{student.get('full_name')}' ({student.get('student_id')}).")
            self.selected_student_id = None
            self.load_students()

    def clear_form(self):
        for k, w in self.entries.items():
            if isinstance(w, ctk.CTkComboBox):
                w.set("")
            else:
                w.delete(0, "end")
        self.program_entry.delete(0, "end")
        self.year_combo.set("")
        self.semester_entry.delete(0, "end")
        self.guardian_name_entry.delete(0, "end")
        self.guardian_phone_entry.delete(0, "end")
        self.emergency_entry.delete(0, "end")
        self.photo_path = None
        self.photo_label.configure(text="No file selected")
        self.selected_student_id = None

    def load_students(self):
        self.tree.delete(*self.tree.get_children())

        search = self.search_entry.get().strip() or None
        students = self.db.get_students(search=search)

        for s in students:
            self.tree.insert("", "end", iid=str(s["id"]), values=(
                s["student_id"],
                s["full_name"],
                s.get("gender", "") or "—",
                s.get("department_name", "") or "—",
                str(s.get("year") or "—"),
                s.get("class_name", "") or "—",
                s.get("phone", "") or "—",
                s.get("email", "") or "—"
            ))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_student_id = int(sel[0])

    def select_student(self, sid):
        self.selected_student_id = sid

    def import_excel(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if not path:
            return
        try:
            df = pd.read_excel(path)
            required = {"student_id", "full_name"}
            if not required.issubset(df.columns):
                messagebox.showerror("Error", "Excel file missing required columns: 'student_id' and 'full_name'")
                return
            count = 0
            for _, row in df.iterrows():
                sid = str(row.get("student_id", ""))
                full = str(row.get("full_name", ""))
                if not sid or not full:
                    continue
                dept_name = str(row.get("department", "")) if pd.notna(row.get("department")) else ""
                dept_id = None
                for d in self.db.get_departments():
                    if d["name"] == dept_name:
                        dept_id = d["id"]
                        break
                year_val = row.get("year")
                year = int(year_val) if pd.notna(year_val) else None
                sem_val = row.get("semester")
                sem = int(sem_val) if pd.notna(sem_val) else None
                result = self.db.add_student(
                    student_id=sid,
                    full_name=full,
                    first_name=str(row.get("first_name", "")) if pd.notna(row.get("first_name")) else None,
                    last_name=str(row.get("last_name", "")) if pd.notna(row.get("last_name")) else None,
                    gender=str(row.get("gender", "")) if pd.notna(row.get("gender")) else None,
                    dob=str(row.get("dob", "")) if pd.notna(row.get("dob")) else None,
                    nationality=str(row.get("nationality", "")) if pd.notna(row.get("nationality")) else None,
                    email=str(row.get("email", "")) if pd.notna(row.get("email")) else None,
                    phone=str(row.get("phone", "")) if pd.notna(row.get("phone")) else None,
                    address=str(row.get("address", "")) if pd.notna(row.get("address")) else None,
                    department_id=dept_id,
                    program=str(row.get("program", "")) if pd.notna(row.get("program")) else None,
                    year=year,
                    semester=sem,
                    class_name=str(row.get("class_name", "")) if pd.notna(row.get("class_name")) else None,
                    guardian_name=str(row.get("guardian_name", "")) if pd.notna(row.get("guardian_name")) else None,
                    guardian_phone=str(row.get("guardian_phone", "")) if pd.notna(row.get("guardian_phone")) else None,
                    emergency_contact=str(row.get("emergency_contact", "")) if pd.notna(
                        row.get("emergency_contact")) else None,
                )
                if result:
                    uname = sid
                    pwd = str(row.get("dob", sid)) if pd.notna(row.get("dob")) else sid
                    email_val = str(row.get("email", "")) if pd.notna(row.get("email")) else None
                    user_id = self.db.create_user(uname, pwd, "student", email_val)
                    if user_id:
                        self.db.link_student_user(result, user_id)
                    count += 1
            messagebox.showinfo("Success", f"Successfully imported {count} student records.")
            log(self.db, self.user, "IMPORT", "Student", f"Imported {count} students from Excel.")
            self.load_students()
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import Excel data: {e}")

    def export_excel(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not path:
            return
        try:
            students = self.db.get_students()
            data = []
            for s in students:
                data.append({
                    "student_id": s["student_id"],
                    "full_name": s["full_name"],
                    "first_name": s.get("first_name", ""),
                    "last_name": s.get("last_name", ""),
                    "gender": s.get("gender", ""),
                    "dob": s.get("dob", ""),
                    "nationality": s.get("nationality", ""),
                    "email": s.get("email", ""),
                    "phone": s.get("phone", ""),
                    "address": s.get("address", ""),
                    "department": s.get("department_name", ""),
                    "program": s.get("program", ""),
                    "year": s.get("year", ""),
                    "semester": s.get("semester", ""),
                    "class_name": s.get("class_name", ""),
                    "guardian_name": s.get("guardian_name", ""),
                    "guardian_phone": s.get("guardian_phone", ""),
                    "emergency_contact": s.get("emergency_contact", ""),
                })
            df = pd.DataFrame(data)
            df.to_excel(path, index=False)
            messagebox.showinfo("Success", f"Exported {len(data)} student records to Excel.")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export Excel data: {e}")

    def print_students(self):
        students = self.db.get_students()
        if not students:
            messagebox.showinfo("Info", "No student records available to print.")
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Print Report - Student Roster")
        dialog.geometry("820x600")
        dialog.configure(fg_color=self.colors["bg_dark"])

        text = ctk.CTkTextbox(
            dialog,
            wrap="none",
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color=self.colors["card_bg"],
            text_color=self.colors["text_main"],
            border_width=1,
            border_color=self.colors["card_border"]
        )
        text.pack(fill="both", expand=True, padx=15, pady=15)

        lines = []
        lines.append("=" * 85)
        lines.append("                         STUDENT ROSTER REPORT")
        lines.append("=" * 85)
        lines.append(f"{'ID':<10} {'Name':<22} {'Gender':<8} {'Dept':<18} {'Phone':<14} {'Email':<20}")
        lines.append("-" * 85)
        for s in students:
            lines.append(
                f"{s['student_id']:<10} "
                f"{s['full_name']:<22} "
                f"{str(s.get('gender', '')):<8} "
                f"{str(s.get('department_name', '')):<18} "
                f"{str(s.get('phone', '')):<14} "
                f"{str(s.get('email', '')):<20}"
            )
        lines.append("=" * 85)
        lines.append(f"Total Student Count: {len(students)}")

        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")