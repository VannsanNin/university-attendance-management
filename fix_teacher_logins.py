import sys

sys.path.insert(0, ".")

from database.db_manager import DatabaseManager

db = DatabaseManager()


def run():
    teachers = db.get_teachers()
    fixed = 0
    for t in teachers:
        tid = t["teacher_id"]
        uid = t["user_id"]
        email = t.get("email") or None

        if uid:
            u = db.get_user(uid)
            if not u:
                print(f"  ! teacher {tid} linked user {uid} missing; creating account")
                user_id = db.create_user(tid, tid, "teacher", email)
                if user_id:
                    db.link_teacher_user(t["id"], user_id)
                    fixed += 1
                continue

            conn = db.get_conn()
            if u["username"] != tid:
                if db.get_user_by_username(tid):
                    print(f"  SKIP {u['username']}->{tid}: username already taken")
                else:
                    conn.execute("UPDATE users SET username=? WHERE id=?", (tid, uid))
                    print(f"  renamed {u['username']} -> {tid}")
            if (email or u.get("email")) and u.get("email") != email:
                conn.execute("UPDATE users SET email=? WHERE id=?", (email, uid))
            conn.commit()
            conn.close()
            db.update_user_password(uid, tid)
            fixed += 1
        else:
            user_id = db.create_user(tid, tid, "teacher", email)
            if user_id:
                db.link_teacher_user(t["id"], user_id)
                print(f"  created login account {tid}/{tid}")
                fixed += 1
            else:
                print(f"  FAILED to create account for {tid}")
    print(f"\nTotal teacher accounts ensured: {fixed}")


if __name__ == "__main__":
    run()
