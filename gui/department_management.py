import customtkinter as ctk
from tkinter import messagebox, ttk


class DepartmentManagementView(ctk.CTkFrame):
    def __init__(self, db, parent):
        super().__init__(parent, fg_color="#0F172A")  # Slate 900 background
        self.db = db
        self.selected_dept_id = None
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
        self.after(50, self.load_departments)

    def build_ui(self):
        # -------------------------------------------------------------
        # Header Section
        # -------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Department Management",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Manage academic departments, faculties, and heads of department",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_muted"]
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # -------------------------------------------------------------
        # Main Two-Column Workspace Container
        # -------------------------------------------------------------
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=2)
        workspace.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # Left Column: Department Form Card
        # -------------------------------------------------------------
        form_card = ctk.CTkFrame(
            workspace,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=10)

        form_title = ctk.CTkLabel(
            form_card,
            text="Department Details",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_main"]
        )
        form_title.pack(anchor="w", padx=20, pady=(20, 15))

        inputs_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        inputs_frame.pack(fill="x", padx=20)

        def create_field_label(text):
            lbl = ctk.CTkLabel(
                inputs_frame,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["text_muted"]
            )
            lbl.pack(anchor="w", pady=(8, 2))
            return lbl

        create_field_label("Department Name *")
        self.name_entry = ctk.CTkEntry(inputs_frame, placeholder_text="e.g. Computer Science", height=38,
                                       corner_radius=8)
        self.name_entry.pack(fill="x")

        create_field_label("Code")
        self.code_entry = ctk.CTkEntry(inputs_frame, placeholder_text="e.g. CS", height=38, corner_radius=8)
        self.code_entry.pack(fill="x")

        create_field_label("Faculty")
        self.faculty_entry = ctk.CTkEntry(inputs_frame, placeholder_text="e.g. Science & Technology", height=38,
                                          corner_radius=8)
        self.faculty_entry.pack(fill="x")

        create_field_label("Head of Department")
        self.hod_entry = ctk.CTkEntry(inputs_frame, placeholder_text="e.g. Dr. John Doe", height=38, corner_radius=8)
        self.hod_entry.pack(fill="x")

        create_field_label("Description")
        self.desc_text = ctk.CTkTextbox(
            inputs_frame,
            height=90,
            corner_radius=8,
            fg_color="#0F172A",
            border_width=1,
            border_color=self.colors["card_border"]
        )
        self.desc_text.pack(fill="x")

        # Action Buttons Container inside Form Card
        btn_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(20, 20))

        ctk.CTkButton(
            btn_frame,
            text="+ Add",
            height=38,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.add_department
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        ctk.CTkButton(
            btn_frame,
            text="Update",
            height=38,
            corner_radius=8,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.update_department
        ).pack(side="left", fill="x", expand=True, padx=2)

        ctk.CTkButton(
            btn_frame,
            text="Delete",
            height=38,
            corner_radius=8,
            fg_color=self.colors["danger"],
            hover_color=self.colors["danger_hover"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.delete_department
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

        # -------------------------------------------------------------
        # Right Column: Filters & Table Container Card
        # -------------------------------------------------------------
        table_card = ctk.CTkFrame(
            workspace,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        table_card.grid(row=0, column=1, sticky="nsew", pady=10)

        # Search Bar
        search_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(15, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search department name or code...",
            width=320,
            height=38,
            corner_radius=8
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self.load_departments())

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=90,
            height=38,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self.load_departments
        ).pack(side="left", padx=8)

        # Table Wrapper
        self.table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Custom Styled Treeview
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Department.Treeview",
            background="#1E293B",
            foreground="#F8FAFC",
            fieldbackground="#1E293B",
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Department.Treeview.Heading",
            background="#0F172A",
            foreground="#94A3B8",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "Department.Treeview",
            background=[("selected", "#334155")],
            foreground=[("selected", "#FFFFFF")]
        )
        style.map(
            "Department.Treeview.Heading",
            background=[("active", "#1E293B")]
        )

        columns = ("id", "name", "code", "faculty", "head", "description")
        self.tree = ttk.Treeview(
            self.table_frame,
            columns=columns,
            show="headings",
            style="Department.Treeview",
            selectmode="browse"
        )

        headings = {
            "id": ("ID", 50),
            "name": ("Department Name", 160),
            "code": ("Code", 70),
            "faculty": ("Faculty", 140),
            "head": ("Head of Dept", 140),
            "description": ("Description", 180)
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
    # Business Logic & Event Handlers
    # -------------------------------------------------------------
    def load_departments(self):
        self.tree.delete(*self.tree.get_children())

        search = self.search_entry.get().strip().lower()
        departments = self.db.get_departments()
        if search:
            departments = [d for d in departments if search in d["name"].lower() or search in d.get("code", "").lower()]

        for dept in departments:
            self.tree.insert("", "end", iid=str(dept["id"]), values=(
                dept["id"],
                dept["name"],
                dept.get("code", "") or "—",
                dept.get("faculty", "") or "—",
                dept.get("head_of_department", "") or "—",
                dept.get("description", "") or "—"
            ))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        dept_id = int(sel[0])
        dept = next((d for d in self.db.get_departments() if d["id"] == dept_id), None)
        if dept:
            self.select_department(dept)

    def select_department(self, dept):
        self.selected_dept_id = dept["id"]
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, dept["name"])
        self.code_entry.delete(0, "end")
        self.code_entry.insert(0, dept.get("code", "") or "")
        self.faculty_entry.delete(0, "end")
        self.faculty_entry.insert(0, dept.get("faculty", "") or "")
        self.hod_entry.delete(0, "end")
        self.hod_entry.insert(0, dept.get("head_of_department", "") or "")
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", dept.get("description", "") or "")

    def add_department(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Department name is required.")
            return
        code = self.code_entry.get().strip() or None
        faculty = self.faculty_entry.get().strip() or None
        hod = self.hod_entry.get().strip() or None
        desc = self.desc_text.get("1.0", "end").strip() or None

        result = self.db.add_department(name, code, faculty, hod, desc)
        if result:
            messagebox.showinfo("Success", f"Department '{name}' added successfully.")
            self.clear_form()
            self.load_departments()
        else:
            messagebox.showerror("Error", "Department name or code already exists.")

    def update_department(self):
        if not self.selected_dept_id:
            messagebox.showinfo("Selection Required", "Please select a department from the table first.")
            return
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Department name is required.")
            return
        code = self.code_entry.get().strip() or None
        faculty = self.faculty_entry.get().strip() or None
        hod = self.hod_entry.get().strip() or None
        desc = self.desc_text.get("1.0", "end").strip() or None

        self.db.update_department(self.selected_dept_id, name, code, faculty, hod, desc)
        messagebox.showinfo("Success", "Department updated successfully.")
        self.clear_form()
        self.load_departments()

    def delete_department(self):
        if not self.selected_dept_id:
            messagebox.showinfo("Selection Required", "Please select a department from the table first.")
            return
        dept = next((d for d in self.db.get_departments() if d["id"] == self.selected_dept_id), None)
        if dept and messagebox.askyesno("Confirm Action",
                                        f"Are you sure you want to delete department '{dept['name']}'?"):
            self.db.delete_department(self.selected_dept_id)
            self.selected_dept_id = None
            self.clear_form()
            self.load_departments()

    def clear_form(self):
        self.name_entry.delete(0, "end")
        self.code_entry.delete(0, "end")
        self.faculty_entry.delete(0, "end")
        self.hod_entry.delete(0, "end")
        self.desc_text.delete("1.0", "end")
        self.selected_dept_id = None