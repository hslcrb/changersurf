# -*- coding: utf-8 -*-
"""
ChangerSurf — Font Format Converter
TTF · OTF · WOFF · WOFF2 완벽 상호변환
단일 파일 · 포터블 · fonttools 기반
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

# ── fonttools 동적 임포트 ──────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────────────────────
# 변환 로직
# ─────────────────────────────────────────────────────────────────────────────

FLAVOR_MAP = {
    ".ttf":   None,
    ".otf":   None,
    ".woff":  "woff",
    ".woff2": "woff2",
}

EXT_LABELS = {
    ".ttf":   "TTF",
    ".otf":   "OTF",
    ".woff":  "WOFF",
    ".woff2": "WOFF2",
}


def convert_font(src_path: Path, dst_ext: str, dst_dir: Path) -> Path:
    src_ext = src_path.suffix.lower()
    if src_ext not in FLAVOR_MAP:
        raise ValueError(f"지원하지 않는 입력 형식: {src_ext}")
    if dst_ext not in FLAVOR_MAP:
        raise ValueError(f"지원하지 않는 출력 형식: {dst_ext}")

    font = TTFont(str(src_path))
    font.flavor = FLAVOR_MAP[dst_ext]

    out_name = src_path.stem + dst_ext
    out_path = dst_dir / out_name
    font.save(str(out_path))
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# 색상 상수
# ─────────────────────────────────────────────────────────────────────────────

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

FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SUB   = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 9)
FONT_BTN   = ("Segoe UI", 10, "bold")
FONT_LOG   = ("Consolas", 9)

FORMATS = [".ttf", ".otf", ".woff", ".woff2"]
FMT_LABELS = {
    ".ttf":   "TTF\nTrueType",
    ".otf":   "OTF\nOpenType",
    ".woff":  "WOFF\nWeb Font",
    ".woff2": "WOFF2\nCompressed",
}


# ─────────────────────────────────────────────────────────────────────────────
# 앱
# ─────────────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChangerSurf — Font Converter")
        self.geometry("800x640")
        self.minsize(680, 540)
        self.configure(bg=BG)
        self.resizable(True, True)

        self.src_files: list[Path] = []
        self.dst_format = tk.StringVar(value=".woff2")
        self.dst_dir: Path | None = None
        self.same_dir = tk.BooleanVar(value=True)
        self._thread: threading.Thread | None = None

        self._build_ui()
        self._check_deps()

    # ── 의존성 체크 ────────────────────────────────────────────────────────────
    def _check_deps(self):
        if not HAS_FONTTOOLS:
            self._log("⚠  fonttools 가 설치되지 않았습니다: pip install fonttools", "warn")
        if not HAS_BROTLI:
            self._log("⚠  brotli 없음 (WOFF2 출력 불가): pip install brotli", "warn")
        if HAS_FONTTOOLS and HAS_BROTLI:
            self._log("✓  준비 완료 — 파일을 추가하고 출력 형식을 선택 후 변환 시작!", "ok")

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # 헤더
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=28, pady=(22, 0))
        tk.Label(hdr, text="ChangerSurf", font=FONT_TITLE, bg=BG, fg=TEXT).pack(side="left")
        tk.Label(hdr, text="Font Format Converter  ·  TTF OTF WOFF WOFF2",
                 font=FONT_SUB, bg=BG, fg=TEXT_DIM).pack(side="left", padx=12, pady=(8,0))

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=28, pady=(12, 0))

        # 본문
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=12)

        # ── 왼쪽: 파일 목록 ──────────────────────────────────────────────────
        left = tk.Frame(body, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True)

        lbl_row = tk.Frame(left, bg=CARD)
        lbl_row.pack(fill="x", padx=14, pady=(12, 4))
        tk.Label(lbl_row, text="입력 파일", font=FONT_BTN, bg=CARD, fg=TEXT).pack(side="left")
        tk.Label(lbl_row, text="TTF · OTF · WOFF · WOFF2",
                 font=FONT_LABEL, bg=CARD, fg=TEXT_DIM).pack(side="left", padx=8)

        lf = tk.Frame(left, bg=CARD)
        lf.pack(fill="both", expand=True, padx=14, pady=(0,8))

        self.file_lb = tk.Listbox(
            lf, bg="#17172200", fg=TEXT,
            selectbackground=ACCENT, selectforeground="#fff",
            font=FONT_LOG, bd=0, highlightthickness=0,
            activestyle="none", relief="flat",
        )
        sb = tk.Scrollbar(lf, orient="vertical", command=self.file_lb.yview, bg=SURFACE)
        self.file_lb.configure(yscrollcommand=sb.set)
        self.file_lb.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        fbtn = tk.Frame(left, bg=CARD)
        fbtn.pack(fill="x", padx=14, pady=(0, 12))
        for txt, cmd in [("＋ 파일 추가", self._add_files),
                         ("✕ 선택 삭제", self._remove_selected),
                         ("전체 지우기",  self._clear_files)]:
            tk.Button(fbtn, text=txt, command=cmd,
                      bg=SURFACE, fg=TEXT_DIM, font=FONT_LABEL,
                      relief="flat", padx=8, pady=4, cursor="hand2",
                      activebackground=BORDER, activeforeground=TEXT
                      ).pack(side="left", padx=(0,6))

        # ── 오른쪽: 설정 ─────────────────────────────────────────────────────
        right = tk.Frame(body, bg=BG, width=230)
        right.pack(side="right", fill="y", padx=(14,0))
        right.pack_propagate(False)

        tk.Label(right, text="출력 형식", font=FONT_BTN, bg=BG, fg=TEXT
                 ).pack(anchor="w", pady=(4,6))

        self._fmt_btns: dict[str, tk.Button] = {}
        fg = tk.Frame(right, bg=BG)
        fg.pack(fill="x")
        for i, ext in enumerate(FORMATS):
            r, c = divmod(i, 2)
            btn = tk.Button(
                fg, text=FMT_LABELS[ext],
                command=lambda e=ext: self._select_fmt(e),
                font=("Segoe UI", 9, "bold"),
                width=10, height=3,
                relief="flat", bd=0,
                cursor="hand2",
            )
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            fg.columnconfigure(c, weight=1)
            self._fmt_btns[ext] = btn
        self._select_fmt(".woff2")

        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=12)
        tk.Label(right, text="저장 위치", font=FONT_BTN, bg=BG, fg=TEXT
                 ).pack(anchor="w", pady=(0,6))

        tk.Checkbutton(
            right, text="원본 파일과 같은 폴더",
            variable=self.same_dir, command=self._toggle_dst,
            bg=BG, fg=TEXT_DIM, selectcolor=SURFACE,
            activebackground=BG, activeforeground=TEXT,
            font=FONT_LABEL, cursor="hand2",
        ).pack(anchor="w")

        self.dst_btn = tk.Button(
            right, text="📁  출력 폴더 선택",
            command=self._pick_dst,
            bg=SURFACE, fg=TEXT_DIM, font=FONT_LABEL,
            relief="flat", padx=8, pady=4, cursor="hand2",
            activebackground=BORDER, activeforeground=TEXT,
            state="disabled",
        )
        self.dst_btn.pack(fill="x", pady=6)

        self.dst_lbl = tk.Label(right, text="—", font=FONT_LABEL,
                                bg=BG, fg=TEXT_DIM, wraplength=210, justify="left")
        self.dst_lbl.pack(anchor="w")

        tk.Frame(right, bg=BORDER, height=1).pack(fill="x", pady=12)

        self.cvt_btn = tk.Button(
            right, text="⚡  변환 시작",
            command=self._start,
            font=("Segoe UI", 13, "bold"),
            bg=ACCENT, fg="#FFF",
            relief="flat", padx=12, pady=14,
            cursor="hand2",
            activebackground="#6555E0", activeforeground="#fff",
        )
        self.cvt_btn.pack(fill="x")

        self.prog_var = tk.StringVar(value="")
        tk.Label(right, textvariable=self.prog_var,
                 font=FONT_LABEL, bg=BG, fg=TEXT_DIM,
                 wraplength=210, justify="left").pack(anchor="w", pady=4)

        # ── 로그 패널 ─────────────────────────────────────────────────────────
        log_frame = tk.Frame(self, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        log_frame.pack(fill="x", padx=28, pady=(0,18))

        log_hdr = tk.Frame(log_frame, bg=SURFACE)
        log_hdr.pack(fill="x", padx=10, pady=(6,2))
        tk.Label(log_hdr, text="변환 로그", font=FONT_LABEL, bg=SURFACE, fg=TEXT_DIM).pack(side="left")
        tk.Button(log_hdr, text="지우기", command=self._clear_log,
                  bg=SURFACE, fg=TEXT_DIM, relief="flat",
                  font=FONT_LABEL, cursor="hand2").pack(side="right")

        self.log_text = tk.Text(
            log_frame, height=6,
            bg=SURFACE, fg=TEXT,
            font=FONT_LOG, bd=0, relief="flat",
            state="disabled", wrap="word",
            highlightthickness=0,
        )
        self.log_text.pack(fill="x", padx=10, pady=(0,8))
        self.log_text.tag_config("ok",   foreground=SUCCESS)
        self.log_text.tag_config("err",  foreground=ERROR)
        self.log_text.tag_config("warn", foreground=WARNING)
        self.log_text.tag_config("info", foreground=ACCENT2)

    # ── 포맷 선택 ──────────────────────────────────────────────────────────────
    def _select_fmt(self, ext: str):
        self.dst_format.set(ext)
        for e, b in self._fmt_btns.items():
            if e == ext:
                b.configure(bg=ACCENT, fg="#fff", activebackground=ACCENT)
            else:
                b.configure(bg=CARD, fg=TEXT_DIM, activebackground=BORDER)

    # ── 저장 위치 ──────────────────────────────────────────────────────────────
    def _toggle_dst(self):
        if self.same_dir.get():
            self.dst_btn.configure(state="disabled")
            self.dst_lbl.configure(text="—")
            self.dst_dir = None
        else:
            self.dst_btn.configure(state="normal")

    def _pick_dst(self):
        d = filedialog.askdirectory(title="출력 폴더 선택")
        if d:
            self.dst_dir = Path(d)
            self.dst_lbl.configure(text=str(self.dst_dir))

    # ── 파일 관리 ──────────────────────────────────────────────────────────────
    def _add_files(self):
        files = filedialog.askopenfilenames(
            title="폰트 파일 선택",
            filetypes=[
                ("폰트 파일", "*.ttf *.otf *.woff *.woff2"),
                ("모든 파일", "*.*"),
            ],
        )
        for f in files:
            p = Path(f)
            if p not in self.src_files:
                self.src_files.append(p)
                tag = EXT_LABELS.get(p.suffix.lower(), p.suffix.upper())
                self.file_lb.insert("end", f"  {p.name}   [{tag}]")

    def _remove_selected(self):
        for i in reversed(self.file_lb.curselection()):
            self.file_lb.delete(i)
            self.src_files.pop(i)

    def _clear_files(self):
        self.file_lb.delete(0, "end")
        self.src_files.clear()

    # ── 변환 ───────────────────────────────────────────────────────────────────
    def _start(self):
        if not HAS_FONTTOOLS:
            messagebox.showerror("오류", "fonttools 미설치\npip install fonttools")
            return
        if not self.src_files:
            messagebox.showwarning("파일 없음", "변환할 파일을 먼저 추가하세요.")
            return
        if self.dst_format.get() == ".woff2" and not HAS_BROTLI:
            messagebox.showerror("오류", "WOFF2 변환에는 brotli 필요\npip install brotli")
            return
        if not self.same_dir.get() and self.dst_dir is None:
            messagebox.showwarning("폴더 미선택", "출력 폴더를 선택하거나\n'원본 파일과 같은 폴더' 옵션을 활성화하세요.")
            return
        if self._thread and self._thread.is_alive():
            messagebox.showinfo("진행 중", "이미 변환이 실행 중입니다.")
            return

        self.cvt_btn.configure(state="disabled", text="변환 중…")
        self._thread = threading.Thread(target=self._do_convert, daemon=True)
        self._thread.start()

    def _do_convert(self):
        dst_ext = self.dst_format.get()
        files   = list(self.src_files)
        total   = len(files)
        ok, fail = 0, 0

        for idx, src in enumerate(files, 1):
            self.prog_var.set(f"{idx}/{total}  {src.name}")
            try:
                if src.suffix.lower() == dst_ext:
                    self._log(f"↷  스킵 (동일 형식): {src.name}", "warn")
                    continue
                dst_dir = src.parent if self.same_dir.get() else self.dst_dir
                dst_dir.mkdir(parents=True, exist_ok=True)
                out = convert_font(src, dst_ext, dst_dir)
                sz  = out.stat().st_size / 1024
                self._log(f"✓  {src.name}  →  {out.name}  ({sz:.1f} KB)", "ok")
                ok += 1
            except Exception as e:
                self._log(f"✗  {src.name}  — {e}", "err")
                fail += 1

        self.prog_var.set(f"완료  ✓{ok}  ✗{fail}")
        self._log(f"── 완료: 성공 {ok}개 / 실패 {fail}개 ──", "info")
        self.after(0, lambda: self.cvt_btn.configure(state="normal", text="⚡  변환 시작"))

    # ── 로그 ───────────────────────────────────────────────────────────────────
    def _log(self, msg: str, tag: str = ""):
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


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
