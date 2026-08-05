import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DatabaseManager


class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()

        # Window Setup
        self.title("University Attendance System")
        self.geometry("950x600")
        self.resizable(False, False)

        # Apply Global Theme Defaults
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        # Configure Main Grid Structure (Left Sidebar | Right Form)
        self.grid_columnconfigure(0, weight=4)  # Visual Sidebar
        self.grid_columnconfigure(1, weight=5)  # Form Container
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_form()

        self.dashboard = None

    def _toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="*")

    def _build_sidebar(self):
        """Creates the branded visual left panel."""
        sidebar = ctk.CTkFrame(self, corner_radius=0, fg_color="#1E1E2E")
        sidebar.grid(row=0, column=0, sticky="nsew")

        # Inner container for vertical centering
        content_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Decorative Logo Badge
        logo_badge = ctk.CTkLabel(
            content_frame,
            text="🎓",
            font=ctk.CTkFont(size=56),
        )
        logo_badge.pack(pady=(0, 15))

        brand_title = ctk.CTkLabel(
            content_frame,
            text="University Attendance\nManagement",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#FFFFFF",
            justify="center",
        )
        brand_title.pack(pady=(0, 10))

        brand_sub = ctk.CTkLabel(
            content_frame,
            text="Secure Portal Access",
            font=ctk.CTkFont(size=13),
            text_color="#A0A0B8",
        )
        brand_sub.pack()

    def _build_form(self):
        """Creates the interactive login form on the right panel."""
        form_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#14141F")
        form_frame.grid(row=0, column=1, sticky="nsew")

        # Form content wrapper
        container = ctk.CTkFrame(form_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Header
        header = ctk.CTkLabel(
            container,
            text="Welcome back",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color="#FFFFFF",
        )
        header.pack(anchor="w", pady=(0, 4))

        sub_header = ctk.CTkLabel(
            container,
            text="Please enter your details to sign in",
            font=ctk.CTkFont(size=13),
            text_color="#8E8EA8",
        )
        sub_header.pack(anchor="w", pady=(0, 30))

        # Username Field
        username_label = ctk.CTkLabel(
            container,
            text="Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#D1D1E0",
        )
        username_label.pack(anchor="w", pady=(0, 5))

        self.username_entry = ctk.CTkEntry(
            container,
            placeholder_text="Enter your username",
            width=320,
            height=42,
            border_width=1,
            corner_radius=8,
            fg_color="#1E1E2E",
            border_color="#2A2A3C",
            text_color="#FFFFFF",
            placeholder_text_color="#6C6C8A",
        )
        self.username_entry.pack(pady=(0, 18))

        # Password Field
        password_label = ctk.CTkLabel(
            container,
            text="Password",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#D1D1E0",
        )
        password_label.pack(anchor="w", pady=(0, 5))

        self.password_entry = ctk.CTkEntry(
            container,
            placeholder_text="••••••••",
            width=320,
            height=42,
            show="*",
            border_width=1,
            corner_radius=8,
            fg_color="#1E1E2E",
            border_color="#2A2A3C",
            text_color="#FFFFFF",
            placeholder_text_color="#6C6C8A",
        )
        self.password_entry.pack(pady=(0, 6))

        # Show Password Toggle
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_check = ctk.CTkCheckBox(
            container,
            text="Show password",
            variable=self.show_password_var,
            command=self._toggle_password_visibility,
            font=ctk.CTkFont(size=12),
            text_color="#8E8EA8",
            fg_color="#3B82F6",
            border_color="#2A2A3C",
            hover_color="#2563EB",
            checkbox_width=18,
            checkbox_height=18,
        )
        self.show_password_check.pack(anchor="w", pady=(0, 10))

        # Error Message Area (Fixed height prevents UI shifting)
        self.error_label = ctk.CTkLabel(
            container,
            text="",
            text_color="#FF5555",
            font=ctk.CTkFont(size=12),
            height=20,
        )
        self.error_label.pack(pady=(0, 10), anchor="w")

        # Action Button
        self.login_btn = ctk.CTkButton(
            container,
            text="Sign In",
            width=320,
            height=44,
            corner_radius=8,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.login,
        )
        self.login_btn.pack()

        # Forgot Password Link
        self.forgot_link = ctk.CTkLabel(
            container,
            text="Forgot password?",
            font=ctk.CTkFont(size=12, underline=True),
            text_color="#6C6C8A",
            cursor="hand2",
        )
        self.forgot_link.pack(pady=(8, 0))
        self.forgot_link.bind("<Button-1>", lambda e: self.forgot_password())

        # Keyboard Bindings
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())

    def forgot_password(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Reset Password")
        dialog.geometry("350x220")
        dialog.transient(self)

        ctk.CTkLabel(dialog, text="Reset Password",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkLabel(dialog, text="Enter your username to reset password:",
                     font=ctk.CTkFont(size=12)).pack(pady=5)

        username_e = ctk.CTkEntry(dialog, width=250, placeholder_text="Username")
        username_e.pack(pady=5)

        ctk.CTkLabel(dialog, text="New Password:", font=ctk.CTkFont(size=12)).pack()
        new_pw_e = ctk.CTkEntry(dialog, width=250, show="*")
        new_pw_e.pack(pady=5)

        def do_reset():
            uname = username_e.get().strip()
            new_pw = new_pw_e.get().strip()
            if not uname or not new_pw:
                messagebox.showerror("Error", "Fill all fields")
                return
            if len(new_pw) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return
            user = self.db.get_user_by_username(uname)
            if not user:
                messagebox.showerror("Error", "Username not found")
                return
            self.db.update_user_password(user["id"], new_pw)
            messagebox.showinfo("Success", f"Password reset for '{uname}'. You can now log in.")
            dialog.destroy()

        ctk.CTkButton(dialog, text="Reset Password", command=do_reset).pack(pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.configure(text="⚠️  Please fill in all fields")
            return

        user = self.db.authenticate(username, password)
        if user:
            self.withdraw()
            from gui.dashboard import DashboardWindow

            self.dashboard = DashboardWindow(self, user)
        else:
            self.error_label.configure(text="❌  Invalid username or password")