import customtkinter as ctk


def enable_mousewheel_scrolling(root):
    """Enable mouse-wheel scrolling for every CTkScrollableFrame.

    customtkinter only binds <MouseWheel>, which on Linux (X11) is delivered
    with delta=0 because wheel events arrive as <Button-4>/<Button-5>. As a
    result wheel scrolling silently stops working. Registering these app-wide
    handlers routes the events to the scrollable frame under the pointer.
    """
    root.bind_all("<Button-4>", _on_wheel, add="+")
    root.bind_all("<Button-5>", _on_wheel, add="+")
    root.bind_all("<MouseWheel>", _on_wheel, add="+")


def _on_wheel(event):
    if event.num == 4:
        delta = -1
    elif event.num == 5:
        delta = 1
    else:
        if not getattr(event, "delta", 0):
            return
        delta = -1 if event.delta > 0 else 1

    frame = _find_scrollable(event.widget)
    if frame is None:
        frame = _find_scrollable(_widget_under_pointer(event.widget))
    if frame is None:
        return

    try:
        if frame._parent_canvas.yview() != (0.0, 1.0):
            frame._parent_canvas.yview("scroll", delta, "units")
    except Exception:
        pass


def _find_scrollable(widget):
    if widget is None:
        return None
    try:
        while widget is not None:
            if isinstance(widget, ctk.CTkScrollableFrame):
                return widget
            widget = widget.master
    except Exception:
        return None
    return None


def _widget_under_pointer(origin):
    try:
        toplevel = origin.winfo_toplevel()
        x, y = toplevel.winfo_pointerx(), toplevel.winfo_pointery()
        return toplevel.winfo_containing(x, y)
    except Exception:
        return None
