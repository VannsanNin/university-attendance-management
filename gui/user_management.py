import customtkinter as ctk
from gui import theme
from gui.skeleton import schedule_table_load
from gui.activity import log
from tkinter import messagebox, ttk


class UserManagementView(ctk.CTkFrame):
    def __init__(self, db, parent, user=None):
        super().__init__(parent, fg_color=theme.c("bg_dark"))  # Slate 900 background
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)
        self.selected_user_id = None
        self._search_after_id = None

        # Color Palette
        self.colors = theme.colors

        self.build_ui()
        schedule_table_load(self, self.table_wrapper, self.load_users)

    def build_ui(self):
        # Header Section
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="User Management",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Manage accounts, roles, and connected user profiles",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_muted"]
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Main Workspace Container
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=3)
        workspace.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # Left Panel: Add/Edit User Form Card
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
            text="Create Account",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors["text_main"]
        )
        form_title.pack(anchor="w", padx=20, pady=(20, 15))

        # Input fields wrapper
        inputs_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        inputs_frame.pack(fill="x", padx=20)

        def create_field_label(text):
            lbl = ctk.CTkLabel(inputs_frame, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                               text_color=self.colors["text_muted"])
            lbl.pack(anchor="w", pady=(8, 2))
            return lbl

        create_field_label("Username *")
        self.username_entry = ctk.CTkEntry(inputs_frame, placeholder_text="e.g. jdoe", height=38, corner_radius=8)
        self.username_entry.pack(fill="x")

        create_field_label("Password *")
        self.password_entry = ctk.CTkEntry(inputs_frame, placeholder_text="••••••••", show="*", height=38,
                                           corner_radius=8)
        self.password_entry.pack(fill="x")

        create_field_label("Role")
        self.role_combo = ctk.CTkComboBox(inputs_frame, values=["admin", "teacher", "student"], height=38,
                                          corner_radius=8)
        self.role_combo.set("admin")
        self.role_combo.pack(fill="x")

        create_field_label("Linked Entity")
        self.link_combo = ctk.CTkComboBox(inputs_frame, values=[""], height=38, corner_radius=8)
        self.link_combo.pack(fill="x")
        self.link_map = {}

        def on_role_change(choice):
            self.link_combo.configure(values=[""])
            self.link_map = {}
            if choice == "student":
                students = self.db.get_students()
                self.link_map = {f"{s['student_id']} - {s['full_name']}": s["id"] for s in students}
                self.link_combo.configure(values=[""] + list(self.link_map.keys()))
            elif choice == "teacher":
                teachers = self.db.get_teachers()
                self.link_map = {f"{t['teacher_id']} - {t['full_name']}": t["id"] for t in teachers}
                self.link_combo.configure(values=[""] + list(self.link_map.keys()))
            else:
                self.link_combo.configure(values=[""])
            self.link_combo.set("")

        self.role_combo.configure(command=on_role_change)

        create_field_label("Email")
        self.email_entry = ctk.CTkEntry(inputs_frame, placeholder_text="name@example.com", height=38, corner_radius=8)
        self.email_entry.pack(fill="x")

        create_field_label("Phone")
        self.phone_entry = ctk.CTkEntry(inputs_frame, placeholder_text="+1 555-0199", height=38, corner_radius=8)
        self.phone_entry.pack(fill="x")

        add_btn = ctk.CTkButton(
            form_card,
            text="+ Add New User",
            height=40,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.add_user
        )
        add_btn.pack(fill="x", padx=20, pady=(25, 20))

        # -------------------------------------------------------------
        # Right Panel: Filters & Table Container Card
        # -------------------------------------------------------------
        table_card = ctk.CTkFrame(
            workspace,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        table_card.grid(row=0, column=1, sticky="nsew", pady=10)

        # Filters Bar
        filter_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(15, 10))

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="🔍 Search by username or email...",
            height=38,
            width=280,
            corner_radius=8
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self._debounced_load())

        self.role_filter = ctk.CTkComboBox(
            filter_frame,
            values=["All Roles", "admin", "teacher", "student"],
            height=38,
            width=130,
            corner_radius=8
        )
        self.role_filter.set("All Roles")
        self.role_filter.pack(side="left", padx=10)
        self.role_filter.configure(command=lambda c: self.load_users())

        # Table Actions (Right Aligned)
        action_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        action_frame.pack(side="right")

        ctk.CTkButton(
            action_frame,
            text="Edit",
            width=70,
            height=34,
            fg_color=theme.c("neutral_btn"),
            hover_color=theme.c("neutral_hover"),
            command=self._edit_selected_row
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            action_frame,
            text="Reset PW",
            width=80,
            height=34,
            fg_color=theme.c("neutral_btn"),
            hover_color=theme.c("neutral_hover"),
            command=self._reset_selected_row
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            action_frame,
            text="Delete",
            width=70,
            height=34,
            fg_color=self.colors["danger"],
            hover_color=self.colors["danger_hover"],
            command=self._delete_selected_row
        ).pack(side="left", padx=2)

        # Custom Styled Treeview Table
        table_wrapper = ctk.CTkFrame(table_card, fg_color="transparent")
        table_wrapper.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.table_wrapper = table_wrapper

        style = ttk.Style()
        style.theme_use("default")

        # Configure Table Colors & Geometry
        style.configure(
            "Treeview",
            background=theme.c("table_bg"),
            foreground=theme.c("table_fg"),
            fieldbackground=theme.c("table_bg"),
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading",
            background=theme.c("table_head_bg"),
            foreground=theme.c("table_head_fg"),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "Treeview",
            background=[("selected", theme.c("table_selected"))],
            foreground=[("selected", theme.c("table_selected_fg"))]
        )
        style.map(
            "Treeview.Heading",
            background=[("active", theme.c("table_head_active"))]
        )

        columns = ("id", "username", "role", "email", "phone", "active", "last_login")
        self.tree = ttk.Treeview(table_wrapper, columns=columns, show="headings", selectmode="browse")

        # Define Columns
        headings = {
            "id": ("ID", 50),
            "username": ("Username", 120),
            "role": ("Role", 90),
            "email": ("Email", 160),
            "phone": ("Phone", 110),
            "active": ("Active", 60),
            "last_login": ("Last Login", 100)
        }

        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, minwidth=width, stretch=True, anchor="w")

        # Scrollbar integration
        scrollbar = ctk.CTkScrollbar(table_wrapper, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # -------------------------------------------------------------
    # Business Logic & Event Handlers
    # -------------------------------------------------------------
    def _debounced_load(self):
        if self._search_after_id:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(300, self.load_users)

    def add_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_combo.get()
        email = self.email_entry.get().strip() or None
        phone = self.phone_entry.get().strip() or None

        if not username or not password:
            messagebox.showerror("Validation Error", "Username and password are required fields.")
            return

        user_id = self.db.create_user(username, password, role, email)
        if not user_id:
            messagebox.showerror("Error", "Username already exists. Please choose another.")
            return

        if phone:
            self.db.update_user(user_id, phone=phone)

        link_key = self.link_combo.get()
        if link_key and link_key in self.link_map:
            linked_id = self.link_map[link_key]
            if role == "student":
                self.db.link_student_user(linked_id, user_id)
            elif role == "teacher":
                self.db.link_teacher_user(linked_id, user_id)

        messagebox.showinfo("Success", f"User account '{username}' created successfully!")
        log(self.db, self.user, "CREATE", "User", f"Created {role} account '{username}'.")
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.email_entry.delete(0, "end")
        self.phone_entry.delete(0, "end")
        self.load_users()

    def load_users(self):
        self.tree.delete(*self.tree.get_children())

        search = self.search_entry.get().strip().lower()
        role_filter = self.role_filter.get()

        users = self.db.get_users()
        if role_filter not in ["All", "All Roles"]:
            users = [u for u in users if u["role"] == role_filter]
        if search:
            users = [u for u in users if search in u["username"].lower() or search in str(u.get("email", "")).lower()]

        for u in users:
            active = "Yes" if u.get("is_active", 1) else "No"
            last = (u.get("last_login") or "")[:10] if u.get("last_login") else "Never"
            self.tree.insert("", "end", iid=str(u["id"]), values=(
                u["id"], u["username"], u["role"].capitalize(),
                u.get("email", "") or "—", u.get("phone", "") or "—",
                active, last
            ))

    def _get_selected_uid(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user from the table first.")
            return None
        return int(sel[0])

    def _edit_selected_row(self):
        uid = self._get_selected_uid()
        if uid:
            self.edit_user(uid)

    def _reset_selected_row(self):
        uid = self._get_selected_uid()
        if uid:
            self.reset_password(uid)

    def _delete_selected_row(self):
        uid = self._get_selected_uid()
        if uid:
            self.delete_user(uid)

    # -------------------------------------------------------------
    # Dialog Windows Refinement
    # -------------------------------------------------------------
    def edit_user(self, uid):
        user = self.db.get_user(uid)
        if not user:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit User - {user['username']}")
        dialog.geometry("400x380")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        dialog.after(100, dialog.grab_set)

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text=f"Edit Account: {user['username']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(15, 10))

        ctk.CTkLabel(card, text="Email Address", text_color=self.colors["text_muted"]).pack(anchor="w", padx=20)
        email_e = ctk.CTkEntry(card, height=36, corner_radius=8)
        email_e.insert(0, user.get("email", "") or "")
        email_e.pack(fill="x", padx=20, pady=(2, 10))

        ctk.CTkLabel(card, text="Role", text_color=self.colors["text_muted"]).pack(anchor="w", padx=20)
        role_var = ctk.StringVar(value=user["role"])
        role_m = ctk.CTkOptionMenu(card, values=["admin", "teacher", "student"], variable=role_var, height=36,
                                   corner_radius=8)
        role_m.pack(fill="x", padx=20, pady=(2, 10))

        ctk.CTkLabel(card, text="Phone Number", text_color=self.colors["text_muted"]).pack(anchor="w", padx=20)
        phone_e = ctk.CTkEntry(card, height=36, corner_radius=8)
        phone_e.insert(0, user.get("phone", "") or "")
        phone_e.pack(fill="x", padx=20, pady=(2, 10))

        active_var = ctk.StringVar(value="1" if user.get("is_active", 1) else "0")
        active_cb = ctk.CTkCheckBox(card, text="Account Active", variable=active_var, onvalue="1", offvalue="0")
        active_cb.pack(anchor="w", padx=20, pady=10)

        def save():
            self.db.update_user(uid, email=email_e.get().strip() or None, role=role_var.get(),
                                is_active=int(active_var.get()))
            self.db.update_user(uid, phone=phone_e.get().strip() or None)
            log(self.db, self.user, "UPDATE", "User", f"Updated account '{user['username']}'.")
            messagebox.showinfo("Success", "User details updated successfully.")
            dialog.destroy()
            self.load_users()

        ctk.CTkButton(
            card,
            text="Save Changes",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=38,
            command=save
        ).pack(fill="x", padx=20, pady=(15, 10))

    def reset_password(self, uid):
        user = self.db.get_user(uid)
        if not user:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Reset Password - {user['username']}")
        dialog.geometry("380x300")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        dialog.after(100, dialog.grab_set)

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text=f"Reset Password",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            card,
            text=f"Target User: {user['username']}",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_muted"]
        ).pack(pady=(0, 10))

        ctk.CTkLabel(card, text="New Password", text_color=self.colors["text_muted"]).pack(anchor="w", padx=20)
        pw_e = ctk.CTkEntry(card, show="*", height=36, corner_radius=8)
        pw_e.pack(fill="x", padx=20, pady=(2, 10))

        ctk.CTkLabel(card, text="Confirm New Password", text_color=self.colors["text_muted"]).pack(anchor="w", padx=20)
        confirm_e = ctk.CTkEntry(card, show="*", height=36, corner_radius=8)
        confirm_e.pack(fill="x", padx=20, pady=(2, 10))

        def save():
            np_ = pw_e.get().strip()
            cp_ = confirm_e.get().strip()
            if not np_:
                messagebox.showerror("Validation Error", "Password cannot be empty.")
                return
            if np_ != cp_:
                messagebox.showerror("Validation Error", "Passwords do not match.")
                return
            self.db.update_user_password(uid, np_)
            log(self.db, self.user, "RESET_PASSWORD", "User", f"Reset password for user '{user['username']}'.")
            messagebox.showinfo("Success", "Password updated successfully.")
            dialog.destroy()

        ctk.CTkButton(
            card,
            text="Confirm Password Reset",
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=38,
            command=save
        ).pack(fill="x", padx=20, pady=(15, 10))

    def delete_user(self, uid):
        user = self.db.get_user(uid)
        if not user:
            return
        if user["role"] == "admin":
            messagebox.showerror("Action Denied", "System Protection: Admin accounts cannot be deleted.")
            return
        if messagebox.askyesno("Confirm Action",
                               f"Are you sure you want to permanently delete user '{user['username']}'?"):
            self.db.delete_user(uid)
            log(self.db, self.user, "DELETE", "User", f"Deleted account '{user['username']}'.")
            self.load_users()