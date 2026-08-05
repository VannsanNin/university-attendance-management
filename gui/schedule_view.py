import customtkinter as ctk
from tkinter import messagebox

class ScheduleView(ctk.CTkFrame):
    def __init__(self, db, parent):
        super().__init__(parent)
        self.db = db
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="Schedule Management",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        msg = "Schedule management is under development."
        ctk.CTkLabel(self, text=msg,
                     font=ctk.CTkFont(size=16),
                     text_color="#888888").pack(pady=50)
