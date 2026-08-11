"""Backfill missing email / phone for all users, students and teachers.

- Generates a unique phone number for every user that has none.
- Sets email for any user missing one (username@university.edu pattern).
- Syncs the linked user's email/phone into the student / teacher profile.
"""
from database.db_manager import DatabaseManager

db = DatabaseManager()
conn = db.get_conn()
cur = conn.cursor()

# ---- collect existing phone numbers to guarantee uniqueness ----
used = set()
for table in ("users", "students", "teachers"):
    cur.execute(f"SELECT phone FROM {table} WHERE phone IS NOT NULL AND phone != ''")
    used.update(r[0] for r in cur.fetchall())

_next = 3456800


def next_phone():
    global _next
    while True:
        phone = f"012{_next:07d}"
        _next += 1
        if phone not in used:
            used.add(phone)
            return phone


updated_users = 0
for u in db.get_users():
    changes = {}
    if not u.get("phone"):
        changes["phone"] = next_phone()
    if not u.get("email"):
        changes["email"] = f"{u['username']}@university.edu"
    if changes:
        db.update_user(u["id"], **changes)
        updated_users += 1

updated_students = 0
for s in db.get_students():
    user = db.get_user(s["user_id"]) if s.get("user_id") else None
    changes = {}
    if not s.get("email"):
        changes["email"] = (user or {}).get("email") or f"{s['student_id'].lower()}@university.edu"
    if not s.get("phone"):
        changes["phone"] = (user or {}).get("phone") or next_phone()
    if changes:
        db.update_student(s["student_id"], **changes)
        updated_students += 1

updated_teachers = 0
for t in db.get_teachers():
    user = db.get_user(t["user_id"]) if t.get("user_id") else None
    changes = {}
    if not t.get("email"):
        changes["email"] = (user or {}).get("email") or f"{t['teacher_id'].lower()}@uams.edu"
    if not t.get("phone"):
        changes["phone"] = (user or {}).get("phone") or next_phone()
    if changes:
        db.update_teacher(t["teacher_id"], **changes)
        updated_teachers += 1

conn.close()
print(f"Updated {updated_users} users, {updated_students} students, {updated_teachers} teachers.")
