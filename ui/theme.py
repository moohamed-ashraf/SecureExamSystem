"""Modern visual theme for the SecureExamSystem desktop UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import scrolledtext, ttk


COLORS: dict[str, str] = {
    "bg": "#f4f6fb",
    "surface": "#ffffff",
    "surface_alt": "#f8fafc",
    "border": "#e2e8f0",
    "text": "#0f172a",
    "text_secondary": "#475569",
    "muted": "#94a3b8",
    "primary": "#4f46e5",
    "primary_dark": "#4338ca",
    "primary_light": "#eef2ff",
    "instructor": "#2563eb",
    "instructor_light": "#eff6ff",
    "student": "#059669",
    "student_light": "#ecfdf5",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "header_from": "#312e81",
    "header_to": "#4f46e5",
    "input_bg": "#ffffff",
    "input_border": "#cbd5e1",
    "log_bg": "#0f172a",
    "log_fg": "#e2e8f0",
    "demo_bg": "#1e293b",
    "demo_fg": "#cbd5e1",
}

FONTS = {
    "family": "Segoe UI",
    "title": ("Segoe UI", 22, "bold"),
    "subtitle": ("Segoe UI", 10),
    "heading": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 10),
    "small": ("Segoe UI", 9),
    "mono": ("Consolas", 10),
    "mono_small": ("Consolas", 9),
    "log": ("Consolas", 9),
}


def apply_theme(root: tk.Tk) -> dict[str, str]:
    """Configure ttk styles and window chrome. Returns the color palette."""
    root.configure(bg=COLORS["bg"])

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    c = COLORS

    style.configure(".", background=c["bg"], foreground=c["text"], font=FONTS["body"])
    style.configure("TFrame", background=c["bg"])
    style.configure("Card.TFrame", background=c["surface"])
    style.configure("TLabel", background=c["bg"], foreground=c["text"], font=FONTS["body"])
    style.configure("Card.TLabel", background=c["surface"], foreground=c["text"], font=FONTS["body"])
    style.configure("CardTitle.TLabel", background=c["surface"], foreground=c["text"], font=FONTS["heading"])
    style.configure("Muted.TLabel", background=c["surface"], foreground=c["text_secondary"], font=FONTS["small"])
    style.configure("Header.TLabel", background=c["header_to"], foreground="#ffffff", font=FONTS["subtitle"])
    style.configure("HeaderTitle.TLabel", background=c["header_to"], foreground="#ffffff", font=FONTS["title"])
    style.configure("Section.TLabel", background=c["bg"], foreground=c["text"], font=FONTS["heading"])
    style.configure("Status.TLabel", background=c["surface"], foreground=c["muted"], font=FONTS["small"])
    style.configure("Success.TLabel", background=c["surface"], foreground=c["success"], font=FONTS["small"])
    style.configure("Warning.TLabel", background=c["surface"], foreground=c["warning"], font=FONTS["small"])
    style.configure("Danger.TLabel", background=c["surface"], foreground=c["danger"], font=FONTS["small"])
    style.configure("Subheading.TLabel", background=c["surface"], foreground=c["text"], font=("Segoe UI", 9, "bold"))
    style.configure("LogTitle.TLabel", background=c["bg"], foreground=c["text"], font=("Segoe UI", 10, "bold"))

    style.configure(
        "Card.TLabelframe",
        background=c["surface"],
        bordercolor=c["border"],
        relief="flat",
        borderwidth=1,
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=c["surface"],
        foreground=c["primary"],
        font=("Segoe UI", 10, "bold"),
    )
    style.configure(
        "TLabelframe",
        background=c["surface"],
        bordercolor=c["border"],
        relief="flat",
    )
    style.configure(
        "TLabelframe.Label",
        background=c["surface"],
        foreground=c["primary"],
        font=("Segoe UI", 10, "bold"),
    )

    style.configure(
        "TNotebook",
        background=c["bg"],
        borderwidth=0,
        tabmargins=[2, 6, 2, 0],
    )
    style.configure(
        "TNotebook.Tab",
        background=c["surface_alt"],
        foreground=c["text_secondary"],
        padding=[18, 10],
        font=("Segoe UI", 10),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", c["surface"]), ("active", c["surface"])],
        foreground=[("selected", c["primary"]), ("active", c["text"])],
        expand=[("selected", [1, 1, 1, 0])],
    )

    style.configure(
        "TEntry",
        fieldbackground=c["input_bg"],
        foreground=c["text"],
        bordercolor=c["input_border"],
        lightcolor=c["input_border"],
        darkcolor=c["input_border"],
        padding=8,
        font=FONTS["body"],
    )
    style.map("TEntry", bordercolor=[("focus", c["primary"])])

    style.configure(
        "TButton",
        background=c["surface"],
        foreground=c["text"],
        bordercolor=c["border"],
        padding=[14, 8],
        font=("Segoe UI", 10),
        focusthickness=0,
    )
    style.map(
        "TButton",
        background=[("active", c["surface_alt"]), ("pressed", c["border"])],
        bordercolor=[("active", c["muted"])],
    )

    style.configure(
        "Primary.TButton",
        background=c["primary"],
        foreground="#ffffff",
        bordercolor=c["primary"],
        padding=[16, 10],
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "Primary.TButton",
        background=[("active", c["primary_dark"]), ("pressed", c["primary_dark"])],
        bordercolor=[("active", c["primary_dark"])],
    )

    style.configure(
        "Success.TButton",
        background=c["student"],
        foreground="#ffffff",
        bordercolor=c["student"],
        padding=[16, 10],
        font=("Segoe UI", 10, "bold"),
    )
    style.map(
        "Success.TButton",
        background=[("active", "#047857"), ("pressed", "#047857")],
    )

    style.configure(
        "Secondary.TButton",
        background=c["primary_light"],
        foreground=c["primary"],
        bordercolor=c["primary_light"],
        padding=[14, 8],
    )
    style.map(
        "Secondary.TButton",
        background=[("active", "#e0e7ff"), ("pressed", "#c7d2fe")],
    )

    style.configure(
        "TScrollbar",
        background=c["surface_alt"],
        troughcolor=c["bg"],
        bordercolor=c["bg"],
        arrowcolor=c["muted"],
    )

    return COLORS


def style_text_widget(
    widget: scrolledtext.ScrolledText | tk.Text,
    *,
    variant: str = "default",
    readonly: bool = False,
) -> None:
    if variant == "log":
        widget.configure(
            bg=COLORS["log_bg"],
            fg=COLORS["log_fg"],
            insertbackground=COLORS["log_fg"],
            selectbackground="#334155",
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=10,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"],
        )
    elif variant == "demo":
        widget.configure(
            bg=COLORS["demo_bg"],
            fg=COLORS["demo_fg"],
            insertbackground=COLORS["demo_fg"],
            selectbackground="#475569",
            relief="flat",
            borderwidth=0,
            padx=12,
            pady=10,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
    elif variant == "code" or readonly:
        widget.configure(
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            selectbackground=COLORS["primary_light"],
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=8,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"],
        )
    else:
        widget.configure(
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["primary"],
            selectbackground=COLORS["primary_light"],
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=8,
            highlightthickness=1,
            highlightbackground=COLORS["input_border"],
            highlightcolor=COLORS["primary"],
        )


def build_header(parent: tk.Misc) -> tk.Frame:
    """Gradient-style header bar."""
    header = tk.Frame(parent, bg=COLORS["header_to"], highlightthickness=0)
    header.pack(fill="x")

    inner = tk.Frame(header, bg=COLORS["header_to"])
    inner.pack(fill="x", padx=24, pady=18)

    title_row = tk.Frame(inner, bg=COLORS["header_to"])
    title_row.pack(fill="x")

    tk.Label(
        title_row,
        text="Secure Exam Submission",
        font=FONTS["title"],
        fg="#ffffff",
        bg=COLORS["header_to"],
    ).pack(side="left")

    badge = tk.Label(
        title_row,
        text="  RSA + AES Hybrid  ",
        font=("Segoe UI", 9, "bold"),
        fg=COLORS["header_to"],
        bg="#c7d2fe",
        padx=4,
        pady=2,
    )
    badge.pack(side="left", padx=(14, 0))

    tk.Label(
        inner,
        text="AES encrypts exam content  ·  RSA protects the session key",
        font=FONTS["subtitle"],
        fg="#c7d2fe",
        bg=COLORS["header_to"],
    ).pack(anchor="w", pady=(6, 0))

    return header


def build_role_banner(parent: ttk.Frame, title: str, detail: str, accent: str, accent_bg: str) -> None:
    """Card-style role description with accent stripe."""
    card = tk.Frame(parent, bg=COLORS["surface"], highlightthickness=1, highlightbackground=COLORS["border"])
    card.pack(fill="x", pady=(0, 14))

    stripe = tk.Frame(card, bg=accent, width=5)
    stripe.pack(side="left", fill="y")
    stripe.pack_propagate(False)

    body = tk.Frame(card, bg=accent_bg, padx=16, pady=14)
    body.pack(side="left", fill="x", expand=True)

    tk.Label(body, text=title, font=FONTS["heading"], fg=COLORS["text"], bg=accent_bg).pack(anchor="w")
    tk.Label(
        body,
        text=detail,
        font=FONTS["body"],
        fg=COLORS["text_secondary"],
        bg=accent_bg,
        wraplength=900,
        justify="left",
    ).pack(anchor="w", pady=(6, 0))


def configure_scroll_canvas(canvas: tk.Canvas) -> None:
    canvas.configure(bg=COLORS["bg"], highlightthickness=0)
