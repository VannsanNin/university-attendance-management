# UAMS — Class Explanation

All classes in the **University Attendance Management System (UAMS)**, grouped by layer.

**Total: 36 classes**

- **Persistence layer** → `database/db_manager.py`
- **Presentation layer** → `gui/*` (CustomTkinter)
- **Utilities** → `gui/skeleton.py`

---

## 1. Persistence Layer

### `DatabaseManager` — `database/db_manager.py`

The **single data-access gateway** for the whole application. Every GUI view receives one instance and performs all database work through it — no view talks to SQLite directly.

| Aspect | Detail |
|---|---|
| **Extends** | — (plain class) |
| **Key attribute** | `db_path` — path to `uams.db` |
| **Setup** | `__init__` calls `init_database()`, which creates ~15 tables and runs idempotent migrations |
| **Connection** | `get_conn()` opens a new `sqlite3` connection with `ROW` factory and foreign keys ON; `close_all_connections()` cleans up |

**Method groups:**
- **Auth/users** — `authenticate()` (bcrypt password check, stamps `last_login`), `change_password()`, `create_user()`, `get_users()`, `update_user()`, `delete_user()`, `get_user()`, `get_user_by_username()`, `update_user_password()`
- **Departments** — `add_department()`, `get_departments()`, `update_department()`, `delete_department()`
- **Students** — `add_student()`, `get_students()`, `get_student()`, `update_student()`, `delete_student()`, `get_student_count()`
- **Teachers** — `add_teacher()`, `get_teachers()`, `get_teacher()`, `update_teacher()`, `delete_teacher()`, `get_teacher_count()`
- **Courses** — `add_course()`, `get_courses()`, `update_course()`, `delete_course()`
- **Classes** — `add_class()`, `get_classes()`, `update_class()`, `delete_class()`
- **Class enrollment** — `add_student_to_class()`, `remove_student_from_class()`, `get_class_students()`, `get_student_classes()`
- **Attendance** — `take_attendance()` (uses `INSERT OR REPLACE` on `UNIQUE(student_id, course_id, attendance_date)`), `get_attendance()`, `update_attendance()`, `delete_attendance()`, `get_attendance_summary()`, `get_today_attendance_stats()`
- **Attendance requests** — `add_attendance_request()`, `get_attendance_requests()`, `review_attendance_request()`, `apply_attendance_request()` (approves a pending request and writes the attendance record)
- **Analytics** — `get_attendance_trend()`, `get_attendance_by_class()`, `get_low_attendance_students()`, `get_department_stats()`, `get_attendance_calendar()`, `get_student_attendance_by_course()`, `get_teacher_course_stats()`, `get_teacher_attendance_stats()`, `get_teacher_attendance_trend()`
- **Notifications** — `add_notification()`, `get_notifications()`, `generate_low_attendance_notifications()`
- **Settings** — `get_setting()`, `set_setting()`, `get_all_settings()`
- **Backup/restore** — `backup_database()`, `restore_database()`, `get_backup_logs()`
- **Audit** — `log_activity()`, `get_activity_logs()`, `get_log_modules()`
- **Linking** — `link_student_user()`, `link_teacher_user()`

---

## 2. Application / Window Layer

### `LoginWindow` — `gui/login.py` (extends `ctk.CTk`)

Application entry point (started by `main.py`). Renders the branded login screen, restores the saved theme, validates credentials via `DatabaseManager.authenticate()`, and opens the `DashboardWindow` on success.

- **Attributes:** `db`, `dashboard`, `username_entry`, `password_entry`, `error_label`, `show_password_var`
- **Methods:** `login()`, `forgot_password()`, `_try_auto_login()` (silent session restore from `session.json`), `apply_theme()`, `_build_sidebar()`, `_build_form()`, `_toggle_password_visibility()`

### `DashboardWindow` — `gui/dashboard.py` (extends `ctk.CTkToplevel`)

The main shell after login. Owns a `Sidebar` and swaps views inside a `content_frame` via `show_frame(name)`. Its `views` map resolves each view key to a `(Class, constructor-args)` pair and lazily builds the frame.

- **Attributes:** `parent`, `user`, `db`, `sidebar`, `frames`, `current_view`
- **Methods:** `show_frame(name)`, `apply_theme()`, `change_password()`, `logout()`, `on_close()`
- Manages logout/close: logs the activity, clears the session, returns to `LoginWindow`.

### `Sidebar` — `gui/sidebar.py` (extends `ctk.CTkFrame`)

Navigation panel. Builds role-aware nav buttons from `NAV_ICONS`, highlights the active item, and delegates navigation through callbacks injected by `DashboardWindow`.

### `MyCoursesView` — `gui/dashboard.py` (extends `ctk.CTkFrame`)

Shows the list of courses assigned to the logged-in teacher.

---

## 3. Dashboard Layer (`gui/dashboard_view.py`)

| Class | Extends | Explanation |
|---|---|---|
| `ProgressBar` | `tkinter.Canvas` | Reusable percentage progress-bar widget drawn on a canvas with rounded fill. Method: `set(value)`. |
| `_BaseDashboard` | `ctk.CTkFrame` | Abstract-ish base for all dashboards. Provides skeleton loading, header/card/stat/empty-state builders, section titles and `_refresh()`. |
| `AdminDashboardView` | `_BaseDashboard` | Admin KPIs, charts, low-attendance warnings and per-department statistics. |
| `TeacherDashboardView` | `_BaseDashboard` | Teacher-scoped stats: course cards, today's attendance, attendance trend. |
| `StudentDashboardView` | `_BaseDashboard` | Student's personal attendance %, per-course breakdown and calendar heatmap. |
| `DashboardView` | `ctk.CTkFrame` | Dispatcher — instantiates the correct `*DashboardView` based on the logged-in role. |

---

## 4. Profile Layer (`gui/profile.py`)

| Class | Extends | Explanation |
|---|---|---|
| `BaseProfileView` | `ctk.CTkFrame` | Shared profile layout: header card with avatar, info rows, attendance status chip. Provides `_refresh()`, `_header_card()`, `_info_row()`. |
| `AdminProfileView` | `BaseProfileView` | Administrator profile page. |
| `TeacherProfileView` | `BaseProfileView` | Teacher profile with linked courses/classes. |
| `StudentProfileView` | `BaseProfileView` | Student profile with attendance summary. |

---

## 5. Management & Feature Views (all extend `ctk.CTkFrame`)

| Class | File | Signature | Explanation |
|---|---|---|---|
| `StudentManagementView` | `student_management.py` | `(db, parent, user)` | Add / edit / delete / search students, assign photos. |
| `TeacherManagementView` | `teacher_management.py` | `(db, parent, user)` | Teacher records and user-account linking. |
| `DepartmentManagementView` | `department_management.py` | `(db, parent, user)` | Department CRUD. |
| `CourseManagementView` | `course_management.py` | `(db, parent, user)` | Course CRUD and teacher assignment. |
| `ClassManagementView` | `class_management.py` | `(db, parent, user)` | Class CRUD and student enrollment. |
| `UserManagementView` | `user_management.py` | `(db, parent, user)` | Users, roles, activation and password reset. |
| `AcademicYearView` | `academic_year_view.py` | `(db, parent, user)` | Academic year and active semester settings. |
| `AttendanceTakeView` | `attendance_view.py` | `(user, db, parent)` | Mark / take attendance per course (Present/Absent/Late/Permission). |
| `AttendanceView` | `attendance_view.py` | `(db, parent, user)` | Browse and filter existing attendance records. |
| `AttendanceRequestsView` | `attendance_requests_view.py` | `(db, parent, user)` | Review and approve/reject attendance-correction requests. |
| `ActivityLogView` | `activity_log_view.py` | `(db, parent, user)` | Audit-log explorer with filters. |
| `ReportsView` | `reports.py` | `(db, parent)` | Aggregated attendance reports with PDF/Excel/CSV export. |
| `SettingsView` | `settings_view.py` | `(db, parent, window)` | University info, theme toggle and SMTP/SMS configuration. |
| `BackupRestoreView` | `backup_restore.py` | `(db, parent)` | Database backup / restore with history. |
| `ScheduleView` | `schedule_view.py` | `(db, parent)` | Timetable / schedule view. |
| `NotificationsView` | `notifications_view.py` | `(db, parent)` | Email / SMS / warning notification list. |
| `AboutView` | `about_view.py` | `(db, parent)` | Application information page. |
| `StudentSubjectsView` | `student_subjects_view.py` | `(db, parent, user)` | Student's subject list. |
| `StudentReportView` | `student_report_view.py` | `(db, parent, user)` | Per-student attendance report. |
| `TeacherClassesView` | `teacher_classes_view.py` | `(db, parent, user)` | Classes owned by the logged-in teacher. |

---

## 6. UI Helper Class

### `SkeletonFrame` — `gui/skeleton.py` (extends `ctk.CTkFrame`)

Pulsing placeholder container shown while real content loads. Provides element factories `bar()` and `block()` (registered for animation) and animation control via `start()` / `stop()` / `animate()`.

---

## Quick Reference — Inheritance

```
DatabaseManager                                    (data access)

LoginWindow ──► DashboardWindow ──► Sidebar
                        │
                        ├── DashboardView ──► _BaseDashboard
                        │                      ├── AdminDashboardView
                        │                      ├── TeacherDashboardView
                        │                      └── StudentDashboardView
                        │
                        ├── BaseProfileView
                        │   ├── AdminProfileView
                        │   ├── TeacherProfileView
                        │   └── StudentProfileView
                        │
                        └── all Management/Feature Views (ctk.CTkFrame)

SkeletonFrame  (loading placeholders, used by dashboards)
ProgressBar    (tkinter.Canvas, used by dashboards)
```
