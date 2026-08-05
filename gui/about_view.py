import customtkinter as ctk

class AboutView(ctk.CTkFrame):
    def __init__(self, db, parent):
        super().__init__(parent)
        self.db = db
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="About",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        info_frame = ctk.CTkFrame(self)
        info_frame.pack(pady=30, padx=40, fill="both", expand=True)

        lines = [
            ("University Attendance Management System", 18, True),
            ("", 10, False),
            ("Version", "1.0.0"),
            ("Developer", "UAMS Team"),
            ("Technology", "Python + CustomTkinter"),
            ("Database", "SQLite"),
            ("", 10, False),
            ("2026 UAMS. All rights reserved.", 14, False),
        ]

        for i, item in enumerate(lines):
            if len(item) == 3 and isinstance(item[1], int):
                if item[0]:
                    ctk.CTkLabel(info_frame, text=item[0],
                                 font=ctk.CTkFont(size=item[1], weight="bold" if item[2] else "normal"),
                                 anchor="center").pack(pady=5)
            elif len(item) == 2:
                f = ctk.CTkFrame(info_frame)
                f.pack(fill="x", pady=2, padx=40)
                ctk.CTkLabel(f, text=item[0] + ":",
                             font=ctk.CTkFont(size=14, weight="bold"),
                             width=120, anchor="e").pack(side="left")
                ctk.CTkLabel(f, text=item[1],
                             font=ctk.CTkFont(size=14),
                             anchor="w").pack(side="left", padx=10)
