import customtkinter as ctk

from gui import theme


def _shades():
    if ctk.get_appearance_mode().lower().startswith("dark"):
        return theme.c("border_alt"), "#3C3C54"
    return theme.c("border_alt"), "#CBD5E1"


class SkeletonFrame(ctk.CTkFrame):
    """Pulsing placeholder container shown while real content loads."""

    def __init__(self, master, fg_color="transparent", corner_radius=0, **kwargs):
        super().__init__(master, fg_color=fg_color, corner_radius=corner_radius, **kwargs)
        self._items = []
        self._after_id = None
        self._phase = 0

    # ---- element factories (create + register, caller packs/grids) ----
    def bar(self, master=None, height=14, width=None, corner_radius=6):
        kwargs = {"height": height, "corner_radius": corner_radius, "fg_color": theme.c("border_alt")}
        if width:
            kwargs["width"] = width
        frame = ctk.CTkFrame(master or self, **kwargs)
        if width:
            frame.pack_propagate(False)
        self._items.append(frame)
        return frame

    def block(self, master=None, height=110, corner_radius=10):
        frame = ctk.CTkFrame(master or self, height=height, corner_radius=corner_radius,
                             fg_color=theme.c("border_alt"))
        self._items.append(frame)
        return frame

    # ---- animation ----
    def start(self, interval=380):
        if self._after_id is None:
            self._pulse(interval)

    def _pulse(self, interval):
        base, alt = _shades()
        self._phase ^= 1
        color = alt if self._phase else base
        for w in self._items:
            try:
                w.configure(fg_color=color)
            except Exception:
                pass
        try:
            self._after_id = self.after(interval, lambda: self._pulse(interval))
        except Exception:
            self._after_id = None

    def destroy(self):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        super().destroy()


def build_dashboard_skeleton(frame):
    """Placeholder layout that resembles a dashboard (header + stat cards + charts)."""
    header = ctk.CTkFrame(frame, fg_color="transparent")
    header.pack(fill="x", pady=(8, 26))
    frame.bar(header, height=26, width=280).pack(side="left")
    frame.bar(header, height=13, width=400).pack(side="left", padx=(16, 0))

    stats = ctk.CTkFrame(frame, fg_color="transparent")
    stats.pack(fill="x", pady=(0, 26))
    for i in range(4):
        stats.grid_columnconfigure(i, weight=1, uniform="stat")
        block = frame.block(stats, height=112)
        block.grid(row=0, column=i, padx=6, pady=6, sticky="nsew")
        frame.bar(block, height=12, width=70).pack(padx=16, pady=(18, 8), anchor="w")
        frame.bar(block, height=16, width=110).pack(padx=16, anchor="w")
        frame.bar(block, height=10, width=150).pack(padx=16, pady=(10, 0), anchor="w")

    pair = ctk.CTkFrame(frame, fg_color="transparent")
    pair.pack(fill="x")
    for c in range(2):
        pair.grid_columnconfigure(c, weight=1, uniform="pair")
        block = frame.block(pair, height=200)
        block.grid(row=0, column=c, padx=6, pady=6, sticky="nsew")
        frame.bar(block, height=13, width=140).pack(padx=16, pady=(16, 12), anchor="w")
        for _ in range(4):
            frame.bar(block, height=10).pack(padx=16, pady=5)
        frame.bar(block, height=10, width=180).pack(padx=16, pady=5, anchor="w")


def build_table_skeleton(frame):
    """Placeholder rows that resemble a data table."""
    frame.bar(frame, height=14, width=200).pack(padx=20, pady=(16, 18), anchor="w")
    for _ in range(7):
        frame.bar(frame, height=16).pack(padx=20, pady=7)


def safe_grab(dialog, delay=10):
    """Set a modal grab on ``dialog`` without crashing if it is closed or not
    yet viewable when the grab fires (Tk raises TclError in those cases)."""
    def _grab():
        try:
            if not dialog.winfo_exists():
                return
            dialog.wait_visibility()
            dialog.grab_set()
        except Exception:
            pass
    dialog.after(delay, _grab)


def schedule_table_load(owner, container, load_cb, min_delay=650):
    """Overlay a skeleton table in ``container`` for ``min_delay`` ms, then load."""
    sk = SkeletonFrame(container, fg_color="transparent")
    sk.place(relx=0, rely=0, relwidth=1, relheight=1)
    build_table_skeleton(sk)
    sk.start()

    def finish():
        try:
            if not owner.winfo_exists():
                return
        except Exception:
            return
        sk.destroy()
        load_cb()

    owner.after(min_delay, finish)
