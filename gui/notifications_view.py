import customtkinter as ctk
from tkinter import messagebox

class NotificationsView(ctk.CTkFrame):
    def __init__(self, db, parent):
        super().__init__(parent)
        self.db = db
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="Notifications",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=40, pady=10)

        ctk.CTkButton(top, text="Generate Low Attendance Warnings",
                       command=self.generate_warnings, height=40).pack(side="left", padx=5)
        ctk.CTkButton(top, text="Refresh", command=self.load_notifications,
                       height=40).pack(side="left", padx=5)

        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=40, pady=10)
        self.load_notifications()

    def generate_warnings(self):
        threshold = self.db.get_setting("low_attendance_warning") or "70"
        try:
            threshold = int(threshold)
        except:
            threshold = 70
        notifs = self.db.generate_low_attendance_notifications(threshold)
        if notifs:
            messagebox.showinfo("Success", f"Generated {len(notifs)} warning(s)")
        else:
            messagebox.showinfo("Info", "No students below attendance threshold")
        self.load_notifications()

    def load_notifications(self):
        for w in self.table_frame.winfo_children():
            w.destroy()

        notifs = self.db.get_notifications()

        headers = ["ID", "Student", "Type", "Message", "Date", "Status"]
        hf = ctk.CTkFrame(self.table_frame)
        hf.pack(fill="x")
        for h in headers:
            ctk.CTkLabel(hf, text=h, font=ctk.CTkFont(size=13, weight="bold"),
                         width=100).pack(side="left", padx=2)

        sc = ctk.CTkScrollableFrame(self.table_frame)
        sc.pack(fill="both", expand=True)

        if not notifs:
            ctk.CTkLabel(sc, text="No notifications", font=ctk.CTkFont(size=14)).pack(pady=20)

        for n in notifs:
            r = ctk.CTkFrame(sc)
            r.pack(fill="x", pady=1)
            for val in [n["id"], n.get("student_name", "N/A"), n.get("type", ""),
                        n.get("message", "")[:50], n.get("sent_date", ""), n.get("status", "")]:
                ctk.CTkLabel(r, text=str(val or ""), width=100).pack(side="left", padx=2)
