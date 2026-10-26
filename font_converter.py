# -*- coding: utf-8 -*-
"""
ChangerSurf - Font Format Converter
TTF / OTF / WOFF / WOFF2 bidirectional conversion  |  rheehose.com
Single file, portable, fonttools-based
"""

import sys
import os
import threading
import webbrowser
import base64
import io
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

try:
    from fontTools.ttLib import TTFont
    HAS_FONTTOOLS = True
except ImportError:
    HAS_FONTTOOLS = False

try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Logo base64 PNG 48x48
_LOGO_B64 = "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"

# Flavor map
FLAVOR_MAP = {
    ".ttf":   None,
    ".otf":   None,
    ".woff":  "woff",
    ".woff2": "woff2",
}
EXT_LABELS = {
    ".ttf": "TTF", ".otf": "OTF", ".woff": "WOFF", ".woff2": "WOFF2"
}


def _resource(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def convert_font(src, dst_ext, dst_dir):
    src_ext = src.suffix.lower()
    if src_ext not in FLAVOR_MAP:
        raise ValueError("Unsupported input format: " + src_ext)
    if dst_ext not in FLAVOR_MAP:
        raise ValueError("Unsupported output format: " + dst_ext)
    font = TTFont(str(src))
    font.flavor = FLAVOR_MAP[dst_ext]
    out = dst_dir / (src.stem + dst_ext)
    font.save(str(out))
    return out


# Colors
BG       = "#0F0F13"
SURFACE  = "#1A1A24"
CARD     = "#22222F"
BORDER   = "#2E2E42"
ACCENT   = "#7C6AF7"
ACCENT2  = "#5ED4F3"
SUCCESS  = "#4ADE80"
ERROR    = "#F87171"
WARNING  = "#FBBF24"
TEXT     = "#F1F0FF"
TEXT_DIM = "#8884AA"

FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_SUB   = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 9)
FONT_BTN   = ("Segoe UI", 10, "bold")
FONT_LOG   = ("Consolas", 9)

FORMATS = [".ttf", ".otf", ".woff", ".woff2"]
FMT_INFO = {
    ".ttf":   ("TTF",   "TrueType"),
    ".otf":   ("OTF",   "OpenType"),
    ".woff":  ("WOFF",  "Web Font"),
    ".woff2": ("WOFF2", "Compressed"),
}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChangerSurf  |  Font Converter")
        self.geometry("840x680")
        self.minsize(700, 560)
        self.configure(bg=BG)
        self.resizable(True, True)

        # Window icon
        try:
            ico = _resource(os.path.join("Assets", "icon.ico"))
            self.iconbitmap(ico)
        except Exception:
            pass

        # Logo PhotoImage
        self._logo_img = None
        if HAS_PIL:
            try:
                raw = base64.b64decode(_LOGO_B64)
                img = Image.open(io.BytesIO(raw)).resize((48, 48), Image.LANCZOS)
                self._logo_img = ImageTk.PhotoImage(img)
            except Exception:
                pass

        self.src_files = []
        self.dst_format = tk.StringVar(value=".woff2")
        self.dst_dir = None
        self.same_dir = tk.BooleanVar(value=True)
        self._thread = None

        self._build_ui()
        self._check_deps()

    def _check_deps(self):
        if not HAS_FONTTOOLS:
            self._log("[WARN] fonttools not installed: pip install fonttools", "warn")
        if not HAS_BROTLI:
            self._log("[WARN] brotli not installed (WOFF2 disabled): pip install brotli", "warn")
        if HAS_FONTTOOLS and HAS_BROTLI:
            self._log("[OK] Ready -- Add files, choose output format, then Convert.", "ok")

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(22, 0))

        if self._logo_img:
            logo_lbl = tk.Label(
                hdr, image=self._logo_img, bg=BG, cursor="hand2")
            logo_lbl.pack(side="left", padx=(0, 14))
            logo_lbl.bind("<Button-1>",
                lambda e: webbrowser.open("https://rheehose.com"))
            logo_lbl.bind("<Enter>",
                lambda e: logo_lbl.configure(bg=SURFACE))
            logo_lbl.bind("<Leave>",
                lambda e: logo_lbl.configure(bg=BG))

        title_col = tk.Frame(hdr, bg=BG)
        title_col.pack(side="left")
        tk.Label(title_col, text="ChangerSurf",
                 font=FONT_TITLE, bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(title_col, text="Font Format Converter  |  TTF  OTF  WOFF  WOFF2",
                 font=FONT_SUB, bg=BG, fg=TEXT_DIM).pack(anchor="w")

        link = tk.Label(hdr, text="rheehose.com",
                        font=("Segoe UI", 9, "underline"),
                        bg=BG, fg=ACCENT2, cursor="hand2")
        link.pack(side="right", padx=(0, 4))
        link.bind("<Button-1>",
            lambda e: webbrowser.open("https://rheehose.com"))
        link.bind("<Enter>", lambda e: link.configure(fg=TEXT))
        link.bind("<Leave>", lambda e: link.configure(fg=ACCENT2))

        tk.Frame(self, bg=BORDER, height=1).pack(
            fill="x", padx=28, pady=(14, 0))

        # Body
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=12)

        # Left: file list
        left = tk.Frame(body, bg=CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True)

        lrow = tk.Frame(left, bg=CARD)
        lrow.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(lrow, text="Input Files",
                 font=FONT_BTN, bg=CARD, fg=TEXT).pack(side="left")
        tk.Label(lrow, text="TTF / OTF / WOFF / WOFF2",
                 font=FONT_LABEL, bg=CARD, fg=TEXT_DIM).pack(side="left", padx=8)

        lf = tk.Frame(left, bg=CARD)
        lf.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        self.file_lb = tk.Listbox(
            lf, bg=CARD, fg=TEXT,
            selectbackground=ACCENT, selectforeground="#fff",
            font=FONT_LOG, bd=0, highlightthickness=0,
            activestyle="none", relief="flat",
        )
        sb = tk.Scrollbar(lf, orient="vertical",
                          command=self.file_lb.yview, bg=SURFACE)
        self.file_lb.configure(yscrollcommand=sb.set)
        self.file_lb.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        fbtn = tk.Frame(left, bg=CARD)
        fbtn.pack(fill="x", padx=14, pady=(0, 12))
        for txt, cmd in [("+ Add Files",  self._add_files),
                         ("- Remove",     self._remove_sel),
                         ("Clear All",    self._clear_files)]:
            tk.Button(fbtn, text=txt, command=cmd,
                      bg=SURFACE, fg=TEXT_DIM, font=FONT_LABEL,
                      relief="flat", padx=8, pady=4, cursor="hand2",
                      activebackground=BORDER, activeforeground=TEXT,
                      ).pack(side="left", padx=(0, 6))

        # Right: settings
        right = tk.Frame(body, bg=BG, width=236)
        right.pack(side="right", fill="y", padx=(14, 0))
        right.pack_propagate(False)

        tk.Label(right, text="Output Format",
                 font=FONT_BTN, bg=BG, fg=TEXT).pack(anchor="w", pady=(4, 6))

        self._fmt_btns = {}
        fg_frame = tk.Frame(right, bg=BG)
        fg_frame.pack(fill="x")
        for i, ext in enumerate(FORMATS):
            r, c = divmod(i, 2)
            name, sub = FMT_INFO[ext]
            btn_label = name + "\n" + sub
            btn = tk.Button(
                fg_frame, text=btn_label,
                command=lambda e=ext: self._select_fmt(e),
                font=("Segoe UI", 9, "bold"),
                width=10, height=3,
                relief="flat", bd=0, cursor="hand2",
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            fg_frame.columnconfigure(c, weight=1)
            self._fmt_btns[ext] = btn
        self._select_fmt(".woff2")

        tk.Frame(right, bg=BORDER, height=1).pack(
            fill="x", pady=12)
        tk.Label(right, text="Save Location",
                 font=FONT_BTN, bg=BG, fg=TEXT).pack(anchor="w", pady=(0, 6))

        tk.Checkbutton(
            right, text="Same folder as source",
            variable=self.same_dir, command=self._toggle_dst,
            bg=BG, fg=TEXT_DIM, selectcolor=SURFACE,
            activebackground=BG, activeforeground=TEXT,
            font=FONT_LABEL, cursor="hand2",
        ).pack(anchor="w")

        self.dst_btn = tk.Button(
            right, text="Choose Output Folder",
            command=self._pick_dst,
            bg=SURFACE, fg=TEXT_DIM, font=FONT_LABEL,
            relief="flat", padx=8, pady=4, cursor="hand2",
            activebackground=BORDER, activeforeground=TEXT,
            state="disabled",
        )
        self.dst_btn.pack(fill="x", pady=6)

        self.dst_lbl = tk.Label(right, text="--", font=FONT_LABEL,
                                bg=BG, fg=TEXT_DIM, wraplength=212, justify="left")
        self.dst_lbl.pack(anchor="w")

        tk.Frame(right, bg=BORDER, height=1).pack(
            fill="x", pady=12)

        self.cvt_btn = tk.Button(
            right, text="Convert",
            command=self._start,
            font=("Segoe UI", 14, "bold"),
            bg=ACCENT, fg="#FFFFFF",
            relief="flat", padx=12, pady=16,
            cursor="hand2",
            activebackground="#6555E0", activeforeground="#fff",
        )
        self.cvt_btn.pack(fill="x")

        self.prog_var = tk.StringVar(value="")
        tk.Label(right, textvariable=self.prog_var,
                 font=FONT_LABEL, bg=BG, fg=TEXT_DIM,
                 wraplength=212, justify="left").pack(anchor="w", pady=4)

        # Log panel
        log_frame = tk.Frame(self, bg=SURFACE,
                             highlightbackground=BORDER, highlightthickness=1)
        log_frame.pack(fill="x", padx=28, pady=(0, 18))

        log_hdr = tk.Frame(log_frame, bg=SURFACE)
        log_hdr.pack(fill="x", padx=10, pady=(6, 2))
        tk.Label(log_hdr, text="Log",
                 font=FONT_LABEL, bg=SURFACE, fg=TEXT_DIM).pack(side="left")
        tk.Button(log_hdr, text="Clear", command=self._clear_log,
                  bg=SURFACE, fg=TEXT_DIM, relief="flat",
                  font=FONT_LABEL, cursor="hand2").pack(side="right")

        self.log_text = tk.Text(
            log_frame, height=6,
            bg=SURFACE, fg=TEXT,
            font=FONT_LOG, bd=0, relief="flat",
            state="disabled", wrap="word",
            highlightthickness=0,
        )
        self.log_text.pack(fill="x", padx=10, pady=(0, 8))
        self.log_text.tag_config("ok",   foreground=SUCCESS)
        self.log_text.tag_config("err",  foreground=ERROR)
        self.log_text.tag_config("warn", foreground=WARNING)
        self.log_text.tag_config("info", foreground=ACCENT2)

    def _select_fmt(self, ext):
        self.dst_format.set(ext)
        for e, b in self._fmt_btns.items():
            if e == ext:
                b.configure(bg=ACCENT, fg="#fff", activebackground=ACCENT)
            else:
                b.configure(bg=CARD, fg=TEXT_DIM, activebackground=BORDER)

    def _toggle_dst(self):
        if self.same_dir.get():
            self.dst_btn.configure(state="disabled")
            self.dst_lbl.configure(text="--")
            self.dst_dir = None
        else:
            self.dst_btn.configure(state="normal")

    def _pick_dst(self):
        d = filedialog.askdirectory(title="Choose Output Folder")
        if d:
            self.dst_dir = Path(d)
            self.dst_lbl.configure(text=str(self.dst_dir))

    def _add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Font Files",
            filetypes=[("Font Files", "*.ttf *.otf *.woff *.woff2"),
                       ("All Files",  "*.*")],
        )
        for f in files:
            p = Path(f)
            if p not in self.src_files:
                self.src_files.append(p)
                tag = EXT_LABELS.get(p.suffix.lower(), p.suffix.upper())
                self.file_lb.insert("end", "  " + p.name + "  [" + tag + "]")

    def _remove_sel(self):
        for i in reversed(self.file_lb.curselection()):
            self.file_lb.delete(i)
            self.src_files.pop(i)

    def _clear_files(self):
        self.file_lb.delete(0, "end")
        self.src_files.clear()

    def _start(self):
        if not HAS_FONTTOOLS:
            messagebox.showerror("Error",
                "fonttools not installed. pip install fonttools")
            return
        if not self.src_files:
            messagebox.showwarning("No Files", "Add font files first.")
            return
        if self.dst_format.get() == ".woff2" and not HAS_BROTLI:
            messagebox.showerror("Error",
                "WOFF2 requires brotli. pip install brotli")
            return
        if not self.same_dir.get() and self.dst_dir is None:
            messagebox.showwarning("No Folder",
                "Choose an output folder or enable same-folder option.")
            return
        if self._thread and self._thread.is_alive():
            return
        self.cvt_btn.configure(state="disabled", text="Converting...")
        self._thread = threading.Thread(target=self._do_convert, daemon=True)
        self._thread.start()

    def _do_convert(self):
        dst_ext = self.dst_format.get()
        files   = list(self.src_files)
        ok = fail = 0
        for idx, src in enumerate(files, 1):
            self.prog_var.set(str(idx) + "/" + str(len(files)) + "  " + src.name)
            try:
                if src.suffix.lower() == dst_ext:
                    self._log("[SKIP] Same format: " + src.name, "warn")
                    continue
                dst_dir = src.parent if self.same_dir.get() else self.dst_dir
                dst_dir.mkdir(parents=True, exist_ok=True)
                out = convert_font(src, dst_ext, dst_dir)
                sz  = out.stat().st_size / 1024
                self._log("[OK] " + src.name + " -> " + out.name
                          + " (" + f"{sz:.1f}" + " KB)", "ok")
                ok += 1
            except Exception as e:
                self._log("[ERR] " + src.name + " : " + str(e), "err")
                fail += 1
        self.prog_var.set("Done  OK:" + str(ok) + "  Fail:" + str(fail))
        self._log("-- Done: " + str(ok) + " succeeded, " + str(fail) + " failed --", "info")
        self.after(0, lambda: self.cvt_btn.configure(
            state="normal", text="Convert"))

    def _log(self, msg, tag=""):
        def _w():
            self.log_text.configure(state="normal")
            self.log_text.insert("end", msg + "\n", tag)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        self.after(0, _w)

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")


if __name__ == "__main__":
    app = App()
    app.mainloop()
