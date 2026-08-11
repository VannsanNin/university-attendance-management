import os

import customtkinter as ctk
from PIL import Image

_ICON_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
)
_CACHE = {}


def _load_raw(name):
    path = os.path.join(_ICON_DIR, f"{name}.png")
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    return None


def _variant(name, variant):
    path = os.path.join(_ICON_DIR, f"{name}_{variant}.png")
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    return None


def _colorize(img, rgb):
    """Recolor every opaque pixel to ``rgb``, preserving alpha."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 0:
                px[x, y] = (rgb[0], rgb[1], rgb[2], a)
    return img


def icon(name, size=(18, 18)):
    """Load a nav icon as a CTkImage, auto-switching the dark/light variant.

    ``{name}_light.png`` files are light-colored (for dark backgrounds) and
    ``{name}_dark.png`` files are dark-colored (for light backgrounds), so the
    light variant is shown in Dark mode and the dark variant in Light mode.

    When a variant is missing, it is derived from the other one (or from the
    plain ``{name}.png``) by recoloring, so icons stay visible in both modes.
    Returns None if the icon does not exist.
    """
    key = (name, size)
    if key in _CACHE:
        return _CACHE[key]

    light = _variant(name, "light")  # light-colored icon  -> Dark mode
    dark = _variant(name, "dark")    # dark-colored icon   -> Light mode

    if light is None and dark is None:
        plain = _load_raw(name)
        if plain is None:
            _CACHE[key] = None
            return None
        dark = plain
        light = _colorize(plain, (255, 255, 255))
    else:
        if light is None:
            light = _colorize(dark, (255, 255, 255))
        if dark is None:
            dark = _colorize(light, (0, 0, 0))

    photo = ctk.CTkImage(light_image=dark, dark_image=light, size=size)
    _CACHE[key] = photo
    return photo
