import re
import calendar as py_calendar
from datetime import date, datetime
from tkinter import Canvas

import customtkinter as ctk

from gui import theme
from gui.skeleton import SkeletonFrame, build_dashboard_skeleton

# ---------------------------------------------------------------------------
# Small schedule helper — parses text like "Mon/Wed 08:00-10:00" into
# (weekdays, start_time, end_time)
# ---------------------------------------------------------------------------
DAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _expand_days(days):
    if len(days) >= 2:
        idx = [DAY_ABBR.index(d) for d in days]
        lo, hi = min(idx), max(idx)
        if hi > lo:
            return [DAY_ABBR[i % 7] for i in range(lo, hi + 1)]
    return days


def parse_schedule(schedule):
    if not schedule:
        return None
    days = set()
    start_time = None
    end_time = None
    for token in str(schedule).split():
        found = re.findall(r"Mon|Tue|Wed|Thu|Fri|Sat|Sun", token)
        if found:
            days.update(_expand_days(found))
        tm = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", token)
        if tm:
            start_time, end_time = tm.group(1), tm.group(2)
    if not days:
        return None
    return days, start_time, end_time


def _month_label(year, month):
    return f"{py_calendar.month_name[month]} {year}"


def _rate_color(rate):
    if rate is None:
        return None
    if rate >= 85:
        return theme.c("success")
    if rate >= 70:
        return theme.c("warning")
    return theme.c("danger")


# ---------------------------------------------------------------------------
# Reusable canvas widgets
# ---------------------------------------------------------------------------
class ProgressBar(Canvas):
    def __init__(self, parent, value=0.0, color=None, height=8, radius=4):
        self._value = value
        self._color = color or theme.c("chart_2")
        self._radius = radius
        super().__init__(parent, height=height, bg=theme.c("card_alt"), highlightthickness=0)
        self.bind("<Configure>", self._redraw)

    def set(self, value):
        self._value = value
        self._redraw()

    def _redraw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1:
            return
        self.create_rectangle(0, 0, w, h, fill=theme.c("border_alt"), outline="")
        pct = max(0.0, min(100.0, self._value))
        fw = max(2, int(w * pct / 100))
        self.create_rectangle(0, 0, fw, h, fill=self._color, outline="")
        if fw < w:
            self.create_line(fw, 0, fw, h, fill=theme.c("card_alt"))


def draw_line_chart(parent, points, width=460, height=210, y_max=100):
    """points: list of (label, value). Returns the Canvas."""
    canvas = Canvas(parent, width=width, height=height, bg=theme.c("card_alt"), highlightthickness=0)
    canvas.pack(fill="x", pady=(6, 0))

    pad_l, pad_r, pad_t, pad_b = 34, 12, 12, 26
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    grid_color = theme.c("border_alt")
    text_color = theme.c("text_table")
    line_color = theme.c("chart_2")

    for g in range(0, 101, 25):
        y = pad_t + plot_h - plot_h * g / y_max
        canvas.create_line(pad_l, y, width - pad_r, y, fill=grid_color, width=1)
        canvas.create_text(pad_l - 6, y, text=str(g), anchor="e", fill=text_color, font=("Inter", 8))

    if not points:
        canvas.create_text(width / 2, height / 2, text="No attendance data yet",
                           fill=text_color, font=("Inter", 11))
        return canvas

    n = len(points)
    step = plot_w / max(n - 1, 1)
    coords = []
    for i, (label, value) in enumerate(points):
        x = pad_l + i * step
        y = pad_t + plot_h - plot_h * min(max(value, 0), y_max) / y_max
        coords.append((x, y))
        canvas.create_text(x, height - 8, text=label, fill=text_color, font=("Inter", 8))

    if n > 1:
        area = [pad_l, pad_t + plot_h] + [c for pt in coords for c in pt] + [coords[-1][0], pad_t + plot_h]
        canvas.create_polygon(area, fill=line_color, outline="", stipple="gray50")

    if n == 1:
        x, y = coords[0]
        canvas.create_line(pad_l, y, width - pad_r, y, fill=line_color, width=2)
    else:
        for i in range(n - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            canvas.create_line(x1, y1, x2, y2, fill=line_color, width=2)

    for x, y in coords:
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=line_color, outline=theme.c("card_alt"))

    for i, (label, value) in enumerate(points):
        if value > 0:
            canvas.create_text(coords[i][0], coords[i][1] - 10, text=f"{value:.0f}",
                               fill=text_color, font=("Inter", 8))

    return canvas


def draw_donut(parent, data, center_value, center_label, size=170):
    """data: list of (value, color). Donut chart on a fixed-size canvas."""
    canvas = Canvas(parent, width=size, height=size, bg=theme.c("card_alt"), highlightthickness=0)
    canvas.pack(pady=(10, 6))
    pad = 14
    total = sum(v for v, _ in data)
    cx = cy = size / 2

    if total <= 0:
        canvas.create_oval(pad, pad, size - pad, size - pad, outline=theme.c("border_alt"), width=2)
        canvas.create_text(cx, cy, text="No data", fill=theme.c("text_table"), font=("Inter", 11))
        return canvas

    start = 90
    bbox = (pad, pad, size - pad, size - pad)
    for value, color in data:
        if value <= 0:
            continue
        extent = -360 * value / total
        canvas.create_arc(bbox, start=start, extent=extent, fill=color, outline=theme.c("card_alt"))
        start += extent

    hr = size * 0.24
    canvas.create_oval(cx - hr, cy - hr, cx + hr, cy + hr, fill=theme.c("card_alt"), outline="")
    canvas.create_text(cx, cy - 10, text=str(center_value), fill=theme.c("text_bright"),
                       font=("Inter", 20, "bold"))
    canvas.create_text(cx, cy + 14, text=center_label, fill=theme.c("text_table"), font=("Inter", 10))
    return canvas


# ---------------------------------------------------------------------------
# Base dashboard — shared building blocks
# ---------------------------------------------------------------------------
class _BaseDashboard(ctk.CTkFrame):
    def __init__(self, parent, user, db, on_navigate=None):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self.db = db
        self.on_navigate = on_navigate
        self.pack(fill="both", expand=True)

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=20)

        self._skeleton = None
        self._show_skeleton()
        self.after(550, self._render_all)

    def _show_skeleton(self):
        self._skeleton = SkeletonFrame(self.scroll, fg_color="transparent")
        self._skeleton.pack(fill="both", expand=True)
        build_dashboard_skeleton(self._skeleton)
        self._skeleton.start()

    def _render_all(self):
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return
        if self._skeleton is not None:
            self._skeleton.destroy()
            self._skeleton = None
        self._build_all()

    def _refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self._show_skeleton()
        self.after(350, self._render_all)

    # ---------- primitives ----------
    def _build_header(self, title, subtitle=None):
        header_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        left = ctk.CTkFrame(header_frame, fg_color="transparent")
        left.pack(side="left")

        ctk.CTkLabel(left, text=title, font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
                     text_color=theme.c("text_bright")).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(left, text=subtitle, font=ctk.CTkFont(size=13),
                         text_color=theme.c("text_table")).pack(anchor="w", pady=(2, 0))

        right = ctk.CTkFrame(header_frame, fg_color="transparent")
        right.pack(side="right")

        ctk.CTkButton(right, text="\u27F3 Refresh", width=96, height=32, corner_radius=8,
                      fg_color=theme.c("card_alt"), hover_color=theme.c("border_alt"),
                      text_color=theme.c("text_body"),
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._refresh).pack(side="left", padx=6)

        date_badge = ctk.CTkFrame(right, fg_color=theme.c("card_alt"), corner_radius=8,
                                  border_width=1, border_color=theme.c("border_alt"))
        date_badge.pack(side="left")
        ctk.CTkLabel(date_badge, text=f"\U0001F4C5  {date.today().strftime('%A, %b %d, %Y')}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=theme.c("text_subtle")).pack(padx=14, pady=6)

    def _section_title(self, text, subtitle=None):
        f = ctk.CTkFrame(self.scroll, fg_color="transparent")
        f.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(f, text=text, font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=theme.c("text_bright")).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(f, text=subtitle, font=ctk.CTkFont(size=12),
                         text_color=theme.c("text_table")).pack(anchor="w", pady=(2, 0))
        return f

    def _make_card(self, parent, accent_color=None):
        card = ctk.CTkFrame(parent, fg_color=theme.c("card_alt"), corner_radius=12,
                            border_width=1, border_color=theme.c("border_alt"))
        if accent_color:
            accent = ctk.CTkFrame(card, fg_color=accent_color, height=4, corner_radius=0)
            accent.pack(fill="x", side="top")
        return card

    def _card_header(self, card, text):
        ctk.CTkLabel(card, text=text, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 4), anchor="w")

    def _empty_state(self, card, message, pady=28):
        ctk.CTkLabel(card, text=message, font=ctk.CTkFont(size=13),
                     text_color=theme.c("text_table")).pack(pady=pady, fill="x")

    def _stat_card(self, parent, icon, value, label, accent_color, sub=None, sub_color=None):
        card = self._make_card(parent, accent_color)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=16, pady=14, fill="both", expand=True)

        ctk.CTkLabel(inner, text=icon, font=ctk.CTkFont(size=22)).pack(anchor="w")
        ctk.CTkLabel(inner, text=str(value), font=ctk.CTkFont(family="Inter", size=30, weight="bold"),
                     text_color=theme.c("text_bright")).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(inner, text=label, font=ctk.CTkFont(size=12),
                     text_color=theme.c("text_table")).pack(anchor="w")
        if sub:
            ctk.CTkLabel(inner, text=sub, font=ctk.CTkFont(size=11),
                         text_color=sub_color or theme.c("text_subtle")).pack(anchor="w", pady=(4, 0))
        return card

    def _status_badge(self, status):
        colors = {
            "Present": theme.c("chart_2"),
            "Absent": theme.c("danger"),
            "Late": theme.c("chart_3"),
            "Permission": theme.c("chart_1"),
            "Excused": theme.c("chart_1"),
            "Completed": theme.c("success"),
            "Ongoing": theme.c("warning"),
            "Upcoming": theme.c("info"),
            "Scheduled": theme.c("text_table"),
        }
        return colors.get(status, theme.c("text_bright"))

    # ---------- shared sections ----------
    def _build_recent_activity(self, records, title="Recent Attendance Activity", limit=8):
        self._section_title(title, "Latest attendance actions")
        card = self._make_card(self.scroll, theme.c("chart_5"))
        card.pack(fill="x", pady=(0, 20))
        self._card_header(card, title)

        if not records:
            self._empty_state(card, "No attendance records yet.")
            return card

        body = ctk.CTkScrollableFrame(card, fg_color="transparent", height=300)
        body.pack(fill="x", padx=16, pady=(0, 14))
        body.pack_propagate(False)
        self._build_activity_timeline(body, records, limit)
        return card

    # ---------- styled schedule rows ----------
    def _build_schedule_list(self, card, rows, limit=8):
        if not rows:
            self._empty_state(card, "No classes scheduled for today.")
            return
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=(2, 14))
        for r in rows[:limit]:
            self._schedule_item(body, r)

    def _schedule_item(self, parent, row):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        item.pack(fill="x", pady=(0, 8))

        time_box = ctk.CTkFrame(item, fg_color=theme.c("border_alt"), corner_radius=8,
                                width=96, height=40)
        time_box.pack(side="left")
        time_box.pack_propagate(False)
        ctk.CTkLabel(time_box, text=row.get("time") or "\u2014",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=theme.c("text_body")
                     ).place(relx=0.5, rely=0.5, anchor="center")

        status = row.get("status") or ""
        color = self._status_badge(status)
        pill = ctk.CTkFrame(item, fg_color="transparent", corner_radius=10,
                            border_width=1, border_color=color)
        pill.pack(side="right")
        ctk.CTkLabel(pill, text=status, font=ctk.CTkFont(size=10, weight="bold"),
                     text_color=color).pack(padx=10, pady=4)

        info = ctk.CTkFrame(item, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=(12, 8))
        ctk.CTkLabel(info, text=row.get("name") or "\u2014",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=theme.c("text_bright"), anchor="w").pack(fill="x")
        meta_parts = [p for p in (row.get("teacher"), row.get("room"))
                      if p and p != "\u2014"]
        if meta_parts:
            ctk.CTkLabel(info, text=" \u00B7 ".join(meta_parts),
                         font=ctk.CTkFont(size=11), text_color=theme.c("text_table"),
                         anchor="w").pack(fill="x", pady=(2, 0))

    # ---------- styled recent activity timeline ----------
    def _build_activity_timeline(self, parent, records, limit=9):
        shown = records[:limit]
        for i, r in enumerate(shown):
            is_last = i == len(shown) - 1
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x")

            rail = ctk.CTkFrame(row, width=18, fg_color="transparent")
            rail.pack(side="left", fill="y")
            rail.pack_propagate(False)
            dot = ctk.CTkFrame(rail, width=10, height=10, corner_radius=5,
                               fg_color=self._status_badge(r.get("status") or ""))
            dot.pack(pady=(6, 0))
            if not is_last:
                line = ctk.CTkFrame(rail, width=2, fg_color=theme.c("border_alt"))
                line.pack(fill="y", expand=True)

            content = ctk.CTkFrame(row, fg_color="transparent")
            content.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=(2, 6))

            top = ctk.CTkFrame(content, fg_color="transparent")
            top.pack(fill="x")
            status = r.get("status") or ""
            ctk.CTkLabel(top, text=status,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=self._status_badge(status)).pack(side="left")
            text = r.get("student_name") or r.get("sid") or "?"
            if r.get("course_code"):
                text += f" \u00B7 {r['course_code']}"
            ctk.CTkLabel(top, text=text, font=ctk.CTkFont(size=12),
                         text_color=theme.c("text_body")).pack(side="left", padx=(6, 0))
            when = r.get("attendance_time") or r.get("attendance_date") or ""
            ctk.CTkLabel(top, text=when, font=ctk.CTkFont(size=11),
                         text_color=theme.c("text_table")).pack(side="right")

    def _activity_scroll_body(self, parent, records, limit, height=320):
        body = ctk.CTkScrollableFrame(parent, fg_color="transparent", height=height)
        body.pack(fill="x", padx=16, pady=(2, 14))
        body.pack_propagate(False)
        self._build_activity_timeline(body, records, limit)
        return body


# ---------------------------------------------------------------------------
# Admin dashboard
# ---------------------------------------------------------------------------
class AdminDashboardView(_BaseDashboard):
    def _build_all(self):
        self._build_header("Dashboard",
                           "Overview of students, teachers, classes and attendance")

        self._build_summary_cards()
        self._build_trend_and_donut()
        self._build_class_and_low()
        self._build_schedule_and_activity()
        self._build_dept_and_calendar()

    # ---------- summary cards ----------
    def _build_summary_cards(self):
        cards_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="stat")

        total_students = self.db.get_student_count()
        total_teachers = self.db.get_teacher_count()
        total_classes = len(self.db.get_classes())
        total_courses = len(self.db.get_courses())
        today_stats = self.db.get_today_attendance_stats()
        overall = self.db.get_attendance_summary()
        today_rows = self._get_today_schedule_rows()

        rate = overall.get("percentage", 0)
        rate_color = theme.c("success") if rate >= 75 else theme.c("warning")

        cards = [
            self._stat_card(cards_frame, "\U0001F9D2", total_students, "Total Students", theme.c("chart_1"),
                            sub=f"{len(self.db.get_departments())} departments"),
            self._stat_card(cards_frame, "\U0001F468\u200D\U0001F3EB", total_teachers, "Total Teachers", theme.c("chart_2"),
                            sub="Faculty members"),
            self._stat_card(cards_frame, "\U0001F3EB", total_classes, "Total Classes", theme.c("chart_4"),
                            sub=f"{total_courses} courses"),
            self._stat_card(cards_frame, "\U0001F4C5", len(today_rows), "Today's Classes", theme.c("chart_5"),
                            sub=date.today().strftime("%b %d, %Y")),
            self._stat_card(cards_frame, "\u2705", today_stats.get("present", 0), "Present Today", theme.c("chart_2"),
                            sub=f"{today_stats.get('total', 0)} records"),
            self._stat_card(cards_frame, "\u274C", today_stats.get("absent", 0), "Absent Today", theme.c("danger"),
                            sub=f"{today_stats.get('late', 0)} late"),
            self._stat_card(cards_frame, "\u23F3", today_stats.get("late", 0), "Late Today", theme.c("chart_3"),
                            sub=f"{today_stats.get('permission', 0)} permission"),
            self._stat_card(cards_frame, "\U0001F4CA", f"{rate}%", "Attendance Rate", rate_color,
                            sub=f"{overall.get('total', 0)} total records"),
        ]

        for idx, card in enumerate(cards):
            card.grid(row=idx // 4, column=idx % 4, padx=6, pady=6, sticky="nsew")

    # ---------- trend + today's donut ----------
    def _build_trend_and_donut(self):
        self._section_title("Charts")
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        for i in range(2):
            grid.grid_columnconfigure(i, weight=1, uniform="twocol")

        # left: attendance trend
        trend_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                  border_width=1, border_color=theme.c("border_alt"))
        trend_card.grid(row=0, column=0, padx=6, sticky="nsew")
        ctk.CTkLabel(trend_card, text="Attendance Trend",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        seg = ctk.CTkSegmentedButton(trend_card, values=["7 Days", "14 Days", "30 Days", "Semester"],
                                     command=lambda v: self._draw_trend(trend_holder, v),
                                     font=ctk.CTkFont(size=11), height=30)
        seg.set("7 Days")
        seg.pack(padx=16, anchor="w")

        trend_holder = ctk.CTkFrame(trend_card, fg_color="transparent")
        trend_holder.pack(fill="x", padx=16, pady=(2, 14))
        self._draw_trend(trend_holder, "7 Days")

        # right: today's attendance donut
        donut_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                  border_width=1, border_color=theme.c("border_alt"))
        donut_card.grid(row=0, column=1, padx=6, sticky="nsew")
        ctk.CTkLabel(donut_card, text="Today's Attendance",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        stats = self.db.get_today_attendance_stats()
        total = stats.get("total", 0) or 0
        present = stats.get("present", 0) or 0
        absent = stats.get("absent", 0) or 0
        late = stats.get("late", 0) or 0
        excused = total - (present + absent + late + (stats.get("permission", 0) or 0))
        pct = round((present + late + (stats.get("permission", 0) or 0) + excused) * 100 / total, 1) if total else 0.0

        draw_donut(donut_card, [
            (present, theme.c("chart_2")),
            (absent, theme.c("danger")),
            (late, theme.c("chart_3")),
            (excused, theme.c("chart_1")),
        ], f"{pct}%", "rate")

        legend = ctk.CTkFrame(donut_card, fg_color="transparent")
        legend.pack(fill="x", padx=16, pady=(2, 14))
        for label, value, color in [("Present", present, theme.c("chart_2")),
                                    ("Absent", absent, theme.c("danger")),
                                    ("Late", late, theme.c("chart_3")),
                                    ("Excused", excused, theme.c("chart_1"))]:
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=6)
            sw = ctk.CTkFrame(item, fg_color=color, width=10, height=10, corner_radius=3)
            sw.pack(side="left")
            sw.pack_propagate(False)
            ctk.CTkLabel(item, text=f"{label} {value}", font=ctk.CTkFont(size=11),
                         text_color=theme.c("text_table")).pack(side="left", padx=(3, 0))

    def _draw_trend(self, holder, period):
        for w in holder.winfo_children():
            w.destroy()
        days = {"7 Days": 7, "14 Days": 14, "30 Days": 30}.get(period, 90)
        trend = self.db.get_attendance_trend(days=days)
        points = [(t["label"], t["rate"]) for t in trend]
        draw_line_chart(holder, points)
        total = sum(t["total"] for t in trend)
        attended = sum(t["attended"] for t in trend)
        avg = round(attended * 100 / total, 1) if total else 0.0
        ctk.CTkLabel(holder, text=f"{total} records tracked \u00B7 {avg}% average over {period}",
                     font=ctk.CTkFont(size=12), text_color=theme.c("text_table")).pack(pady=(4, 0))

    # ---------- by class + low attendance ----------
    def _build_class_and_low(self):
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        for i in range(2):
            grid.grid_columnconfigure(i, weight=1, uniform="twocol")

        # attendance by class
        by_class_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                     border_width=1, border_color=theme.c("border_alt"))
        by_class_card.grid(row=0, column=0, padx=6, sticky="nsew")
        ctk.CTkLabel(by_class_card, text="Attendance by Class",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        classes = self.db.get_attendance_by_class()
        if not classes:
            self._empty_state(by_class_card, "No classes found.")
        else:
            body = ctk.CTkFrame(by_class_card, fg_color="transparent")
            body.pack(fill="x", padx=16, pady=(0, 14))
            for cl in classes[:7]:
                row = ctk.CTkFrame(body, fg_color="transparent")
                row.pack(fill="x", pady=3)
                label = cl.get("class_name") or "\u2014"
                if cl.get("department_name"):
                    label += f" \u00B7 {cl['department_name']}"
                ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12),
                             text_color=theme.c("text_body"), anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(row, text=f"{cl['att_rate']}%", font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=_rate_color(cl["att_rate"]) or theme.c("text_bright")).pack(side="right")
                bar = ProgressBar(body, value=cl["att_rate"], color=_rate_color(cl["att_rate"]) or theme.c("border_alt"))
                bar.pack(fill="x", pady=(1, 3))
                ctk.CTkLabel(body, text=f"{cl['student_count']} students \u00B7 {cl['att_total']} records",
                             font=ctk.CTkFont(size=10), text_color=theme.c("text_subtle"),
                             anchor="w").pack(fill="x")

        # low attendance
        threshold = int(self.db.get_setting("low_attendance_warning") or 75)
        low_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                border_width=1, border_color=theme.c("border_alt"))
        low_card.grid(row=0, column=1, padx=6, sticky="nsew")
        ctk.CTkLabel(low_card, text=f"\u26A0 Low Attendance (below {threshold}%)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("warning")).pack(padx=16, pady=(14, 6), anchor="w")

        low_students = self.db.get_low_attendance_students(threshold=threshold, limit=8)
        if not low_students:
            self._empty_state(low_card, "No students below the warning threshold.")
        else:
            body = ctk.CTkFrame(low_card, fg_color="transparent")
            body.pack(fill="x", padx=16, pady=(0, 14))
            for s in low_students:
                row = ctk.CTkFrame(body, fg_color="transparent")
                row.pack(fill="x", pady=3)
                ctk.CTkLabel(row, text=s["full_name"], font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=theme.c("text_bright"), anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(row, text=f"{s['rate']}%", font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=theme.c("danger")).pack(side="right")
                bar = ProgressBar(body, value=s["rate"], color=theme.c("danger"))
                bar.pack(fill="x", pady=(1, 3))
                ctk.CTkLabel(body, text=f"{s.get('department_name') or s.get('class_name') or s['student_id']} \u00B7 {s['total']} records",
                             font=ctk.CTkFont(size=10), text_color=theme.c("text_subtle"),
                             anchor="w").pack(fill="x")

    # ---------- schedule + recent activity ----------
    def _build_schedule_and_activity(self):
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        for i in range(2):
            grid.grid_columnconfigure(i, weight=1, uniform="twocol")

        rows = self._get_today_schedule_rows()
        sched_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                  border_width=1, border_color=theme.c("border_alt"))
        sched_card.grid(row=0, column=0, padx=6, sticky="nsew")
        ctk.CTkLabel(sched_card, text="Today's Schedule",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        if not rows:
            self._empty_state(sched_card, "No classes scheduled for today.\nUse Take Attendance to start a session.")
        else:
            self._build_schedule_list(sched_card, rows)

        records = self.db.get_attendance(limit=10)
        act_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                border_width=1, border_color=theme.c("border_alt"))
        act_card.grid(row=0, column=1, padx=6, sticky="nsew")
        ctk.CTkLabel(act_card, text="Recent Activity",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        if not records:
            self._empty_state(act_card, "No attendance records yet.")
        else:
            self._activity_scroll_body(act_card, records, 9)

    # ---------- department stats + calendar ----------
    def _build_dept_and_calendar(self):
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        for i in range(2):
            grid.grid_columnconfigure(i, weight=1, uniform="twocol")

        dept_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                 border_width=1, border_color=theme.c("border_alt"))
        dept_card.grid(row=0, column=0, padx=6, sticky="nsew")
        ctk.CTkLabel(dept_card, text="Department Statistics",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        depts = self.db.get_department_stats()
        if not depts:
            self._empty_state(dept_card, "No departments found.")
        else:
            body = ctk.CTkFrame(dept_card, fg_color="transparent")
            body.pack(fill="x", padx=16, pady=(0, 14))
            for d in depts[:7]:
                row = ctk.CTkFrame(body, fg_color="transparent")
                row.pack(fill="x", pady=3)
                ctk.CTkLabel(row, text=d["name"], font=ctk.CTkFont(size=12),
                             text_color=theme.c("text_body"), anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(row, text=f"{d['att_rate']}%", font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=_rate_color(d["att_rate"]) or theme.c("text_bright")).pack(side="right")
                bar = ProgressBar(body, value=d["att_rate"], color=_rate_color(d["att_rate"]) or theme.c("border_alt"))
                bar.pack(fill="x", pady=(1, 3))
                ctk.CTkLabel(body, text=f"{d['students']} students \u00B7 {d['att_total']} records",
                             font=ctk.CTkFont(size=10), text_color=theme.c("text_subtle"),
                             anchor="w").pack(fill="x")

        today = date.today()
        days = self.db.get_attendance_calendar(year=today.year, month=today.month)
        cal_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                border_width=1, border_color=theme.c("border_alt"))
        cal_card.grid(row=0, column=1, padx=6, sticky="nsew")
        ctk.CTkLabel(cal_card, text="Attendance Calendar",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")
        ctk.CTkLabel(cal_card, text=_month_label(today.year, today.month),
                     font=ctk.CTkFont(size=12), text_color=theme.c("text_table")).pack(padx=16, anchor="w")

        cal_grid = ctk.CTkFrame(cal_card, fg_color="transparent")
        cal_grid.pack(padx=16, pady=(8, 4))

        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for c, name in enumerate(day_names):
            ctk.CTkLabel(cal_grid, text=name, font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=theme.c("text_table"), width=40).grid(row=0, column=c, padx=2, pady=2)

        first_wd = py_calendar.monthrange(today.year, today.month)[0]
        first_wd = (first_wd - 1) % 7
        row = 1
        col = first_wd
        for d in days:
            color = _rate_color(d["rate"])
            if color is None:
                fg, txt = theme.c("border_alt"), theme.c("text_table")
            elif d["rate"] >= 85:
                fg, txt = theme.c("success"), "#FFFFFF"
            elif d["rate"] >= 70:
                fg, txt = theme.c("warning"), "#1F2937"
            else:
                fg, txt = theme.c("danger"), "#FFFFFF"
            cell = ctk.CTkFrame(cal_grid, width=40, height=40, corner_radius=8, fg_color=fg)
            cell.grid(row=row, column=col, padx=2, pady=2)
            cell.grid_propagate(False)
            ctk.CTkLabel(cell, text=str(d["day"]), font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=txt).place(relx=0.5, rely=0.5, anchor="center")
            col += 1
            if col == 7:
                col = 0
                row += 1

        legend = ctk.CTkFrame(cal_card, fg_color="transparent")
        legend.pack(padx=16, pady=(4, 14), fill="x")
        for label, color in [("Good \u226585%", theme.c("success")),
                             ("Average \u226570%", theme.c("warning")),
                             ("Poor <70%", theme.c("danger")),
                             ("No data", theme.c("border_alt"))]:
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=6)
            sw = ctk.CTkFrame(item, fg_color=color, width=10, height=10, corner_radius=3)
            sw.pack(side="left")
            sw.pack_propagate(False)
            ctk.CTkLabel(item, text=label, font=ctk.CTkFont(size=10),
                         text_color=theme.c("text_table")).pack(side="left", padx=(3, 0))

    # ---------- helpers ----------
    def _get_today_schedule_rows(self):
        rows = []
        today_wd = date.today().strftime("%a")
        now = datetime.now().strftime("%H:%M")
        attendance_today = self.db.get_attendance(attendance_date=date.today().isoformat())
        class_ids_today = {r.get("class_id") for r in attendance_today if r.get("class_id")}
        course_ids_today = {r.get("course_id") for r in attendance_today if r.get("course_id")}

        for cl in self.db.get_classes():
            parsed = parse_schedule(cl.get("schedule"))
            if parsed:
                days, start_t, end_t = parsed
                if today_wd not in days:
                    continue
                time_str = f"{start_t}\u2013{end_t}" if start_t and end_t else ""
                status = "Upcoming"
                if start_t and end_t:
                    if now > end_t:
                        status = "Completed"
                    elif now >= start_t:
                        status = "Ongoing"
                rows.append({"time": time_str, "name": cl["class_name"],
                             "teacher": cl.get("teacher_name") or "\u2014",
                             "room": cl.get("room") or "\u2014", "status": status})
            elif cl["id"] in class_ids_today:
                rows.append({"time": "\u2014", "name": cl["class_name"],
                             "teacher": cl.get("teacher_name") or "\u2014",
                             "room": cl.get("room") or "\u2014", "status": "Completed"})

        if course_ids_today:
            for course in self.db.get_courses():
                if course["id"] in course_ids_today:
                    rows.append({"time": "\u2014", "name": course["course_code"],
                                 "teacher": course.get("teacher_name") or "\u2014",
                                 "room": "\u2014", "status": "Completed"})

        return sorted(rows, key=lambda r: (r["time"] == "\u2014", r["time"]))


# ---------------------------------------------------------------------------
# Teacher dashboard
# ---------------------------------------------------------------------------
class TeacherDashboardView(_BaseDashboard):
    def _build_all(self):
        self._build_header("My Dashboard", "Overview of your classes, courses and attendance")

        teacher = self.db.get_teacher_by_user_id(self.user["id"])
        if not teacher:
            self._empty_state(self.scroll, "Teacher profile not linked to this account. Contact the administrator.")
            return
        self.teacher = teacher

        self._build_summary_cards()
        self._build_trend_and_stats()
        self._build_courses_and_low()
        self._build_schedule_and_activity()

    def _build_summary_cards(self):
        cards_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="stat")

        tid = self.teacher["id"]
        classes = [c for c in self.db.get_classes() if c.get("teacher_id") == tid]
        courses = self.db.get_courses(teacher_id=tid)
        course_ids = {c["id"] for c in courses}
        today_stats = self.db.get_teacher_attendance_stats(tid)
        overall = self.db.get_attendance_summary()

        cards = [
            self._stat_card(cards_frame, "\U0001F3EB", len(classes), "My Classes", theme.c("chart_4"),
                            sub=f"{len(courses)} assigned courses"),
            self._stat_card(cards_frame, "\U0001F4DA", len(courses), "My Courses", theme.c("chart_1"),
                            sub="Subjects you teach"),
            self._stat_card(cards_frame, "\U0001F4C5", today_stats.get("total", 0), "Today's Attendance", theme.c("chart_3"),
                            sub=f"{today_stats.get('present', 0)} present \u00B7 {today_stats.get('absent', 0)} absent"),
            self._stat_card(cards_frame, "\U0001F4CA", f"{today_stats.get('rate', 0)}%", "Today's Rate", theme.c("chart_2"),
                            sub=f"{today_stats.get('late', 0)} late today"),
        ]
        for idx, card in enumerate(cards):
            card.grid(row=0, column=idx, padx=6, pady=6, sticky="nsew")

    def _build_trend_and_stats(self):
        self._section_title("Charts")
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        for i in range(2):
            grid.grid_columnconfigure(i, weight=1, uniform="twocol")

        trend_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                  border_width=1, border_color=theme.c("border_alt"))
        trend_card.grid(row=0, column=0, padx=6, sticky="nsew")
        ctk.CTkLabel(trend_card, text="My Attendance Trend",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        seg = ctk.CTkSegmentedButton(trend_card, values=["7 Days", "14 Days", "30 Days"],
                                     command=lambda v: self._draw_teacher_trend(trend_holder, v),
                                     font=ctk.CTkFont(size=11), height=30)
        seg.set("7 Days")
        seg.pack(padx=16, anchor="w")
        trend_holder = ctk.CTkFrame(trend_card, fg_color="transparent")
        trend_holder.pack(fill="x", padx=16, pady=(2, 14))
        self._draw_teacher_trend(trend_holder, "7 Days")

        stats_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                  border_width=1, border_color=theme.c("border_alt"))
        stats_card.grid(row=0, column=1, padx=6, sticky="nsew")
        ctk.CTkLabel(stats_card, text="Today's Attendance",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        stats = self.db.get_teacher_attendance_stats(self.teacher["id"])
        total = stats.get("total", 0) or 0
        present = stats.get("present", 0) or 0
        absent = stats.get("absent", 0) or 0
        late = stats.get("late", 0) or 0

        draw_donut(stats_card, [
            (present, theme.c("chart_2")),
            (absent, theme.c("danger")),
            (late, theme.c("chart_3")),
        ], f"{stats.get('rate', 0)}%", "rate")

        legend = ctk.CTkFrame(stats_card, fg_color="transparent")
        legend.pack(fill="x", padx=16, pady=(2, 14))
        for label, value, color in [("Present", present, theme.c("chart_2")),
                                    ("Absent", absent, theme.c("danger")),
                                    ("Late", late, theme.c("chart_3"))]:
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=8)
            sw = ctk.CTkFrame(item, fg_color=color, width=10, height=10, corner_radius=3)
            sw.pack(side="left")
            sw.pack_propagate(False)
            ctk.CTkLabel(item, text=f"{label} {value}", font=ctk.CTkFont(size=11),
                         text_color=theme.c("text_table")).pack(side="left", padx=(3, 0))

    def _draw_teacher_trend(self, holder, period):
        for w in holder.winfo_children():
            w.destroy()
        days = {"7 Days": 7, "14 Days": 14}.get(period, 30)
        trend = self.db.get_teacher_attendance_trend(self.teacher["id"], days=days)
        draw_line_chart(holder, [(t["label"], t["rate"]) for t in trend])
        total = sum(t["total"] for t in trend)
        attended = sum(t["attended"] for t in trend)
        avg = round(attended * 100 / total, 1) if total else 0.0
        ctk.CTkLabel(holder, text=f"{total} records tracked \u00B7 {avg}% average over {period}",
                     font=ctk.CTkFont(size=12), text_color=theme.c("text_table")).pack(pady=(4, 0))

    def _build_courses_and_low(self):
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        for i in range(2):
            grid.grid_columnconfigure(i, weight=1, uniform="twocol")

        courses_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                    border_width=1, border_color=theme.c("border_alt"))
        courses_card.grid(row=0, column=0, padx=6, sticky="nsew")
        ctk.CTkLabel(courses_card, text="Course Performance",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        courses = self.db.get_teacher_course_stats(self.teacher["id"])
        if not courses:
            self._empty_state(courses_card, "No attendance recorded for your courses yet.")
        else:
            body = ctk.CTkFrame(courses_card, fg_color="transparent")
            body.pack(fill="x", padx=16, pady=(0, 14))
            for c in courses[:7]:
                row = ctk.CTkFrame(body, fg_color="transparent")
                row.pack(fill="x", pady=3)
                ctk.CTkLabel(row, text=f"{c['course_code']} \u00B7 {c['course_name']}",
                             font=ctk.CTkFont(size=12),
                             text_color=theme.c("text_body"), anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(row, text=f"{c['rate']}%", font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=_rate_color(c["rate"]) or theme.c("text_bright")).pack(side="right")
                bar = ProgressBar(body, value=c["rate"], color=_rate_color(c["rate"]) or theme.c("border_alt"))
                bar.pack(fill="x", pady=(1, 3))
                ctk.CTkLabel(body, text=f"{c['students_tracked']} students \u00B7 {c['total']} records",
                             font=ctk.CTkFont(size=10), text_color=theme.c("text_subtle"),
                             anchor="w").pack(fill="x")

        threshold = int(self.db.get_setting("low_attendance_warning") or 75)
        low_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                border_width=1, border_color=theme.c("border_alt"))
        low_card.grid(row=0, column=1, padx=6, sticky="nsew")
        ctk.CTkLabel(low_card, text=f"\u26A0 Low Attendance (below {threshold}%)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("warning")).pack(padx=16, pady=(14, 6), anchor="w")

        low_students = self.db.get_low_attendance_students(threshold=threshold, limit=8,
                                                           teacher_id=self.teacher["id"])
        if not low_students:
            self._empty_state(low_card, "No students below the warning threshold in your courses.")
        else:
            body = ctk.CTkFrame(low_card, fg_color="transparent")
            body.pack(fill="x", padx=16, pady=(0, 14))
            for s in low_students:
                row = ctk.CTkFrame(body, fg_color="transparent")
                row.pack(fill="x", pady=3)
                ctk.CTkLabel(row, text=s["full_name"], font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=theme.c("text_bright"), anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(row, text=f"{s['rate']}%", font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=theme.c("danger")).pack(side="right")
                bar = ProgressBar(body, value=s["rate"], color=theme.c("danger"))
                bar.pack(fill="x", pady=(1, 3))
                ctk.CTkLabel(body, text=f"{s.get('class_name') or s['student_id']} \u00B7 {s['total']} records",
                             font=ctk.CTkFont(size=10), text_color=theme.c("text_subtle"),
                             anchor="w").pack(fill="x")

    def _build_schedule_and_activity(self):
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        for i in range(2):
            grid.grid_columnconfigure(i, weight=1, uniform="twocol")

        rows = self._get_teacher_today_rows()
        sched_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                  border_width=1, border_color=theme.c("border_alt"))
        sched_card.grid(row=0, column=0, padx=6, sticky="nsew")
        ctk.CTkLabel(sched_card, text="Today's Classes",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        if not rows:
            self._empty_state(sched_card, "No classes scheduled for you today.")
        else:
            self._build_schedule_list(sched_card, rows)

            ctk.CTkButton(sched_card, text="\u2705 Quick Take Attendance",
                          fg_color=theme.c("primary"), hover_color=theme.c("primary_hover"),
                          height=38, corner_radius=8, font=ctk.CTkFont(size=13, weight="bold"),
                          command=lambda: self.on_navigate and self.on_navigate("take_attendance")
                          ).pack(padx=16, pady=(8, 14), fill="x")

        records = self.db.get_attendance(limit=10)
        course_ids = {c["id"] for c in self.db.get_courses(teacher_id=self.teacher["id"])}
        records = [r for r in records if r.get("course_id") in course_ids]

        act_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                border_width=1, border_color=theme.c("border_alt"))
        act_card.grid(row=0, column=1, padx=6, sticky="nsew")
        ctk.CTkLabel(act_card, text="Recent Sessions",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        if not records:
            self._empty_state(act_card, "No attendance sessions yet.")
        else:
            self._activity_scroll_body(act_card, records, 9)

    def _get_teacher_today_rows(self):
        rows = []
        tid = self.teacher["id"]
        today_wd = date.today().strftime("%a")
        now = datetime.now().strftime("%H:%M")
        course_ids = {c["id"] for c in self.db.get_courses(teacher_id=tid)}
        class_ids = {cl["id"] for cl in self.db.get_classes() if cl.get("teacher_id") == tid}
        attendance_today = self.db.get_attendance(attendance_date=date.today().isoformat())

        for cl in self.db.get_classes():
            if cl.get("teacher_id") != tid and cl["id"] not in class_ids:
                continue
            parsed = parse_schedule(cl.get("schedule"))
            if parsed:
                days, start_t, end_t = parsed
                if today_wd not in days:
                    continue
                time_str = f"{start_t}\u2013{end_t}" if start_t and end_t else ""
                status = "Upcoming"
                if start_t and end_t:
                    if now > end_t:
                        status = "Completed"
                    elif now >= start_t:
                        status = "Ongoing"
                rows.append({"time": time_str, "name": cl["class_name"],
                             "room": cl.get("room") or "\u2014", "status": status})
            elif cl["id"] in {r.get("class_id") for r in attendance_today if r.get("class_id")}:
                rows.append({"time": "\u2014", "name": cl["class_name"],
                             "room": cl.get("room") or "\u2014", "status": "Completed"})

        today_courses = {r.get("course_id") for r in attendance_today if r.get("course_id")} & course_ids
        if today_courses:
            for c in self.db.get_courses(teacher_id=tid):
                if c["id"] in today_courses:
                    rows.append({"time": "\u2014", "name": c["course_code"],
                                 "room": "\u2014", "status": "Completed"})

        return sorted(rows, key=lambda r: (r["time"] == "\u2014", r["time"]))


# ---------------------------------------------------------------------------
# Student dashboard
# ---------------------------------------------------------------------------
class StudentDashboardView(_BaseDashboard):
    def _build_all(self):
        self._build_header("My Dashboard", "Overview of your attendance and upcoming classes")

        student = self.db.get_student_by_user_id(self.user["id"])
        if not student:
            self._empty_state(self.scroll, "Student profile not linked to this account. Contact the administrator.")
            return
        self.student = student

        self._build_summary_cards()
        self._build_course_breakdown()
        self._build_schedule_and_calendar()
        self._build_recent_history()

    def _build_summary_cards(self):
        cards_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="stat")

        summary = self.db.get_attendance_summary(student_id=self.student["id"])
        rate = summary.get("percentage", 0) or 0
        threshold = int(self.db.get_setting("low_attendance_warning") or 75)
        rate_color = theme.c("success") if rate >= 75 else theme.c("warning")

        cards = [
            self._stat_card(cards_frame, "\U0001F4CA", f"{rate}%", "My Attendance Rate", rate_color,
                            sub=f"{self.student['student_id']} \u00B7 {self.student['class_name'] or self.student['department_name'] or ''}"),
            self._stat_card(cards_frame, "\u2705", summary.get("present_count", 0) or 0, "Present", theme.c("chart_2"),
                            sub=f"{summary.get('total', 0) or 0} total sessions"),
            self._stat_card(cards_frame, "\u274C", summary.get("absent_count", 0) or 0, "Absent", theme.c("danger"),
                            sub=f"{summary.get('permission_count', 0) or 0} permission"),
            self._stat_card(cards_frame, "\u23F3", summary.get("late_count", 0) or 0, "Late", theme.c("chart_3"),
                            sub="Arrived late"),
        ]
        for idx, card in enumerate(cards):
            card.grid(row=0, column=idx, padx=6, pady=6, sticky="nsew")

        if rate < threshold:
            warn = ctk.CTkFrame(self.scroll, fg_color=theme.c("card_alt"), corner_radius=10,
                                border_width=1, border_color=theme.c("warning"))
            warn.pack(fill="x", pady=(0, 20))
            ctk.CTkLabel(warn, text=f"\u26A0  Warning: Your attendance is {rate}%, below the {threshold}% threshold. "
                                    "Please contact your advisor.",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=theme.c("warning")).pack(padx=18, pady=14, anchor="w")

    def _build_course_breakdown(self):
        self._section_title("Attendance by Course")
        card = ctk.CTkFrame(self.scroll, fg_color=theme.c("card_alt"), corner_radius=12,
                            border_width=1, border_color=theme.c("border_alt"))
        card.pack(fill="x", pady=(0, 20))

        rows = self.db.get_student_attendance_by_course(self.student["id"])
        if not rows:
            self._empty_state(card, "No attendance records for your courses yet.")
            return

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=16, pady=(0, 14))
        for c in rows:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"{c['course_code']} \u00B7 {c['course_name']}",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=theme.c("text_bright"), anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(row, text=f"{c['rate']}%", font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=_rate_color(c["rate"]) or theme.c("text_bright")).pack(side="right")
            bar = ProgressBar(body, value=c["rate"], color=_rate_color(c["rate"]) or theme.c("border_alt"))
            bar.pack(fill="x", pady=(1, 3))
            ctk.CTkLabel(body,
                         text=f"{c['present']} present \u00B7 {c['absent']} absent \u00B7 {c['late']} late \u00B7 {c['total']} sessions",
                         font=ctk.CTkFont(size=10), text_color=theme.c("text_subtle"),
                         anchor="w").pack(fill="x")

    def _build_schedule_and_calendar(self):
        grid = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 20))
        for i in range(2):
            grid.grid_columnconfigure(i, weight=1, uniform="twocol")

        rows = self._get_student_today_rows()
        sched_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                  border_width=1, border_color=theme.c("border_alt"))
        sched_card.grid(row=0, column=0, padx=6, sticky="nsew")
        ctk.CTkLabel(sched_card, text="Today's / Upcoming Classes",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")

        if not rows:
            self._empty_state(sched_card, "No classes scheduled for you today.")
        else:
            self._build_schedule_list(sched_card, rows)

        today = date.today()
        days = self.db.get_attendance_calendar(year=today.year, month=today.month)
        cal_card = ctk.CTkFrame(grid, fg_color=theme.c("card_alt"), corner_radius=12,
                                border_width=1, border_color=theme.c("border_alt"))
        cal_card.grid(row=0, column=1, padx=6, sticky="nsew")
        ctk.CTkLabel(cal_card, text="Attendance Calendar",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=theme.c("text_bright")).pack(padx=16, pady=(14, 6), anchor="w")
        ctk.CTkLabel(cal_card, text=_month_label(today.year, today.month),
                     font=ctk.CTkFont(size=12), text_color=theme.c("text_table")).pack(padx=16, anchor="w")

        cal_grid = ctk.CTkFrame(cal_card, fg_color="transparent")
        cal_grid.pack(padx=16, pady=(8, 4))

        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for c, name in enumerate(day_names):
            ctk.CTkLabel(cal_grid, text=name, font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=theme.c("text_table"), width=40).grid(row=0, column=c, padx=2, pady=2)

        first_wd = py_calendar.monthrange(today.year, today.month)[0]
        first_wd = (first_wd - 1) % 7
        row = 1
        col = first_wd
        for d in days:
            color = _rate_color(d["rate"])
            if color is None:
                fg, txt = theme.c("border_alt"), theme.c("text_table")
            elif d["rate"] >= 85:
                fg, txt = theme.c("success"), "#FFFFFF"
            elif d["rate"] >= 70:
                fg, txt = theme.c("warning"), "#1F2937"
            else:
                fg, txt = theme.c("danger"), "#FFFFFF"
            cell = ctk.CTkFrame(cal_grid, width=40, height=40, corner_radius=8, fg_color=fg)
            cell.grid(row=row, column=col, padx=2, pady=2)
            cell.grid_propagate(False)
            ctk.CTkLabel(cell, text=str(d["day"]), font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=txt).place(relx=0.5, rely=0.5, anchor="center")
            col += 1
            if col == 7:
                col = 0
                row += 1

        legend = ctk.CTkFrame(cal_card, fg_color="transparent")
        legend.pack(padx=16, pady=(4, 14), fill="x")
        for label, color in [("Good \u226585%", theme.c("success")),
                             ("Average \u226570%", theme.c("warning")),
                             ("Poor <70%", theme.c("danger")),
                             ("No data", theme.c("border_alt"))]:
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=6)
            sw = ctk.CTkFrame(item, fg_color=color, width=10, height=10, corner_radius=3)
            sw.pack(side="left")
            sw.pack_propagate(False)
            ctk.CTkLabel(item, text=label, font=ctk.CTkFont(size=10),
                         text_color=theme.c("text_table")).pack(side="left", padx=(3, 0))

    def _build_recent_history(self):
        records = self.db.get_attendance(student_id=self.student["id"], limit=10)
        self._build_recent_activity(records, title="Recent Attendance")

    def _get_student_today_rows(self):
        rows = []
        sid = self.student["id"]
        today_wd = date.today().strftime("%a")
        now = datetime.now().strftime("%H:%M")
        student_classes = self.db.get_student_classes(sid)
        class_ids = {cl["id"] for cl in student_classes}
        attendance_today = self.db.get_attendance(student_id=sid,
                                                  attendance_date=date.today().isoformat())

        for cl in student_classes:
            parsed = parse_schedule(cl.get("schedule"))
            if parsed:
                days, start_t, end_t = parsed
                if today_wd not in days:
                    continue
                time_str = f"{start_t}\u2013{end_t}" if start_t and end_t else ""
                status = "Upcoming"
                if start_t and end_t:
                    if now > end_t:
                        status = "Completed"
                    elif now >= start_t:
                        status = "Ongoing"
                rows.append({"time": time_str, "name": cl["class_name"],
                             "teacher": cl.get("teacher_name") or "\u2014", "status": status})
            elif cl["id"] in {r.get("class_id") for r in attendance_today if r.get("class_id")}:
                rows.append({"time": "\u2014", "name": cl["class_name"],
                             "teacher": cl.get("teacher_name") or "\u2014", "status": "Completed"})

        today_courses = {r.get("course_id") for r in attendance_today if r.get("course_id")}
        for c in self.db.get_courses():
            if c["id"] in today_courses:
                rows.append({"time": "\u2014", "name": c["course_code"],
                             "teacher": c.get("teacher_name") or "\u2014", "status": "Completed"})

        return sorted(rows, key=lambda r: (r["time"] == "\u2014", r["time"]))


# ---------------------------------------------------------------------------
# Entry point — dispatches to the right dashboard for the logged-in role
# ---------------------------------------------------------------------------
class DashboardView(ctk.CTkFrame):
    def __init__(self, user, db, parent, on_navigate=None):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self.db = db
        self.on_navigate = on_navigate
        self.pack(fill="both", expand=True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        role = user.get("role", "")
        view_cls = {
            "teacher": TeacherDashboardView,
            "student": StudentDashboardView,
        }.get(role, AdminDashboardView)

        self.view = view_cls(self, user, db, on_navigate=on_navigate)
        self.view.grid(row=0, column=0, sticky="nsew")
