import customtkinter as ctk
from gui import theme

class TeacherClassesView(ctk.CTkFrame):
    def __init__(self, db, parent, user):
        super().__init__(parent, fg_color=theme.c("bg_dark"))
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="My Classes",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        conn = db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM teachers WHERE user_id=?", (user["id"],))
        teacher = cursor.fetchone()
        conn.close()

        if not teacher:
            ctk.CTkLabel(self, text="Teacher profile not linked.",
                         font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        classes = db.get_classes()
        teacher_classes = [c for c in classes if c.get("teacher_id") == teacher["id"]]

        if not teacher_classes:
            ctk.CTkLabel(self, text="No classes assigned to you.",
                         font=ctk.CTkFont(size=16)).pack(pady=50)
            return

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=40, pady=10)

        for cl in teacher_classes:
            card = ctk.CTkFrame(scroll, fg_color=theme.c("card_alt"), corner_radius=8,
                                border_width=1, border_color=theme.c("border_alt"))
            card.pack(fill="x", pady=5)

            header = f"{cl['class_name']} ({cl['department_name']})"
            ctk.CTkLabel(card, text=header, font=ctk.CTkFont(size=15, weight="bold"),
                         anchor="w").pack(padx=15, pady=(10, 5))

            students = db.get_class_students(cl["id"])
            if students:
                for s in students:
                    ctk.CTkLabel(card, text=f"  {s['student_id']} - {s['full_name']}",
                                 font=ctk.CTkFont(size=13), anchor="w").pack(padx=25, pady=1)
            else:
                ctk.CTkLabel(card, text="  No students assigned",
                             font=ctk.CTkFont(size=13), text_color=theme.c("gray_soft")).pack(padx=25, pady=1)
