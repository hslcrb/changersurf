# -*- coding: utf-8 -*-
"""
ChangerSurf - 폰트 형식 변환기
TTF / OTF / WOFF / WOFF2 상호 변환  |  rheehose.com
Easy 모드 & 심화 모드 지원
"""

import sys
import os
import threading
import webbrowser
import base64
import io
import ctypes
import math
import tkinter as tk
import tkinter.font as tkfont
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

# 로고 Base64 PNG 48x48
_LOGO_B64 = "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"

# 형식 매핑
FLAVOR_MAP = {
    ".ttf":   None,
    ".otf":   None,
    ".woff":  "woff",
    ".woff2": "woff2",
}
EXT_LABELS = {
    ".ttf": "TTF", ".otf": "OTF",
    ".woff": "WOFF", ".woff2": "WOFF2"
}


def _resource(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def load_custom_font():
    """WantedSans Variable TTF를 Windows GDI에 등록, Tkinter에서 사용 가능하게."""
    try:
        path = _resource(os.path.join("Assets", "fonts", "WantedSansVariable.ttf"))
        if os.path.exists(path):
            ctypes.windll.gdi32.AddFontResourceExW(ctypes.c_wchar_p(path), 0x10, 0)
            ctypes.windll.gdi32.AddFontResourceW(ctypes.c_wchar_p(path))
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x001D, 0, 0)
    except Exception:
        pass

    try:
        fams = tkfont.families()
        for cand in ["Wanted Sans", "Wanted Sans Variable", "WantedSans", "WantedSansVariable"]:
            if cand in fams:
                return cand
        for f in fams:
            if "wanted" in f.lower():
                return f
    except Exception:
        pass
    return "Wanted Sans"


def convert_font(src, dst_ext, dst_dir):
    src_ext = src.suffix.lower()
    if src_ext not in FLAVOR_MAP:
        raise ValueError("지원하지 않는 입력 형식: " + src_ext)
    if dst_ext not in FLAVOR_MAP:
        raise ValueError("지원하지 않는 출력 형식: " + dst_ext)
    font = TTFont(str(src))
    font.flavor = FLAVOR_MAP[dst_ext]
    out = dst_dir / (src.stem + dst_ext)
    font.save(str(out))
    return out


# 색상 테마
BG        = "#FFFFFF"
BG2       = "#F4F6FB"
CARD      = "#EDF0F8"
BORDER    = "#D0D8EE"
NAVY      = "#3a4ca8"
NAVY_DK   = "#2c3d8f"
NAVY_LT   = "#5566c0"
TEXT      = "#1A1E3A"
TEXT_DIM  = "#7580A8"
SUCCESS   = "#1D8A4E"
ERROR     = "#C0392B"
WARNING   = "#B07C00"
LOGBG     = "#F0F3FA"

# 노드 전용 테마 색상 (좌: 파랑 / 우: 빨강)
BLUE_BG      = "#EEF4FF"
BLUE_BORDER  = "#B8D0FF"
BLUE_ACCENT  = "#2654EA"
BLUE_TEXT    = "#10266B"

RED_BG       = "#FFF1F2"
RED_BORDER   = "#FFCCD0"
RED_ACCENT   = "#D82D42"
RED_TEXT     = "#70111F"

FORMATS = [".ttf", ".otf", ".woff", ".woff2"]
FMT_INFO = {
    ".ttf":   ("TTF",   "트루타입"),
    ".otf":   ("OTF",   "오픈타입"),
    ".woff":  ("WOFF",  "웹 폰트"),
    ".woff2": ("WOFF2", "압축 웹폰트"),
}

# Easy 모드용 포맷 카드 정보
EASY_OPTIONS = [
    (".woff",  "웹 폰트 (WOFF)",     "웹 표준 폰트 (사실은 woff)"),
    (".woff2", "초압축 웹폰트 (WOFF2)", "최신 브라우저용 고압축 웹폰트"),
    (".ttf",   "설치용 폰트 (TTF)",   "윈도우·문서용 범용 트루타입"),
    (".otf",   "디자인 폰트 (OTF)",   "인쇄·출판 그래픽용 오픈타입"),
]

# 폰트 변수
F_TITLE = None
F_SUB   = None
F_LABEL = None
F_BTN   = None
F_LOG   = None
F_SMALL = None


def init_fonts(fam):
    global F_TITLE, F_SUB, F_LABEL, F_BTN, F_LOG, F_SMALL
    F_TITLE = (fam, 22, 'bold')
    F_SUB   = (fam, 11)
    F_LABEL = (fam, 11)
    F_BTN   = (fam, 12, 'bold')
    F_LOG   = (fam, 11)
    F_SMALL = (fam, 10)


# Pill 버튼 (Canvas 기반, tkfont로 크기 측정)
class PillButton(tk.Canvas):
    """진짜 둥근 Pill 형태 버튼."""
    def __init__(self, parent, text, command=None,
                 bg=None, fg=None, hover_bg=None,
                 font=None, padx=18, pady=8, radius=20,
                 **kw):
        self._bg       = bg or NAVY
        self._fg       = fg or '#FFFFFF'
        self._hover_bg = hover_bg or NAVY_DK
        self._font     = font or F_BTN
        self._text     = text
        self._command  = command
        self._padx     = padx
        self._pady     = pady
        self._radius   = radius
        self._disabled = False
        self._current_color = self._bg

        mf = tkfont.Font(family=self._font[0],
                         size=self._font[1],
                         weight=self._font[2] if len(self._font) > 2 else 'normal')
        tw = mf.measure(text)
        th = mf.metrics('linespace')

        self._width_px = tw + padx * 2
        self._height_px = th + pady * 2

        try:
            parent_bg = parent.cget('bg')
        except Exception:
            parent_bg = BG

        super().__init__(parent, width=self._width_px, height=self._height_px,
                         bd=0, highlightthickness=0,
                         bg=parent_bg, **kw)

        self._draw(self._current_color)
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)
        self.bind('<ButtonRelease-1>', self._on_release)
        self.bind('<Configure>', self._on_configure)

    def _on_configure(self, e):
        if e.width > 1 and e.height > 1:
            if e.width != self._width_px or e.height != self._height_px:
                self._width_px = e.width
                self._height_px = e.height
                self._draw(self._current_color)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1+r, y1,   x2-r, y1,
            x2,   y1,   x2,   y1+r,
            x2,   y2-r, x2,   y2,
            x2-r, y2,   x1+r, y2,
            x1,   y2,   x1,   y2-r,
            x1,   y1+r, x1,   y1,
        ]
        return self.create_polygon(pts, smooth=True, **kw)

    def _draw(self, color):
        self.delete('all')
        r = min(self._radius, self._height_px // 2)
        self._rounded_rect(0, 0, self._width_px, self._height_px, r,
                            fill=color, outline='')
        self.create_text(
            self._width_px // 2, self._height_px // 2,
            text=self._text, fill=self._fg,
            font=self._font, anchor='center'
        )

    def _on_enter(self, e):
        if not self._disabled:
            self._current_color = self._hover_bg
            self._draw(self._current_color)
            self.configure(cursor='hand2')

    def _on_leave(self, e):
        if not self._disabled:
            self._current_color = self._bg
            self._draw(self._current_color)

    def _on_click(self, e):
        if not self._disabled:
            self._current_color = self._hover_bg
            self._draw(self._current_color)

    def _on_release(self, e):
        if not self._disabled:
            self._current_color = self._bg
            self._draw(self._current_color)
            if self._command:
                self._command()

    def set_disabled(self, val):
        self._disabled = val
        self._current_color = CARD if val else self._bg
        self._draw(self._current_color)

    def set_text(self, text):
        self._text = text
        self._draw(self._current_color)


# 모드 스위치 버튼 (이지 | 심화)
class ModeSwitch(tk.Canvas):
    """작고 세련된 세그먼트 스위치 형태 토글."""
    def __init__(self, parent, on_change=None, **kw):
        self._mode = "easy"  # "easy" or "advanced"
        self._on_change = on_change
        self._width_px = 118
        self._height_px = 32
        self._thumb_x = 3.0
        self._target_x = 3.0
        self._animating = False

        super().__init__(parent, width=self._width_px, height=self._height_px,
                         bd=0, highlightthickness=0, bg=BG, cursor='hand2', **kw)
        self._draw()
        self.bind('<Button-1>', self._on_click)

    def _draw(self):
        self.delete('all')
        w, h = self._width_px, self._height_px
        r = h // 2
        # 배경 트랙
        pts = [
            r, 0,  w-r, 0,
            w, 0,  w, r,
            w, h-r, w, h,
            w-r, h, r, h,
            0, h,  0, h-r,
            0, r,  0, 0
        ]
        self.create_polygon(pts, smooth=True, fill=BG2, outline=BORDER)

        # 슬라이더 썸 (흰색 둥근 Pill)
        tw = (w - 6) // 2
        tx1 = self._thumb_x
        tx2 = tx1 + tw
        ty1, ty2 = 3, h - 3
        tr = (ty2 - ty1) // 2
        thumb_pts = [
            tx1+tr, ty1, tx2-tr, ty1,
            tx2, ty1,    tx2, ty1+tr,
            tx2, ty2-tr, tx2, ty2,
            tx2-tr, ty2, tx1+tr, ty2,
            tx1, ty2,    tx1, ty2-tr,
            tx1, ty1+tr, tx1, ty1
        ]
        self.create_polygon(thumb_pts, smooth=True, fill=NAVY, outline='')

        # 텍스트
        mid1 = 3 + tw // 2
        mid2 = w - 3 - tw // 2
        c1 = '#FFFFFF' if self._mode == 'easy' else TEXT_DIM
        c2 = '#FFFFFF' if self._mode == 'advanced' else TEXT_DIM
        self.create_text(mid1, h // 2, text='이지', font=F_SMALL, fill=c1)
        self.create_text(mid2, h // 2, text='심화', font=F_SMALL, fill=c2)

    def _on_click(self, e):
        self._mode = 'advanced' if self._mode == 'easy' else 'easy'
        tw = (self._width_px - 6) // 2
        self._target_x = 3.0 if self._mode == 'easy' else float(self._width_px - 3 - tw)
        self._start_anim()
        if self._on_change:
            self._on_change(self._mode)

    def _start_anim(self):
        if not self._animating:
            self._animating = True
            self._step_anim()

    def _step_anim(self):
        dx = self._target_x - self._thumb_x
        if abs(dx) < 0.5:
            self._thumb_x = self._target_x
            self._animating = False
            self._draw()
        else:
            self._thumb_x += dx * 0.4
            self._draw()
            self.after(16, self._step_anim)
 

# 물리 튕기는 쫀득한 화살표 (Spring & Squish/Stretch Physics)
class SpringArrow(tk.Canvas):
    """물리 기반으로 쫀득하게 튕기는 대형 인터랙티브 화살표."""
    def __init__(self, parent, **kw):
        self._width_px = 110
        self._height_px = 280
        super().__init__(parent, width=self._width_px, height=self._height_px,
                         bd=0, highlightthickness=0, bg=BG, cursor='hand2', **kw)

        # 스프링 물리 변수 (감쇠 진동자)
        self.x = 0.0          # 변위 (수평 오프셋)
        self.vx = 0.0         # 속도
        self.target_x = 0.0   # 평형 위치
        self.k = 0.16         # 탄성 계수
        self.damping = 0.84   # 감쇠비
        self._animating = False

        self._draw()
        self.bind('<Enter>', self._on_hover)
        self.bind('<Button-1>', self._on_click)

    def _draw(self):
        self.delete('all')
        cx = self._width_px // 2 + self.x
        cy = self._height_px // 2

        # 쫀득한 Squish & Stretch: 변위 방향으로 길어지고 수직 방향으로 압축
        stretch_x = 1.0 + self.x * 0.025
        stretch_y = max(0.65, 1.0 - self.x * 0.018)

        # 은은한 펄스 후광 원
        glow_r = 34 * stretch_x
        self.create_oval(cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                         fill=BG2, outline=BORDER, width=1)

        # 화살표 축 (굵은 둥근 기둥)
        shaft_len = 26 * stretch_x
        shaft_h   = 10 * stretch_y
        self.create_line(cx - shaft_len, cy, cx + shaft_len * 0.4, cy,
                         width=int(shaft_h * 2), capstyle='round', fill=NAVY)

        # 화살표 촉 (둥근 세련된 형태)
        head_sz = 18 * stretch_y
        tip_x   = cx + shaft_len * 0.7 + 10 * stretch_x
        arrow_pts = [
            tip_x, cy,
            cx - 2, cy - head_sz,
            cx + 2, cy,
            cx - 2, cy + head_sz,
        ]
        self.create_polygon(arrow_pts, smooth=True, fill=RED_ACCENT, outline='')

        # 중앙 텍스트 안내 (변환 방향)
        self.create_text(cx, cy + 54, text="변환", font=F_SMALL, fill=TEXT_DIM)

    def kick(self, force=20.0):
        """외력을 가해 쫀득하게 튕겨나가는 스프링 개시."""
        self.vx += force
        if not self._animating:
            self._animating = True
            self._step_spring()

    def recoil_and_shoot(self):
        """변환 시 반동으로 뒤로 쑥 들어갔다가 앞으로 팍 튕겨나가는 젤리 모션."""
        self.x = -26.0
        self.vx = 42.0
        if not self._animating:
            self._animating = True
            self._step_spring()

    def _step_spring(self):
        # 훅의 법칙 + 감쇠: a = -k*(x - target) - damping*v
        ax = -self.k * (self.x - self.target_x) - (1.0 - self.damping) * self.vx
        self.vx += ax
        self.x  += self.vx

        self._draw()

        if abs(self.x - self.target_x) < 0.15 and abs(self.vx) < 0.15:
            self.x = self.target_x
            self.vx = 0.0
            self._animating = False
            self._draw()
        else:
            self.after(16, self._step_spring)

    def _on_hover(self, e):
        self.kick(16.0)

    def _on_click(self, e):
        self.kick(26.0)


# Easy 모드: 좌측 파일 선택 노드 (파랑 테마)
class EasyFileNode(tk.Canvas):
    """현재 파일 선택 및 정보를 큼지막하게 표시하는 파란색 노드."""
    def __init__(self, parent, on_pick=None, **kw):
        self._width_px = 330
        self._height_px = 320
        self._on_pick = on_pick
        self.file_path = None

        super().__init__(parent, width=self._width_px, height=self._height_px,
                         bd=0, highlightthickness=0, bg=BG, cursor='hand2', **kw)
        self._draw()
        self.bind('<Button-1>', self._on_click)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1+r, y1,   x2-r, y1,
            x2,   y1,   x2,   y1+r,
            x2,   y2-r, x2,   y2,
            x2-r, y2,   x1+r, y2,
            x1,   y2,   x1,   y2-r,
            x1,   y1+r, x1,   y1,
        ]
        return self.create_polygon(pts, smooth=True, **kw)

    def set_file(self, path):
        self.file_path = Path(path) if path else None
        self._draw()

    def _draw(self):
        self.delete('all')
        w, h = self._width_px, self._height_px

        # 파란색 메인 카드 배경
        self._rounded_rect(3, 3, w-3, h-3, 18, fill=BLUE_BG, outline=BLUE_BORDER, width=2)

        # 상단 헤더 태그
        self.create_text(w // 2, 34, text="현재 폰트 파일", font=F_BTN, fill=BLUE_TEXT)

        # 파일 아이콘 (문서 형태 벡터 드로잉)
        icx, icy = w // 2, 115
        iw, ih = 56, 70
        ix1, iy1 = icx - iw // 2, icy - ih // 2
        ix2, iy2 = icx + iw // 2, icy + ih // 2
        fold = 16

        # 종이 본체
        pts = [
            ix1, iy1,
            ix2 - fold, iy1,
            ix2, iy1 + fold,
            ix2, iy2,
            ix1, iy2,
        ]
        self.create_polygon(pts, fill='#FFFFFF', outline=BLUE_BORDER, width=2)
        # 접힌 귀 모서리
        fold_pts = [
            ix2 - fold, iy1,
            ix2 - fold, iy1 + fold,
            ix2, iy1 + fold
        ]
        self.create_polygon(fold_pts, fill='#E2ECFF', outline=BLUE_BORDER, width=2)
        # 아이콘 내부 텍스트 "Aa"
        self.create_text(icx, icy + 8, text="Aa", font=('Times New Roman', 20, 'bold'), fill=BLUE_ACCENT)

        if not self.file_path:
            # 파일 미선택 시
            self.create_text(w // 2, 192, text="클릭하여 폰트 파일 선택",
                             font=(F_BTN[0], 13, 'bold'), fill=BLUE_TEXT)
            self.create_text(w // 2, 226,
                             text="TTF · OTF · WOFF · WOFF2\n(어디든 클릭하면 탐색기가 열립니다)",
                             font=F_SMALL, fill=TEXT_DIM, justify='center')
        else:
            # 파일 선택 완료 시
            fname = self.file_path.name
            if len(fname) > 24:
                fname = fname[:21] + "..."
            self.create_text(w // 2, 184, text=fname,
                             font=(F_BTN[0], 13, 'bold'), fill=TEXT)

            ext = self.file_path.suffix.upper().replace('.', '')
            try:
                sz = self.file_path.stat().st_size / 1024
                sz_str = f"{sz:.1f} KB" if sz < 1024 else f"{sz/1024:.2f} MB"
            except Exception:
                sz_str = ""
            info_str = f"[{ext}]  {sz_str}"
            self.create_text(w // 2, 212, text=info_str, font=F_LABEL, fill=BLUE_ACCENT)

            # 변경 힌트 뱃지
            bw, bh = 110, 28
            bx1, by1 = w // 2 - bw // 2, 246
            bx2, by2 = w // 2 + bw // 2, by1 + bh
            self._rounded_rect(bx1, by1, bx2, by2, 12, fill='#FFFFFF', outline=BLUE_BORDER)
            self.create_text(w // 2, by1 + bh // 2, text="다른 파일 선택", font=F_SMALL, fill=BLUE_TEXT)

    def _on_click(self, e):
        if self._on_pick:
            self._on_pick()


# Easy 모드: 우측 바꿀 형식 카드 (빨강 테마 단일 선택 버튼)
class EasyFormatCard(tk.Canvas):
    """바꿀 형식 선택용 큼직한 가로형 카드."""
    def __init__(self, parent, ext, title, sub, on_select=None, **kw):
        self.ext = ext
        self.title_text = title
        self.sub_text = sub
        self._on_select = on_select
        self._selected = False
        self._hover = False
        self._width_px = 300
        self._height_px = 56

        super().__init__(parent, width=self._width_px, height=self._height_px,
                         bd=0, highlightthickness=0, bg=RED_BG, cursor='hand2', **kw)
        self._draw()
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>',    self._on_enter)
        self.bind('<Leave>',    self._on_leave)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1+r, y1,   x2-r, y1,
            x2,   y1,   x2,   y1+r,
            x2,   y2-r, x2,   y2,
            x2-r, y2,   x1+r, y2,
            x1,   y2,   x1,   y2-r,
            x1,   y1+r, x1,   y1,
        ]
        return self.create_polygon(pts, smooth=True, **kw)

    def set_selected(self, val):
        self._selected = val
        self._draw()

    def _draw(self):
        self.delete('all')
        w, h = self._width_px, self._height_px
        if self._selected:
            bg_c    = RED_ACCENT
            fg_c    = '#FFFFFF'
            sub_c   = '#FFD8DC'
            outline = RED_ACCENT
        elif self._hover:
            bg_c    = '#FFFFFF'
            fg_c    = RED_ACCENT
            sub_c   = TEXT_DIM
            outline = RED_ACCENT
        else:
            bg_c    = '#FFFFFF'
            fg_c    = TEXT
            sub_c   = TEXT_DIM
            outline = RED_BORDER

        self._rounded_rect(2, 2, w-2, h-2, 12, fill=bg_c, outline=outline, width=1.5)

        # 라디오 원형 인디케이터
        rcx, rcy, rr = 24, h // 2, 7
        if self._selected:
            self.create_oval(rcx-rr, rcy-rr, rcx+rr, rcy+rr, fill='#FFFFFF', outline='')
            self.create_oval(rcx-4, rcy-4, rcx+4, rcy+4, fill=RED_ACCENT, outline='')
        else:
            self.create_oval(rcx-rr, rcy-rr, rcx+rr, rcy+rr, fill='#FFFFFF', outline=RED_BORDER, width=2)

        # 텍스트
        self.create_text(44, h // 2 - 10, text=self.title_text,
                         font=(F_BTN[0], 12, 'bold'), fill=fg_c, anchor='w')
        self.create_text(44, h // 2 + 10, text=self.sub_text,
                         font=F_SMALL, fill=sub_c, anchor='w')

    def _on_click(self, e):
        if self._on_select:
            self._on_select(self.ext)

    def _on_enter(self, e):
        self._hover = True
        if not self._selected:
            self._draw()

    def _on_leave(self, e):
        self._hover = False
        if not self._selected:
            self._draw()


# 포맷 토글 버튼 (심화 모드용 둥근 사각형)
class FormatToggle(tk.Canvas):
    """포맷 선택용 둥근 사각형 토글."""
    def __init__(self, parent, name, sub, command=None, **kw):
        self.fmt_title = name
        self.fmt_sub   = sub
        self._command  = command
        self._active   = False
        w, h = 112, 58
        self._width_px, self._height_px = w, h
        try:
            parent_bg = parent.cget('bg')
        except Exception:
            parent_bg = BG
        super().__init__(parent, width=w, height=h,
                         bd=0, highlightthickness=0,
                         bg=parent_bg, **kw)
        self._draw()
        self.bind('<Button-1>', self._on_click)
        self.bind('<Enter>',    self._on_enter)
        self.bind('<Leave>',    self._on_leave)
        self.bind('<Configure>', self._on_configure)

    def _on_configure(self, e):
        if e.width > 1 and e.height > 1:
            if e.width != self._width_px or e.height != self._height_px:
                self._width_px = e.width
                self._height_px = e.height
                self._draw()

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1+r, y1,   x2-r, y1,
            x2,   y1,   x2,   y1+r,
            x2,   y2-r, x2,   y2,
            x2-r, y2,   x1+r, y2,
            x1,   y2,   x1,   y2-r,
            x1,   y1+r, x1,   y1,
        ]
        return self.create_polygon(pts, smooth=True, **kw)

    def _draw(self, hover=False):
        self.delete('all')
        if self._active:
            bg_c, fg_c, sub_c = NAVY, '#FFFFFF', '#BEC8F0'
        elif hover:
            bg_c, fg_c, sub_c = CARD, NAVY, TEXT_DIM
        else:
            bg_c, fg_c, sub_c = BG2, TEXT, TEXT_DIM
        outline = NAVY if self._active else BORDER
        self._rounded_rect(1, 1, self._width_px-1, self._height_px-1, 14,
                            fill=bg_c, outline=outline)
        cx = self._width_px // 2
        cy = self._height_px // 2
        self.create_text(cx, cy - 10, text=self.fmt_title,
                          fill=fg_c,
                          font=(F_BTN[0], 13, 'bold'),
                          anchor='center')
        self.create_text(cx, cy + 11, text=self.fmt_sub,
                          fill=sub_c,
                          font=F_SMALL,
                          anchor='center')

    def _on_click(self, e):
        if self._command:
            self._command()

    def _on_enter(self, e):
        if not self._active:
            self._draw(hover=True)
        self.configure(cursor='hand2')

    def _on_leave(self, e):
        self._draw(hover=False)

    def set_active(self, val):
        self._active = val
        self._draw()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # WantedSans 폰트 등록 (창 생성 후)
        self._fam = load_custom_font()
        init_fonts(self._fam)

        self.title('ChangerSurf  |  폰트 변환기')
        self.geometry('880x620')
        self.configure(bg=BG)
        self.resizable(False, False)

        try:
            ico = _resource(os.path.join('Assets', 'icon.ico'))
            self.iconbitmap(ico)
        except Exception:
            pass

        self._logo_img = None
        if HAS_PIL:
            try:
                raw = base64.b64decode(_LOGO_B64)
                img = Image.open(io.BytesIO(raw)).resize((48, 48), Image.LANCZOS)
                self._logo_img = ImageTk.PhotoImage(img)
            except Exception:
                pass

        # 공통 상태
        self.current_mode = "easy"  # "easy" or "advanced"
        self._thread = None

        # 심화 모드용 데이터
        self.src_files   = []
        self.dst_format  = tk.StringVar(value='.woff2')
        self.dst_dir     = None
        self.same_dir    = tk.BooleanVar(value=True)
        self._fmt_toggles = {}

        # Easy 모드용 데이터
        self.easy_src_file = None
        self.easy_dst_ext  = tk.StringVar(value='.woff2')
        self._easy_cards   = {}
        self.easy_last_out = None

        self._build_header()
        self._build_easy_view()
        self._build_advanced_view()
        self._switch_mode("easy")
        self._check_deps()

    def _check_deps(self):
        if not HAS_FONTTOOLS:
            self._log('[경고] fonttools 미설치: pip install fonttools', 'warn')
        if not HAS_BROTLI:
            self._log('[경고] brotli 미설치 (WOFF2 불가): pip install brotli', 'warn')
        if HAS_FONTTOOLS and HAS_BROTLI:
            self._log('[준비] 파일 추가 -> 형식 선택 -> 변환 시작!', 'ok')

    def _build_header(self):
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill='x', padx=30, pady=(20, 0))

        if self._logo_img:
            ll = tk.Label(hdr, image=self._logo_img, bg=BG, cursor='hand2')
            ll.pack(side='left', padx=(0, 14))
            ll.bind('<Button-1>', lambda e: webbrowser.open('https://rheehose.com'))
            ll.bind('<Enter>', lambda e: ll.configure(bg=BG2))
            ll.bind('<Leave>', lambda e: ll.configure(bg=BG))

        tc = tk.Frame(hdr, bg=BG)
        tc.pack(side='left')
        tk.Label(tc, text='ChangerSurf', font=F_TITLE, bg=BG, fg=NAVY).pack(anchor='w')
        tk.Label(tc, text='폰트 형식 변환기  |  TTF · OTF · WOFF · WOFF2',
                 font=F_SUB, bg=BG, fg=TEXT_DIM).pack(anchor='w')

        # 우측: 모드 스위치 & 웹 링크
        rw = tk.Frame(hdr, bg=BG)
        rw.pack(side='right')

        # 모드 스위치
        self.mode_switch = ModeSwitch(rw, on_change=self._switch_mode)
        self.mode_switch.pack(side='left', padx=(0, 14))

        lnk = tk.Label(rw, text='rheehose.com', font=(self._fam, 10, 'underline'),
                       bg=BG, fg=NAVY_LT, cursor='hand2')
        lnk.pack(side='left', padx=(0, 4))
        lnk.bind('<Button-1>', lambda e: webbrowser.open('https://rheehose.com'))
        lnk.bind('<Enter>', lambda e: lnk.configure(fg=NAVY))
        lnk.bind('<Leave>', lambda e: lnk.configure(fg=NAVY_LT))

        tk.Frame(self, bg=BORDER, height=1).pack(fill='x', padx=30, pady=(16, 0))

    # ==========================
    # Easy 모드 뷰
    # ==========================
    def _build_easy_view(self):
        self.easy_frame = tk.Frame(self, bg=BG)

        # 양쪽 두 개 노드 및 중앙 화살표
        node_row = tk.Frame(self.easy_frame, bg=BG)
        node_row.pack(fill='x', padx=30, pady=(16, 0))

        # 좌측 노드: 현재 파일 (파랑 테마)
        self.easy_file_node = EasyFileNode(node_row, on_pick=self._easy_pick_file)
        self.easy_file_node.pack(side='left', padx=(0, 10))

        # 가운데: 물리 튕김 쫀득한 화살표
        self.spring_arrow = SpringArrow(node_row)
        self.spring_arrow.pack(side='left', padx=6)

        # 우측 노드: 바꿀 형식 (빨강 테마)
        right_box = tk.Frame(node_row, bg=RED_BG,
                             highlightbackground=RED_BORDER, highlightthickness=2)
        right_box.pack(side='right', fill='both', expand=True, padx=(10, 0))

        tk.Label(right_box, text="바꿀 형식 선택", font=F_BTN, bg=RED_BG, fg=RED_TEXT).pack(pady=(18, 12))

        cards_frame = tk.Frame(right_box, bg=RED_BG)
        cards_frame.pack(fill='both', expand=True, padx=14, pady=(0, 14))

        for ext, title, sub in EASY_OPTIONS:
            card = EasyFormatCard(cards_frame, ext, title, sub, on_select=self._easy_select_format)
            card.pack(fill='x', pady=4)
            self._easy_cards[ext] = card

        self._easy_select_format('.woff2')

        # 하단 변환 실행 바
        bot = tk.Frame(self.easy_frame, bg=BG)
        bot.pack(fill='x', padx=30, pady=(20, 0))

        self.easy_btn = PillButton(
            bot, "이 형식으로 바로 변환하기",
            command=self._easy_start_convert,
            bg=NAVY, fg='#FFFFFF', hover_bg=NAVY_DK,
            font=(self._fam, 15, 'bold'), padx=24, pady=12, radius=26
        )
        self.easy_btn.pack(fill='x')

        self.easy_status_var = tk.StringVar(value="파일을 선택하고 변환 버튼을 누르면 원본 폴더에 즉시 저장됩니다.")
        self.easy_status_lbl = tk.Label(
            bot, textvariable=self.easy_status_var, font=F_LABEL, bg=BG, fg=TEXT_DIM,
            cursor='arrow'
        )
        self.easy_status_lbl.pack(pady=8)
        self.easy_status_lbl.bind('<Button-1>', self._easy_open_folder)

    def _easy_pick_file(self):
        f = filedialog.askopenfilename(
            title='변환할 폰트 파일 선택',
            filetypes=[
                ('폰트 파일', '*.ttf *.otf *.woff *.woff2'),
                ('모든 파일', '*.*'),
            ]
        )
        if f:
            self.easy_src_file = Path(f)
            self.easy_file_node.set_file(self.easy_src_file)
            self.easy_status_var.set(f"선택됨: {self.easy_src_file.name}  |  목표 형식을 선택하고 변환하세요.")
            self.spring_arrow.kick(24.0)

    def _easy_select_format(self, ext):
        self.easy_dst_ext.set(ext)
        for e, c in self._easy_cards.items():
            c.set_selected(e == ext)
        self.spring_arrow.kick(12.0)

    def _easy_start_convert(self):
        if not HAS_FONTTOOLS:
            messagebox.showerror('오류', 'fonttools 가 설치되지 않았습니다.\npip install fonttools')
            return
        if not self.easy_src_file or not self.easy_src_file.exists():
            messagebox.showwarning('파일 없음', '왼쪽 영역을 클릭하여 변환할 폰트 파일을 먼저 선택하세요.')
            self._easy_pick_file()
            return
        dst_ext = self.easy_dst_ext.get()
        if dst_ext == '.woff2' and not HAS_BROTLI:
            messagebox.showerror('오류', 'WOFF2 변환에는 brotli 가 필요합니다.\npip install brotli')
            return
        if self.easy_src_file.suffix.lower() == dst_ext:
            messagebox.showinfo('동일 형식', '이미 해당 형식의 파일입니다. 다른 형식을 선택하세요.')
            return

        self.spring_arrow.recoil_and_shoot()
        self.easy_btn.set_text("변환 중...")
        self.easy_btn.set_disabled(True)
        threading.Thread(target=self._easy_do_convert, daemon=True).start()

    def _easy_do_convert(self):
        src = self.easy_src_file
        dst_ext = self.easy_dst_ext.get()
        dst_dir = src.parent
        try:
            out = convert_font(src, dst_ext, dst_dir)
            self.easy_last_out = out
            sz = out.stat().st_size / 1024
            msg = f"[완료] {out.name} ({sz:.1f} KB) 생성 완료!  [여기를 클릭하여 폴더 열기]"
            self.easy_status_var.set(msg)
            self.easy_status_lbl.configure(fg=SUCCESS, cursor='hand2')
        except Exception as e:
            self.easy_status_var.set(f"[오류] 변환 실패: {e}")
            self.easy_status_lbl.configure(fg=ERROR, cursor='arrow')
        finally:
            self.easy_btn.set_text("이 형식으로 바로 변환하기")
            self.easy_btn.set_disabled(False)

    def _easy_open_folder(self, e=None):
        if self.easy_last_out and self.easy_last_out.parent.exists():
            try:
                os.startfile(str(self.easy_last_out.parent))
            except Exception:
                pass
        elif self.easy_src_file and self.easy_src_file.parent.exists():
            try:
                os.startfile(str(self.easy_src_file.parent))
            except Exception:
                pass

    # ==========================
    # 심화 모드 뷰
    # ==========================
    def _build_advanced_view(self):
        self.adv_frame = tk.Frame(self, bg=BG)

        body = tk.Frame(self.adv_frame, bg=BG)
        body.pack(fill='both', expand=True, padx=30, pady=14)

        # 왼쪽 파일 목록
        left = tk.Frame(body, bg=CARD,
                        highlightbackground=BORDER, highlightthickness=1)
        left.pack(side='left', fill='both', expand=True)

        lrow = tk.Frame(left, bg=CARD)
        lrow.pack(fill='x', padx=16, pady=(14, 6))
        tk.Label(lrow, text='입력 파일 목록',
                 font=F_BTN, bg=CARD, fg=NAVY).pack(side='left')
        tk.Label(lrow, text='TTF / OTF / WOFF / WOFF2 다중 선택',
                 font=F_LABEL, bg=CARD, fg=TEXT_DIM).pack(side='left', padx=10)

        lf = tk.Frame(left, bg=CARD)
        lf.pack(fill='both', expand=True, padx=16, pady=(0, 10))
        self.file_lb = tk.Listbox(
            lf, bg=BG, fg=TEXT,
            selectbackground=NAVY, selectforeground='#fff',
            font=F_LOG, bd=0, highlightthickness=0,
            activestyle='none', relief='flat', height=7,
        )
        sb = tk.Scrollbar(lf, orient='vertical',
                          command=self.file_lb.yview, bg=CARD)
        self.file_lb.configure(yscrollcommand=sb.set)
        self.file_lb.pack(side='left', fill='both', expand=True)
        sb.pack(side='right', fill='y')

        fbtn = tk.Frame(left, bg=CARD)
        fbtn.pack(fill='x', padx=16, pady=(0, 14))
        PillButton(fbtn, '+ 파일 추가', command=self._add_files,
                   bg=NAVY, fg='#fff', hover_bg=NAVY_DK,
                   font=F_SMALL, padx=14, pady=6, radius=20
                   ).pack(side='left', padx=(0, 6))
        PillButton(fbtn, '- 선택 삭제', command=self._remove_sel,
                   bg=BG2, fg=NAVY, hover_bg=CARD,
                   font=F_SMALL, padx=14, pady=6, radius=20
                   ).pack(side='left', padx=(0, 6))
        PillButton(fbtn, '전체 지우기', command=self._clear_files,
                   bg=BG2, fg=TEXT_DIM, hover_bg=CARD,
                   font=F_SMALL, padx=14, pady=6, radius=20
                   ).pack(side='left')

        # 오른쪽 설정
        right = tk.Frame(body, bg=BG, width=252)
        right.pack(side='right', fill='y', padx=(16, 0))
        right.pack_propagate(False)

        tk.Label(right, text='출력 형식',
                 font=F_BTN, bg=BG, fg=TEXT).pack(anchor='w', pady=(2, 8))

        fgf = tk.Frame(right, bg=BG)
        fgf.pack(fill='x')
        for i, ext in enumerate(FORMATS):
            r, c = divmod(i, 2)
            name, sub = FMT_INFO[ext]
            tog = FormatToggle(fgf, name, sub,
                               command=lambda e=ext: self._select_fmt(e))
            tog.grid(row=r, column=c, padx=4, pady=4, sticky='nsew')
            fgf.columnconfigure(c, weight=1)
            self._fmt_toggles[ext] = tog
        self._select_fmt('.woff2')

        tk.Frame(right, bg=BORDER, height=1).pack(fill='x', pady=14)
        tk.Label(right, text='저장 위치',
                 font=F_BTN, bg=BG, fg=TEXT).pack(anchor='w', pady=(0, 8))

        tk.Checkbutton(
            right, text='원본 파일과 같은 폴더',
            variable=self.same_dir, command=self._toggle_dst,
            bg=BG, fg=TEXT, selectcolor=BG,
            activebackground=BG, activeforeground=NAVY,
            font=F_LABEL, cursor='hand2',
        ).pack(anchor='w')

        self._dst_pill = PillButton(
            right, '출력 폴더 선택', command=self._pick_dst,
            bg=BG2, fg=TEXT_DIM, hover_bg=CARD,
            font=F_LABEL, padx=14, pady=6, radius=20
        )
        self._dst_pill.pack(fill='x', pady=8)
        self._dst_pill.set_disabled(True)

        self.dst_lbl = tk.Label(right, text='--', font=F_SMALL,
                                bg=BG, fg=TEXT_DIM, wraplength=222, justify='left')
        self.dst_lbl.pack(anchor='w')

        tk.Frame(right, bg=BORDER, height=1).pack(fill='x', pady=14)

        self.cvt_pill = PillButton(
            right, '변환 시작', command=self._start,
            bg=NAVY, fg='#FFFFFF', hover_bg=NAVY_DK,
            font=(self._fam, 14, 'bold'), padx=20, pady=14, radius=30
        )
        self.cvt_pill.pack(fill='x')

        self.prog_var = tk.StringVar(value='')
        tk.Label(right, textvariable=self.prog_var,
                 font=F_SMALL, bg=BG, fg=TEXT_DIM,
                 wraplength=222, justify='left').pack(anchor='w', pady=6)

        # 로그 패널
        log_frame = tk.Frame(self.adv_frame, bg=LOGBG,
                             highlightbackground=BORDER, highlightthickness=1)
        log_frame.pack(fill='x', padx=30, pady=(0, 14))

        lh = tk.Frame(log_frame, bg=LOGBG)
        lh.pack(fill='x', padx=12, pady=(6, 2))
        tk.Label(lh, text='변환 로그',
                 font=F_LABEL, bg=LOGBG, fg=TEXT_DIM).pack(side='left')
        PillButton(lh, '지우기', command=self._clear_log,
                   bg=BG2, fg=TEXT_DIM, hover_bg=CARD,
                   font=F_SMALL, padx=10, pady=3, radius=12
                   ).pack(side='right')

        self.log_text = tk.Text(
            log_frame, height=4,
            bg=LOGBG, fg=TEXT,
            font=F_LOG, bd=0, relief='flat',
            state='disabled', wrap='word',
            highlightthickness=0,
        )
        self.log_text.pack(fill='x', padx=12, pady=(0, 8))
        self.log_text.tag_config('ok',   foreground=SUCCESS)
        self.log_text.tag_config('err',  foreground=ERROR)
        self.log_text.tag_config('warn', foreground=WARNING)
        self.log_text.tag_config('info', foreground=NAVY)

    def _switch_mode(self, mode):
        self.current_mode = mode
        if mode == "easy":
            self.adv_frame.pack_forget()
            self.easy_frame.pack(fill='both', expand=True)
        else:
            self.easy_frame.pack_forget()
            self.adv_frame.pack(fill='both', expand=True)

    def _select_fmt(self, ext):
        self.dst_format.set(ext)
        for e, t in self._fmt_toggles.items():
            t.set_active(e == ext)

    def _toggle_dst(self):
        if self.same_dir.get():
            self._dst_pill.set_disabled(True)
            self.dst_lbl.configure(text='--')
            self.dst_dir = None
        else:
            self._dst_pill.set_disabled(False)

    def _pick_dst(self):
        d = filedialog.askdirectory(title='출력 폴더 선택')
        if d:
            self.dst_dir = Path(d)
            self.dst_lbl.configure(text=str(self.dst_dir))

    def _add_files(self):
        files = filedialog.askopenfilenames(
            title='폰트 파일 선택',
            filetypes=[
                ('폰트 파일', '*.ttf *.otf *.woff *.woff2'),
                ('모든 파일', '*.*'),
            ],
        )
        for f in files:
            p = Path(f)
            if p not in self.src_files:
                self.src_files.append(p)
                tag = EXT_LABELS.get(p.suffix.lower(), p.suffix.upper())
                self.file_lb.insert('end', '  ' + p.name + '  [' + tag + ']')

    def _remove_sel(self):
        for i in reversed(self.file_lb.curselection()):
            self.file_lb.delete(i)
            self.src_files.pop(i)

    def _clear_files(self):
        self.file_lb.delete(0, 'end')
        self.src_files.clear()

    def _start(self):
        if not HAS_FONTTOOLS:
            messagebox.showerror('오류',
                'fonttools 가 설치되지 않았습니다.\npip install fonttools')
            return
        if not self.src_files:
            messagebox.showwarning('파일 없음', '변환할 파일을 먼저 추가하세요.')
            return
        if self.dst_format.get() == '.woff2' and not HAS_BROTLI:
            messagebox.showerror('오류',
                'WOFF2 변환에는 brotli 가 필요합니다.\npip install brotli')
            return
        if not self.same_dir.get() and self.dst_dir is None:
            messagebox.showwarning('폴더 미선택',
                '출력 폴더를 선택하거나 원본 폴더 옵션을 활성화하세요.')
            return
        if self._thread and self._thread.is_alive():
            return
        self.cvt_pill.set_text('변환 중...')
        self.cvt_pill.set_disabled(True)
        self._thread = threading.Thread(target=self._do_convert, daemon=True)
        self._thread.start()

    def _do_convert(self):
        dst_ext = self.dst_format.get()
        files   = list(self.src_files)
        ok = fail = 0
        for idx, src in enumerate(files, 1):
            self.prog_var.set(str(idx) + '/' + str(len(files)) + '  ' + src.name)
            try:
                if src.suffix.lower() == dst_ext:
                    self._log('[건너뜀] 동일 형식: ' + src.name, 'warn')
                    continue
                dst_dir = src.parent if self.same_dir.get() else self.dst_dir
                dst_dir.mkdir(parents=True, exist_ok=True)
                out = convert_font(src, dst_ext, dst_dir)
                sz  = out.stat().st_size / 1024
                self._log(
                    '[완료] ' + src.name + ' -> ' + out.name
                    + ' (' + f'{sz:.1f}' + ' KB)', 'ok')
                ok += 1
            except Exception as e:
                self._log('[오류] ' + src.name + ' : ' + str(e), 'err')
                fail += 1
        self.prog_var.set('완료  성공:' + str(ok) + '  실패:' + str(fail))
        self._log(
            '-- 완료: 성공 ' + str(ok) + '개, 실패 ' + str(fail) + '개 --', 'info')
        self.after(0, self._reset_convert_btn)

    def _reset_convert_btn(self):
        self.cvt_pill.set_text('변환 시작')
        self.cvt_pill.set_disabled(False)

    def _log(self, msg, tag=''):
        def _w():
            self.log_text.configure(state='normal')
            self.log_text.insert('end', msg + '\n', tag)
            self.log_text.see('end')
            self.log_text.configure(state='disabled')
        self.after(0, _w)

    def _clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', 'end')
        self.log_text.configure(state='disabled')


if __name__ == '__main__':
    app = App()
    app.mainloop()
