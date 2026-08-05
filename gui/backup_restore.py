import customtkinter as ctk
from gui import theme
from tkinter import messagebox, filedialog
from datetime import datetime
import os
import threading

class BackupRestoreView(ctk.CTkFrame):
    def __init__(self, db, parent):
        super().__init__(parent, fg_color=theme.c("bg_dark"))
        self.db = db
        self.auto_timer = None
        self.pack(fill="both", expand=True)

        ctk.CTkLabel(self, text="Database Backup & Restore",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=40, pady=10)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = ctk.CTkFrame(main)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(left, text="Backup", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        self.backup_path = os.path.join(os.path.dirname(self.db.db_path), "backup")
        os.makedirs(self.backup_path, exist_ok=True)

        ctk.CTkLabel(left, text=f"Backup directory:", font=ctk.CTkFont(size=12)).pack()
        ctk.CTkLabel(left, text=self.backup_path, font=ctk.CTkFont(size=11), text_color="gray").pack()

        ctk.CTkButton(left, text="Create Backup Now", command=self.create_backup,
                      height=40).pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(left, text="Auto Backup Settings", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))
        self.auto_var = ctk.StringVar(value="0")
        cb = ctk.CTkCheckBox(left, text="Enable auto backup (every hour)", variable=self.auto_var,
                             onvalue="1", offvalue="0", command=self.toggle_auto_backup)
        cb.pack(pady=5)
        ctk.CTkButton(left, text="Save Setting", command=self.save_auto_backup).pack(pady=5)

        ctk.CTkLabel(right, text="Restore", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkLabel(right, text="Warning: Restoring will overwrite current data!",
                     text_color="red", font=ctk.CTkFont(size=12)).pack(pady=5)
        ctk.CTkButton(right, text="Select Backup File & Restore",
                      command=self.restore_backup, fg_color=theme.c("lightcoral"),
                      height=40).pack(fill="x", padx=20, pady=10)

        self.log_frame = ctk.CTkScrollableFrame(self)
        self.log_frame.pack(fill="both", expand=True, padx=40, pady=10)
        ctk.CTkLabel(self.log_frame, text="Backup History:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.load_logs()

        auto_setting = self.db.get_setting("auto_backup")
        if auto_setting == "1":
            self.auto_var.set("1")
            self.schedule_auto_backup()

    def create_backup(self):
        filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        path = os.path.join(self.backup_path, filename)
        result = self.db.backup_database(path)
        if result is True:
            messagebox.showinfo("Success", f"Backup created: {filename}")
            self.load_logs()
        else:
            messagebox.showerror("Error", f"Backup failed: {result}")

    def restore_backup(self):
        path = filedialog.askopenfilename(
            initialdir=self.backup_path,
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        if not path:
            return
        if messagebox.askyesno("Confirm Restore", "This will overwrite all current data. Continue?"):
            result = self.db.restore_database(path)
            if result is True:
                messagebox.showinfo("Success", "Database restored successfully")
            else:
                messagebox.showerror("Error", f"Restore failed: {result}")

    def save_auto_backup(self):
        self.db.set_setting("auto_backup", self.auto_var.get())
        messagebox.showinfo("Success", "Auto backup setting saved")

    def toggle_auto_backup(self):
        if self.auto_var.get() == "1":
            self.schedule_auto_backup()
        else:
            self.cancel_auto_backup()

    def schedule_auto_backup(self):
        self.cancel_auto_backup()
        self.auto_timer = threading.Timer(3600, self.auto_backup_worker)
        self.auto_timer.daemon = True
        self.auto_timer.start()

    def cancel_auto_backup(self):
        if self.auto_timer:
            self.auto_timer.cancel()
            self.auto_timer = None

    def auto_backup_worker(self):
        try:
            filename = f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            path = os.path.join(self.backup_path, filename)
            self.db.backup_database(path)
        finally:
            if self.auto_var.get() == "1":
                self.auto_timer = threading.Timer(3600, self.auto_backup_worker)
                self.auto_timer.daemon = True
                self.auto_timer.start()

    def load_logs(self):
        children = self.log_frame.winfo_children()
        for w in children[1:]:
            w.destroy()
        logs = self.db.get_backup_logs()
        if not logs:
            ctk.CTkLabel(self.log_frame, text="No backups yet").pack(anchor="w")
            return
        for log_entry in logs:
            ctk.CTkLabel(self.log_frame,
                         text=f"{log_entry['created_at']} - {os.path.basename(log_entry['file_path'])}",
                         anchor="w").pack(fill="x", pady=1)
