import customtkinter as ctk

class TeacherProfileView(ctk.CTkFrame):
    def __init__(self, db, parent, user):
        super().__init__(parent)
        self.db = db
        self.user = user
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="My Profile",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        conn = db.get_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT t.*, d.name as department_name FROM teachers t
            LEFT JOIN departments d ON t.department_id = d.id
            WHERE t.user_id=?""", (user["id"],))
        teacher = cursor.fetchone()
        conn.close()

        if teacher:
            info = ctk.CTkFrame(self)
            info.pack(pady=20, padx=40, fill="both", expand=True)

            fields = [
                ("Teacher ID", teacher["teacher_id"]),
                ("Full Name", teacher["full_name"]),
                ("Email", teacher["email"]),
                ("Phone", teacher["phone"]),
                ("Department", teacher["department_name"]),
            ]
            for i, (label, value) in enumerate(fields):
                f = ctk.CTkFrame(info)
                f.grid(row=i, column=0, sticky="ew", pady=2, padx=20)
                ctk.CTkLabel(f, text=label + ":", font=ctk.CTkFont(size=14, weight="bold"),
                             width=150, anchor="w").pack(side="left")
                ctk.CTkLabel(f, text=value or "N/A", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        else:
            ctk.CTkLabel(self, text="Teacher profile not found. Contact admin.",
                         font=ctk.CTkFont(size=16)).pack(pady=50)
