from database.db_manager import DatabaseManager
from datetime import datetime

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

print("\nDone! Sample data added successfully.")
