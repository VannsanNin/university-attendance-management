import customtkinter as ctk

# ---------------------------------------------------------------------------
# Design tokens — all app colors live here. Both palettes share the same keys
# so any widget can just do theme.c("card_bg") and it re-themes automatically.
# ---------------------------------------------------------------------------

DARK = {
    # Surfaces
    "bg": "#0F172A",
    "bg_dark": "#0F172A",
    "surface": "#1E293B",
    "surface_alt": "#1D1D2C",
    "hover": "#1D1D2C",
    "hover_bg": "#1E293B",
    "border": "#334155",
    "field_bg": "#1E293B",
    "field_border": "#334155",
    "segmented_bg": "#0F172A",
    "card_bg": "#1E293B",
    "card_border": "#334155",
    "card_alt": "#1E1E2E",
    "border_alt": "#2A2A3C",

    # Buttons / accents
    "primary": "#0EA5E9",
    "primary_hover": "#0284C7",
    "accent": "#6C7CFF",
    "accent_hover": "#5766E8",
    "accent_muted": "#2C2E4A",
    "info": "#3B82F6",
    "success": "#10B981",
    "success_hover": "#059669",
    "danger": "#EF4444",
    "danger_hover": "#DC2626",
    "warning": "#F59E0B",
    "neutral": "#334155",
    "neutral_btn": "#334155",
    "neutral_hover": "#475569",
    "active": "#0EA5E9",
    "active_bg": "#0EA5E9",
    "active_text": "#FFFFFF",

    # Text
    "text": "#F8FAFC",
    "text_main": "#F8FAFC",
    "text_muted": "#94A3B8",
    "text_faint": "#5C5C74",
    "text_bright": "#FFFFFF",
    "on_accent": "#FFFFFF",
    "text_subtle": "#A0A0B8",
    "text_table": "#9CA3AF",
    "text_body": "#D1D5DB",
    "placeholder": "#6C6C8A",
    "error_text": "#FF5555",
    "white": "#FFFFFF",

    # ttk.Treeview tables
    "table_bg": "#1E293B",
    "table_fg": "#F8FAFC",
    "table_head_bg": "#0F172A",
    "table_head_fg": "#94A3B8",
    "table_selected": "#334155",
    "table_selected_fg": "#FFFFFF",
    "table_head_active": "#1E293B",

    # Dashboard charts / stat accents
    "chart_1": "#3B82F6",
    "chart_2": "#10B981",
    "chart_3": "#F59E0B",
    "chart_4": "#8B5CF6",
    "chart_5": "#14B8A6",

    # Login screen
    "login_sidebar": "#1E1E2E",
    "login_form": "#14141F",
    "login_title": "#FFFFFF",
    "login_sub": "#A0A0B8",
    "login_label": "#D1D1E0",
    "login_placeholder": "#6C6C8A",
    "login_blue": "#3B82F6",
    "login_blue_hover": "#2563EB",
    "login_border": "#2A2A3C",
    "login_error": "#FF5555",

    # Sidebar
    "sidebar_bg": "#0F172A",
    "sidebar_card": "#1E293B",
    "sidebar_hover": "#1E293B",
    "sidebar_border": "#1E293B",
    "sidebar_text": "#F8FAFC",
    "sidebar_text_muted": "#94A3B8",
    "sidebar_active": "#0EA5E9",
    "sidebar_active_text": "#FFFFFF",
    "sidebar_danger": "#EF4444",
    "sidebar_danger_hover": "#DC2626",

    # Misc semantic colors
    "green": "#2E8B57",
    "lightcoral": "#CD5C5C",
    "gold": "#DAA520",
    "steelblue": "#4682B4",
    "gray_soft": "#888888",
    "success_green": "#3DD68C",
}

LIGHT = {
    # Surfaces
    "bg": "#F1F5F9",
    "bg_dark": "#F1F5F9",
    "surface": "#FFFFFF",
    "surface_alt": "#E2E8F0",
    "hover": "#E2E8F0",
    "hover_bg": "#E2E8F0",
    "border": "#CBD5E1",
    "field_bg": "#FFFFFF",
    "field_border": "#CBD5E1",
    "segmented_bg": "#E2E8F0",
    "card_bg": "#FFFFFF",
    "card_border": "#CBD5E1",
    "card_alt": "#FFFFFF",
    "border_alt": "#E2E8F0",

    # Buttons / accents
    "primary": "#0EA5E9",
    "primary_hover": "#0284C7",
    "accent": "#4F5FE6",
    "accent_hover": "#4453CE",
    "accent_muted": "#E0E4FF",
    "info": "#2563EB",
    "success": "#059669",
    "success_hover": "#047857",
    "danger": "#DC2626",
    "danger_hover": "#B91C1C",
    "warning": "#D97706",
    "neutral": "#E2E8F0",
    "neutral_btn": "#E2E8F0",
    "neutral_hover": "#CBD5E1",
    "active": "#0284C7",
    "active_bg": "#0EA5E9",
    "active_text": "#FFFFFF",

    # Text
    "text": "#0F172A",
    "text_main": "#0F172A",
    "text_muted": "#64748B",
    "text_faint": "#94A3B8",
    "text_bright": "#0F172A",
    "on_accent": "#FFFFFF",
    "text_subtle": "#475569",
    "text_table": "#64748B",
    "text_body": "#334155",
    "placeholder": "#94A3B8",
    "error_text": "#DC2626",
    "white": "#FFFFFF",

    # ttk.Treeview tables
    "table_bg": "#FFFFFF",
    "table_fg": "#0F172A",
    "table_head_bg": "#E2E8F0",
    "table_head_fg": "#475569",
    "table_selected": "#BAE6FD",
    "table_selected_fg": "#0F172A",
    "table_head_active": "#CBD5E1",

    # Dashboard charts / stat accents
    "chart_1": "#3B82F6",
    "chart_2": "#10B981",
    "chart_3": "#F59E0B",
    "chart_4": "#8B5CF6",
    "chart_5": "#14B8A6",

    # Login screen
    "login_sidebar": "#E2E8F0",
    "login_form": "#F8FAFC",
    "login_title": "#0F172A",
    "login_sub": "#64748B",
    "login_label": "#334155",
    "login_placeholder": "#94A3B8",
    "login_blue": "#0EA5E9",
    "login_blue_hover": "#0284C7",
    "login_border": "#CBD5E1",
    "login_error": "#DC2626",

    # Sidebar
    "sidebar_bg": "#FFFFFF",
    "sidebar_card": "#F1F5F9",
    "sidebar_hover": "#E2E8F0",
    "sidebar_border": "#E2E8F0",
    "sidebar_text": "#0F172A",
    "sidebar_text_muted": "#64748B",
    "sidebar_active": "#0EA5E9",
    "sidebar_active_text": "#FFFFFF",
    "sidebar_danger": "#DC2626",
    "sidebar_danger_hover": "#B91C1C",

    # Misc semantic colors
    "green": "#15803D",
    "lightcoral": "#DC2626",
    "gold": "#B45309",
    "steelblue": "#2563EB",
    "gray_soft": "#64748B",
    "success_green": "#059669",
}

PALETTES = {"dark": DARK, "light": LIGHT}

colors = DARK


def set_mode(mode):
    """Switch CustomTkinter appearance mode and the active palette."""
    global colors
    m = str(mode).lower()
    if m == "system":
        ctk.set_appearance_mode("system")
        m = ctk.get_appearance_mode().lower()
    else:
        if m not in PALETTES:
            m = "dark"
        ctk.set_appearance_mode(m)
    colors = PALETTES.get(m, DARK)


def c(key):
    """Look up a color in the active palette."""
    return colors[key]


FONT_FAMILY = "Segoe UI"
FONT_TITLE = ctk.CTkFont(family=FONT_FAMILY, size=26, weight="bold")
FONT_SECTION = ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold")
FONT_LABEL = ctk.CTkFont(family=FONT_FAMILY, size=13)
FONT_HINT = ctk.CTkFont(family=FONT_FAMILY, size=11)
FONT_BUTTON = ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")

# Sidebar-specific
FONT_LOGO = ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold")
FONT_NAV = ctk.CTkFont(family=FONT_FAMILY, size=13)
FONT_NAV_GROUP = ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold")

CARD_RADIUS = 14
FIELD_RADIUS = 8
FIELD_HEIGHT = 36
