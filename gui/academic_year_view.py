import customtkinter as ctk
from gui import theme
from tkinter import messagebox, ttk
from datetime import datetime


class AcademicYearView(ctk.CTkFrame):
    def __init__(self, db, parent):
        super().__init__(parent, fg_color=theme.c("bg_dark"))  # Slate 900 background
        self.db = db
        self.pack(fill="both", expand=True)

        # Unified Color Palette Tokens
        self.colors = theme.colors

        self.build_ui()
        self.load_years()

    def build_ui(self):
        # -------------------------------------------------------------
        # Header Section
        # -------------------------------------------------------------
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))

        title = ctk.CTkLabel(
            header_frame,
            text="Academic Year & Semester",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color=self.colors["text_main"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Manage academic terms, semester date ranges, and active status",
            font=ctk.CTkFont(size=13),
            text_color=self.colors["text_muted"]
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # -------------------------------------------------------------
        # Main Container
        # -------------------------------------------------------------
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Form Card
        form_card = ctk.CTkFrame(
            main,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        form_card.pack(fill="x", pady=(5, 15))

        form_grid = ctk.CTkFrame(form_card, fg_color="transparent")
        form_grid.pack(fill="x", padx=20, pady=15)

        def add_label(text, col):
            lbl = ctk.CTkLabel(
                form_grid,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors["text_muted"]
            )
            lbl.grid(row=0, column=col, padx=(10, 4), pady=5, sticky="e")

        # Row 0 Form Components
        add_label("Year *", 0)
        self.year_entry = ctk.CTkEntry(form_grid, width=110, height=36, corner_radius=8)
        self.year_entry.insert(0, str(datetime.now().year))
        self.year_entry.grid(row=0, column=1, padx=4, pady=5, sticky="w")

        add_label("Semester", 2)
        self.semester_combo = ctk.CTkComboBox(form_grid, values=["1", "2", "3"], width=90, height=36, corner_radius=8)
        self.semester_combo.set("1")
        self.semester_combo.grid(row=0, column=3, padx=4, pady=5, sticky="w")

        add_label("Start Date", 4)
        self.start_entry = ctk.CTkEntry(form_grid, width=130, height=36, corner_radius=8, placeholder_text="YYYY-MM-DD")
        self.start_entry.grid(row=0, column=5, padx=4, pady=5, sticky="w")

        add_label("End Date", 6)
        self.end_entry = ctk.CTkEntry(form_grid, width=130, height=36, corner_radius=8, placeholder_text="YYYY-MM-DD")
        self.end_entry.grid(row=0, column=7, padx=4, pady=5, sticky="w")

        ctk.CTkButton(
            form_grid,
            text="+ Add Academic Year",
            width=160,
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.add_year
        ).grid(row=0, column=8, padx=(15, 5), pady=5)

        # -------------------------------------------------------------
        # Table Section Card
        # -------------------------------------------------------------
        table_card = ctk.CTkFrame(
            main,
            fg_color=self.colors["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["card_border"]
        )
        table_card.pack(fill="both", expand=True)

        # Actions Toolbar Inside Table Card
        toolbar = ctk.CTkFrame(table_card, fg_color="transparent")
        toolbar.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            toolbar,
            text="Academic Years List",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(side="left")

        btn_box = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_box.pack(side="right")

        ctk.CTkButton(
            btn_box,
            text="Activate Selected",
            height=34,
            corner_radius=6,
            fg_color=self.colors["success"],
            hover_color=self.colors["success_hover"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._activate_selected_row
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_box,
            text="Edit Selected",
            height=34,
            corner_radius=6,
            fg_color=self.colors["neutral_btn"],
            hover_color=self.colors["neutral_hover"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._edit_selected_row
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_box,
            text="Delete Selected",
            height=34,
            corner_radius=6,
            fg_color=self.colors["danger"],
            hover_color=self.colors["danger_hover"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self._delete_selected_row
        ).pack(side="left", padx=2)

        # Treeview Wrapper
        self.table_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Custom Styled Treeview Table
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "AcadYear.Treeview",
            background=theme.c("table_bg"),
            foreground=theme.c("table_fg"),
            fieldbackground=theme.c("table_bg"),
            rowheight=36,
            font=("Segoe UI", 10),
            borderwidth=0
        )
        style.configure(
            "AcadYear.Treeview.Heading",
            background=theme.c("table_head_bg"),
            foreground=theme.c("table_head_fg"),
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=6
        )
        style.map(
            "AcadYear.Treeview",
            background=[("selected", theme.c("table_selected"))],
            foreground=[("selected", theme.c("table_selected_fg"))]
        )
        style.map(
            "AcadYear.Treeview.Heading",
            background=[("active", theme.c("table_head_active"))]
        )

        columns = ("id", "year", "semester", "start_date", "end_date", "status")
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", style="AcadYear.Treeview",
                                 selectmode="browse")

        headings = {
            "id": ("ID", 70),
            "year": ("Year", 110),
            "semester": ("Semester", 110),
            "start_date": ("Start Date", 140),
            "end_date": ("End Date", 140),
            "status": ("Status", 110)
        }

        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text, anchor="w")
            self.tree.column(col, width=width, minwidth=width, stretch=True, anchor="w")

        scrollbar = ctk.CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # -------------------------------------------------------------
    # Business Logic & Database Actions
    # -------------------------------------------------------------
    def add_year(self):
        year = self.year_entry.get().strip()
        semester = self.semester_combo.get()
        start_date = self.start_entry.get().strip() or None
        end_date = self.end_entry.get().strip() or None

        if not year:
            messagebox.showerror("Validation Error", "Year is required.")
            return

        conn = self.db.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO academic_years (year, semester, start_date, end_date) VALUES (?,?,?,?)",
                (year, int(semester), start_date, end_date)
            )
            conn.commit()
            messagebox.showinfo("Success", f"Academic year '{year}' Semester {semester} added successfully.")
            self.start_entry.delete(0, "end")
            self.end_entry.delete(0, "end")
            self.load_years()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            conn.close()

    def load_years(self):
        self.tree.delete(*self.tree.get_children())

        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM academic_years ORDER BY year DESC, semester DESC")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            is_active = row.get("is_active")
            status_text = "● Active" if is_active else "○ Inactive"

            self.tree.insert("", "end", iid=str(row["id"]), values=(
                str(row["id"]),
                row["year"],
                f"Semester {row['semester']}",
                row.get("start_date") or "—",
                row.get("end_date") or "—",
                status_text
            ))

    def _get_selected_year_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select an academic year from the table.")
            return None
        return int(sel[0])

    def _edit_selected_row(self):
        year_id = self._get_selected_year_id()
        if year_id:
            self.edit_year(year_id)

    def _delete_selected_row(self):
        year_id = self._get_selected_year_id()
        if year_id:
            self.delete_year(year_id)

    def _activate_selected_row(self):
        year_id = self._get_selected_year_id()
        if year_id:
            self.activate_year(year_id)

    def edit_year(self, year_id):
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM academic_years WHERE id=?", (year_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Academic Year #{year_id}")
        dialog.geometry("420x260")
        dialog.configure(fg_color=self.colors["bg_dark"])
        dialog.transient(self)
        dialog.after(100, dialog.grab_set)

        card = ctk.CTkFrame(dialog, fg_color=self.colors["card_bg"], corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            card,
            text="Edit Academic Year Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_main"]
        ).pack(pady=(15, 10))

        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(pady=5, padx=10)

        def add_lbl(text, row_idx, col_idx):
            lbl = ctk.CTkLabel(f, text=text, font=ctk.CTkFont(size=12, weight="bold"),
                               text_color=self.colors["text_muted"])
            lbl.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="e")

        add_lbl("Year:", 0, 0)
        year_e = ctk.CTkEntry(f, width=110, height=34, corner_radius=6)
        year_e.insert(0, row["year"])
        year_e.grid(row=0, column=1, padx=5, pady=5)

        add_lbl("Semester:", 0, 2)
        sem_e = ctk.CTkComboBox(f, values=["1", "2", "3"], width=90, height=34, corner_radius=6)
        sem_e.set(str(row["semester"]))
        sem_e.grid(row=0, column=3, padx=5, pady=5)

        add_lbl("Start Date:", 1, 0)
        start_e = ctk.CTkEntry(f, width=110, height=34, corner_radius=6, placeholder_text="YYYY-MM-DD")
        start_e.insert(0, row.get("start_date") or "")
        start_e.grid(row=1, column=1, padx=5, pady=5)

        add_lbl("End Date:", 1, 2)
        end_e = ctk.CTkEntry(f, width=110, height=34, corner_radius=6, placeholder_text="YYYY-MM-DD")
        end_e.insert(0, row.get("end_date") or "")
        end_e.grid(row=1, column=3, padx=5, pady=5)

        def save():
            conn2 = self.db.get_conn()
            cur = conn2.cursor()
            cur.execute(
                "UPDATE academic_years SET year=?, semester=?, start_date=?, end_date=? WHERE id=?",
                (year_e.get().strip(), int(sem_e.get()), start_e.get().strip() or None, end_e.get().strip() or None,
                 year_id)
            )
            conn2.commit()
            conn2.close()
            messagebox.showinfo("Success", "Academic year details updated successfully.")
            dialog.destroy()
            self.load_years()

        ctk.CTkButton(
            card,
            text="Save Changes",
            command=save,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            height=36,
            corner_radius=8
        ).pack(fill="x", padx=25, pady=(15, 10))

    def delete_year(self, year_id):
        if messagebox.askyesno("Confirm Action", "Are you sure you want to delete this academic year?"):
            conn = self.db.get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM academic_years WHERE id=?", (year_id,))
            conn.commit()
            conn.close()
            self.load_years()

    def activate_year(self, year_id):
        conn = self.db.get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE academic_years SET is_active=0")
        cursor.execute("UPDATE academic_years SET is_active=1 WHERE id=?", (year_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Academic year set as Active term.")
        self.load_years()