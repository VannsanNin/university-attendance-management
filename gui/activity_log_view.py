import customtkinter as ctk
from tkinter import messagebox, ttk

from gui import theme
from gui.skeleton import schedule_table_load

ACTION_COLORS = {
    "CREATE": theme.c("success"),
    "UPDATE": theme.c("warning"),
    "DELETE": theme.c("danger"),
    "LOGIN": theme.c("info"),
    "LOGOUT": theme.c("info"),
    "AUTH": theme.c("info"),
}

ACTIONS = ["", "CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "AUTH"]
ROLES = ["", "admin", "teacher", "student"]


class ActivityLogView(ctk.CTkFrame):
    """Admin-only audit trail of user actions across the system."""

    def __init__(self, db, parent, user=None):
        super().__init__(parent, fg_color=theme.c("bg_dark"))
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)

        self.colors = theme.colors

        self._build_header()
        self._build_filters()
        self._build_table()
        schedule_table_load(self, self.table_frame, self.load_logs)

    # -------------------------------------------------------------
    # Header
    # -------------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text="Activity Logs",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="Audit trail of all user actions",
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_muted"]
        ).pack(side="left", padx=12, pady=(8, 0))

        ctk.CTkButton(
            header,
            text="\u21bb Refresh",
            command=self.load_logs,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="right", padx=4)

    # -------------------------------------------------------------
    # Filters
    # -------------------------------------------------------------
    def _build_filters(self):
        card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        card.pack(fill="x", padx=30, pady=(5, 15))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=15)

        self.search_entry = ctk.CTkEntry(
            inner, width=180, height=36, corner_radius=8,
            placeholder_text="Search username / detail..."
        )
        self.search_entry.pack(side="left", padx=2)

        self.module_combo = ctk.CTkComboBox(inner, width=170, height=36, corner_radius=8, values=["All modules"])
        self.module_combo.pack(side="left", padx=2)
        self.module_combo.set("All modules")

        self.action_combo = ctk.CTkComboBox(
            inner, width=110, height=36, corner_radius=8,
            values=["All actions"] + [a for a in ACTIONS if a]
        )
        self.action_combo.pack(side="left", padx=2)
        self.action_combo.set("All actions")

        self.role_combo = ctk.CTkComboBox(
            inner, width=120, height=36, corner_radius=8,
            values=["All roles"] + [r for r in ROLES if r]
        )
        self.role_combo.pack(side="left", padx=2)
        self.role_combo.set("All roles")

        self.start_entry = ctk.CTkEntry(inner, width=125, height=36, corner_radius=8, placeholder_text="Start (YYYY-MM-DD)")
        self.start_entry.pack(side="left", padx=2)

        self.end_entry = ctk.CTkEntry(inner, width=125, height=36, corner_radius=8, placeholder_text="End (YYYY-MM-DD)")
        self.end_entry.pack(side="left", padx=2)

        ctk.CTkButton(
            inner,
            text="\U0001f50d Search",
            width=90,
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.load_logs
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            inner,
            text="Reset",
            width=80,
            height=36,
            corner_radius=8,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.reset_filters
        ).pack(side="left", padx=2)

        self.search_entry.bind("<Return>", lambda e: self.load_logs())
        self.module_combo.bind("<<ComboboxSelected>>", lambda e: self.load_logs())
        self.action_combo.bind("<<ComboboxSelected>>", lambda e: self.load_logs())
        self.role_combo.bind("<<ComboboxSelected>>", lambda e: self.load_logs())

    def reset_filters(self):
        self.search_entry.delete(0, "end")
        self.module_combo.set("All modules")
        self.action_combo.set("All actions")
        self.role_combo.set("All roles")
        self.start_entry.delete(0, "end")
        self.end_entry.delete(0, "end")
        self.load_logs()

    # -------------------------------------------------------------
    # Table
    # -------------------------------------------------------------
    def _build_table(self):
        table_card = ctk.CTkFrame(
            self,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        table_card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        toolbar = ctk.CTkFrame(table_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(15, 10))

        self.count_label = ctk.CTkLabel(
            toolbar,
            text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=self.colors["text_main"]
        )
        self.count_label.pack(side="left")

        ctk.CTkButton(
            toolbar,
            text="Clear Old Logs",
            height=32,
            corner_radius=6,
            fg_color=self.colors["danger"],
            hover_color=self.colors["danger_hover"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._clear_old_logs
        ).pack(side="right")

        self.table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "ActivityLog.Treeview",
            background=theme.c("table_bg"),
            foreground=theme.c("table_fg"),
            fieldbackground=theme.c("table_bg"),
            rowheight=34,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "ActivityLog.Treeview.Heading",
            background=theme.c("table_head_bg"),
            foreground=theme.c("table_head_fg"),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "ActivityLog.Treeview",
            background=[("selected", theme.c("table_selected"))],
            foreground=[("selected", theme.c("table_selected_fg"))]
        )
        style.map(
            "ActivityLog.Treeview.Heading",
            background=[("active", theme.c("table_head_active"))]
        )

        columns = ("time", "user", "role", "action", "module", "description")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings",
                                 style="ActivityLog.Treeview", selectmode="browse")

        headings = {
            "time": ("Time", 160),
            "user": ("User", 110),
            "role": ("Role", 90),
            "action": ("Action", 90),
            "module": ("Module", 160),
            "description": ("Description", 520),
        }

        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, minwidth=width, stretch=True, anchor="w")

        for action, color in ACTION_COLORS.items():
            self.tree.tag_configure(action, foreground=color)

        scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # -------------------------------------------------------------
    # Data loading
    # -------------------------------------------------------------
    def _filters(self):
        kwargs = {}
        search = self.search_entry.get().strip() if hasattr(self, "search_entry") else ""
        if search:
            kwargs["search"] = search

        module = self.module_combo.get()
        if module and module != "All modules":
            kwargs["module"] = module

        action = self.action_combo.get()
        if action and action != "All actions":
            kwargs["action"] = action

        role = self.role_combo.get()
        if role and role != "All roles":
            kwargs["role"] = role

        start = self.start_entry.get().strip()
        if start:
            kwargs["start_date"] = start

        end = self.end_entry.get().strip()
        if end:
            kwargs["end_date"] = end

        return kwargs

    def load_logs(self):
        self.tree.delete(*self.tree.get_children())

        kwargs = self._filters()
        try:
            records = self.db.get_activity_logs(**kwargs)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load activity logs:\n{e}")
            return

        for r in records:
            action = r.get("action", "") or ""
            tag = action if action in ACTION_COLORS else ""
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                (r.get("created_at") or "")[:19],
                r.get("username") or "\u2014",
                r.get("role") or "\u2014",
                action or "\u2014",
                r.get("module") or "\u2014",
                r.get("description") or "",
            ), tags=(tag,))

        total = len(records)
        self.count_label.configure(
            text=f"Showing {total} log entr{'y' if total == 1 else 'ies'}"
        )

    def _clear_old_logs(self):
        days = messagebox.askquestion(
            "Clear Old Logs",
            "Delete all activity logs?\n\nThis action cannot be undone.",
            icon="warning"
        )
        if days != "yes":
            return
        try:
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM activity_logs")
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "All activity logs cleared.")
            self.load_logs()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear logs:\n{e}")
