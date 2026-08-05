import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# Design tokens — keep every color/spacing decision here so the whole view
# stays consistent and easy to retheme later.
# ---------------------------------------------------------------------------
COLOR_BG = "#0F0F17"
COLOR_SURFACE = "#171723"
COLOR_SURFACE_ALT = "#1D1D2C"
COLOR_BORDER = "#2A2A3C"
COLOR_ACCENT = "#6C7CFF"
COLOR_ACCENT_HOVER = "#5766E8"
COLOR_ACCENT_MUTED = "#2C2E4A"
COLOR_TEXT = "#EDEDF5"
COLOR_TEXT_MUTED = "#8A8AA3"
COLOR_DANGER = "#E5484D"
COLOR_DANGER_HOVER = "#C93E42"
COLOR_SUCCESS = "#3DD68C"

FONT_FAMILY = "Segoe UI"
FONT_TITLE = ctk.CTkFont(family=FONT_FAMILY, size=26, weight="bold")
FONT_SECTION = ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")
FONT_LABEL = ctk.CTkFont(family=FONT_FAMILY, size=13)
FONT_HINT = ctk.CTkFont(family=FONT_FAMILY, size=11)
FONT_BUTTON = ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")

CARD_RADIUS = 14
FIELD_RADIUS = 8
FIELD_HEIGHT = 36


def card(parent, **kwargs):
    """A consistent elevated container used to group related settings."""
    defaults = dict(fg_color=COLOR_SURFACE, corner_radius=CARD_RADIUS,
                     border_width=1, border_color=COLOR_BORDER)
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def section_header(parent, text, hint=None):
    wrap = ctk.CTkFrame(parent, fg_color="transparent")
    wrap.pack(fill="x", padx=18, pady=(16, 4))

    row = ctk.CTkFrame(wrap, fg_color="transparent")
    row.pack(fill="x")
    accent = ctk.CTkFrame(row, width=3, height=16, fg_color=COLOR_ACCENT, corner_radius=2)
    accent.pack(side="left", padx=(0, 8))
    accent.pack_propagate(False)
    ctk.CTkLabel(row, text=text, font=FONT_SECTION, text_color=COLOR_TEXT).pack(side="left")

    if hint:
        ctk.CTkLabel(wrap, text=hint, font=FONT_HINT, text_color=COLOR_TEXT_MUTED,
                     anchor="w").pack(fill="x", pady=(2, 0))
    return wrap


def labeled_field(parent, label, widget_factory, width_label=190):
    """widget_factory(row) -> widget, already packed on the right."""
    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(fill="x", padx=18, pady=6)
    ctk.CTkLabel(row, text=label, width=width_label, anchor="w",
                 font=FONT_LABEL, text_color=COLOR_TEXT_MUTED).pack(side="left")
    return widget_factory(row)


def primary_button(parent, text, command, fg_color=COLOR_ACCENT, hover_color=COLOR_ACCENT_HOVER, **kw):
    return ctk.CTkButton(
        parent, text=text, command=command, height=38, corner_radius=FIELD_RADIUS,
        font=FONT_BUTTON, fg_color=fg_color, hover_color=hover_color,
        text_color="#0F0F17" if fg_color == COLOR_ACCENT else COLOR_TEXT, **kw
    )


def ghost_button(parent, text, command, width=70):
    return ctk.CTkButton(
        parent, text=text, command=command, width=width, height=28, corner_radius=FIELD_RADIUS,
        font=FONT_HINT, fg_color="transparent", hover_color=COLOR_SURFACE_ALT,
        border_width=1, border_color=COLOR_BORDER, text_color=COLOR_TEXT_MUTED
    )


class SettingsView(ctk.CTkFrame):
    def __init__(self, db, parent):
        super().__init__(parent, fg_color=COLOR_BG)
        self.db = db
        self.pack(fill="both", expand=True)
        self.build_ui()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(28, 6))
        ctk.CTkLabel(header, text="Settings", font=FONT_TITLE, text_color=COLOR_TEXT).pack(anchor="w")
        ctk.CTkLabel(header, text="Manage university profile and system-wide preferences",
                     font=FONT_HINT, text_color=COLOR_TEXT_MUTED).pack(anchor="w", pady=(2, 0))

        self.tab_view = ctk.CTkTabview(
            self, fg_color="transparent",
            segmented_button_fg_color=COLOR_SURFACE,
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
            segmented_button_unselected_color=COLOR_SURFACE,
            segmented_button_unselected_hover_color=COLOR_SURFACE_ALT,
            text_color=COLOR_TEXT,
            corner_radius=CARD_RADIUS,
        )
        self.tab_view.pack(fill="both", expand=True, padx=40, pady=10)

        self.univ_tab = self.tab_view.add("University Information")
        self.sys_tab = self.tab_view.add("System Settings")

        self.build_university_tab()
        self.build_system_tab()

    # ------------------------------------------------------------------
    # University tab
    # ------------------------------------------------------------------
    def build_university_tab(self):
        scroll = ctk.CTkScrollableFrame(self.univ_tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=6, pady=6)

        settings = self.db.get_all_settings()

        info_card = card(scroll)
        info_card.pack(fill="x", pady=(4, 16))
        section_header(info_card, "University Profile", "Shown on reports, IDs, and outgoing email")

        fields = [
            ("university_name", "University Name"),
            ("address", "Address"),
            ("phone", "Phone"),
            ("email", "Email"),
            ("website", "Website"),
        ]

        self.univ_entries = {}
        for key, label in fields:
            def make(key=key):
                def factory(row):
                    e = ctk.CTkEntry(row, width=360, height=FIELD_HEIGHT, corner_radius=FIELD_RADIUS,
                                      fg_color=COLOR_SURFACE_ALT, border_color=COLOR_BORDER,
                                      text_color=COLOR_TEXT, font=FONT_LABEL)
                    e.insert(0, settings.get(key, ""))
                    e.pack(side="left", padx=(10, 0))
                    return e
                return factory
            self.univ_entries[key] = labeled_field(info_card, label, make())

        logo_card = card(scroll)
        logo_card.pack(fill="x", pady=(0, 16))
        section_header(logo_card, "Branding", "Logo used across generated documents")

        logo_row = ctk.CTkFrame(logo_card, fg_color="transparent")
        logo_row.pack(fill="x", padx=18, pady=(6, 18))
        ctk.CTkLabel(logo_row, text="Logo", width=190, anchor="w",
                     font=FONT_LABEL, text_color=COLOR_TEXT_MUTED).pack(side="left")
        self.logo_path_var = ctk.StringVar(value=settings.get("logo", ""))
        ctk.CTkEntry(logo_row, width=290, height=FIELD_HEIGHT, corner_radius=FIELD_RADIUS,
                     fg_color=COLOR_SURFACE_ALT, border_color=COLOR_BORDER,
                     text_color=COLOR_TEXT, font=FONT_LABEL,
                     textvariable=self.logo_path_var).pack(side="left", padx=(10, 8))
        ghost_button(logo_row, "Browse", self.pick_logo, width=90).pack(side="left")

        primary_button(scroll, "Save University Info", self.save_university).pack(
            anchor="w", padx=4, pady=(0, 20))

    def pick_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if path:
            self.logo_path_var.set(path)

    def save_university(self):
        for key, entry in self.univ_entries.items():
            self.db.set_setting(key, entry.get().strip())
        self.db.set_setting("logo", self.logo_path_var.get())
        messagebox.showinfo("Success", "University information saved")

    # ------------------------------------------------------------------
    # System tab
    # ------------------------------------------------------------------
    def build_system_tab(self):
        scroll = ctk.CTkScrollableFrame(self.sys_tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=6, pady=6)

        settings = self.db.get_all_settings()

        # --- General preferences -----------------------------------------
        gen_card = card(scroll)
        gen_card.pack(fill="x", pady=(4, 16))
        section_header(gen_card, "General")

        self.theme_var = ctk.StringVar(value=settings.get("theme", "Dark"))
        self.lang_var = ctk.StringVar(value=settings.get("language", "English"))
        self.tz_var = ctk.StringVar(value=settings.get("timezone", "UTC"))
        self.df_var = ctk.StringVar(value=settings.get("date_format", "YYYY-MM-DD"))

        def option_menu(row, var, values):
            m = ctk.CTkOptionMenu(row, values=values, variable=var, width=220, height=FIELD_HEIGHT,
                                   corner_radius=FIELD_RADIUS, fg_color=COLOR_SURFACE_ALT,
                                   button_color=COLOR_ACCENT_MUTED, button_hover_color=COLOR_ACCENT,
                                   text_color=COLOR_TEXT, font=FONT_LABEL, dropdown_fg_color=COLOR_SURFACE_ALT)
            m.pack(side="left", padx=(10, 0))
            return m

        labeled_field(gen_card, "Theme", lambda r: option_menu(r, self.theme_var, ["Dark", "Light", "System"]))
        labeled_field(gen_card, "Language", lambda r: option_menu(r, self.lang_var, ["English", "French", "Arabic", "Spanish"]))
        labeled_field(gen_card, "Time Zone", lambda r: option_menu(r, self.tz_var, [
            "UTC", "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "Europe/London", "Europe/Paris", "Asia/Dubai", "Asia/Riyadh"]))
        labeled_field(gen_card, "Date Format", lambda r: option_menu(r, self.df_var, [
            "YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"]))

        self.ab_var = ctk.StringVar(value=settings.get("auto_backup", "0"))
        labeled_field(gen_card, "Auto Backup", lambda r: ctk.CTkCheckBox(
            r, text="Enable daily backups", variable=self.ab_var, onvalue="1", offvalue="0",
            font=FONT_LABEL, text_color=COLOR_TEXT, fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER, border_color=COLOR_BORDER).pack(side="left", padx=(10, 0)) or r)

        self.warn_entry = None
        def warn_factory(row):
            e = ctk.CTkEntry(row, width=100, height=FIELD_HEIGHT, corner_radius=FIELD_RADIUS,
                              fg_color=COLOR_SURFACE_ALT, border_color=COLOR_BORDER,
                              text_color=COLOR_TEXT, font=FONT_LABEL)
            e.insert(0, settings.get("low_attendance_warning", "70"))
            e.pack(side="left", padx=(10, 4))
            ctk.CTkLabel(row, text="%", font=FONT_LABEL, text_color=COLOR_TEXT_MUTED).pack(side="left")
            return e
        self.warn_entry = labeled_field(gen_card, "Low Attendance Warning", warn_factory)
        ctk.CTkFrame(gen_card, fg_color="transparent", height=8).pack()

        # --- SMTP / notifications (collapsible) ----------------------------
        smtp_card = card(scroll)
        smtp_card.pack(fill="x", pady=(0, 16))

        smtp_head = ctk.CTkFrame(smtp_card, fg_color="transparent")
        smtp_head.pack(fill="x", padx=18, pady=(16, 4))
        left = ctk.CTkFrame(smtp_head, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        accent = ctk.CTkFrame(left, width=3, height=16, fg_color=COLOR_ACCENT, corner_radius=2)
        accent.pack(side="left", padx=(0, 8))
        accent.pack_propagate(False)
        ctk.CTkLabel(left, text="Email & SMS Notifications", font=FONT_SECTION,
                     text_color=COLOR_TEXT).pack(side="left")

        self.smtp_collapsed = ctk.BooleanVar(value=True)
        self.smtp_toggle = ghost_button(smtp_head, "Show", self.toggle_smtp, width=70)
        self.smtp_toggle.pack(side="right")

        self.smtp_frame = ctk.CTkFrame(smtp_card, fg_color="transparent")

        smtp_fields = [
            ("smtp_server", "SMTP Server"),
            ("smtp_port", "SMTP Port"),
            ("smtp_email", "SMTP Email"),
            ("smtp_password", "SMTP Password"),
        ]
        self.smtp_entries = {}
        for key, label in smtp_fields:
            def make(key=key):
                def factory(row):
                    show = "•" if "password" in key else ""
                    e = ctk.CTkEntry(row, width=360, height=FIELD_HEIGHT, corner_radius=FIELD_RADIUS,
                                      fg_color=COLOR_SURFACE_ALT, border_color=COLOR_BORDER,
                                      text_color=COLOR_TEXT, font=FONT_LABEL, show=show)
                    e.insert(0, settings.get(key, ""))
                    e.pack(side="left", padx=(10, 0))
                    return e
                return factory
            self.smtp_entries[key] = labeled_field(self.smtp_frame, label, make())

        def sms_factory(row):
            e = ctk.CTkEntry(row, width=360, height=FIELD_HEIGHT, corner_radius=FIELD_RADIUS,
                              fg_color=COLOR_SURFACE_ALT, border_color=COLOR_BORDER,
                              text_color=COLOR_TEXT, font=FONT_LABEL, show="•")
            e.insert(0, settings.get("sms_api_key", ""))
            e.pack(side="left", padx=(10, 0))
            return e
        self.sms_entry = labeled_field(self.smtp_frame, "SMS API Key", sms_factory)
        ctk.CTkFrame(smtp_card, fg_color="transparent", height=10).pack()

        # --- Actions ---------------------------------------------------
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=4, pady=(0, 24))

        primary_button(btn_row, "Save System Settings", self.save_system).pack(side="left", padx=(0, 8))
        primary_button(btn_row, "Backup Database", self.backup_db,
                        fg_color=COLOR_SURFACE_ALT, hover_color=COLOR_BORDER).pack(side="left", padx=8)
        primary_button(btn_row, "Restore Database", self.restore_db,
                        fg_color=COLOR_DANGER, hover_color=COLOR_DANGER_HOVER).pack(side="left", padx=8)

    def toggle_smtp(self):
        if self.smtp_collapsed.get():
            self.smtp_frame.pack(fill="x", pady=(0, 4))
            self.smtp_collapsed.set(False)
            self.smtp_toggle.configure(text="Hide")
        else:
            self.smtp_frame.pack_forget()
            self.smtp_collapsed.set(True)
            self.smtp_toggle.configure(text="Show")

    def save_system(self):
        self.db.set_setting("theme", self.theme_var.get())
        ctk.set_appearance_mode(self.theme_var.get().lower())
        self.db.set_setting("language", self.lang_var.get())
        self.db.set_setting("timezone", self.tz_var.get())
        self.db.set_setting("date_format", self.df_var.get())
        self.db.set_setting("auto_backup", self.ab_var.get())
        self.db.set_setting("low_attendance_warning", self.warn_entry.get().strip())
        for key, entry in self.smtp_entries.items():
            self.db.set_setting(key, entry.get().strip())
        self.db.set_setting("sms_api_key", self.sms_entry.get().strip())
        messagebox.showinfo("Success", "System settings saved")

    def backup_db(self):
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backup")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"uams_backup_{timestamp}.db")
        result = self.db.backup_database(backup_path)
        if result is True:
            messagebox.showinfo("Success", f"Database backed up to:\n{backup_path}")
        else:
            messagebox.showerror("Error", f"Backup failed: {result}")

    def restore_db(self):
        path = filedialog.askopenfilename(filetypes=[("SQLite DB", "*.db"), ("All files", "*.*")])
        if not path:
            return
        if not messagebox.askyesno("Confirm Restore", "This will overwrite the current database. Are you sure?"):
            return
        result = self.db.restore_database(path)
        if result is True:
            messagebox.showinfo("Success", "Database restored. Some features may need a restart.")
        else:
            messagebox.showerror("Error", f"Restore failed: {result}")