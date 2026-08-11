import customtkinter as ctk

from gui import theme
from gui.icons import icon

NAV_ICONS = {
    "dashboard": "dashboard",
    "users": "members",
    "students": "members",
    "teachers": "profile",
    "departments": "reservations",
    "courses": "books",
    "classes": "book_icon",
    "attendance": "fines",
    "reports": "reports",
    "academic_year": "reservations",
    "settings": "settings",
    "take_attendance": "fines",
    "attendance_view": "fines",
    "attendance_requests": "fines",
    "activity_logs": "reports",
    "attendance_report": "reports",
    "my_attendance": "fines",
    "my_subjects": "books",
    "my_classes": "book_icon",
    "my_courses": "books",
    "admin_profile": "profile",
    "teacher_profile": "profile",
    "student_profile": "profile",
}


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, user, on_navigate, on_change_password, on_logout):
        super().__init__(parent, fg_color=theme.c("sidebar_bg"), width=240, corner_radius=0)
        self.user = user
        self.on_navigate = on_navigate
        self.on_change_password_cb = on_change_password
        self.on_logout_cb = on_logout

        self.nav_buttons = {}
        self.colors = theme.colors

        self.pack(side="left", fill="y", expand=False)
        self.build_ui()

    def apply_theme(self):
        self.colors = theme.colors
        self.configure(fg_color=theme.c("sidebar_bg"))
        for child in self.winfo_children():
            child.destroy()
        self.nav_buttons = {}
        self.build_ui()

    def build_ui(self):
        # -------------------------------------------------------------
        # Header / Brand Title
        # -------------------------------------------------------------
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 15))

        title = ctk.CTkLabel(
            brand_frame,
            text="UAMS",
            font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
            text_color=self.colors["active_bg"],
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            brand_frame,
            text="Attendance Portal",
            font=ctk.CTkFont(size=11),
            text_color=self.colors["text_muted"],
        )
        subtitle.pack(anchor="w")

        # -------------------------------------------------------------
        # User Badge Frame
        # -------------------------------------------------------------
        user_card = ctk.CTkFrame(self, fg_color=self.colors["card_bg"], corner_radius=8)
        user_card.pack(fill="x", padx=12, pady=(0, 15))

        user_name = self.user.get("full_name") or self.user.get("username", "User")
        user_role = (self.user.get("role") or "User").capitalize()

        ctk.CTkLabel(
            user_card,
            text=user_name,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_main"],
            anchor="w",
        ).pack(fill="x", padx=10, pady=(8, 0))

        ctk.CTkLabel(
            user_card,
            text=user_role,
            font=ctk.CTkFont(size=10),
            text_color=self.colors["active_bg"],
            anchor="w",
        ).pack(fill="x", padx=10, pady=(0, 8))

        # -------------------------------------------------------------
        # Navigation Items Scroll Area
        # -------------------------------------------------------------
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=8, pady=0)

        items = self.get_nav_items()

        for key, label in items:
            if key is None and label == "---":
                # Section Separator
                sep = ctk.CTkFrame(scroll_frame, height=1, fg_color=self.colors["border"])
                sep.pack(fill="x", padx=8, pady=8)
                continue

            is_subitem = label.startswith("    \u2022")
            label = label.strip()
            btn = ctk.CTkButton(
                scroll_frame,
                text=label,
                image=icon(NAV_ICONS.get(key)),
                compound="left",
                anchor="w",
                height=34 if is_subitem else 38,
                corner_radius=8,
                fg_color="transparent",
                hover_color=self.colors["hover_bg"],
                text_color=self.colors["text_muted"] if is_subitem else self.colors["text_main"],
                font=ctk.CTkFont(size=11 if is_subitem else 12, weight="normal" if is_subitem else "bold"),
                command=lambda k=key: self.on_navigate(k),
            )
            btn.pack(fill="x", pady=1, padx=2)
            self.nav_buttons[key] = btn

        # -------------------------------------------------------------
        # Footer Action Area (Change Password & Logout)
        # -------------------------------------------------------------
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=12, pady=15)

        change_pwd_btn = ctk.CTkButton(
            footer_frame,
            text="\U0001F511 Change Password",
            anchor="w",
            height=34,
            corner_radius=8,
            fg_color="transparent",
            hover_color=self.colors["hover_bg"],
            text_color=self.colors["text_muted"],
            font=ctk.CTkFont(size=12),
            command=self.on_change_password,
        )
        change_pwd_btn.pack(fill="x", pady=(0, 6))

        logout_btn = ctk.CTkButton(
            footer_frame,
            text="\U0001F6AA Logout",
            height=36,
            corner_radius=8,
            fg_color=self.colors["danger"],
            hover_color=self.colors["danger_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_logout,
        )
        logout_btn.pack(fill="x")

    def get_nav_items(self):
        role = self.user.get("role", "")

        if role == "admin":
            items = [
                ("dashboard",      "  Dashboard"),
                (None, "---"),
                ("users",          "  User Management"),
                (None, "---"),
                ("students",       "  Student Management"),
                ("teachers",       "  Teacher Management"),
                ("departments",    "  Department Management"),
                ("courses",        "  Course / Subject Management"),
                ("classes",        "  Class Management"),
                (None, "---"),
                ("attendance",     "  Attendance Management"),
                ("attendance_requests", "    \u2022 Student Requests"),
                ("reports",        "  Reports"),
                ("activity_logs",  "  Activity Logs"),
                (None, "---"),
                ("academic_year",  "  Academic Year / Semester"),
                ("settings",       "  Settings"),
                (None, "---"),
                ("admin_profile",  "  My Profile"),
            ]
        elif role == "teacher":
            items = [
                ("dashboard",       "  Dashboard"),
                (None, "---"),
                ("my_subjects",     "  My Subjects"),
                ("my_classes",      "  My Classes"),
                (None, "---"),
                ("take_attendance", "  Take Attendance"),
                ("attendance_view", "  Attendance History"),
                ("attendance_requests", "    \u2022 Student Requests"),
                (None, "---"),
                ("reports",         "  Reports"),
                ("teacher_profile", "  My Profile"),
            ]
        else:
            items = [
                ("dashboard",         "  Dashboard"),
                (None, "---"),
                ("my_attendance",     "  My Attendance"),
                ("attendance_requests", "    \u2022 My Requests"),
                ("attendance_report", "  Attendance Report"),
                ("my_subjects",       "  My Subjects"),
                (None, "---"),
                ("student_profile",   "  My Profile"),
            ]
        return items

    def set_active(self, name):
        for key, btn in self.nav_buttons.items():
            btn.configure(
                fg_color="transparent",
                text_color=self.colors["text_muted"] if "\u2022" in btn.cget("text") else self.colors["text_main"],
            )
        if name in self.nav_buttons:
            self.nav_buttons[name].configure(
                fg_color=self.colors["active_bg"],
                text_color=self.colors["active_text"],
            )

    def on_change_password(self):
        if callable(self.on_change_password_cb):
            self.on_change_password_cb()

    def on_logout(self):
        if callable(self.on_logout_cb):
            self.on_logout_cb()
