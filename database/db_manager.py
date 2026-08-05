import sqlite3
import os
import pickle
import bcrypt
from datetime import datetime, date
from threading import Timer

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uams.db")

class DatabaseManager:
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH
        self.init_database()

    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_database(self):
        conn = self.get_conn()
        cursor = conn.cursor()

        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                code TEXT UNIQUE,
                faculty TEXT,
                head_of_department TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','teacher','student')),
                email TEXT,
                phone TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                gender TEXT CHECK(gender IN ('Male','Female','Other')),
                dob DATE,
                nationality TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                department_id INTEGER,
                program TEXT,
                year INTEGER,
                semester INTEGER,
                class_name TEXT,
                photo_path TEXT,
                guardian_name TEXT,
                guardian_phone TEXT,
                emergency_contact TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id TEXT NOT NULL UNIQUE,
                full_name TEXT NOT NULL,
                gender TEXT CHECK(gender IN ('Male','Female','Other')),
                dob DATE,
                email TEXT,
                phone TEXT,
                address TEXT,
                department_id INTEGER,
                position TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT NOT NULL UNIQUE,
                course_name TEXT NOT NULL,
                teacher_id INTEGER,
                semester INTEGER,
                credit INTEGER,
                department_id INTEGER,
                academic_year TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id),
                FOREIGN KEY (department_id) REFERENCES departments(id)
            );

            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL,
                department_id INTEGER,
                teacher_id INTEGER,
                academic_year TEXT,
                semester INTEGER,
                advisor TEXT,
                room TEXT,
                schedule TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (department_id) REFERENCES departments(id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            );

            CREATE TABLE IF NOT EXISTS class_students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                UNIQUE(class_id, student_id)
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                class_id INTEGER,
                attendance_date DATE NOT NULL,
                attendance_time TIME,
                status TEXT NOT NULL CHECK(status IN ('Present','Absent','Late','Permission','Excused')),
                taken_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (course_id) REFERENCES courses(id),
                FOREIGN KEY (class_id) REFERENCES classes(id),
                FOREIGN KEY (taken_by) REFERENCES users(id),
                UNIQUE(student_id, course_id, attendance_date)
            );

            CREATE TABLE IF NOT EXISTS face_encodings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL UNIQUE,
                encoding BLOB,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                type TEXT CHECK(type IN ('email','sms','warning')),
                message TEXT,
                sent_date DATE,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id)
            );

            CREATE TABLE IF NOT EXISTS academic_years (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT NOT NULL,
                semester INTEGER NOT NULL,
                start_date DATE,
                end_date DATE,
                is_active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS backup_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # ── Migrate old tables: add missing columns ──
        for stmt in [
            "ALTER TABLE users ADD COLUMN phone TEXT",
            "ALTER TABLE departments ADD COLUMN faculty TEXT",
            "ALTER TABLE departments ADD COLUMN head_of_department TEXT",
            "ALTER TABLE departments ADD COLUMN description TEXT",
            "ALTER TABLE students ADD COLUMN first_name TEXT",
            "ALTER TABLE students ADD COLUMN last_name TEXT",
            "ALTER TABLE students ADD COLUMN nationality TEXT",
            "ALTER TABLE students ADD COLUMN program TEXT",
            "ALTER TABLE students ADD COLUMN semester INTEGER",
            "ALTER TABLE students ADD COLUMN guardian_name TEXT",
            "ALTER TABLE students ADD COLUMN guardian_phone TEXT",
            "ALTER TABLE students ADD COLUMN emergency_contact TEXT",
            "ALTER TABLE teachers ADD COLUMN gender TEXT",
            "ALTER TABLE teachers ADD COLUMN dob DATE",
            "ALTER TABLE teachers ADD COLUMN address TEXT",
            "ALTER TABLE teachers ADD COLUMN position TEXT",
            "ALTER TABLE courses ADD COLUMN academic_year TEXT",
            "ALTER TABLE classes ADD COLUMN academic_year TEXT",
            "ALTER TABLE classes ADD COLUMN semester INTEGER",
            "ALTER TABLE classes ADD COLUMN advisor TEXT",
            "ALTER TABLE classes ADD COLUMN room TEXT",
            "ALTER TABLE classes ADD COLUMN schedule TEXT",
            "ALTER TABLE attendance ADD COLUMN attendance_time TIME",
        ]:
            try:
                cursor.execute(stmt)
            except:
                pass

        # ── Migrate attendance CHECK to include Excused ──
        try:
            cursor.execute("INSERT INTO attendance (student_id, course_id, attendance_date, status) VALUES (0, 0, '2000-01-01', 'Excused')")
            cursor.execute("DELETE FROM attendance WHERE student_id=0 AND course_id=0")
            conn.commit()
        except:
            cursor.execute("ALTER TABLE attendance RENAME TO attendance_old")
            cursor.execute('''CREATE TABLE attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                class_id INTEGER,
                attendance_date DATE NOT NULL,
                attendance_time TIME,
                status TEXT NOT NULL CHECK(status IN ('Present','Absent','Late','Permission','Excused')),
                taken_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (course_id) REFERENCES courses(id),
                FOREIGN KEY (class_id) REFERENCES classes(id),
                FOREIGN KEY (taken_by) REFERENCES users(id),
                UNIQUE(student_id, course_id, attendance_date)
            )''')
            cursor.execute("""INSERT INTO attendance (id, student_id, course_id, class_id, attendance_date, status, taken_by, created_at)
                SELECT id, student_id, course_id, class_id, attendance_date, status, taken_by, created_at FROM attendance_old""")
            cursor.execute("DROP TABLE attendance_old")
            conn.commit()

        cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
        if cursor.fetchone()[0] == 0:
            admin_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, email) VALUES (?,?,?,?)",
                ("admin", admin_hash, "admin", "admin@uams.edu")
            )

        default_settings = [
            ("university_name", "University"),
            ("academic_year", str(datetime.now().year)),
            ("semester", "1"),
            ("theme", "Dark"),
            ("language", "English"),
            ("auto_backup", "0"),
            ("low_attendance_warning", "70"),
            ("smtp_server", ""),
            ("smtp_port", "587"),
            ("smtp_email", ""),
            ("smtp_password", ""),
            ("sms_api_key", ""),
        ]
        for key, value in default_settings:
            cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", (key, value))

        conn.commit()
        conn.close()

    # ---- Connection tracking ----
    def close_all_connections(self):
        if hasattr(self, '_conn') and self._conn:
            try:
                self._conn.close()
            except:
                pass
            self._conn = None

    # ---- Auth ----
    def authenticate(self, username, password):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND is_active=1", (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
            cursor.execute("UPDATE users SET last_login=? WHERE id=?", (datetime.now().isoformat(), user["id"]))
            conn.commit()
            conn.close()
            return dict(user)
        conn.close()
        return None

    def change_password(self, user_id, old_password, new_password):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        if row and bcrypt.checkpw(old_password.encode(), row["password_hash"].encode()):
            new_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            cursor.execute("UPDATE users SET password_hash=? WHERE id=?", (new_hash, user_id))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    def create_user(self, username, password, role, email=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, email) VALUES (?,?,?,?)",
                (username, pw_hash, role, email)
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_users(self, role=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        if role:
            cursor.execute("SELECT * FROM users WHERE role=?", (role,))
        else:
            cursor.execute("SELECT * FROM users ORDER BY role, username")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users

    def update_user(self, user_id, **kwargs):
        conn = self.get_conn()
        cursor = conn.cursor()
        allowed = {"username", "email", "is_active", "role"}
        for key, value in kwargs.items():
            if key in allowed:
                cursor.execute(f"UPDATE users SET {key}=? WHERE id=?", (value, user_id))
        conn.commit()
        conn.close()

    def delete_user(self, user_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=? AND role!='admin'", (user_id,))
        conn.commit()
        conn.close()

    # ---- Departments ----
    def add_department(self, name, code=None, faculty=None, head_of_department=None, description=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO departments (name, code, faculty, head_of_department, description)
                VALUES (?,?,?,?,?)""", (name, code, faculty, head_of_department, description))
            conn.commit()
            dept_id = cursor.lastrowid
            conn.close()
            return dept_id
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_departments(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departments ORDER BY name")
        depts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return depts

    def update_department(self, dept_id, name=None, code=None, faculty=None, head_of_department=None, description=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        if name is not None:
            cursor.execute("UPDATE departments SET name=? WHERE id=?", (name, dept_id))
        if code is not None:
            cursor.execute("UPDATE departments SET code=? WHERE id=?", (code, dept_id))
        if faculty is not None:
            cursor.execute("UPDATE departments SET faculty=? WHERE id=?", (faculty, dept_id))
        if head_of_department is not None:
            cursor.execute("UPDATE departments SET head_of_department=? WHERE id=?", (head_of_department, dept_id))
        if description is not None:
            cursor.execute("UPDATE departments SET description=? WHERE id=?", (description, dept_id))
        conn.commit()
        conn.close()

    def delete_department(self, dept_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM departments WHERE id=?", (dept_id,))
        conn.commit()
        conn.close()

    # ---- Students ----
    def add_student(self, student_id, full_name, gender=None, dob=None, phone=None,
                    email=None, address=None, department_id=None, year=None,
                    class_name=None, photo_path=None, first_name=None, last_name=None,
                    nationality=None, program=None, semester=None,
                    guardian_name=None, guardian_phone=None, emergency_contact=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO students 
                (student_id, full_name, first_name, last_name, gender, dob, nationality,
                 phone, email, address, department_id, program, year, semester,
                 class_name, photo_path, guardian_name, guardian_phone, emergency_contact)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (student_id, full_name, first_name, last_name, gender, dob, nationality,
                 phone, email, address, department_id, program, year, semester,
                 class_name, photo_path, guardian_name, guardian_phone, emergency_contact))
            conn.commit()
            sid = cursor.lastrowid
            conn.close()
            return sid
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_students(self, search=None, department_id=None, class_name=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        query = """SELECT s.*, d.name as department_name FROM students s
                   LEFT JOIN departments d ON s.department_id = d.id"""
        conditions = []
        params = []
        if search:
            conditions.append("(s.student_id LIKE ? OR s.full_name LIKE ? OR s.phone LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if department_id:
            conditions.append("s.department_id=?")
            params.append(department_id)
        if class_name:
            conditions.append("s.class_name=?")
            params.append(class_name)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY s.student_id"
        cursor.execute(query, params)
        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return students

    def get_student(self, student_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT s.*, d.name as department_name FROM students s
            LEFT JOIN departments d ON s.department_id = d.id WHERE s.id=?""", (student_id,))
        student = cursor.fetchone()
        conn.close()
        return dict(student) if student else None

    def update_student(self, sid, **kwargs):
        conn = self.get_conn()
        cursor = conn.cursor()
        allowed = {"student_id","full_name","first_name","last_name","gender","dob","nationality","phone","email","address","department_id","program","year","semester","class_name","photo_path","guardian_name","guardian_phone","emergency_contact"}
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                cursor.execute(f"UPDATE students SET {key}=? WHERE id=?", (value, sid))
        conn.commit()
        conn.close()

    def delete_student(self, sid):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id=?", (sid,))
        conn.commit()
        conn.close()

    def get_student_count(self):
        conn = self.get_conn()
        row = conn.execute("SELECT COUNT(*) as cnt FROM students").fetchone()
        conn.close()
        return row["cnt"]

    # ---- Teachers ----
    def add_teacher(self, teacher_id, full_name, email=None, phone=None, department_id=None,
                    gender=None, dob=None, address=None, position=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO teachers (teacher_id, full_name, email, phone, department_id, gender, dob, address, position)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (teacher_id, full_name, email, phone, department_id, gender, dob, address, position))
            conn.commit()
            tid = cursor.lastrowid
            conn.close()
            return tid
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_teachers(self, search=None, department_id=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        query = """SELECT t.*, d.name as department_name FROM teachers t
                   LEFT JOIN departments d ON t.department_id = d.id"""
        conditions = []
        params = []
        if search:
            conditions.append("(t.teacher_id LIKE ? OR t.full_name LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if department_id:
            conditions.append("t.department_id=?")
            params.append(department_id)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY t.teacher_id"
        cursor.execute(query, params)
        teachers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return teachers

    def get_teacher(self, teacher_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT t.*, d.name as department_name FROM teachers t
            LEFT JOIN departments d ON t.department_id = d.id WHERE t.id=?""", (teacher_id,))
        teacher = cursor.fetchone()
        conn.close()
        return dict(teacher) if teacher else None

    def update_teacher(self, tid, **kwargs):
        conn = self.get_conn()
        cursor = conn.cursor()
        allowed = {"teacher_id","full_name","email","phone","department_id","gender","dob","address","position"}
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                cursor.execute(f"UPDATE teachers SET {key}=? WHERE id=?", (value, tid))
        conn.commit()
        conn.close()

    def delete_teacher(self, tid):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teachers WHERE id=?", (tid,))
        conn.commit()
        conn.close()

    def get_teacher_count(self):
        conn = self.get_conn()
        row = conn.execute("SELECT COUNT(*) as cnt FROM teachers").fetchone()
        conn.close()
        return row["cnt"]

    # ---- Courses ----
    def add_course(self, course_code, course_name, teacher_id=None, semester=None, credit=None, department_id=None,
                   academic_year=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO courses (course_code, course_name, teacher_id, semester, credit, department_id, academic_year)
                VALUES (?,?,?,?,?,?,?)""",
                (course_code, course_name, teacher_id, semester, credit, department_id, academic_year))
            conn.commit()
            cid = cursor.lastrowid
            conn.close()
            return cid
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_courses(self, search=None, department_id=None, teacher_id=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        query = """SELECT c.*, t.full_name as teacher_name, d.name as department_name
                   FROM courses c
                   LEFT JOIN teachers t ON c.teacher_id = t.id
                   LEFT JOIN departments d ON c.department_id = d.id"""
        conditions = []
        params = []
        if search:
            conditions.append("(c.course_code LIKE ? OR c.course_name LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
        if department_id:
            conditions.append("c.department_id=?")
            params.append(department_id)
        if teacher_id:
            conditions.append("c.teacher_id=?")
            params.append(teacher_id)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY c.course_code"
        cursor.execute(query, params)
        courses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return courses

    def update_course(self, cid, **kwargs):
        conn = self.get_conn()
        cursor = conn.cursor()
        allowed = {"course_code","course_name","teacher_id","semester","credit","department_id","academic_year"}
        for key, value in kwargs.items():
            if key in allowed and value is not None:
                cursor.execute(f"UPDATE courses SET {key}=? WHERE id=?", (value, cid))
        conn.commit()
        conn.close()

    def delete_course(self, cid):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM courses WHERE id=?", (cid,))
        conn.commit()
        conn.close()

    # ---- Classes ----
    def add_class(self, class_name, department_id=None, teacher_id=None, advisor=None, room=None,
                  schedule=None, academic_year=None, semester=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT INTO classes (class_name, department_id, teacher_id, advisor, room, schedule, academic_year, semester)
                VALUES (?,?,?,?,?,?,?,?)""",
                (class_name, department_id, teacher_id, advisor, room, schedule, academic_year, semester))
            conn.commit()
            cid = cursor.lastrowid
            conn.close()
            return cid
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_classes(self, department_id=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        query = """SELECT cl.*, d.name as department_name, t.full_name as teacher_name
                   FROM classes cl
                   LEFT JOIN departments d ON cl.department_id = d.id
                   LEFT JOIN teachers t ON cl.teacher_id = t.id"""
        params = []
        if department_id:
            query += " WHERE cl.department_id=?"
            params.append(department_id)
        query += " ORDER BY cl.class_name"
        cursor.execute(query, params)
        classes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return classes

    def update_class(self, cid, **kwargs):
        conn = self.get_conn()
        cursor = conn.cursor()
        allowed = {"class_name","department_id","teacher_id","advisor","room","schedule","academic_year","semester"}
        for key, value in kwargs.items():
            if key in allowed:
                cursor.execute(f"UPDATE classes SET {key}=? WHERE id=?", (value, cid))
        conn.commit()
        conn.close()

    def delete_class(self, cid):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM classes WHERE id=?", (cid,))
        conn.commit()
        conn.close()

    # ---- Class Students ----
    def add_student_to_class(self, class_id, student_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO class_students (class_id, student_id) VALUES (?,?)", (class_id, student_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def remove_student_from_class(self, class_id, student_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM class_students WHERE class_id=? AND student_id=?", (class_id, student_id))
        conn.commit()
        conn.close()

    def get_class_students(self, class_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT s.* FROM students s
            JOIN class_students cs ON s.id = cs.student_id
            WHERE cs.class_id=? ORDER BY s.student_id""", (class_id,))
        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return students

    def get_student_classes(self, student_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT cl.* FROM classes cl
            JOIN class_students cs ON cl.id = cs.class_id
            WHERE cs.student_id=?""", (student_id,))
        classes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return classes

    # ---- Attendance ----
    def take_attendance(self, student_id, course_id, attendance_date, status, taken_by=None, class_id=None, attendance_time=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("""INSERT OR REPLACE INTO attendance 
                (student_id, course_id, class_id, attendance_date, attendance_time, status, taken_by)
                VALUES (?,?,?,?,?,?,?)""",
                (student_id, course_id, class_id, attendance_date, attendance_time, status, taken_by))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False

    def get_attendance(self, student_id=None, course_id=None, class_id=None, 
                       start_date=None, end_date=None, status=None, attendance_date=None,
                       limit=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        query = """SELECT a.*, s.full_name as student_name, s.student_id as sid,
                   c.course_name, c.course_code
                   FROM attendance a
                   JOIN students s ON a.student_id = s.id
                   JOIN courses c ON a.course_id = c.id"""
        conditions = []
        params = []
        if student_id:
            conditions.append("a.student_id=?")
            params.append(student_id)
        if course_id:
            conditions.append("a.course_id=?")
            params.append(course_id)
        if class_id:
            conditions.append("a.class_id=?")
            params.append(class_id)
        if start_date:
            conditions.append("a.attendance_date>=?")
            params.append(start_date)
        if end_date:
            conditions.append("a.attendance_date<=?")
            params.append(end_date)
        if status:
            conditions.append("a.status=?")
            params.append(status)
        if attendance_date:
            conditions.append("a.attendance_date=?")
            params.append(attendance_date)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY a.attendance_date DESC, s.student_id"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        cursor.execute(query, params)
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return records

    def update_attendance(self, att_id, status):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE attendance SET status=? WHERE id=?", (status, att_id))
        conn.commit()
        conn.close()

    def delete_attendance(self, att_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM attendance WHERE id=?", (att_id,))
        conn.commit()
        conn.close()

    def get_attendance_summary(self, student_id=None, course_id=None, class_id=None,
                               start_date=None, end_date=None, month=None, year=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        conditions = []
        params = []
        if student_id:
            conditions.append("a.student_id=?")
            params.append(student_id)
        if course_id:
            conditions.append("a.course_id=?")
            params.append(course_id)
        if class_id:
            conditions.append("a.class_id=?")
            params.append(class_id)
        if start_date:
            conditions.append("a.attendance_date>=?")
            params.append(start_date)
        if end_date:
            conditions.append("a.attendance_date<=?")
            params.append(end_date)
        where = " AND ".join(conditions) if conditions else "1=1"
        query = f"""SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present_count,
            SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) as absent_count,
            SUM(CASE WHEN a.status='Late' THEN 1 ELSE 0 END) as late_count,
            SUM(CASE WHEN a.status='Permission' THEN 1 ELSE 0 END) as permission_count,
            SUM(CASE WHEN a.status='Excused' THEN 1 ELSE 0 END) as excused_count
            FROM attendance a WHERE {where}"""
        cursor.execute(query, params)
        summary = dict(cursor.fetchone())
        conn.close()
        if summary["total"] and summary["total"] > 0:
            summary["percentage"] = round((summary["present_count"] + summary["late_count"] + summary["permission_count"] + summary.get("excused_count", 0)) / summary["total"] * 100, 1)
        else:
            summary["percentage"] = 0.0
        return summary

    def get_today_attendance_stats(self, course_id=None, attendance_date=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        date_str = attendance_date or date.today().isoformat()
        conditions = ["a.attendance_date=?"]
        params = [date_str]
        if course_id:
            conditions.append("a.course_id=?")
            params.append(course_id)
        where = " AND ".join(conditions)
        cursor.execute(f"""SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) as present,
            SUM(CASE WHEN a.status='Absent' THEN 1 ELSE 0 END) as absent,
            SUM(CASE WHEN a.status='Late' THEN 1 ELSE 0 END) as late,
            SUM(CASE WHEN a.status='Permission' THEN 1 ELSE 0 END) as permission,
            SUM(CASE WHEN a.status='Excused' THEN 1 ELSE 0 END) as excused
            FROM attendance a WHERE {where}""", params)
        stats = dict(cursor.fetchone())
        conn.close()
        return {k: (v or 0) for k, v in stats.items()}

    # ---- Face Recognition ----
    def save_face_encoding(self, student_id, encoding):
        conn = self.get_conn()
        cursor = conn.cursor()
        blob = pickle.dumps(encoding)
        cursor.execute("""INSERT OR REPLACE INTO face_encodings (student_id, encoding)
            VALUES (?,?)""", (student_id, blob))
        conn.commit()
        conn.close()

    def get_face_encodings(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT fe.*, s.student_id, s.full_name FROM face_encodings fe
            JOIN students s ON fe.student_id = s.id""")
        rows = cursor.fetchall()
        conn.close()
        result = []
        for row in rows:
            d = dict(row)
            d["encoding"] = pickle.loads(row["encoding"])
            result.append(d)
        return result

    def delete_face_encoding(self, student_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM face_encodings WHERE student_id=?", (student_id,))
        conn.commit()
        conn.close()

    # ---- Notifications ----
    def add_notification(self, student_id, type_, message):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO notifications (student_id, type, message, sent_date)
            VALUES (?,?,?,?)""", (student_id, type_, message, date.today().isoformat()))
        conn.commit()
        nid = cursor.lastrowid
        conn.close()
        return nid

    def get_notifications(self, student_id=None, status=None):
        conn = self.get_conn()
        cursor = conn.cursor()
        query = """SELECT n.*, s.full_name as student_name FROM notifications n
                   LEFT JOIN students s ON n.student_id = s.id"""
        conditions = []
        params = []
        if student_id:
            conditions.append("n.student_id=?")
            params.append(student_id)
        if status:
            conditions.append("n.status=?")
            params.append(status)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY n.created_at DESC"
        cursor.execute(query, params)
        notifs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return notifs

    # ---- Settings ----
    def get_setting(self, key):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row["value"] if row else None

    def set_setting(self, key, value):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
        conn.commit()
        conn.close()

    def get_all_settings(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM settings")
        settings = {row["key"]: row["value"] for row in cursor.fetchall()}
        conn.close()
        return settings

    # ---- Backup ----
    def backup_database(self, backup_path):
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
            conn = self.get_conn()
            conn.execute("INSERT INTO backup_log (file_path) VALUES (?)", (backup_path,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return str(e)

    def restore_database(self, backup_path):
        import shutil
        try:
            if not os.path.exists(backup_path):
                return "Backup file not found"
            self.close_all_connections()
            shutil.copy2(backup_path, self.db_path)
            return True
        except Exception as e:
            return str(e)

    def get_backup_logs(self):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backup_log ORDER BY created_at DESC")
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

    def update_user_password(self, user_id, new_password):
        conn = self.get_conn()
        cursor = conn.cursor()
        pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("UPDATE users SET password_hash=? WHERE id=?", (pw_hash, user_id))
        conn.commit()
        conn.close()
        return True

    def get_user_by_username(self, username):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def get_user(self, user_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def link_student_user(self, student_id, user_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET user_id=? WHERE id=?", (user_id, student_id))
        conn.commit()
        conn.close()

    def link_teacher_user(self, teacher_id, user_id):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE teachers SET user_id=? WHERE id=?", (user_id, teacher_id))
        conn.commit()
        conn.close()

    def generate_low_attendance_notifications(self, threshold=70):
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.full_name, s.student_id,
                   COUNT(*) as total,
                   SUM(CASE WHEN a.status='Present' OR a.status='Late' OR a.status='Permission' THEN 1 ELSE 0 END) as attended
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            GROUP BY s.id
            HAVING (attended * 100.0 / total) < ?
        """, (threshold,))
        low_attendance = [dict(r) for r in cursor.fetchall()]
        conn.close()
        notifs = []
        for s in low_attendance:
            pct = round(s["attended"] / s["total"] * 100, 1)
            msg = f"Low attendance warning: {s['full_name']} ({s['student_id']}) - {pct}%"
            nid = self.add_notification(s["id"], "warning", msg)
            notifs.append(nid)
        return notifs

    def close_all_connections(self):
        if hasattr(self, '_conn') and self._conn:
            try:
                self._conn.close()
            except:
                pass
            self._conn = None
