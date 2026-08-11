import customtkinter as ctk
from gui import theme
from gui.skeleton import schedule_table_load
from gui.activity import log
from tkinter import messagebox, ttk


class TeacherManagementView(ctk.CTkFrame):
    def __init__(self, db, parent, user=None):
        super().__init__(parent, fg_color=theme.c("bg_dark"))  # Slate 900 background
        self.db = db
        self.user = user
        self.selected_teacher_id = None
        self.pack(fill="both", expand=True)

        # Unified Color Palette Tokens
        self.colors = theme.colors

        self.build_ui()
        schedule_table_load(self, self.table_frame, self.load_teachers)

    def build_ui(self):
        # -------------------------------------------------------------
        # Header Section
        # -------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Teacher Management",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Manage faculty profiles, department assignments, and contact details",
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

        fields = [
            ("Teacher ID:", 0, 0), ("Full Name:", 0, 2),
            ("Gender:", 1, 0), ("Date of Birth:", 1, 2),
            ("Email:", 2, 0), ("Phone:", 2, 2),
            ("Address:", 3, 0), ("Position:", 3, 2),
        ]

        self.entries = {}
        for label, row, col in fields:
            lbl = ctk.CTkLabel(
                form_grid,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["text_muted"]
            )
            lbl.grid(row=row, column=col, padx=(10, 5), pady=6, sticky="e")

            if label == "Gender:":
                entry = ctk.CTkComboBox(form_grid, values=["Male", "Female", "Other"], height=36, corner_radius=8)
            else:
                entry = ctk.CTkEntry(form_grid, height=36, corner_radius=8)

            entry.grid(row=row, column=col + 1, padx=(5, 15), pady=6, sticky="ew")
            self.entries[label] = entry

        # Department Combo Row
        lbl_dept = ctk.CTkLabel(
            form_grid,
            text="Department:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_muted"]
        )
        lbl_dept.grid(row=4, column=0, padx=(10, 5), pady=6, sticky="e")

        self.dept_combo = ctk.CTkComboBox(form_grid, values=[""], height=36, corner_radius=8)
        self.dept_combo.grid(row=4, column=1, padx=(5, 15), pady=6, sticky="ew")
        self.load_departments()

        # Toolbar Actions Inside Form Card
        btn_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(5, 15))

        actions = [
            ("+ Add Teacher", self.add_teacher, self.colors["primary"], self.colors["primary_hover"]),
            ("Edit Selected", self.edit_teacher, self.colors["neutral_btn"], self.colors["neutral_hover"]),
            ("Delete Selected", self.delete_teacher, self.colors["danger"], self.colors["danger_hover"]),
            ("Print Roster", self.print_teachers, self.colors["neutral_btn"], self.colors["neutral_hover"]),
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

        # Search Control
        search_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(15, 10))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search teacher name, ID, position, or email...",
            width=320,
            height=38,
            corner_radius=8
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<Return>", lambda e: self.load_teachers())

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=90,
            height=38,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self.load_teachers
        ).pack(side="left", padx=8)

        # Table Wrapper
        self.table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Treeview Custom Styling
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Teacher.Treeview",
            background=theme.c("table_bg"),
            foreground=theme.c("table_fg"),
            fieldbackground=theme.c("table_bg"),
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Teacher.Treeview.Heading",
            background=theme.c("table_head_bg"),
            foreground=theme.c("table_head_fg"),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "Teacher.Treeview",
            background=[("selected", theme.c("table_selected"))],
            foreground=[("selected", theme.c("table_selected_fg"))]
        )
        style.map(
            "Teacher.Treeview.Heading",
            background=[("active", theme.c("table_head_active"))]
        )

        columns = ("id", "name", "gender", "department", "position", "phone", "email")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", style="Teacher.Treeview",
                                 selectmode="browse")

        headings = {
            "id": ("ID", 70),
            "name": ("Full Name", 180),
            "gender": ("Gender", 80),
            "department": ("Department", 160),
            "position": ("Position", 130),
            "phone": ("Phone", 120),
            "email": ("Email Address", 200)
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
    def load_departments(self):
        depts = self.db.get_departments()
        self.dept_combo.configure(values=[d["name"] for d in depts])

    def get_form_data(self):
        data = {}
        for k, w in self.entries.items():
            if isinstance(w, ctk.CTkComboBox):
                data[k] = w.get()
            else:
                data[k] = w.get().strip()
        return data

    def add_teacher(self):
        data = self.get_form_data()
        tid = data.get("Teacher ID:", "")
        name = data.get("Full Name:", "")
        if not tid or not name:
            messagebox.showerror("Validation Error", "Teacher ID and Full Name are required.")
            return

        dept_name = self.dept_combo.get()
        dept_id = None
        for d in self.db.get_departments():
            if d["name"] == dept_name:
                dept_id = d["id"]
                break

        result = self.db.add_teacher(
            teacher_id=tid,
            full_name=name,
            gender=data.get("Gender:", "") or None,
            dob=data.get("Date of Birth:", "") or None,
            email=data.get("Email:", "") or None,
            phone=data.get("Phone:", "") or None,
            address=data.get("Address:", "") or None,
            department_id=dept_id,
            position=data.get("Position:", "") or None,
        )
        if result:
            password = tid
            user_id = self.db.create_user(tid, password, "teacher", data.get("Email:", "") or None)
            if user_id:
                self.db.link_teacher_user(result, user_id)
            messagebox.showinfo("Success", f"Teacher profile '{name}' created successfully.")
            log(self.db, self.user, "CREATE", "Teacher", f"Added teacher {tid} '{name}'.")
            self.clear_form()
            self.load_teachers()
        else:
            messagebox.showerror("Error", "Teacher ID already exists in system.")

    def edit_teacher(self):
        if not self.selected_teacher_id:
            messagebox.showinfo("Selection Required", "Please select a teacher from the table first.")
            return
        t = self.db.get_teacher(self.selected_teacher_id)
        if not t:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Teacher Profile")
        dialog.geometry("460x480")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        dialog.after(100, dialog.grab_set)

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text=f"Edit Profile: {t.get('full_name', '')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(15, 10))

        form_f = ctk.CTkFrame(card, fg_color="transparent")
        form_f.pack(fill="both", expand=True, padx=15, pady=5)

        fields = [
            ("full_name", "Full Name"), ("gender", "Gender"),
            ("dob", "DOB"), ("email", "Email"),
            ("phone", "Phone"), ("address", "Address"),
            ("position", "Position"),
        ]
        entries = {}
        for i, (key, label) in enumerate(fields):
            ctk.CTkLabel(form_f, text=label + ":", text_color=self.colors["text_muted"]).grid(row=i, column=0, padx=10,
                                                                                              pady=3, sticky="e")
            if key == "gender":
                e = ctk.CTkComboBox(form_f, width=220, values=["Male", "Female", "Other"], height=32)
                e.set(str(t.get(key, "") or ""))
            else:
                e = ctk.CTkEntry(form_f, width=220, height=32)
                e.insert(0, str(t.get(key, "") or ""))
            e.grid(row=i, column=1, padx=10, pady=3, sticky="w")
            entries[key] = e

        ctk.CTkLabel(form_f, text="Department:", text_color=self.colors["text_muted"]).grid(row=len(fields), column=0,
                                                                                            padx=10, pady=3, sticky="e")
        dept_e = ctk.CTkComboBox(form_f, width=220, values=[d["name"] for d in self.db.get_departments()], height=32)
        dept_e.set(t.get("department_name", "") or "")
        dept_e.grid(row=len(fields), column=1, padx=10, pady=3, sticky="w")

        def save():
            kwargs = {}
            for key, w in entries.items():
                val = w.get().strip()
                kwargs[key] = val or None
            dept_val = dept_e.get()
            for d in self.db.get_departments():
                if d["name"] == dept_val:
                    kwargs["department_id"] = d["id"]
                    break
            self.db.update_teacher(self.selected_teacher_id, **kwargs)
            log(self.db, self.user, "UPDATE", "Teacher",
                f"Updated teacher profile '{t.get('full_name')}'.")
            messagebox.showinfo("Success", "Teacher details updated successfully.")
            dialog.destroy()
            self.load_teachers()

        ctk.CTkButton(
            card,
            text="Save Changes",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=38,
            command=save
        ).pack(fill="x", padx=20, pady=(10, 15))

    def delete_teacher(self):
        if not self.selected_teacher_id:
            messagebox.showinfo("Selection Required", "Please select a teacher from the table first.")
            return
        t = self.db.get_teacher(self.selected_teacher_id)
        if t and messagebox.askyesno("Confirm Deletion", f"Permanently delete faculty record for '{t['full_name']}'?"):
            self.db.delete_teacher(self.selected_teacher_id)
            log(self.db, self.user, "DELETE", "Teacher",
                f"Deleted teacher '{t['full_name']}' ({t.get('teacher_id')}).")
            self.selected_teacher_id = None
            self.load_teachers()

    def clear_form(self):
        for k, w in self.entries.items():
            if isinstance(w, ctk.CTkComboBox):
                w.set("")
            else:
                w.delete(0, "end")
        self.dept_combo.set("")
        self.selected_teacher_id = None

    def load_teachers(self):
        self.tree.delete(*self.tree.get_children())

        search = self.search_entry.get().strip() or None
        teachers = self.db.get_teachers(search=search)

        for t in teachers:
            self.tree.insert("", "end", iid=str(t["id"]), values=(
                t["teacher_id"],
                t["full_name"],
                t.get("gender", "") or "—",
                t.get("department_name", "") or "—",
                t.get("position", "") or "—",
                t.get("phone", "") or "—",
                t.get("email", "") or "—"
            ))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if sel:
            self.selected_teacher_id = int(sel[0])

    def select_teacher(self, tid):
        self.selected_teacher_id = tid

    def print_teachers(self):
        teachers = self.db.get_teachers()
        if not teachers:
            messagebox.showinfo("Info", "No faculty records available to print.")
            return
        dialog = ctk.CTkToplevel(self)
        dialog.title("Print Report - Faculty Roster")
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
        lines.append("                         FACULTY ROSTER REPORT")
        lines.append("=" * 85)
        lines.append(f"{'ID':<10} {'Name':<22} {'Gender':<8} {'Department':<18} {'Phone':<14} {'Email':<20}")
        lines.append("-" * 85)
        for t in teachers:
            lines.append(
                f"{t['teacher_id']:<10} "
                f"{t['full_name']:<22} "
                f"{str(t.get('gender', '')):<8} "
                f"{str(t.get('department_name', '')):<18} "
                f"{str(t.get('phone', '')):<14} "
                f"{str(t.get('email', '')):<20}"
            )
        lines.append("=" * 85)
        lines.append(f"Total Faculty Count: {len(teachers)}")

        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")