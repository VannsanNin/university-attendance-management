import customtkinter as ctk
from tkinter import messagebox
import os
import pickle

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import face_recognition
    FR_AVAILABLE = True
except ImportError:
    FR_AVAILABLE = False


class FaceRecognitionView(ctk.CTkFrame):
    def __init__(self, db, parent):
        super().__init__(parent)
        self.db = db
        self.pack(fill="both", expand=True)

        avail = []
        if not CV2_AVAILABLE:
            avail.append("OpenCV not installed (pip install opencv-python)")
        if not FR_AVAILABLE:
            avail.append("face_recognition not installed (pip install face_recognition)")

        if avail:
            ctk.CTkLabel(self, text="Face Recognition Module",
                         font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
            for msg in avail:
                ctk.CTkLabel(self, text=msg, text_color="red",
                             font=ctk.CTkFont(size=14)).pack(pady=5)
            ctk.CTkLabel(self, text="Install missing packages to use this feature",
                         font=ctk.CTkFont(size=12)).pack(pady=10)
            return

        ctk.CTkLabel(self, text="Face Recognition Attendance",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=40, pady=10)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right = ctk.CTkFrame(main)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        ctk.CTkLabel(left, text="Register Face",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkLabel(left, text="Student ID:").pack()
        self.student_id_entry = ctk.CTkEntry(left, width=250)
        self.student_id_entry.pack(pady=5)
        self.status_label = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=5)
        ctk.CTkButton(left, text="Register Face from Camera",
                      command=self.register_face).pack(pady=5)
        ctk.CTkButton(left, text="List Registered Faces",
                      command=self.list_faces).pack(pady=5)

        ctk.CTkLabel(right, text="Mark Attendance",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkLabel(right, text="Course:").pack()
        self.course_combo = ctk.CTkComboBox(right, width=250, values=[""])
        self.course_combo.pack(pady=5)
        self.load_courses()
        ctk.CTkButton(right, text="Start Face Recognition",
                      command=self.start_recognition,
                      fg_color="#2E8B57").pack(pady=10)

        self.log_frame = ctk.CTkScrollableFrame(self)
        self.log_frame.pack(fill="both", expand=True, padx=40, pady=10)
        ctk.CTkLabel(self.log_frame, text="Log:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w")

    def load_courses(self):
        courses = self.db.get_courses()
        self.course_combo.configure(values=[f"{c['course_code']} - {c['course_name']}" for c in courses])

    def log(self, msg):
        ctk.CTkLabel(self.log_frame, text=msg, anchor="w").pack(fill="x")

    def register_face(self):
        sid = self.student_id_entry.get().strip()
        if not sid:
            messagebox.showerror("Error", "Enter student ID")
            return

        students = self.db.get_students(search=sid)
        if not students:
            messagebox.showerror("Error", "Student not found")
            return
        student = students[0]

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot access camera")
            return

        self.status_label.configure(text="Look at camera... Press SPACE to capture, ESC to cancel")
        face_encoding = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            face_locs = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, face_locs)

            for (top, right, bottom, left), enc in zip(face_locs, encodings):
                top *= 4; right *= 4; bottom *= 4; left *= 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, "Press SPACE to capture", (left, top-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            cv2.imshow("Register Face", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            if key == 32 and encodings:
                face_encoding = encodings[0]
                break

        cap.release()
        cv2.destroyAllWindows()

        if face_encoding is not None:
            self.db.save_face_encoding(student["id"], face_encoding)
            self.status_label.configure(text=f"Face registered for {student['full_name']}",
                                        text_color="#2E8B57")
            self.log(f"Registered: {student['full_name']} ({student['student_id']})")
        else:
            self.status_label.configure(text="Registration cancelled", text_color="red")

    def list_faces(self):
        for w in self.log_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.log_frame, text="Registered Faces:",
                     font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        faces = self.db.get_face_encodings()
        if not faces:
            ctk.CTkLabel(self.log_frame, text="No faces registered").pack()
            return
        for f in faces:
            r = ctk.CTkFrame(self.log_frame)
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=f"{f['student_id']} - {f['full_name']}",
                         anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(r, text="Delete", width=60, fg_color="red",
                          command=lambda sid=f["student_id"]: self.delete_face(sid)).pack(side="right")

    def delete_face(self, student_id):
        if messagebox.askyesno("Confirm", "Delete face data?"):
            self.db.delete_face_encoding(student_id)
            self.list_faces()

    def start_recognition(self):
        course_str = self.course_combo.get()
        if not course_str:
            messagebox.showerror("Error", "Select a course")
            return
        course_code = course_str.split(" - ")[0]
        course_id = None
        for c in self.db.get_courses():
            if c["course_code"] == course_code:
                course_id = c["id"]
                break

        known_faces = self.db.get_face_encodings()
        if not known_faces:
            messagebox.showinfo("Info", "No registered faces. Register faces first.")
            return

        known_encodings = [f["encoding"] for f in known_faces]
        known_ids = [f["student_id"] for f in known_faces]
        known_names = [f["full_name"] for f in known_faces]

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot access camera")
            return

        marked = set()
        from datetime import date as dt_date

        self.log("Starting face recognition...")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            small = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            face_locs = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, face_locs)

            for (top, right, bottom, left), face_enc in zip(face_locs, encodings):
                top *= 4; right *= 4; bottom *= 4; left *= 4
                matches = face_recognition.compare_faces(known_encodings, face_enc, tolerance=0.5)
                name = "Unknown"
                color = (0, 0, 255)

                if any(matches):
                    idx = matches.index(True)
                    student_id = known_ids[idx]
                    name = known_names[idx]

                    if student_id not in marked:
                        students = self.db.get_students(search=student_id)
                        if students:
                            self.db.take_attendance(
                                students[0]["id"], course_id,
                                dt_date.today().isoformat(), "Present"
                            )
                            marked.add(student_id)
                            self.log(f"Marked: {name} ({student_id}) - Present")
                    color = (0, 255, 0)

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            cv2.putText(frame, f"Marked: {len(marked)} | ESC to quit", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.imshow("Face Recognition Attendance", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        self.log(f"Session ended. {len(marked)} students marked.")
        messagebox.showinfo("Done", f"Attendance marked for {len(marked)} students")
