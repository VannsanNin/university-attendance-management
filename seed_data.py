from database.db_manager import DatabaseManager
from datetime import datetime, date, timedelta
import random

db = DatabaseManager()

# ── Departments ──
departments = [
    ("Computer Science", "CS"),
    ("Information Technology", "IT"),
    ("Software Engineering", "SE"),
    ("Data Science", "DS"),
    ("Cybersecurity", "CY"),
    ("Information Systems", "IS"),
]

for name, code in departments:
    dept_id = db.add_department(name, code)
    if dept_id:
        print(f"  Added department: {name} ({code})")
    else:
        print(f"  Skipped (exists): {name} ({code})")

# ── Teachers ──
teachers = [
    ("T001", "Dr. John Smith", "john.smith@uams.edu", "0123456789", 1),
    ("T002", "Prof. Jane Doe", "jane.doe@uams.edu", "0123456790", 2),
    ("T003", "Mr. Robert Brown", "robert.brown@uams.edu", "0123456791", 3),
    ("T004", "Dr. Emily Davis", "emily.davis@uams.edu", "0123456792", 4),
    ("T005", "Ms. Sarah Wilson", "sarah.wilson@uams.edu", "0123456793", 5),
    ("T006", "Dr. Michael Lee", "michael.lee@uams.edu", "0123456794", 6),
]

for tid, name, email, phone, dept_id in teachers:
    teacher_id = db.add_teacher(tid, name, email, phone, dept_id)
    if teacher_id:
        print(f"  Added teacher: {name} ({tid})")
    else:
        print(f"  Skipped (exists): {name} ({tid})")

# ── Courses ──
courses = [
    ("CS101",  "Introduction to Programming",    1, 1, 4, 1),
    ("CS201",  "Data Structures",                 1, 2, 3, 1),
    ("CS301",  "Algorithms",                      1, 3, 3, 1),
    ("CS401",  "Operating Systems",               1, 4, 3, 1),
    ("IT101",  "Database Systems",                2, 1, 3, 2),
    ("IT201",  "Networking Fundamentals",         2, 2, 3, 2),
    ("IT301",  "Web Development",                 2, 3, 3, 2),
    ("SE101",  "Software Engineering Principles", 3, 1, 3, 3),
    ("SE201",  "Project Management",              3, 2, 3, 3),
    ("DS101",  "Statistics for Data Science",     4, 1, 3, 4),
    ("DS201",  "Machine Learning",                4, 2, 4, 4),
    ("CY101",  "Network Security",                5, 1, 3, 5),
    ("CY201",  "Ethical Hacking",                 5, 2, 3, 5),
    ("IS101",  "Business Information Systems",    6, 1, 3, 6),
    ("IS201",  "E-Commerce",                      6, 2, 3, 6),
]

for code, name, teacher_id, sem, credit, dept_id in courses:
    course_id = db.add_course(code, name, teacher_id, sem, credit, dept_id)
    if course_id:
        print(f"  Added course: {name} ({code})")
    else:
        print(f"  Skipped (exists): {name} ({code})")

# ── Class schedules (only fills empty schedule/room for demo) ──
schedule_templates = [
    ("Mon/Wed/Fri 08:00-10:00", "Room 101"),
    ("Tue/Thu 10:00-12:00", "Room 102"),
    ("Mon/Wed 14:00-15:30", "Lab 1"),
    ("Tue/Thu 14:00-16:00", "Room 201"),
    ("Fri 09:00-11:00", "Room 202"),
    ("Sat 08:00-09:30", "Lab 2"),
]
for i, cl in enumerate(db.get_classes()):
    if not cl.get("schedule"):
        tmpl = schedule_templates[i % len(schedule_templates)]
        db.update_class(cl["id"], schedule=tmpl[0], room=tmpl[1])
        print(f"  Scheduled class: {cl['class_name']} -> {tmpl[0]} ({tmpl[1]})")

# ── Link user accounts to teacher / student profiles ──
teachers = db.get_teachers()
teacher_users = [u for u in db.get_users() if u["role"] == "teacher"]
for idx, u in enumerate(teacher_users):
    if idx < len(teachers) and not teachers[idx].get("user_id"):
        db.link_teacher_user(teachers[idx]["id"], u["id"])
        print(f"  Linked teacher: {teachers[idx]['full_name']} <-> {u['username']}")

linked = 0
for s in db.get_students():
    user = db.get_user_by_username(s["student_id"])
    if user and user["role"] == "student" and not s.get("user_id"):
        db.link_student_user(s["id"], user["id"])
        linked += 1
print(f"  Linked {linked} student accounts to profiles.")

# ── Attendance records (last 35 days for every enrolled student) ──
random.seed(42)


def seed_attendance(days_back=35):
    conn = db.get_conn()
    cursor = conn.cursor()
    classes = cursor.execute("SELECT id, department_id FROM classes").fetchall()
    courses = cursor.execute("SELECT id, department_id FROM courses").fetchall()
    course_by_dept = {}
    for c in courses:
        course_by_dept.setdefault(c["department_id"], []).append(c["id"])
    rows = cursor.execute("SELECT class_id, student_id FROM class_students").fetchall()
    class_students = [(r["class_id"], r["student_id"]) for r in rows]
    conn.close()

    # pick the course used for each class
    class_course = {}
    for cl in classes:
        dept_id = cl["department_id"]
        if dept_id in course_by_dept and course_by_dept[dept_id]:
            class_course[cl["id"]] = course_by_dept[dept_id][0]

    statuses = ["Present"] * 82 + ["Late"] * 6 + ["Absent"] * 8 + ["Permission"] * 4
    risk_statuses = ["Present"] * 55 + ["Late"] * 10 + ["Absent"] * 32 + ["Permission"] * 3
    today = date.today()
    start = today - timedelta(days=days_back)

    # designate a handful of students as "at risk" (low attendance demo)
    unique_students = sorted({sid for _, sid in class_students})
    at_risk = set(unique_students[::14])

    count = 0
    d = start
    while d <= today:
        # skip most weekends (keep one recent Saturday for demo data)
        if d.weekday() >= 5 and d != today:
            d += timedelta(days=1)
            continue
        date_str = d.isoformat()
        for class_id, student_id in class_students:
            course_id = class_course.get(class_id)
            if not course_id:
                continue
            pool = risk_statuses if student_id in at_risk else statuses
            status = random.choice(pool)
            time_str = f"{random.randint(7, 9):02d}:{random.randint(0, 59):02d}"
            if status == "Late":
                time_str = f"{random.randint(9, 10):02d}:{random.randint(0, 59):02d}"
            db.take_attendance(student_id, course_id, date_str, status,
                               taken_by=2, class_id=class_id,
                               attendance_time=time_str)
            count += 1
        d += timedelta(days=1)

    # ensure the linked teacher's own courses also have data for the demo
    linked_teacher_id = db.get_teacher_by_user_id(teacher_users[0]["id"])["id"] if teacher_users else None
    if linked_teacher_id:
        linked_courses = db.get_courses(teacher_id=linked_teacher_id)
        roster = sorted({sid for _, sid in class_students})[:40]
        d = start
        while d <= today:
            if d.weekday() >= 5 and d != today:
                d += timedelta(days=1)
                continue
            date_str = d.isoformat()
            for sid in roster:
                for course in linked_courses:
                    pool = risk_statuses if sid in at_risk else statuses
                    status = random.choice(pool)
                    time_str = f"{random.randint(7, 9):02d}:{random.randint(0, 59):02d}"
                    if status == "Late":
                        time_str = f"{random.randint(9, 10):02d}:{random.randint(0, 59):02d}"
                    db.take_attendance(sid, course["id"], date_str, status,
                                       taken_by=teacher_users[0]["id"],
                                       class_id=None, attendance_time=time_str)
                    count += 1
            d += timedelta(days=1)

    print(f"  Seeded {count} attendance records over {days_back} days ({len(at_risk)} at-risk students).")


seed_attendance()

print("\nDone! Sample data added successfully.")
