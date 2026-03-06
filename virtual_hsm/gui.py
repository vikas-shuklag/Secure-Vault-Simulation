"""
Virtual HSM — Graphical User Interface
Tkinter-based dashboard for interacting with the Virtual HSM.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import platform
import time

from virtual_hsm.hsm_core import HSMCore

# ─── Color Palette ───────────────────────────────────────────────────
BG_DARK      = "#0d1117"
BG_CARD      = "#161b22"
BG_INPUT     = "#21262d"
FG_TEXT       = "#c9d1d9"
FG_DIM        = "#8b949e"
FG_BRIGHT     = "#f0f6fc"
ACCENT_BLUE   = "#58a6ff"
ACCENT_GREEN  = "#3fb950"
ACCENT_PURPLE = "#bc8cff"
ACCENT_ORANGE = "#d29922"
ACCENT_RED    = "#f85149"
BORDER_COLOR  = "#30363d"

FONT_TITLE    = ("Courier New", 18, "bold")
FONT_SECTION  = ("Courier New", 12, "bold")
FONT_LABEL    = ("Courier New", 10)
FONT_BUTTON   = ("Courier New", 10, "bold")
FONT_INPUT    = ("Courier New", 10)
FONT_OUTPUT   = ("Courier New", 9)

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 30


def _bring_to_front(window):
    """Force a Tkinter window to the foreground on macOS."""
    window.lift()
    window.attributes('-topmost', True)
    window.after(300, lambda: window.attributes('-topmost', False))
    window.focus_force()
    if platform.system() == 'Darwin':
        try:
            import subprocess
            subprocess.Popen([
                'osascript', '-e',
                'tell application "System Events" to set frontmost of '
                'the first process whose unix id is '
                + str(__import__("os").getpid()) + ' to true'
            ])
        except Exception:
            pass


class HSMApp:
    """
    Single-window app: starts with an auth screen,
    then replaces it with the full HSM dashboard.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Virtual HSM Dashboard")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)
        self.hsm = HSMCore()
        self.failed_login_attempts = 0
        self.locked_until = 0.0

        # Size and center
        w, h = 760, 720
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(680, 600)

        # Container for swapping screens
        self.container = tk.Frame(self.root, bg=BG_DARK)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Start with the auth screen
        self._show_auth_screen()

        # Force to front on macOS
        self.root.update_idletasks()
        _bring_to_front(self.root)

    def run(self):
        self.root.mainloop()

    # ─── Auth Screen ─────────────────────────────────────────────

    def _show_auth_screen(self):
        """Show the login screen inside the main window."""
        for w in self.container.winfo_children():
            w.destroy()

        frame = tk.Frame(self.container, bg=BG_DARK)
        frame.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        # Lock icon
        tk.Label(
            frame, text="🔐", font=("Arial", 48),
            bg=BG_DARK, fg=FG_TEXT
        ).pack(pady=(0, 10))

        tk.Label(
            frame, text="VIRTUAL HSM", font=FONT_TITLE,
            bg=BG_DARK, fg=ACCENT_BLUE
        ).pack(pady=(0, 5))

        tk.Label(
            frame, text="Hardware Security Module Simulation",
            font=FONT_LABEL, bg=BG_DARK, fg=FG_DIM
        ).pack(pady=(0, 30))

        # Password row
        pw_frame = tk.Frame(frame, bg=BG_DARK)
        pw_frame.pack(pady=5)

        tk.Label(
            pw_frame, text="Password:", font=FONT_LABEL,
            bg=BG_DARK, fg=FG_DIM
        ).pack(side=tk.LEFT, padx=(0, 10))

        self.pw_entry = tk.Entry(
            pw_frame, show="•", font=FONT_INPUT, width=24,
            bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
            relief=tk.FLAT, highlightthickness=1,
            highlightbackground=BORDER_COLOR, highlightcolor=ACCENT_BLUE
        )
        self.pw_entry.pack(side=tk.LEFT)
        self.pw_entry.focus_set()
        self.pw_entry.bind("<Return>", lambda e: self._do_login())

        # Login button
        self.login_button = tk.Button(
            frame, text="  AUTHENTICATE  ", font=FONT_BUTTON,
            bg=ACCENT_BLUE, fg=BG_DARK, activebackground="#79c0ff",
            relief=tk.FLAT, padx=24, pady=8, cursor="hand2",
            command=self._do_login
        )
        self.login_button.pack(pady=20)

        self.auth_status = tk.Label(
            frame, text="", font=FONT_LABEL, bg=BG_DARK, fg=ACCENT_RED
        )
        self.auth_status.pack()

    def _do_login(self):
        if time.monotonic() < self.locked_until:
            wait_seconds = int(self.locked_until - time.monotonic()) + 1
            self.auth_status.config(text=f"✗ Too many attempts. Retry in {wait_seconds}s.")
            return

        pw = self.pw_entry.get()
        if self.hsm.login(pw):
            self.failed_login_attempts = 0
            self.locked_until = 0.0
            self._show_dashboard()
        else:
            self.failed_login_attempts += 1
            attempts_left = MAX_LOGIN_ATTEMPTS - self.failed_login_attempts
            if attempts_left <= 0:
                self.locked_until = time.monotonic() + LOCKOUT_SECONDS
                self.failed_login_attempts = 0
                self.auth_status.config(
                    text=f"✗ Locked for {LOCKOUT_SECONDS}s after repeated failures."
                )
                self._set_login_controls(enabled=False)
                self.root.after(LOCKOUT_SECONDS * 1000, self._unlock_login)
            else:
                self.auth_status.config(text=f"✗ Invalid password. {attempts_left} attempt(s) left.")
            self.pw_entry.delete(0, tk.END)

    def _set_login_controls(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        self.pw_entry.configure(state=state)
        self.login_button.configure(state=state)

    def _unlock_login(self):
        if time.monotonic() < self.locked_until:
            return
        self._set_login_controls(enabled=True)
        self.auth_status.config(text="")
        self.pw_entry.focus_set()

    # ─── Dashboard Screen ────────────────────────────────────────

    def _show_dashboard(self):
        """Replace auth screen with the full HSM dashboard."""
        for w in self.container.winfo_children():
            w.destroy()

        # ── Header ──
        header = tk.Frame(self.container, bg=BG_DARK)
        header.pack(fill=tk.X, padx=20, pady=(15, 5))

        tk.Label(
            header, text="⬡ VIRTUAL HSM", font=FONT_TITLE,
            bg=BG_DARK, fg=ACCENT_BLUE
        ).pack(side=tk.LEFT)

        tk.Label(
            header, text="Keys never leave the boundary",
            font=FONT_LABEL, bg=BG_DARK, fg=FG_DIM
        ).pack(side=tk.RIGHT)

        # Separator
        tk.Frame(self.container, bg=BORDER_COLOR, height=1).pack(fill=tk.X, padx=20, pady=8)

        # ── Main content frame ──
        content = tk.Frame(self.container, bg=BG_DARK)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=1)

        # ── Section 1: Key Generation ──
        self._build_keygen_section(content, row=0, col=0)

        # ── Section 2: Encryption / Decryption ──
        self._build_crypto_section(content, row=0, col=1)

        # ── Section 3: Signing ──
        self._build_signing_section(content, row=1, col=0, colspan=2)

        # ── Section 4: Admin Controls ──
        self._build_admin_section(content, row=2, col=0, colspan=2)

        # ── Section 5: Output Log ──
        self._build_output_section()

        self._log("HSM initialized. Keys are stored internally and will NEVER be exported.")

    def _make_card(self, parent, title, row, col, colspan=1):
        """Create a styled card frame with a title."""
        card = tk.LabelFrame(
            parent, text=f"  {title}  ", font=FONT_SECTION,
            bg=BG_CARD, fg=ACCENT_BLUE,
            bd=1, relief=tk.GROOVE,
            highlightbackground=BORDER_COLOR, highlightthickness=1,
            padx=12, pady=10
        )
        card.grid(row=row, column=col, columnspan=colspan,
                  padx=6, pady=6, sticky="nsew")
        return card

    # ── Section 1: Key Generation ────────────────────────────────

    def _build_keygen_section(self, parent, row, col):
        card = self._make_card(parent, "🔑 Key Generation", row, col)

        tk.Label(
            card, text="Generate keys inside the HSM.",
            font=FONT_LABEL, bg=BG_CARD, fg=FG_DIM
        ).pack(anchor=tk.W, pady=(0, 10))

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame, text="Generate AES Key", font=FONT_BUTTON,
            bg=ACCENT_GREEN, fg=BG_DARK, activebackground="#56d364",
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=self._gen_aes
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_frame, text="Generate RSA Key", font=FONT_BUTTON,
            bg=ACCENT_PURPLE, fg=BG_DARK, activebackground="#d2a8ff",
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=self._gen_rsa
        ).pack(side=tk.LEFT)

    # ── Section 2: Encryption / Decryption ───────────────────────

    def _build_crypto_section(self, parent, row, col):
        card = self._make_card(parent, "🔒 Encrypt / Decrypt", row, col)

        # Key ID
        tk.Label(card, text="Key ID:", font=FONT_LABEL, bg=BG_CARD, fg=FG_DIM).pack(anchor=tk.W)
        self.crypto_key_entry = tk.Entry(
            card, font=FONT_INPUT, bg=BG_INPUT, fg=FG_TEXT,
            insertbackground=FG_TEXT, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=BORDER_COLOR,
            highlightcolor=ACCENT_BLUE
        )
        self.crypto_key_entry.pack(fill=tk.X, pady=(2, 8))

        # Data
        tk.Label(card, text="Data:", font=FONT_LABEL, bg=BG_CARD, fg=FG_DIM).pack(anchor=tk.W)
        self.crypto_data_entry = tk.Entry(
            card, font=FONT_INPUT, bg=BG_INPUT, fg=FG_TEXT,
            insertbackground=FG_TEXT, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=BORDER_COLOR,
            highlightcolor=ACCENT_BLUE
        )
        self.crypto_data_entry.pack(fill=tk.X, pady=(2, 10))

        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame, text="Encrypt", font=FONT_BUTTON,
            bg=ACCENT_BLUE, fg=BG_DARK, activebackground="#79c0ff",
            relief=tk.FLAT, padx=14, pady=5, cursor="hand2",
            command=self._encrypt
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_frame, text="Decrypt", font=FONT_BUTTON,
            bg=ACCENT_ORANGE, fg=BG_DARK, activebackground="#e3b341",
            relief=tk.FLAT, padx=14, pady=5, cursor="hand2",
            command=self._decrypt
        ).pack(side=tk.LEFT)

    # ── Section 3: Signing ───────────────────────────────────────

    def _build_signing_section(self, parent, row, col, colspan):
        card = self._make_card(parent, "✍️  Sign / Verify", row, col, colspan)

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X)
        inner.columnconfigure(1, weight=1)
        inner.columnconfigure(3, weight=1)

        # Key ID
        tk.Label(inner, text="Key ID:", font=FONT_LABEL, bg=BG_CARD, fg=FG_DIM).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 6))
        self.sign_key_entry = tk.Entry(
            inner, font=FONT_INPUT, bg=BG_INPUT, fg=FG_TEXT,
            insertbackground=FG_TEXT, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=BORDER_COLOR,
            highlightcolor=ACCENT_BLUE
        )
        self.sign_key_entry.grid(row=0, column=1, sticky="ew", padx=(0, 16))

        # Data
        tk.Label(inner, text="Data:", font=FONT_LABEL, bg=BG_CARD, fg=FG_DIM).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 6))
        self.sign_data_entry = tk.Entry(
            inner, font=FONT_INPUT, bg=BG_INPUT, fg=FG_TEXT,
            insertbackground=FG_TEXT, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=BORDER_COLOR,
            highlightcolor=ACCENT_BLUE
        )
        self.sign_data_entry.grid(row=0, column=3, sticky="ew")

        # Signature field
        tk.Label(inner, text="Signature:", font=FONT_LABEL, bg=BG_CARD, fg=FG_DIM).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 6), pady=(8, 0))
        self.sig_entry = tk.Entry(
            inner, font=FONT_INPUT, bg=BG_INPUT, fg=FG_TEXT,
            insertbackground=FG_TEXT, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=BORDER_COLOR,
            highlightcolor=ACCENT_BLUE
        )
        self.sig_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=(8, 0))

        # Buttons
        btn_frame = tk.Frame(card, bg=BG_CARD)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(
            btn_frame, text="Sign Data", font=FONT_BUTTON,
            bg=ACCENT_GREEN, fg=BG_DARK, activebackground="#56d364",
            relief=tk.FLAT, padx=14, pady=5, cursor="hand2",
            command=self._sign
        ).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(
            btn_frame, text="Verify Signature", font=FONT_BUTTON,
            bg=ACCENT_PURPLE, fg=BG_DARK, activebackground="#d2a8ff",
            relief=tk.FLAT, padx=14, pady=5, cursor="hand2",
            command=self._verify
        ).pack(side=tk.LEFT)

    # ── Section 4: Admin Controls ───────────────────────────────

    def _build_admin_section(self, parent, row, col, colspan):
        card = self._make_card(parent, "🛡️  Admin", row, col, colspan)

        inner = tk.Frame(card, bg=BG_CARD)
        inner.pack(fill=tk.X)
        inner.columnconfigure(1, weight=1)
        inner.columnconfigure(3, weight=1)

        tk.Label(inner, text="Old Password:", font=FONT_LABEL, bg=BG_CARD, fg=FG_DIM).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 6)
        )
        self.old_password_entry = tk.Entry(
            inner, show="*", font=FONT_INPUT, bg=BG_INPUT, fg=FG_TEXT,
            insertbackground=FG_TEXT, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=BORDER_COLOR,
            highlightcolor=ACCENT_BLUE
        )
        self.old_password_entry.grid(row=0, column=1, sticky="ew", padx=(0, 16))

        tk.Label(inner, text="New Password:", font=FONT_LABEL, bg=BG_CARD, fg=FG_DIM).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 6)
        )
        self.new_password_entry = tk.Entry(
            inner, show="*", font=FONT_INPUT, bg=BG_INPUT, fg=FG_TEXT,
            insertbackground=FG_TEXT, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=BORDER_COLOR,
            highlightcolor=ACCENT_BLUE
        )
        self.new_password_entry.grid(row=0, column=3, sticky="ew")

        tk.Button(
            card, text="Rotate Password", font=FONT_BUTTON,
            bg=ACCENT_ORANGE, fg=BG_DARK, activebackground="#e3b341",
            relief=tk.FLAT, padx=14, pady=5, cursor="hand2",
            command=self._rotate_password
        ).pack(anchor=tk.W, pady=(10, 0))

    # ── Section 4: Output Log ────────────────────────────────────

    def _build_output_section(self):
        frame = tk.LabelFrame(
            self.container, text="  📋 Output Log  ", font=FONT_SECTION,
            bg=BG_CARD, fg=ACCENT_BLUE,
            bd=1, relief=tk.GROOVE,
            highlightbackground=BORDER_COLOR, highlightthickness=1,
            padx=8, pady=8
        )
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(6, 15))

        self.output = scrolledtext.ScrolledText(
            frame, font=FONT_OUTPUT, bg=BG_DARK, fg=ACCENT_GREEN,
            insertbackground=ACCENT_GREEN, relief=tk.FLAT,
            wrap=tk.WORD, height=10, state=tk.DISABLED,
            selectbackground=ACCENT_BLUE, selectforeground=BG_DARK
        )
        self.output.pack(fill=tk.BOTH, expand=True)

    # ─── Logging ─────────────────────────────────────────────────

    def _log(self, message: str, tag: str = "info"):
        """Append a message to the output log."""
        self.output.configure(state=tk.NORMAL)
        prefix = {"info": "ℹ", "ok": "✓", "err": "✗", "key": "🔑"}.get(tag, "›")
        self.output.insert(tk.END, f" {prefix}  {message}\n")
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    # ─── HSM Operations ─────────────────────────────────────────

    def _gen_aes(self):
        try:
            key_id = self.hsm.generate_key("AES")
            self._log(f"AES-256 key generated  →  {key_id}", "key")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._log(f"Key generation failed: {e}", "err")

    def _gen_rsa(self):
        try:
            key_id = self.hsm.generate_key("RSA")
            self._log(f"RSA-2048 key generated  →  {key_id}", "key")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._log(f"Key generation failed: {e}", "err")

    def _encrypt(self):
        key_id = self.crypto_key_entry.get().strip()
        data = self.crypto_data_entry.get().strip()
        if not key_id or not data:
            messagebox.showwarning("Input Required", "Please enter both Key ID and Data.")
            return
        try:
            ct = self.hsm.encrypt(key_id, data)
            self._log(f"Encrypted ({key_id})  →  {ct}", "ok")
        except Exception as e:
            messagebox.showerror("Encryption Error", str(e))
            self._log(f"Encryption failed: {e}", "err")

    def _decrypt(self):
        key_id = self.crypto_key_entry.get().strip()
        data = self.crypto_data_entry.get().strip()
        if not key_id or not data:
            messagebox.showwarning("Input Required", "Please enter both Key ID and ciphertext.")
            return
        try:
            pt = self.hsm.decrypt(key_id, data)
            self._log(f"Decrypted ({key_id})  →  {pt}", "ok")
        except Exception as e:
            messagebox.showerror("Decryption Error", str(e))
            self._log(f"Decryption failed: {e}", "err")

    def _sign(self):
        key_id = self.sign_key_entry.get().strip()
        data = self.sign_data_entry.get().strip()
        if not key_id or not data:
            messagebox.showwarning("Input Required", "Please enter both Key ID and Data.")
            return
        try:
            sig = self.hsm.sign(key_id, data)
            self.sig_entry.delete(0, tk.END)
            self.sig_entry.insert(0, sig)
            self._log(f"Signed ({key_id})  →  {sig[:60]}...", "ok")
        except Exception as e:
            messagebox.showerror("Signing Error", str(e))
            self._log(f"Signing failed: {e}", "err")

    def _verify(self):
        key_id = self.sign_key_entry.get().strip()
        data = self.sign_data_entry.get().strip()
        sig = self.sig_entry.get().strip()
        if not key_id or not data or not sig:
            messagebox.showwarning("Input Required", "Please enter Key ID, Data, and Signature.")
            return
        try:
            valid = self.hsm.verify(key_id, data, sig)
            if valid:
                self._log(f"Verification ({key_id})  →  ✓ VALID", "ok")
                messagebox.showinfo("Verification", "✓ Signature is VALID")
            else:
                self._log(f"Verification ({key_id})  →  ✗ INVALID", "err")
                messagebox.showwarning("Verification", "✗ Signature is INVALID")
        except Exception as e:
            messagebox.showerror("Verification Error", str(e))
            self._log(f"Verification failed: {e}", "err")

    def _rotate_password(self):
        old_password = self.old_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()

        if not old_password or not new_password:
            messagebox.showwarning("Input Required", "Please enter old and new password.")
            return
        if len(new_password) < 8:
            messagebox.showwarning("Weak Password", "New password must be at least 8 characters.")
            return

        try:
            changed = self.hsm.rotate_password(old_password, new_password)
            if not changed:
                messagebox.showerror("Password Rotation", "Old password is incorrect.")
                self._log("Password rotation failed: old password mismatch.", "err")
                return

            self._log("Admin password rotated. Re-authentication required.", "ok")
            messagebox.showinfo("Password Rotation", "Password updated. Please log in again.")
            self.hsm.logout()
            self._show_auth_screen()
        except Exception as e:
            messagebox.showerror("Password Rotation Error", str(e))
            self._log(f"Password rotation failed: {e}", "err")


def start_gui():
    """Launch the Virtual HSM Dashboard."""
    app = HSMApp()
    app.run()


if __name__ == "__main__":
    start_gui()
