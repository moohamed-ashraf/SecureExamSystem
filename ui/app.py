"""Desktop UI — separate Instructor and Student portals."""

from __future__ import annotations

import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from aes.aes_main import AES
from hybrid.hybrid_system import EncryptedPackage, HybridCryptosystem, bytes_to_hex
from rsa.rsa_main import RSA
from ui.theme import (
    COLORS,
    FONTS,
    apply_theme,
    build_header,
    build_role_banner,
    configure_scroll_canvas,
    style_text_widget,
)


KEYS_DIR = "keys"
SUBMISSIONS_DIR = "submissions"
DECRYPTED_DIR = "decrypted"
DEFAULT_PUBLIC = os.path.join(KEYS_DIR, "instructor_public.json")
DEFAULT_PRIVATE = os.path.join(KEYS_DIR, "instructor_private.json")

INSTRUCTIONS_TEXT = """
═══════════════════════════════════════════════════════════════════
  SECURE EXAM SUBMISSION SYSTEM — USER GUIDE
  Hybrid Cryptosystem: RSA + AES (implemented from scratch)
═══════════════════════════════════════════════════════════════════

OVERVIEW
────────
• AES encrypts the exam file/message (fast, for large data).
• RSA encrypts only the AES session key (small, uses public/private keys).
• Students CANNOT decrypt submissions — only the instructor can.

Folders created automatically:
  keys/          → RSA public & private key files
  submissions/   → Encrypted .submission packages from students
  decrypted/     → Decrypted exam files (instructor saves here)


═══════════════════════════════════════════════════════════════════
  PART A — INSTRUCTOR (Instructor Portal tab)
═══════════════════════════════════════════════════════════════════

STEP 1: Generate RSA keys (one time per course)
  1. Open tab: Instructor Portal
  2. Click: Generate RSA Key Pair (2048-bit)
  3. Wait 10–30 seconds
  4. Keys saved to:
       keys/instructor_public.json   ← SHARE with students
       keys/instructor_private.json ← KEEP SECRET, never share

STEP 2: Share public key with students
  1. Click: Copy Public Key for Students
  2. Save/copy instructor_public.json
  3. Give this file to every student (email, LMS, USB, etc.)
  ⚠ Never share instructor_private.json

STEP 3: Receive encrypted submission
  1. Student sends you a file: STU-XXX_filename.submission
  2. Click Browse → select the .submission file
  3. Click Load Submission
  4. Preview shows encrypted AES key and ciphertext (Base64)

STEP 4: Decrypt and read exam
  1. Click Decrypt Submission (uses PRIVATE key)
  2. System: RSA decrypts AES key → AES decrypts exam
  3. Read decrypted content in the text box
  4. Click Save Decrypted Exam File to export original exam

Instructor checklist:
  ☐ Generate keys
  ☐ Share public key only
  ☐ Load .submission file
  ☐ Decrypt
  ☐ Save decrypted exam


═══════════════════════════════════════════════════════════════════
  PART B — STUDENT (Student Portal tab)
═══════════════════════════════════════════════════════════════════

STEP 1: Load instructor public key
  1. Open tab: Student Portal
  2. Set path to instructor_public.json (from your instructor)
  3. Click Verify Key

STEP 2: Prepare exam
  1. Enter your Student ID (e.g. STU-001)
  2. Either:
     • Type exam answers in the text box, OR
     • Click Upload / Load Exam File (pdf, txt, etc.)

STEP 3: Encrypt
  1. Click Encrypt Submission
  2. System will:
     • Generate random AES session key
     • AES-CBC encrypt your exam
     • RSA encrypt AES key with instructor PUBLIC key
  3. View encrypted output in sections 4 (AES key, IV, ciphertext)

STEP 4: Send to instructor
  1. Click Send / Save Package
  2. File saved to: submissions/STU-XXX_filename.submission
  3. Send this .submission file to instructor (email, LMS, etc.)

Student checklist:
  ☐ Load instructor public key
  ☐ Enter ID + exam content
  ☐ Encrypt
  ☐ Send / Save package
  ☐ Deliver .submission file to instructor

⚠ Students cannot decrypt — no private key.


═══════════════════════════════════════════════════════════════════
  PART C — FULL WORKFLOW (both roles)
═══════════════════════════════════════════════════════════════════

  INSTRUCTOR                    STUDENT
  ──────────                    ───────
  Generate RSA keys
  Share public key      ──────► Load public key
                                Encrypt exam
                                Save .submission
  Load .submission      ◄────── Send file
  Decrypt with private key
  Read original exam


═══════════════════════════════════════════════════════════════════
  PART D — CRYPTO DEMO TAB
═══════════════════════════════════════════════════════════════════

Optional tests for your report/demo video:
  • AES-128 Block Demo — one block encrypt/decrypt
  • RSA Demo — small message with RSA
  • Full Hybrid Demo — complete workflow test


═══════════════════════════════════════════════════════════════════
  PART E — RUN FROM TERMINAL
═══════════════════════════════════════════════════════════════════

  cd SecureExamSystem
  py main.py              → Open this GUI
  py main.py --mode demo  → Console demo only


═══════════════════════════════════════════════════════════════════
  PART F — TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════

  "Public key not found"
    → Instructor must generate keys first, or student needs correct path.

  "Decryption failed"
    → Wrong private key, or submission encrypted with different public key.

  "Student ID required"
    → Enter Student ID before encrypting.

  Key generation slow
    → Normal for RSA-2048; wait up to 30 seconds.


═══════════════════════════════════════════════════════════════════
  KEYS SUMMARY
═══════════════════════════════════════════════════════════════════

  Key / Data              Who has it        Used for
  ─────────────────────────────────────────────────────────
  RSA public (n, e)       Everyone          Encrypt AES session key
  RSA private (n, d)      Instructor only   Decrypt AES session key
  AES session key         Per submission    Encrypt/decrypt exam
  .submission file        Student → Inst.   Stores all encrypted data

═══════════════════════════════════════════════════════════════════
"""


def ensure_directories() -> None:
    for directory in (KEYS_DIR, SUBMISSIONS_DIR, DECRYPTED_DIR):
        os.makedirs(directory, exist_ok=True)


def _bind_mousewheel(widget: tk.Misc) -> None:
    """Mouse wheel does not work on Windows Text widgets unless bound explicitly."""

    def _scroll(event: tk.Event) -> str:
        if event.num == 4:
            widget.yview_scroll(-3, "units")
        elif event.num == 5:
            widget.yview_scroll(3, "units")
        else:
            widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    widget.bind("<MouseWheel>", _scroll)
    widget.bind("<Button-4>", _scroll)
    widget.bind("<Button-5>", _scroll)
    widget.bind("<Button-1>", lambda _e: widget.focus_set(), add="+")


def _make_scrolled_text(
    parent: tk.Misc,
    *,
    readonly: bool = False,
    variant: str = "default",
    **kwargs,
) -> scrolledtext.ScrolledText:
    widget = scrolledtext.ScrolledText(parent, **kwargs)
    style_text_widget(widget, variant=variant, readonly=readonly or kwargs.get("state") == "disabled")
    _bind_mousewheel(widget)
    if readonly:
        widget.bind("<Key>", lambda _e: "break")
    return widget


def _wrap_scrollable(parent: ttk.Frame) -> ttk.Frame:
    """Wrap a notebook tab in a vertical scroll area. Returns the inner content frame."""
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    canvas = tk.Canvas(parent, highlightthickness=0, borderwidth=0)
    configure_scroll_canvas(canvas)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    inner = ttk.Frame(canvas)
    inner_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _refresh_scroll_region(_event: tk.Event | None = None) -> None:
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event: tk.Event) -> None:
        canvas.itemconfig(inner_id, width=event.width)

    def _scroll_canvas(event: tk.Event) -> str:
        if event.num == 4:
            canvas.yview_scroll(-3, "units")
        elif event.num == 5:
            canvas.yview_scroll(3, "units")
        else:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    inner.bind("<Configure>", _refresh_scroll_region, add="+")
    canvas.bind("<Configure>", _on_canvas_configure)

    def _bind_scroll(widget: tk.Misc) -> None:
        if isinstance(widget, (scrolledtext.ScrolledText, tk.Text)):
            return
        widget.bind("<MouseWheel>", _scroll_canvas)
        widget.bind("<Button-4>", _scroll_canvas)
        widget.bind("<Button-5>", _scroll_canvas)
        for child in widget.winfo_children():
            _bind_scroll(child)

    def _bind_all_scroll() -> None:
        _bind_scroll(canvas)
        _bind_scroll(inner)

    inner._scroll_refresh = _refresh_scroll_region  # type: ignore[attr-defined]
    inner._scroll_bind_all = _bind_all_scroll  # type: ignore[attr-defined]
    _bind_all_scroll()
    return inner


def _finish_scrollable_tab(parent: ttk.Frame) -> None:
    if hasattr(parent, "_scroll_bind_all"):
        parent._scroll_bind_all()
        parent._scroll_refresh()


class SecureExamApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("SecureExamSystem")
        self.geometry("1080x860")
        self.minsize(960, 740)

        apply_theme(self)
        ensure_directories()

        # Instructor
        self.public_key_path = tk.StringVar(value=DEFAULT_PUBLIC)
        self.private_key_path = tk.StringVar(value=DEFAULT_PRIVATE)

        # Student (public key only)
        self.student_public_key_path = tk.StringVar(value=DEFAULT_PUBLIC)
        self.student_id = tk.StringVar(value="STU-001")
        self.student_file_path = tk.StringVar()
        self.instructor_package_path = tk.StringVar()

        self._current_package: EncryptedPackage | None = None
        self._last_decrypted: bytes | None = None

        self._build_ui()
        self._log("Open the Instructions tab for a step-by-step guide.")

    def _build_ui(self) -> None:
        build_header(self)

        content = ttk.Frame(self, padding=(16, 12, 16, 0))
        content.pack(fill="both", expand=True)

        notebook = ttk.Notebook(content)
        notebook.pack(fill="both", expand=True)

        instructions_frame = ttk.Frame(notebook, padding=(4, 12, 4, 4))
        instructor_frame = ttk.Frame(notebook, padding=(4, 12, 4, 4))
        student_frame = ttk.Frame(notebook, padding=(4, 12, 4, 4))
        demo_frame = ttk.Frame(notebook, padding=(4, 12, 4, 4))

        notebook.add(instructions_frame, text="Instructions")
        notebook.add(instructor_frame, text="Instructor Portal")
        notebook.add(student_frame, text="Student Portal")
        notebook.add(demo_frame, text="Crypto Demo")

        self._build_instructions_tab(_wrap_scrollable(instructions_frame))
        self._build_instructor_tab(_wrap_scrollable(instructor_frame))
        self._build_student_tab(_wrap_scrollable(student_frame))
        self._build_demo_tab(_wrap_scrollable(demo_frame))

        log_frame = ttk.Frame(self, padding=(16, 8, 16, 14))
        log_frame.pack(fill="x")
        ttk.Label(log_frame, text="Activity Log", style="LogTitle.TLabel").pack(anchor="w", pady=(0, 6))
        self.log_box = _make_scrolled_text(log_frame, height=6, wrap="word", font=FONTS["log"], variant="log")
        self.log_box.pack(fill="x")

    def _build_instructions_tab(self, parent: ttk.Frame) -> None:
        intro = tk.Frame(
            parent,
            bg=COLORS["primary_light"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        intro.pack(fill="x", pady=(0, 16))
        tk.Label(
            intro,
            text="How to Use SecureExamSystem",
            font=FONTS["heading"],
            fg=COLORS["primary"],
            bg=COLORS["primary_light"],
        ).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(
            intro,
            text="Follow the steps below for your role. All tabs are scrollable.",
            font=FONTS["small"],
            fg=COLORS["text_secondary"],
            bg=COLORS["primary_light"],
        ).pack(anchor="w", padx=16, pady=(0, 14))

        body = tk.Label(
            parent,
            text=INSTRUCTIONS_TEXT.strip(),
            wraplength=820,
            justify="left",
            font=FONTS["mono_small"],
            fg=COLORS["text"],
            bg=COLORS["bg"],
            anchor="nw",
        )
        body.pack(anchor="w", fill="x")
        parent.bind("<Configure>", lambda e: body.configure(wraplength=max(e.width - 16, 320)), add="+")
        _finish_scrollable_tab(parent)

    def _role_banner(self, parent: ttk.Frame, title: str, detail: str, accent: str, accent_bg: str) -> None:
        build_role_banner(parent, title, detail, accent, accent_bg)

    def _build_instructor_tab(self, parent: ttk.Frame) -> None:
        self._role_banner(
            parent,
            "Instructor Role",
            "Generate RSA keys, keep the private key secret, and decrypt student submissions. "
            "RSA decrypts the AES session key; AES decrypts the exam file.",
            COLORS["instructor"],
            COLORS["instructor_light"],
        )

        keys_lf = ttk.LabelFrame(parent, text="Step 1 — RSA Key Management", padding=14, style="Card.TLabelframe")
        keys_lf.pack(fill="x", pady=(0, 10))

        for label, var, browse in (
            ("Public key (share with students):", self.public_key_path, self._browse_public_key),
            ("Private key (keep secret):", self.private_key_path, self._browse_private_key),
        ):
            row = ttk.Frame(keys_lf, style="Card.TFrame")
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, width=28, style="Card.TLabel").pack(side="left")
            ttk.Entry(row, textvariable=var).pack(side="left", fill="x", expand=True, padx=(4, 8))
            ttk.Button(row, text="Browse", style="Secondary.TButton", command=browse).pack(side="left")

        btn_row = ttk.Frame(keys_lf, style="Card.TFrame")
        btn_row.pack(fill="x", pady=(10, 4))
        ttk.Button(
            btn_row,
            text="Generate RSA Key Pair (2048-bit)",
            style="Primary.TButton",
            command=self._generate_keys_async,
        ).pack(side="left")
        ttk.Button(btn_row, text="Load Keys", style="Secondary.TButton", command=self._load_instructor_keys).pack(
            side="left", padx=(8, 0)
        )
        ttk.Button(
            btn_row,
            text="Copy Public Key for Students",
            style="Secondary.TButton",
            command=self._copy_public_key_for_students,
        ).pack(side="left", padx=(8, 0))
        self.instructor_key_status = ttk.Label(
            keys_lf, text="Status: No keys loaded", style="Status.TLabel"
        )
        self.instructor_key_status.pack(anchor="w", pady=(6, 0))

        recv_lf = ttk.LabelFrame(
            parent, text="Step 2 — Receive Encrypted Submission", padding=14, style="Card.TLabelframe"
        )
        recv_lf.pack(fill="x", pady=(0, 10))

        row = ttk.Frame(recv_lf, style="Card.TFrame")
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Submission file:", width=14, style="Card.TLabel").pack(side="left")
        ttk.Entry(row, textvariable=self.instructor_package_path).pack(
            side="left", fill="x", expand=True, padx=(4, 8)
        )
        ttk.Button(row, text="Browse", style="Secondary.TButton", command=self._instructor_browse_submission).pack(
            side="left"
        )
        ttk.Button(
            row, text="Load Submission", style="Primary.TButton", command=self._instructor_load_submission
        ).pack(side="left", padx=(8, 0))

        dec_lf = ttk.LabelFrame(
            parent, text="Step 3 — Decrypt (Private Key + AES)", padding=14, style="Card.TLabelframe"
        )
        dec_lf.pack(fill="x", pady=(0, 10))

        row = ttk.Frame(dec_lf, style="Card.TFrame")
        row.pack(fill="x", pady=4)
        ttk.Button(row, text="Decrypt Submission", style="Primary.TButton", command=self._instructor_decrypt).pack(
            side="left"
        )
        ttk.Button(
            row,
            text="Save Decrypted Exam File",
            style="Secondary.TButton",
            command=self._instructor_save_decrypted,
        ).pack(side="left", padx=(8, 0))

        ttk.Label(parent, text="Decrypted exam (original content):", style="Section.TLabel").pack(
            anchor="w", pady=(4, 6)
        )
        self.instructor_decrypted_box = _make_scrolled_text(
            parent,
            height=10,
            wrap="word",
            font=FONTS["body"],
            state="disabled",
            variant="code",
        )
        self.instructor_decrypted_box.pack(fill="x")

        preview_lf = ttk.LabelFrame(
            parent, text="Encrypted package preview (read-only)", padding=12, style="Card.TLabelframe"
        )
        preview_lf.pack(fill="x", pady=(10, 0))
        self.instructor_preview_box = _make_scrolled_text(
            preview_lf, height=4, wrap="word", font=FONTS["mono_small"], state="disabled", variant="code"
        )
        self.instructor_preview_box.pack(fill="x")
        _finish_scrollable_tab(parent)

    def _build_student_tab(self, parent: ttk.Frame) -> None:
        self._role_banner(
            parent,
            "Student Role",
            "Encrypt the exam with AES using a random session key, then protect that key with the "
            "instructor public key only. You cannot decrypt submissions without the private key.",
            COLORS["student"],
            COLORS["student_light"],
        )

        key_lf = ttk.LabelFrame(
            parent, text="Step 1 — Load Instructor Public Key", padding=14, style="Card.TLabelframe"
        )
        key_lf.pack(fill="x", pady=(0, 10))

        row = ttk.Frame(key_lf, style="Card.TFrame")
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Public key file:", width=14, style="Card.TLabel").pack(side="left")
        ttk.Entry(row, textvariable=self.student_public_key_path).pack(
            side="left", fill="x", expand=True, padx=(4, 8)
        )
        ttk.Button(row, text="Browse", style="Secondary.TButton", command=self._browse_student_public_key).pack(
            side="left"
        )
        ttk.Button(
            row, text="Verify Key", style="Primary.TButton", command=self._student_verify_public_key
        ).pack(side="left", padx=(8, 0))

        submit_lf = ttk.LabelFrame(
            parent, text="Step 2 — Prepare Exam Submission", padding=14, style="Card.TLabelframe"
        )
        submit_lf.pack(fill="x", pady=(0, 10))

        row = ttk.Frame(submit_lf, style="Card.TFrame")
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Student ID:", width=14, style="Card.TLabel").pack(side="left")
        ttk.Entry(row, textvariable=self.student_id, width=24).pack(side="left")

        ttk.Label(submit_lf, text="Exam content (UTF-8) or load file:", style="Card.TLabel").pack(
            anchor="w", pady=(10, 6)
        )
        self.student_message_box = _make_scrolled_text(
            submit_lf, height=6, wrap="word", font=FONTS["body"]
        )
        self.student_message_box.pack(fill="x", pady=(0, 8))
        self.student_message_box.insert("1.0", "My exam answers for the cryptography course.")

        row = ttk.Frame(submit_lf, style="Card.TFrame")
        row.pack(fill="x")
        ttk.Button(row, text="Upload / Load Exam File", style="Secondary.TButton", command=self._student_load_file).pack(
            side="left"
        )
        self.student_file_label = ttk.Label(row, text="No file selected", style="Status.TLabel")
        self.student_file_label.pack(side="left", padx=(12, 0))

        action_lf = ttk.LabelFrame(parent, text="Step 3 — Encrypt & Send", padding=14, style="Card.TLabelframe")
        action_lf.pack(fill="x", pady=(0, 10))

        row = ttk.Frame(action_lf, style="Card.TFrame")
        row.pack(fill="x", pady=4)
        ttk.Button(row, text="Encrypt Submission", style="Success.TButton", command=self._student_encrypt).pack(
            side="left"
        )
        ttk.Button(row, text="Send / Save Package", style="Primary.TButton", command=self._student_send).pack(
            side="left", padx=(8, 0)
        )

        out_lf = ttk.LabelFrame(
            parent, text="Step 4 — Encrypted Output (send this to instructor)", padding=14, style="Card.TLabelframe"
        )
        out_lf.pack(fill="x")

        ttk.Label(out_lf, text="Encrypted AES session key (RSA + Base64):", style="Subheading.TLabel").pack(
            anchor="w"
        )
        self.student_enc_key_box = _make_scrolled_text(
            out_lf, height=3, wrap="word", font=FONTS["mono_small"], state="disabled", variant="code"
        )
        self.student_enc_key_box.pack(fill="x", pady=(4, 8))

        ttk.Label(out_lf, text="Encrypted exam data — IV (Base64):", style="Subheading.TLabel").pack(anchor="w")
        self.student_iv_box = _make_scrolled_text(
            out_lf, height=2, wrap="word", font=FONTS["mono_small"], state="disabled", variant="code"
        )
        self.student_iv_box.pack(fill="x", pady=(4, 8))

        ttk.Label(out_lf, text="Encrypted exam data — Ciphertext (Base64):", style="Subheading.TLabel").pack(
            anchor="w"
        )
        self.student_cipher_box = _make_scrolled_text(
            out_lf, height=4, wrap="word", font=FONTS["mono_small"], state="disabled", variant="code"
        )
        self.student_cipher_box.pack(fill="x")

        self.student_saved_path = tk.StringVar(value="")
        self.student_save_label = ttk.Label(out_lf, textvariable=self.student_saved_path, style="Success.TLabel")
        self.student_save_label.pack(anchor="w", pady=(8, 0))
        _finish_scrollable_tab(parent)

    def _build_demo_tab(self, parent: ttk.Frame) -> None:
        intro = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        intro.pack(fill="x", pady=(0, 14))
        tk.Label(
            intro,
            text="Crypto Component Tests",
            font=FONTS["heading"],
            fg=COLORS["text"],
            bg=COLORS["surface"],
        ).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(
            intro,
            text="Run low-level AES, RSA, and full hybrid workflow demos for your report or video.",
            font=FONTS["small"],
            fg=COLORS["text_secondary"],
            bg=COLORS["surface"],
        ).pack(anchor="w", padx=16, pady=(0, 14))

        btn_row = ttk.Frame(parent)
        btn_row.pack(fill="x", pady=(0, 12))
        ttk.Button(btn_row, text="AES-128 Block Demo", style="Secondary.TButton", command=self._demo_aes).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(btn_row, text="RSA Demo", style="Secondary.TButton", command=self._demo_rsa).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(btn_row, text="Full Hybrid Demo", style="Primary.TButton", command=self._demo_hybrid).pack(
            side="left"
        )

        ttk.Label(parent, text="Demo output", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        self.demo_output = _make_scrolled_text(parent, height=16, wrap="word", font=FONTS["log"], variant="demo")
        self.demo_output.pack(fill="x")
        _finish_scrollable_tab(parent)

    def _set_readonly_text(self, widget: scrolledtext.ScrolledText, content: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")
        _bind_mousewheel(widget)

    def _log(self, message: str) -> None:
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def _demo_log(self, message: str) -> None:
        self.demo_output.insert("end", message + "\n")
        self.demo_output.see("end")

    # --- Instructor ---

    def _browse_public_key(self) -> None:
        path = filedialog.askopenfilename(initialdir=KEYS_DIR, filetypes=[("JSON", "*.json")])
        if path:
            self.public_key_path.set(path)

    def _browse_private_key(self) -> None:
        path = filedialog.askopenfilename(initialdir=KEYS_DIR, filetypes=[("JSON", "*.json")])
        if path:
            self.private_key_path.set(path)

    def _generate_keys_async(self) -> None:
        def task() -> None:
            try:
                self._log("[Instructor] Generating RSA-2048 key pair...")
                self.instructor_key_status.configure(text="Status: Generating...", style="Warning.TLabel")
                rsa = RSA.generate_keys(bits=2048)
                pub = self.public_key_path.get()
                priv = self.private_key_path.get()
                rsa.save_public_key(pub)
                rsa.save_private_key(priv)
                self.student_public_key_path.set(pub)
                self.instructor_key_status.configure(text="Status: Keys generated and saved", style="Success.TLabel")
                self._log(f"[Instructor] Public key: {pub}")
                self._log(f"[Instructor] Private key: {priv}")
                messagebox.showinfo("Instructor", "RSA key pair generated.\nShare the PUBLIC key with students.")
            except Exception as exc:
                self.instructor_key_status.configure(text="Status: Error", style="Danger.TLabel")
                messagebox.showerror("Error", str(exc))

        threading.Thread(target=task, daemon=True).start()

    def _load_instructor_keys(self) -> None:
        try:
            pub = RSA.load_public_key(self.public_key_path.get())
            priv = RSA.load_private_key(self.private_key_path.get())
            if pub.n != priv.n:
                raise ValueError("Public and private keys do not match")
            self.instructor_key_status.configure(text="Status: Keys loaded", style="Success.TLabel")
            self._log("[Instructor] Keys loaded.")
            messagebox.showinfo("Instructor", "Keys loaded successfully.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _copy_public_key_for_students(self) -> None:
        pub = self.public_key_path.get()
        if not os.path.isfile(pub):
            messagebox.showwarning("Warning", "Generate or load keys first.")
            return
        dest = filedialog.asksaveasfilename(
            title="Save public key for students",
            initialdir=KEYS_DIR,
            initialfile="instructor_public.json",
            filetypes=[("JSON", "*.json")],
        )
        if dest:
            shutil.copy(pub, dest)
            self.student_public_key_path.set(dest)
            self._log(f"[Instructor] Public key copied for students: {dest}")
            messagebox.showinfo("Done", f"Public key saved to:\n{dest}\n\nGive this file to students.")

    def _instructor_browse_submission(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=SUBMISSIONS_DIR,
            filetypes=[("Submission", "*.submission"), ("JSON", "*.json")],
        )
        if path:
            self.instructor_package_path.set(path)

    def _instructor_load_submission(self) -> None:
        path = self.instructor_package_path.get()
        if not path:
            messagebox.showwarning("Warning", "Select a submission file.")
            return
        try:
            package = EncryptedPackage.load(path)
            self._current_package = package
            preview = (
                f"Student: {package.student_id}\n"
                f"File: {package.filename}\n"
                f"AES key (RSA, Base64): {package.encrypted_aes_key_b64[:60]}...\n"
                f"IV: {package.iv_b64[:40]}...\n"
                f"Ciphertext: {package.ciphertext_b64[:60]}..."
            )
            self._set_readonly_text(self.instructor_preview_box, preview)
            self._log(f"[Instructor] Loaded submission: {path}")
            messagebox.showinfo("Instructor", "Submission loaded. Click Decrypt Submission.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _instructor_decrypt(self) -> None:
        try:
            if self._current_package is None:
                path = self.instructor_package_path.get()
                if not path:
                    raise ValueError("Load a submission file first")
                self._current_package = EncryptedPackage.load(path)

            private_key = RSA.load_private_key(self.private_key_path.get())
            plaintext = HybridCryptosystem.decrypt_submission(self._current_package, private_key)
            self._last_decrypted = plaintext

            try:
                text = plaintext.decode("utf-8")
            except UnicodeDecodeError:
                text = f"[Binary file: {len(plaintext)} bytes]\nHex preview: {bytes_to_hex(plaintext[:64])}..."

            self._set_readonly_text(self.instructor_decrypted_box, text)
            self._log(
                f"[Instructor] Decrypted submission from {self._current_package.student_id}"
            )
            messagebox.showinfo("Instructor", "Decryption successful.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _instructor_save_decrypted(self) -> None:
        if self._last_decrypted is None:
            messagebox.showwarning("Warning", "Decrypt a submission first.")
            return
        name = self._current_package.filename if self._current_package else "exam_decrypted.txt"
        path = filedialog.asksaveasfilename(initialdir=DECRYPTED_DIR, initialfile=name)
        if path:
            with open(path, "wb") as f:
                f.write(self._last_decrypted)
            self._log(f"[Instructor] Saved decrypted file: {path}")
            messagebox.showinfo("Instructor", f"Saved to:\n{path}")

    # --- Student ---

    def _browse_student_public_key(self) -> None:
        path = filedialog.askopenfilename(initialdir=KEYS_DIR, filetypes=[("JSON", "*.json")])
        if path:
            self.student_public_key_path.set(path)

    def _student_verify_public_key(self) -> None:
        try:
            RSA.load_public_key(self.student_public_key_path.get())
            self._log("[Student] Instructor public key verified.")
            messagebox.showinfo("Student", "Instructor public key is valid.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _student_load_file(self) -> None:
        path = filedialog.askopenfilename(title="Upload exam file")
        if not path:
            return
        self.student_file_path.set(path)
        with open(path, "rb") as f:
            data = f.read()
        try:
            preview = data.decode("utf-8")
            if len(preview) > 8000:
                preview = preview[:8000] + "\n... (truncated preview)"
        except UnicodeDecodeError:
            preview = f"[Binary file: {os.path.basename(path)}, {len(data)} bytes]"
        self.student_message_box.delete("1.0", "end")
        self.student_message_box.insert("1.0", preview)
        self.student_file_label.configure(text=f"Loaded: {os.path.basename(path)}")
        self._log(f"[Student] Loaded file: {path}")

    def _student_get_plaintext(self) -> tuple[bytes, str]:
        student_id = self.student_id.get().strip()
        if not student_id:
            raise ValueError("Student ID is required")

        if self.student_file_path.get():
            path = self.student_file_path.get()
            with open(path, "rb") as f:
                return f.read(), os.path.basename(path)

        text = self.student_message_box.get("1.0", "end").strip()
        if not text:
            raise ValueError("Enter exam content or upload a file")
        return text.encode("utf-8"), f"{student_id}_exam.txt"

    def _student_encrypt(self) -> None:
        try:
            public_key = RSA.load_public_key(self.student_public_key_path.get())
            plaintext, filename = self._student_get_plaintext()
            student_id = self.student_id.get().strip()

            package = HybridCryptosystem.encrypt_submission(
                plaintext, student_id, filename, public_key
            )
            self._current_package = package

            self._set_readonly_text(self.student_enc_key_box, package.encrypted_aes_key_b64)
            self._set_readonly_text(self.student_iv_box, package.iv_b64)
            self._set_readonly_text(self.student_cipher_box, package.ciphertext_b64)
            self.student_saved_path.set("Not saved yet — click Send / Save Package")

            self._log(f"[Student] Encrypted (AES exam + RSA session key)")
            messagebox.showinfo(
                "Student",
                "Encryption complete.\n\n"
                "AES encrypted your exam.\n"
                "RSA encrypted the AES key with instructor public key.\n"
                "Click Send / Save Package to deliver to instructor.",
            )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def _student_send(self) -> None:
        if self._current_package is None:
            messagebox.showwarning("Warning", "Encrypt the submission first.")
            return
        student_id = self.student_id.get().strip()
        filename = self._current_package.filename
        out_path = os.path.join(SUBMISSIONS_DIR, f"{student_id}_{filename}.submission")
        self._current_package.save(out_path)
        self.instructor_package_path.set(out_path)
        self.student_saved_path.set(f"Saved: {out_path}")
        self._log(f"[Student] Submission sent/saved: {out_path}")
        messagebox.showinfo(
            "Student",
            f"Submission saved to:\n{out_path}\n\nDeliver this file to the instructor.",
        )

    # --- Demo ---

    def _demo_aes(self) -> None:
        self.demo_output.delete("1.0", "end")
        key = AES.generate_key()
        aes = AES(key)
        plaintext = b"ExamAnswer123456"
        ciphertext = aes.encrypt_block(plaintext)
        self._demo_log("=== AES-128 Block Demo ===")
        self._demo_log(f"Match: {plaintext == aes.decrypt_block(ciphertext)}")

    def _demo_rsa(self) -> None:
        self.demo_output.delete("1.0", "end")
        rsa = RSA.generate_keys(bits=1024)
        message = b"AES-KEY-16BYTES!"
        self._demo_log("=== RSA Demo ===")
        self._demo_log(f"Match: {message == rsa.decrypt(rsa.encrypt(message))}")

    def _demo_hybrid(self) -> None:
        self.demo_output.delete("1.0", "end")
        rsa = RSA.generate_keys(bits=1024)
        exam = b"Student exam answers."
        package = HybridCryptosystem.encrypt_submission(exam, "STU-DEMO", "demo.txt", rsa)
        recovered = HybridCryptosystem.decrypt_submission(package, rsa)
        self._demo_log(f"Hybrid Match: {exam == recovered}")


def run_ui() -> None:
    SecureExamApp().mainloop()
