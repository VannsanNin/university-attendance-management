import customtkinter as ctk
from gui import theme

class StudentSubjectsView(ctk.CTkFrame):
    def __init__(self, db, parent, user):
        super().__init__(parent, fg_color=theme.c("bg_dark"))
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="My Subjects",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        conn = db.get_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT s.id, s.department_id FROM students s
            WHERE s.user_id=?""", (user["id"],))
        student = cursor.fetchone()
        conn.close()

        if not student:
            ctk.CTkLabel(self, text="Student profile not found. Contact admin.",
                         font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        courses = self.db.get_courses(department_id=student["department_id"])

        if not courses:
            ctk.CTkLabel(self, text="No subjects available for your department.",
                         font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=40, pady=10)

        for c in courses:
            card = ctk.CTkFrame(scroll, fg_color=theme.c("card_alt"), corner_radius=8,
                                border_width=1, border_color=theme.c("border_alt"))
            card.pack(fill="x", pady=5)

            info = f"{c['course_code']} - {c['course_name']}"
            if c.get("credit"):
                info += f" | Credit: {c['credit']}"
            if c.get("teacher_name"):
                info += f" | Teacher: {c['teacher_name']}"

            ctk.CTkLabel(card, text=info, font=ctk.CTkFont(size=14),
                         anchor="w").pack(padx=15, pady=10)
