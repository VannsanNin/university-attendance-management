# Project Structure Explained

A desktop **University Attendance Management System (UAMS)** built with
Python, **CustomTkinter** (GUI) and **SQLite** (storage). Entry point is
`main.py`.

```
School Attendence Management System/
├── main.py                  # Application entry point
├── README.md                # Overview, install & usage docs
├── ClassDiagram.md          # Class-level documentation
├── classExplain.md          # Class explanations
├── structure-explain.md     # This file
├── requirements.txt         # Python dependencies
├── session.json             # Remembered login (auto-saved/cleared)
├── uams.db                  # Live SQLite database
│
├── database/                # Data layer
│   ├── __init__.py
│   └── db_manager.py        # Schema creation + all CRUD queries
│
├── gui/                     # Presentation layer (one file per view)
│   ├── __init__.py
│   ├── login.py             # Login / logout window
│   ├── dashboard.py         # Main app window & navigation hub
│   ├── dashboard_view.py    # Attendance dashboard (stats, calendar)
│   ├── sidebar.py           # Left-hand role-based navigation menu
│   ├── skeleton.py          # Reusable table-loading helper
│   ├── theme.py             # Central styling / colors
│   ├── scroll.py            # Global mousewheel scrolling helper
│   ├── icons.py             # Icon loading helpers
│   ├── activity.py          # Audit-log helper
│   ├── student_management.py
│   ├── teacher_management.py
│   ├── department_management.py
│   ├── course_management.py
│   ├── class_management.py
│   ├── academic_year_view.py
│   ├── attendance_view.py   # Take & view attendance
│   ├── attendance_requests_view.py
│   ├── reports.py           # Reports + Excel/CSV/PDF export
│   ├── student_report_view.py
│   ├── student_subjects_view.py
│   ├── user_management.py
│   ├── settings_view.py     # University info, SMTP, theme toggle
│   ├── backup_restore.py    # DB backup & restore
│   ├── activity_log_view.py
│   ├── notifications_view.py
│   ├── teacher_classes_view.py
│   ├── profile.py
│   ├── about_view.py
│   └── schedule_view.py
│
├── utils/                   # Shared helpers
│   ├── __init__.py
│   └── session.py           # Remember-me / session persistence
├── assets/icons/            # UI icons (SVG / PNG)
├── photos/                  # Student photo uploads
├── backup/                  # Database backup files (*.db)
├── seed_data.py             # One-off script: populate sample data
├── backfill_contacts.py     # One-off script: fill contact info
├── fix_teacher_logins.py    # One-off script: reset teacher passwords
│
├── .venv/                   # Virtual environment (not committed)
├── __pycache__/             # Python bytecode (generated)
└── .idea/                   # PyCharm/IDE settings (not committed)
```

## How it fits together

**1. Entry point (`main.py`)**
Sets the global CustomTkinter theme (`dark` / `blue`), ensures the
`photos/` and `backup/` folders exist, then opens `LoginWindow` and starts
the GUI main loop. Mousewheel scrolling is enabled app-wide.

**2. Data layer (`database/db_manager.py`)**
A single `DatabaseManager` class is the only module that talks to SQLite.
It:
- Creates every table on first run (`init_database`) — departments, users,
  students, teachers, courses, classes, attendance, etc.
- Exposes CRUD methods used by every view.
- Hashes passwords with `bcrypt`.
- Stores the DB at project root as `uams.db`.

Views receive a `DatabaseManager` instance via their constructor.

**3. Presentation layer (`gui/`)**
Every screen is a CustomTkinter view class. `dashboard.py` is the shell;
each module (student, teacher, course, attendance, reports…) is a separate
view that is swapped in based on the logged-in user's role.

Shared pieces:
- `theme.py` — one place to change colors/appearance across all views.
- `skeleton.py` — fills a `ttk.Treeview` from a query result (used by most
  list screens).
- `activity.py` — wraps `log_activity` so any view can write an audit log.
- `scroll.py` — attaches global mousewheel scrolling.

**4. Utilities (`utils/session.py`)**
Saves/loads/clears the remembered login in `session.json` so users don't
have to re-enter credentials.

**5. Support folders & scripts**
- `systemflow/` — plain-text documentation describing each user workflow.
- `photos/` — stored student photos referenced by the students table.
- `backup/` — `.db` snapshots produced by `backup_restore.py`.
- `assets/icons/` — images loaded by `gui/icons.py`.
- `seed_data.py`, `backfill_contacts.py`, `fix_teacher_logins.py` —
  admin/data-fix scripts, not part of the app runtime.

## Key conventions

- Views are constructed as `SomeView(db, parent)`; the DB manager is passed
  in, never created per-view.
- Table screens use `ttk.Treeview` filled through
  `skeleton.schedule_table_load`.
- User actions are logged via `gui.activity.log(...)`.
- `session.json` is generated at runtime and ignored by git.
