import customtkinter as ctk
from gui import theme


class StudentSubjectsView(ctk.CTkFrame):
    def __init__(self, db, parent, user):
        super().__init__(parent, fg_color=theme.c("bg_dark"), corner_radius=0)
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)

        self._build_ui()

    def _build_ui(self):
        # Top Header Bar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="My Subjects",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Registered courses and assigned department instructors",
            font=ctk.CTkFont(size=12),
            text_color=theme.c("text_muted")
        ).pack(anchor="w", pady=(2, 0))

        # Refresh Button Action
        ctk.CTkButton(
            header,
            text="Refresh",
            width=90,
            height=32,
            corner_radius=8,
            fg_color=theme.c("card_bg"),
            hover_color=theme.c("border"),
            text_color=theme.c("text_bright"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._load_courses
        ).pack(side="right")

        # Main Scrollable Container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=30, pady=10)

        self._load_courses()

    def _load_courses(self):
        # Clear existing children inside scroll frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Query Student Profile & Department ID
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT s.id, s.department_id FROM students s WHERE s.user_id=?",
            (self.user["id"],)
        )
        student = cursor.fetchone()
        conn.close()

        if not student:
            self._render_empty_state("Student profile not found. Please contact an administrator.")
            return

        courses = self.db.get_courses(department_id=student["department_id"])

        if not courses:
            self._render_empty_state("No subject modules available for your enrolled department.")
            return

        # Render Course Cards Grid
        for course in courses:
            self._render_course_card(course)

    def _render_course_card(self, c):
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=theme.c("card_alt"),
            corner_radius=10,
            border_width=1,
            border_color=theme.c("border_alt")
        )
        card.pack(fill="x", pady=6)

        # Card Left Content Area
        left_box = ctk.CTkFrame(card, fg_color="transparent")
        left_box.pack(side="left", fill="both", expand=True, padx=16, pady=14)

        # Top Meta Bar: Code Badge + Credit Tag
        meta_bar = ctk.CTkFrame(left_box, fg_color="transparent")
        meta_bar.pack(anchor="w", pady=(0, 4))

        # Course Code Badge
        code_badge = ctk.CTkFrame(
            meta_bar,
            fg_color=theme.c("card_bg"),
            corner_radius=6,
            border_width=1,
            border_color=theme.c("border")
        )
        code_badge.pack(side="left")

        ctk.CTkLabel(
            code_badge,
            text=c.get("course_code", "N/A"),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme.c("text_bright")
        ).pack(padx=8, pady=2)

        # Credits Badge
        if c.get("credit"):
            ctk.CTkLabel(
                meta_bar,
                text=f"•  {c['credit']} Credits",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=theme.c("text_muted")
            ).pack(side="left", padx=10)

        # Subject Title
        ctk.CTkLabel(
            left_box,
            text=c.get("course_name", "Untitled Course"),
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme.c("text_bright"),
            anchor="w"
        ).pack(anchor="w")

        # Instructor Name
        teacher_name = c.get("teacher_name") or "Unassigned Instructor"
        ctk.CTkLabel(
            left_box,
            text=f"Instructor: {teacher_name}",
            font=ctk.CTkFont(size=12),
            text_color=theme.c("text_muted"),
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))

    def _render_empty_state(self, message):
        empty_box = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=theme.c("card_bg"),
            corner_radius=12
        )
        empty_box.pack(fill="x", pady=40, padx=20)

        ctk.CTkLabel(
            empty_box,
            text=message,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=theme.c("text_muted")
        ).pack(pady=30)