"""
Project IDE Opener - Modern UI v2.0
------------------------------------------------
Modern + shortcut di Favorit (IDE / Explorer / Both)
Jalan: python main.py  |  Build: build_exe.bat
"""

import os, json, string, stat, subprocess, threading, shutil, traceback, sys
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser

try:
    import ctypes
    _GetFileAttributesW = ctypes.windll.kernel32.GetFileAttributesW
except Exception:
    _GetFileAttributesW = None

_FILE_ATTR_HIDDEN = getattr(stat, "FILE_ATTRIBUTE_HIDDEN", 2)
_PROJECT_MARKERS = (".vscode", "package.json", "pyproject.toml", ".git", "requirements.txt", "go.mod", "Cargo.toml", ".sln", ".csproj")
_ICON_MAP = {
    ".py": "🐍", ".js": "📜", ".ts": "📜", ".html": "🌐", ".css": "🎨",
    ".json": "🔧", ".md": "📝", ".txt": "📄", ".pdf": "📕", ".zip": "📦",
    ".exe": "⚙️", ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".gif": "🖼️",
    ".mp4": "🎬", ".mp3": "🎵", ".xlsx": "📊", ".docx": "📃",
}

# ---------- Logger Terminal ----------
def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line, file=sys.stderr if level in ("ERROR","WARN") else sys.stdout, flush=True)
    # juga tulis ke file log opsional
    try:
        logfile = Path(__file__).parent / "app.log"
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except: pass

APP_TITLE = "Project IDE Opener"
APP_VERSION = "2.0 Modern"
CONFIG_FILE = Path.home() / ".vscode_opener_config.json"

# Modern Themes: Obsidian Dark (default) & Warm Studio Light
THEMES = {
    "dark": {
        "bg": "#09090B",
        "card": "#18181B",
        "sidebar": "#111114",
        "surface2": "#121216",
        "input_bg": "#121215",
        "header": "#09090B",
        "header_btn": "#18181B",
        "header_btn_hover": "#27272A",
        "header_fg": "#F4F4F5",
        "header_sub": "#A1A1AA",
        "accent": "#6366F1",
        "accent_hover": "#4F46E5",
        "accent2": "#6366F1",
        "accent_fg": "#A5B4FC",
        "accent_soft": "#1E1B4B",
        "accent_soft_hover": "#312E81",
        "border": "#27272A",
        "border2": "#3F3F46",
        "text": "#F4F4F5",
        "text2": "#A1A1AA",
        "text3": "#71717A",
        "btn_sec": "#27272A",
        "btn_sec_hover": "#3F3F46",
        "hover_bg": "#27272A",
        "row_alt": "#141417",
        "tree_sel": "#312E81",
        "tree_head": "#141417",
        "tree_head_fg": "#D4D4D8",
        "scroll_trough": "#111114",
        "scroll_bg": "#3F3F46",
        "scroll_active": "#52525B",
        "success": "#10B981",
        "danger": "#F87171",
        "danger_soft": "#450A0A",
        "warning": "#FBBF24",
    },
    "light": {
        "bg": "#F4F4F5",
        "card": "#FFFFFF",
        "sidebar": "#FAFAFA",
        "surface2": "#F4F4F5",
        "input_bg": "#FFFFFF",
        "header": "#18181B",
        "header_btn": "#27272A",
        "header_btn_hover": "#3F3F46",
        "header_fg": "#FAFAFA",
        "header_sub": "#A1A1AA",
        "accent": "#4F46E5",
        "accent_hover": "#4338CA",
        "accent2": "#4F46E5",
        "accent_fg": "#4F46E5",
        "accent_soft": "#EEF2FF",
        "accent_soft_hover": "#E0E7FF",
        "border": "#E4E4E7",
        "border2": "#D4D4D8",
        "text": "#18181B",
        "text2": "#52525B",
        "text3": "#A1A1AA",
        "btn_sec": "#F4F4F5",
        "btn_sec_hover": "#E4E4E7",
        "hover_bg": "#EEF2FF",
        "row_alt": "#FAFAFA",
        "tree_sel": "#E0E7FF",
        "tree_head": "#F4F4F5",
        "tree_head_fg": "#3F3F46",
        "scroll_trough": "#F4F4F5",
        "scroll_bg": "#D4D4D8",
        "scroll_active": "#A1A1AA",
        "success": "#10B981",
        "danger": "#EF4444",
        "danger_soft": "#FEE2E2",
        "warning": "#F59E0B",
    },
}

C = dict(THEMES["dark"])

def apply_theme(name):
    C.clear()
    C.update(THEMES.get(name, THEMES["dark"]))

_LOCALAPPDATA = Path(os.environ.get("LOCALAPPDATA", ""))
_PROGRAM_FILES = Path(os.environ.get("ProgramFiles", "C:/Program Files"))
_PROGRAM_FILES_X86 = Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)"))

IDE_SPECS = [
    {
        "id": "vscode", "name": "VS Code", "short": "VS", "icon": "💙",
        "cmds": ["code"],
        "paths": [
            _LOCALAPPDATA / "Programs/Microsoft VS Code/bin/code.cmd",
            _PROGRAM_FILES / "Microsoft VS Code/bin/code.cmd",
            _PROGRAM_FILES / "Microsoft VS Code/Code.exe",
            _PROGRAM_FILES_X86 / "Microsoft VS Code/bin/code.cmd",
        ],
    },
    {
        "id": "cursor", "name": "Cursor", "short": "Cursor", "icon": "⚡",
        "cmds": ["cursor"],
        "paths": [
            _LOCALAPPDATA / "Programs/cursor/Cursor.exe",
            _LOCALAPPDATA / "Programs/Cursor/Cursor.exe",
            _LOCALAPPDATA / "Programs/cursor/resources/app/bin/cursor.cmd",
            _PROGRAM_FILES / "cursor/Cursor.exe",
            _PROGRAM_FILES / "Cursor/Cursor.exe",
        ],
    },
    {
        "id": "antigravity", "name": "Antigravity IDE", "short": "Antigravity", "icon": "⬛",
        "prefer_paths": True,
        "paths": [
            _LOCALAPPDATA / "Programs/Antigravity IDE/bin/antigravity.cmd",
            _LOCALAPPDATA / "Programs/Antigravity IDE/bin/agy.cmd",
            _LOCALAPPDATA / "Programs/Antigravity IDE/Antigravity IDE.exe",
            _LOCALAPPDATA / "Programs/Antigravity IDE/Antigravity.exe",
            _PROGRAM_FILES / "Antigravity IDE/Antigravity IDE.exe",
            _PROGRAM_FILES / "Antigravity IDE/Antigravity.exe",
        ],
        "scan_dirs": [
            _LOCALAPPDATA / "Programs/Antigravity IDE",
            _PROGRAM_FILES / "Antigravity IDE",
        ],
        "cmds": ["agy", "antigravity"],
    },
    {
        "id": "windsurf", "name": "Windsurf", "short": "Windsurf", "icon": "🏄",
        "cmds": ["windsurf"],
        "paths": [
            _LOCALAPPDATA / "Programs/Windsurf/Windsurf.exe",
            _LOCALAPPDATA / "Programs/Windsurf/bin/windsurf.cmd",
            _PROGRAM_FILES / "Windsurf/Windsurf.exe",
        ],
    },
    {
        "id": "trae", "name": "Trae", "short": "Trae", "icon": "🤖",
        "cmds": ["trae"],
        "paths": [
            _LOCALAPPDATA / "Programs/Trae/Trae.exe",
            _PROGRAM_FILES / "Trae/Trae.exe",
        ],
    },
    {
        "id": "zed", "name": "Zed", "short": "Zed", "icon": "⚙️",
        "cmds": ["zed"],
        "paths": [
            _LOCALAPPDATA / "Programs/Zed/Zed.exe",
            _LOCALAPPDATA / "Zed/Zed.exe",
        ],
    },
    {
        "id": "sublime", "name": "Sublime Text", "short": "Sublime", "icon": "🟧",
        "cmds": ["subl", "sublime_text"],
        "paths": [
            _PROGRAM_FILES / "Sublime Text/subl.exe",
            _PROGRAM_FILES / "Sublime Text 3/subl.exe",
            _PROGRAM_FILES_X86 / "Sublime Text/subl.exe",
        ],
    },
    {
        "id": "phpstorm", "name": "PhpStorm", "short": "PhpStorm", "icon": "🐘",
        "cmds": ["phpstorm", "phpstorm64"],
        "jetbrains": ("PhpStorm", "phpstorm64.exe"),
    },
    {
        "id": "webstorm", "name": "WebStorm", "short": "WebStorm", "icon": "🌐",
        "cmds": ["webstorm", "webstorm64"],
        "jetbrains": ("WebStorm", "webstorm64.exe"),
    },
    {
        "id": "pycharm", "name": "PyCharm", "short": "PyCharm", "icon": "🐍",
        "cmds": ["pycharm", "pycharm64"],
        "jetbrains": ("PyCharm", "pycharm64.exe"),
    },
    {
        "id": "idea", "name": "IntelliJ IDEA", "short": "IDEA", "icon": "☕",
        "cmds": ["idea", "idea64"],
        "jetbrains": ("IntelliJ IDEA", "idea64.exe"),
    },
    {
        "id": "goland", "name": "GoLand", "short": "GoLand", "icon": "🐹",
        "cmds": ["goland", "goland64"],
        "jetbrains": ("GoLand", "goland64.exe"),
    },
    {
        "id": "android_studio", "name": "Android Studio", "short": "Studio", "icon": "📱",
        "cmds": ["studio", "studio64"],
        "paths": [
            _PROGRAM_FILES / "Android/Android Studio/bin/studio64.exe",
            _LOCALAPPDATA / "Programs/Android Studio/bin/studio64.exe",
        ],
    },
    {
        "id": "visualstudio", "name": "Visual Studio", "short": "VS IDE", "icon": "🟣",
        "cmds": ["devenv"],
        "paths": [
            _PROGRAM_FILES / "Microsoft Visual Studio/2022/Community/Common7/IDE/devenv.exe",
            _PROGRAM_FILES / "Microsoft Visual Studio/2022/Professional/Common7/IDE/devenv.exe",
            _PROGRAM_FILES / "Microsoft Visual Studio/2022/Enterprise/Common7/IDE/devenv.exe",
            _PROGRAM_FILES_X86 / "Microsoft Visual Studio/2019/Community/Common7/IDE/devenv.exe",
        ],
    },
    {
        "id": "notepadpp", "name": "Notepad++", "short": "NPP", "icon": "📝",
        "cmds": ["notepad++"],
        "paths": [
            _PROGRAM_FILES / "Notepad++/notepad++.exe",
            _PROGRAM_FILES_X86 / "Notepad++/notepad++.exe",
        ],
    },
]

def _find_jetbrains_exe(product_prefix, exe_name):
    # 1. JetBrains Toolbox: %LOCALAPPDATA%\JetBrains\Toolbox\apps\<Product>\ch-*\*\bin\<exe>
    tb_root = _LOCALAPPDATA / "JetBrains/Toolbox/apps"
    if tb_root.exists():
        try:
            for prod_dir in tb_root.iterdir():
                if prod_dir.is_dir() and prod_dir.name.lower().startswith(product_prefix.lower().replace(" ", "")):
                    for ch in prod_dir.iterdir():
                        if ch.is_dir():
                            for ver in ch.iterdir():
                                exe = ver / "bin" / exe_name
                                if exe.exists():
                                    return str(exe)
        except Exception:
            pass
    # 2. Standard install: C:\Program Files\JetBrains\<Product>*\bin\<exe>
    jb_root = _PROGRAM_FILES / "JetBrains"
    if jb_root.exists():
        try:
            for d in jb_root.iterdir():
                if d.is_dir() and d.name.lower().startswith(product_prefix.lower()):
                    exe = d / "bin" / exe_name
                    if exe.exists():
                        return str(exe)
        except Exception:
            pass
    return None

def _find_in_paths(spec):
    for p in spec.get("paths", []):
        try:
            if p.exists():
                return str(p)
        except Exception:
            pass
    for d in spec.get("scan_dirs", []):
        try:
            if d.is_dir():
                for f in d.iterdir():
                    if f.is_file() and f.suffix.lower() == ".exe":
                        nl = f.name.lower()
                        if not nl.startswith(("unins", "update", "crash", "elevat")):
                            return str(f)
        except Exception:
            pass
    return None

def detect_installed_ides():
    """Auto-detect semua IDE/editor yang terinstall di perangkat ini."""
    found = []
    for spec in IDE_SPECS:
        exe_path = None
        if spec.get("prefer_paths"):
            exe_path = _find_in_paths(spec)
        if not exe_path:
            for cmd in spec.get("cmds", []):
                w = shutil.which(cmd)
                if w:
                    exe_path = w
                    break
        if not exe_path and not spec.get("prefer_paths"):
            exe_path = _find_in_paths(spec)
        if not exe_path and "jetbrains" in spec:
            prod, exe_name = spec["jetbrains"]
            exe_path = _find_jetbrains_exe(prod, exe_name)
        if exe_path:
            found.append({
                "id": spec["id"],
                "name": spec["name"],
                "short": spec["short"],
                "icon": spec["icon"],
                "path": exe_path,
            })
    return found

def find_vscode():
    for ide in detect_installed_ides():
        if ide["id"] == "vscode":
            return ide["path"]
    return None

def get_drives():
    return [f"{c}:\\" for c in string.ascii_uppercase if os.path.exists(f"{c}:\\")]

def get_quick_access():
    home=Path.home()
    # Pakai emoji Windows standar (Segoe UI Emoji) - pasti tampil di Windows 10/11
    items=[
        ("🏠  Home", str(home)),
        ("🖥️  Desktop", str(home/"Desktop")),
        ("📄  Documents", str(home/"Documents")),
        ("⬇️  Downloads", str(Path("D:/Download") if Path("D:/Download").exists() else home/"Downloads")),
        ("💻  GIT Desktop", "D:\\GIT_DESKTOP"),
        ("📁  Project", "D:\\PROJECT"),
    ]
    # hanya tampilkan yang ada
    out=[]
    for l,p in items:
        if os.path.exists(p) and (l,p) not in out:
            out.append((l,p))
    return out

def load_config():
    default={"recent":[],"favorites":[],"last_path":str(Path.home()),"show_hidden":False,"selected_ide":"","theme":"dark"}
    if CONFIG_FILE.exists():
        try:
            d=json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            for k in default:
                if k not in d: d[k]=default[k]
            return d
        except: return default
    return default

def save_config(cfg):
    try: CONFIG_FILE.write_text(json.dumps(cfg,indent=2,ensure_ascii=False),encoding="utf-8")
    except Exception as e: print(e)

# ---------- Helpers UI ----------
def mk_btn(parent, text, bg, fg, hover_bg=None, cmd=None, padx=10, pady=4, font=("Segoe UI",9,"bold")):
    b=tk.Button(parent, text=text, bg=bg, fg=fg, activebackground=hover_bg or bg,
                activeforeground=fg, relief="flat", bd=0, padx=padx, pady=pady,
                font=font, cursor="hand2", takefocus=0, command=cmd)
    if hover_bg:
        b.bind("<Enter>", lambda e: b.config(bg=hover_bg))
        b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

class FavCard(tk.Frame):
    """Kartu Favorit modern dengan 3 shortcut + drag handle"""
    def __init__(self, parent, path, on_vs, on_exp, on_both, on_del, on_nav, drag_start=None, drag_motion=None, drag_end=None, ide_short="VS"):
        super().__init__(parent, bg=C["card"], highlightbackground=C["border"], highlightthickness=1, bd=0)
        self.path = path
        p = Path(path)
        name = p.name or path
        is_unc_fav = path.startswith("\\\\") or path.startswith("//")
        exists = True if is_unc_fav else p.exists()

        # Hover effect
        self.bind("<Enter>", lambda e: self.config(highlightbackground=C["accent"]))
        self.bind("<Leave>", lambda e: self.config(highlightbackground=C["border"]))

        # Drag handle (kiri paling) - area drag & drop
        handle = tk.Label(self, text="⠿", bg=C["card"], fg=C["text3"], font=("Segoe UI",10), cursor="fleur", padx=4)
        handle.pack(side="left", fill="y", pady=4)
        handle.bind("<Enter>", lambda e: handle.config(fg=C["accent_fg"], bg=C["hover_bg"]))
        handle.bind("<Leave>", lambda e: handle.config(fg=C["text3"], bg=C["card"]))
        # tooltip via status? cukup cursor
        if drag_start:
            handle.bind("<Button-1>", lambda e: drag_start(e, path, self))
            handle.bind("<B1-Motion>", drag_motion)
            handle.bind("<ButtonRelease-1>", drag_end)
            # juga card bisa di-drag via handle saja biar tidak bentrok klik navigasi
            self._handle = handle

        # Left clickable area
        left = tk.Frame(self, bg=C["card"])
        left.pack(side="left", fill="both", expand=True, padx=(4,6), pady=8)
        left.bind("<Button-1>", lambda e: on_nav(path))
        left.bind("<Enter>", lambda e: self.config(highlightbackground=C["accent"]))
        left.bind("<Leave>", lambda e: self.config(highlightbackground=C["border"]))

        # Icon + Text - pakai font emoji agar tampil
        if is_unc_fav:
            icon = "📁"
        else:
            icon = "📦" if (p/".git").exists() or (p/"package.json").exists() or (p/"pyproject.toml").exists() else "📁"
        # top row: icon + name
        top = tk.Frame(left, bg=C["card"])
        top.pack(fill="x")
        top.bind("<Button-1>", lambda e: on_nav(path))
        lbl_icon = tk.Label(top, text=icon, bg=C["card"], font=("Segoe UI Emoji",11), cursor="hand2")
        lbl_icon.pack(side="left")
        lbl_name = tk.Label(top, text=name, bg=C["card"], fg=C["text"], font=("Segoe UI",9,"bold"), anchor="w", cursor="hand2")
        lbl_name.pack(side="left", padx=(6,0))
        lbl_hilang = None
        if not exists:
            lbl_hilang = tk.Label(top, text="• hilang", bg=C["card"], fg=C["danger"], font=("Segoe UI",7), cursor="hand2")
            lbl_hilang.pack(side="left", padx=6)

        # path label - responsive wraplength akan diupdate via on_sidebar_resize
        lbl_path = tk.Label(left, text=path, bg=C["card"], fg=C["text2"], font=("Consolas",7), anchor="w", cursor="hand2", wraplength=180, justify="left")
        lbl_path.pack(fill="x", pady=(2,0))
        lbl_path.bind("<Button-1>", lambda e: on_nav(path))
        self.lbl_path = lbl_path
        self.lbl_name = lbl_name
        self._left = left

        # Right buttons
        right = tk.Frame(self, bg=C["card"])
        right.pack(side="right", padx=(0,8), pady=6)

        # IDE button - primary
        b1 = mk_btn(right, f" {ide_short}", C["accent2"], "white", C["accent_hover"], lambda: on_vs(path), padx=8, pady=3, font=("Segoe UI",7,"bold"))
        b1.pack(side="left", padx=2)
        # Explorer
        b2 = mk_btn(right, "📂", C["btn_sec"], C["text"], C["btn_sec_hover"], lambda: on_exp(path), padx=6, pady=3, font=("Segoe UI",8))
        b2.pack(side="left", padx=2)
        # Both
        b3 = mk_btn(right, f"{ide_short}+📂", C["accent_soft"], C["accent_fg"], C["accent_soft_hover"], lambda: on_both(path), padx=6, pady=3, font=("Segoe UI",7,"bold"))
        b3.pack(side="left", padx=2)

        # Delete
        bd = mk_btn(right, "×", C["card"], C["text3"], C["danger_soft"], lambda: on_del(path), padx=6, pady=3, font=("Segoe UI",9,"bold"))
        bd.config(fg=C["danger"])
        bd.pack(side="left", padx=(4,0))
        self._right = right

        # Make card clickable - SELURUH area kiri + kartu (kecuali handle & tombol kanan)
        # biar klik di mana saja (icon, nama, path, background) langsung buka konten
        def _nav(e=None): on_nav(path)
        # outer card juga clickable (area kosong)
        self.bind("<Button-1>", lambda e: _nav() if e.widget in (self, left, top, lbl_icon, lbl_name, lbl_path) or str(e.widget).startswith(str(left)) else None)
        # set cursor hand2 + bind semua elemen kiri
        for w in [self, left, top, lbl_icon, lbl_name, lbl_path] + ([lbl_hilang] if lbl_hilang else []):
            try:
                w.bind("<Button-1>", lambda e: _nav())
                w.config(cursor="hand2")
            except: pass
        # juga bind left container secara rekursif agar tidak ada dead zone
        left.bind("<Button-1>", lambda e: _nav())
        top.bind("<Button-1>", lambda e: _nav())

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg=load_config()
        self.theme_name = self.cfg.get("theme", "dark")
        apply_theme(self.theme_name)
        self.installed_ides = detect_installed_ides()
        self.active_ide = self._pick_active_ide(self.cfg.get("selected_ide", ""))
        self.vscode_path = self.active_ide["path"] if self.active_ide else None
        self.current_path=Path(self.cfg.get("last_path", str(Path.home())))
        if not self.current_path.exists(): self.current_path=Path.home()
        self.history=[self.current_path]; self.history_idx=0
        self.show_hidden=self.cfg.get("show_hidden", False)
        self.all_items=[]
        self.current_selection=self.current_path
        self._load_seq = 0
        self._search_seq = 0
        self._filter_after_id = None
        self._sidebar_resize_after = None
        self._win_resize_after = None
        self._last_sidebar_w = 0
        self._last_win_w = 0

        # AppID + DPI Awareness Windows agar font & ikon tajam di layar HiDPI
        try:
            import ctypes
            try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception: pass
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Yudha.ProjectIDEOpener.2.0")
        except Exception: pass
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.geometry("1250x760")
        self.minsize(680, 480)
        self.configure(bg=C["bg"])

        self._build_style()
        self._build_ui()
        self._refresh_all()
        # set icon + dark titlebar setelah UI jadi
        self.update_idletasks()
        self._apply_titlebar_theme()
        self._set_window_icon()
        self.after(200, self._set_window_icon)

    def _apply_titlebar_theme(self):
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            val = ctypes.c_int(1 if self.theme_name == "dark" else 0)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(val), ctypes.sizeof(val))
        except Exception:
            pass

    def toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.cfg["theme"] = self.theme_name
        save_config(self.cfg)
        apply_theme(self.theme_name)
        self._rebuild_ui()

    def _rebuild_ui(self):
        cur_q = self.search_var.get() if hasattr(self, "search_var") else ""
        for w in self.winfo_children():
            w.destroy()
        self._last_sidebar_w = 0
        self._last_win_w = 0
        self.configure(bg=C["bg"])
        self._build_style()
        self._build_ui()
        self._apply_titlebar_theme()
        if cur_q:
            self.search_var.set(cur_q)
        self.build_breadcrumb()
        self.apply_filter()
        self.update_selection_label()
        self.status(f"🎨 Tema diubah ke {'Obsidian Dark' if self.theme_name == 'dark' else 'Studio Light'}")

    def _build_style(self):
        style=ttk.Style(self)
        try: style.theme_use("clam")
        except: pass
        style.configure("TFrame", background=C["bg"])
        style.configure("Card.TFrame", background=C["card"])
        style.configure("Sidebar.TFrame", background=C["sidebar"])
        style.configure("Header.TLabel", background=C["header"], foreground=C["header_fg"], font=("Segoe UI",11,"bold"))
        style.configure("HeaderSub.TLabel", background=C["header"], foreground=C["header_sub"], font=("Segoe UI",8))
        style.configure("Title.TLabel", background=C["card"], foreground=C["text"], font=("Segoe UI",9,"bold"))
        style.configure("Muted.TLabel", background=C["bg"], foreground=C["text2"], font=("Segoe UI",8))
        style.configure("Treeview", background=C["card"], fieldbackground=C["card"], foreground=C["text"],
                        rowheight=32, font=("Segoe UI",9), borderwidth=0, relief="flat")
        style.configure("Treeview.Heading", background=C["tree_head"], foreground=C["tree_head_fg"], font=("Segoe UI",8,"bold"),
                        relief="flat", borderwidth=0, padding=(8, 7))
        style.map("Treeview", background=[("selected", C["tree_sel"])], foreground=[("selected", C["text"])])
        style.map("Treeview.Heading", background=[("active", C["hover_bg"])])
        style.configure("TEntry", padding=6)
        style.configure("TCombobox", padding=5, fieldbackground=C["input_bg"], background=C["btn_sec"],
                        foreground=C["text"], bordercolor=C["border2"], arrowsize=13, arrowcolor=C["text2"])
        style.map("TCombobox", fieldbackground=[("readonly", C["input_bg"])], selectbackground=[("readonly", C["input_bg"])],
                  selectforeground=[("readonly", C["text"])], foreground=[("readonly", C["text"])])
        style.configure("Vertical.TScrollbar", troughcolor=C["scroll_trough"], background=C["scroll_bg"], borderwidth=0, arrowsize=11, width=10)
        style.map("Vertical.TScrollbar", background=[("active", C["scroll_active"])])

    def _set_window_icon(self):
        """Set icon title bar + taskbar (pakai logo.ico, fallback logo.png)"""
        try:
            import sys as _sys
            base = Path(getattr(_sys, '_MEIPASS', Path(__file__).parent))
            ico = base / "logo.ico"
            png = base / "logo.png"
            if not ico.exists():
                ico = Path(__file__).parent / "logo.ico"
            if not png.exists():
                png = Path(__file__).parent / "logo.png"
            # cari juga di cwd & D:\GIT_DESKTOP\OpenerProject sebagai fallback terakhir
            if not ico.exists():
                for cand in [Path.cwd()/ "logo.ico", Path("D:/GIT_DESKTOP/OpenerProject/logo.ico")]:
                    if cand.exists():
                        ico=cand; break
            if not png.exists():
                for cand in [Path.cwd()/ "logo.png", Path("D:/GIT_DESKTOP/OpenerProject/logo.png")]:
                    if cand.exists():
                        png=cand; break
            log(f"icon try: ico={ico} exists={ico.exists()} png={png} exists={png.exists()}", "INFO")
            # 1. iconbitmap untuk title bar (wajib .ico)
            if ico.exists():
                done=False
                for method in [lambda: self.iconbitmap(str(ico)), lambda: self.iconbitmap(default=str(ico)), lambda: self.wm_iconbitmap(str(ico))]:
                    try:
                        method()
                        done=True
                        log(f"iconbitmap OK via {method}", "INFO")
                        break
                    except Exception as e:
                        log(f"iconbitmap try fail: {e}", "WARN")
                        continue
                if not done:
                    log("iconbitmap semua gagal", "ERROR")
                # 2. iconphoto untuk taskbar (pakai PNG, karena PhotoImage tidak support .ico dengan baik)
                if png.exists():
                    try:
                        img = tk.PhotoImage(file=str(png))
                        self.iconphoto(True, img)
                        self._icon_ref = img
                        # juga via wm call
                        try: self.tk.call('wm', 'iconphoto', self._w, img)
                        except: pass
                        log(f"iconphoto PNG OK: {png}", "INFO")
                    except Exception as e2:
                        log(f"iconphoto PNG fail: {e2}", "ERROR")
                else:
                    log("png tidak ada untuk iconphoto", "WARN")
            elif png.exists():
                try:
                    img = tk.PhotoImage(file=str(png))
                    self.iconphoto(True, img)
                    self._icon_ref = img
                    log(f"icon set PNG: {png}", "INFO")
                except Exception as e:
                    log(f"iconphoto PNG fail: {e}", "ERROR")
            else:
                log("logo.ico/png tidak ditemukan, pakai default", "WARN")
        except Exception as e:
            log(f"icon load gagal: {e}\n{traceback.format_exc()}", "ERROR")

    def _build_ui(self):
        # ===== HEADER =====
        header = tk.Frame(self, bg=C["header"], height=58)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Frame(self, bg=C["accent"], height=2).pack(fill="x")

        # Left header: icon + title
        lh = tk.Frame(header, bg=C["header"])
        lh.pack(side="left", padx=16, pady=10)
        tk.Label(lh, text="◆", bg=C["header"], fg=C["accent_fg"], font=("Segoe UI",17,"bold")).pack(side="left")
        tx = tk.Frame(lh, bg=C["header"])
        tx.pack(side="left", padx=10)
        tk.Label(tx, text=APP_TITLE, bg=C["header"], fg=C["header_fg"], font=("Segoe UI",11,"bold"), anchor="w").pack(anchor="w")
        tk.Label(tx, text=f"v{APP_VERSION}  •  Buka folder ke IDE pilihan + Explorer dalam 1 klik", bg=C["header"], fg=C["header_sub"], font=("Segoe UI",7), anchor="w").pack(anchor="w")

        # Right header: detected IDE status + theme toggle + buttons
        rh = tk.Frame(header, bg=C["header"])
        rh.pack(side="right", padx=16)
        ide_cnt = len(self.installed_ides)
        ide_ok = ide_cnt > 0
        vs_txt = f"●  {ide_cnt} IDE Terdeteksi" if ide_ok else "●  IDE Tidak Ditemukan"
        vs_fg = "#34D399" if ide_ok else "#F87171"
        self.lbl_vs_header = tk.Label(rh, text=vs_txt, bg=C["header_btn"], fg=vs_fg, font=("Segoe UI",8,"bold"), padx=10, pady=4)
        self.lbl_vs_header.pack(side="left", padx=(0,6))
        theme_lbl = "☀️ Light" if self.theme_name == "dark" else "🌙 Dark"
        mk_btn(rh, theme_lbl, C["header_btn"], C["header_fg"], C["header_btn_hover"], self.toggle_theme, padx=10, pady=4, font=("Segoe UI",8)).pack(side="left", padx=3)
        mk_btn(rh, "🔄 Scan IDE", C["header_btn"], C["header_sub"], C["header_btn_hover"], self.rescan_ides, padx=10, pady=4, font=("Segoe UI",8)).pack(side="left", padx=3)
        mk_btn(rh, "📋 Logs", C["header_btn"], C["header_sub"], C["header_btn_hover"], self.show_logs, padx=10, pady=4, font=("Segoe UI",8)).pack(side="left", padx=3)
        mk_btn(rh, "⚙ Settings", C["header_btn"], C["header_sub"], C["header_btn_hover"], self.show_settings, padx=10, pady=4, font=("Segoe UI",8)).pack(side="left", padx=3)

        # ===== TOOLBAR NAV =====
        toolbar = tk.Frame(self, bg=C["card"], highlightbackground=C["border"], highlightthickness=1)
        toolbar.pack(fill="x", padx=12, pady=(10,0))

        inner = tk.Frame(toolbar, bg=C["card"])
        inner.pack(fill="x", padx=10, pady=8)

        # nav buttons
        nav = tk.Frame(inner, bg=C["card"])
        nav.pack(side="left")
        for txt, cmd, tip in [("◀", self.go_back, "Back"), ("▶", self.go_forward, "Forward"), ("⬆", self.go_up, "Up"), ("↻", self.refresh, "Refresh")]:
            mk_btn(nav, txt, C["btn_sec"], C["text"], C["btn_sec_hover"], cmd, padx=8, pady=4, font=("Segoe UI",9,"bold")).pack(side="left", padx=2)

        tk.Frame(inner, bg=C["border"], width=1, height=28).pack(side="left", padx=10, fill="y")

        tk.Label(inner, text="Lokasi", bg=C["card"], fg=C["text2"], font=("Segoe UI",8,"bold")).pack(side="left")
        self.path_var=tk.StringVar(value=str(self.current_path))
        entry_wrap = tk.Frame(inner, bg=C["input_bg"], highlightbackground=C["border2"], highlightthickness=1)
        entry_wrap.pack(side="left", fill="x", expand=True, padx=8)
        self.entry_path=tk.Entry(entry_wrap, textvariable=self.path_var, font=("Consolas",9), bg=C["input_bg"], fg=C["text"],
                                 insertbackground=C["text"], relief="flat", bd=0, highlightthickness=0)
        self.entry_path.pack(fill="x", padx=8, pady=5, expand=True)
        self.entry_path.bind("<Return>", lambda e: self.navigate_to(self.path_var.get()))
        self.entry_path.bind("<FocusIn>", lambda e: entry_wrap.config(highlightbackground=C["accent"]))
        self.entry_path.bind("<FocusOut>", lambda e: (entry_wrap.config(highlightbackground=C["border2"]), self.path_var.set(str(self.current_path))))

        mk_btn(inner, "Go", C["accent2"], "white", C["accent_hover"], lambda: self.navigate_to(self.path_var.get()), padx=12, pady=5).pack(side="left", padx=2)
        mk_btn(inner, "📂 Browse", C["btn_sec"], C["text"], C["btn_sec_hover"], self.browse_dialog, padx=10, pady=5, font=("Segoe UI",8,"bold")).pack(side="left", padx=2)

        # ===== SEARCH BAR =====
        search_bar = tk.Frame(self, bg=C["bg"])
        search_bar.pack(fill="x", padx=12, pady=8)
        tk.Label(search_bar, text="🔍", bg=C["bg"], fg=C["text2"], font=("Segoe UI",10)).pack(side="left", padx=(2,4))
        s_wrap = tk.Frame(search_bar, bg=C["input_bg"], highlightbackground=C["border"], highlightthickness=1)
        s_wrap.pack(side="left", fill="x", expand=True)
        self.search_var=tk.StringVar()
        self.search_var.trace_add("write", self._schedule_filter)
        se=tk.Entry(s_wrap, textvariable=self.search_var, font=("Segoe UI",9), bg=C["input_bg"], fg=C["text"],
                    insertbackground=C["text"], relief="flat", bd=0, highlightthickness=0)
        se.pack(side="left", fill="x", padx=(10,2), pady=6, expand=True)
        se.insert(0, "")
        self.entry_search = se
        se.bind("<FocusIn>", lambda e: s_wrap.config(highlightbackground=C["accent"]))
        se.bind("<FocusOut>", lambda e: s_wrap.config(highlightbackground=C["border"]))
        mk_btn(s_wrap, "✕", C["input_bg"], C["text3"], C["btn_sec"], lambda: self.search_var.set(""), padx=6, pady=2, font=("Segoe UI",8,"bold")).pack(side="right", padx=4)

        # hidden toggle + count + recursive
        self.hidden_var=tk.BooleanVar(value=self.show_hidden)
        chk = tk.Checkbutton(search_bar, text="Hidden", variable=self.hidden_var, command=self.toggle_hidden,
                             bg=C["bg"], fg=C["text2"], selectcolor=C["card"], font=("Segoe UI",8), activebackground=C["bg"], activeforeground=C["text"], cursor="hand2")
        chk.pack(side="left", padx=(10,6))
        self.recursive_var=tk.BooleanVar(value=True)
        chk2 = tk.Checkbutton(search_bar, text="🔍 Cari rekursif", variable=self.recursive_var, command=self.apply_filter,
                              bg=C["bg"], fg=C["text2"], selectcolor=C["card"], font=("Segoe UI",8,"bold"), activebackground=C["bg"], activeforeground=C["text"], cursor="hand2")
        chk2.pack(side="left", padx=4)
        self._search_hint_lbl = tk.Label(search_bar, text="contoh: index.php → public\\index.php", bg=C["bg"], fg=C["text3"], font=("Segoe UI",7,"italic"))
        self._search_hint_lbl.pack(side="left", padx=4)
        self.lbl_count = tk.Label(search_bar, text="", bg=C["bg"], fg=C["text2"], font=("Segoe UI",8,"bold"))
        self.lbl_count.pack(side="right", padx=4)

        # ===== TOOLBAR: sidebar toggle + responsive hint =====
        ctrl_bar = tk.Frame(self, bg=C["bg"])
        ctrl_bar.pack(fill="x", padx=12, pady=(0,6))
        self.btn_toggle_sidebar = mk_btn(ctrl_bar, "☰  Sembunyikan Sidebar", C["card"], C["text"], C["btn_sec_hover"], self.toggle_sidebar, padx=10, pady=4, font=("Segoe UI",8,"bold"))
        self.btn_toggle_sidebar.config(highlightbackground=C["border"], highlightthickness=1)
        self.btn_toggle_sidebar.pack(side="left")
        self._ctrl_hint_lbl = tk.Label(ctrl_bar, text="  •  Drag garis tengah  •  Auto-collapse <850px", bg=C["bg"], fg=C["text3"], font=("Segoe UI",7))
        self._ctrl_hint_lbl.pack(side="left", padx=8)
        # shortcut jaringan
        mk_btn(ctrl_bar, "🌐  Buka \\it-4", C["accent_soft"], C["accent_fg"], C["accent_soft_hover"], lambda: self.navigate_to("\\\\it-4"), padx=8, pady=3, font=("Segoe UI",7,"bold")).pack(side="left", padx=4)
        mk_btn(ctrl_bar, "🌐  Input IP/Server", C["btn_sec"], C["text"], C["btn_sec_hover"], self.prompt_network_path, padx=8, pady=3, font=("Segoe UI",7)).pack(side="left", padx=2)
        self._ctrl_f9_lbl = tk.Label(ctrl_bar, text="F9 / Ctrl+B toggle", bg=C["bg"], fg=C["text3"], font=("Segoe UI",7,"italic"))
        self._ctrl_f9_lbl.pack(side="right")

        # ===== MAIN PANED - RESPONSIVE =====
        self.paned = tk.PanedWindow(self, bg=C["bg"], sashwidth=6, sashrelief="raised", bd=0, opaqueresize=True)
        self.paned.pack(fill="both", expand=True, padx=12, pady=(0,12))
        paned = self.paned

        # LEFT SIDEBAR - scrollable, responsive
        self.sidebar_wrap = tk.Frame(paned, bg=C["sidebar"], highlightbackground=C["border"], highlightthickness=1)
        self.sidebar_visible = True
        self.sidebar_width = 340
        self._auto_collapsed = False  # flag untuk auto-collapse
        paned.add(self.sidebar_wrap, minsize=220, width=self.sidebar_width, stretch="never")

        # Canvas scroll for sidebar
        canvas = tk.Canvas(self.sidebar_wrap, bg=C["sidebar"], highlightthickness=0)
        sb = ttk.Scrollbar(self.sidebar_wrap, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        left = tk.Frame(canvas, bg=C["sidebar"])
        self.left_frame = left
        self.sidebar_canvas = canvas
        self.sidebar_left = left
        canvas.create_window((0,0), window=left, anchor="nw")

        def on_conf(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            self._schedule_sidebar_resize()
        left.bind("<Configure>", on_conf)
        # resize sidebar_wrap juga trigger responsive (debounced)
        self.sidebar_wrap.bind("<Configure>", lambda e: self._schedule_sidebar_resize())
        # mousewheel - handler global cerdas: deteksi posisi kursor
        # agar sidebar & konten scroll terpisah sesuai area hover
        def _on_global_wheel(e):
            try:
                x, y = e.x_root, e.y_root
                w = self.winfo_containing(x, y)
                if not w:
                    return
                # walk up untuk cek apakah di dalam sidebar
                cur = w
                while cur is not None:
                    if cur == self.sidebar_wrap or cur == self.sidebar_canvas or cur == self.sidebar_left:
                        self.sidebar_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
                        return "break"
                    # descendant dari sidebar_left (semua isi sidebar)
                    try:
                        if str(cur).startswith(str(self.sidebar_left)):
                            self.sidebar_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
                            return "break"
                    except: pass
                    # jika di atas tree, biarkan tree yang scroll (native)
                    # tapi kita handle manual biar konsisten
                    try:
                        if cur == self.tree or str(cur).startswith(str(self.tree)):
                            # Treeview handle sendiri, jangan scroll sidebar
                            return  # biarkan default Treeview
                    except: pass
                    cur = cur.master if hasattr(cur, 'master') else None
                # tidak di sidebar/tree -> biarkan default
            except: pass
        self.bind_all("<MouseWheel>", _on_global_wheel)

        # --- Section helper ---
        def section(title, icon=""):
            f=tk.Frame(left, bg=C["sidebar"])
            f.pack(fill="x", padx=12, pady=(14,6))
            tk.Label(f, text=f"{icon}  {title}", bg=C["sidebar"], fg=C["text"], font=("Segoe UI",8,"bold")).pack(anchor="w")
            tk.Frame(f, bg=C["border"], height=1).pack(fill="x", pady=(6,0))
            return f

        # Quick Access - FIX emoji font
        section("AKSES CEPAT", "⚡")
        self.quick_items=get_quick_access()
        q_frame=tk.Frame(left, bg=C["sidebar"])
        q_frame.pack(fill="x", padx=8)
        self.btn_quick=[]
        for label, path in self.quick_items:
            b=tk.Button(q_frame, text=f"  {label}", anchor="w", bg=C["card"], fg=C["text"], relief="flat", bd=0,
                        font=("Segoe UI Emoji", 8), padx=8, pady=6, cursor="hand2", takefocus=0,
                        highlightbackground=C["border"], highlightthickness=1,
                        command=lambda p=path: self.navigate_to(p))
            b.pack(fill="x", pady=2)
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg=C["hover_bg"]))
            b.bind("<Leave>", lambda e, btn=b: btn.config(bg=C["card"]))
            self.btn_quick.append(b)

        # Drives - pakai emoji standar
        section("DRIVE", "💾")
        d_frame=tk.Frame(left, bg=C["sidebar"])
        d_frame.pack(fill="x", padx=8)
        for d in get_drives():
            b=tk.Button(d_frame, text=f"  💾  {d}", anchor="w", bg=C["card"], fg=C["text"], relief="flat", bd=0,
                        font=("Segoe UI Emoji", 8), padx=8, pady=5, cursor="hand2", takefocus=0,
                        highlightbackground=C["border"], highlightthickness=1,
                        command=lambda p=d: self.navigate_to(p))
            b.pack(fill="x", pady=2)
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg=C["hover_bg"]))
            b.bind("<Leave>", lambda e, btn=b: btn.config(bg=C["card"]))

        # FAVORIT - MODERN CARD WITH SHORTCUTS
        sec_fav = section("FAVORIT  •  klik kartu untuk navigasi", "⭐")
        # fav controls
        fav_ctrl = tk.Frame(left, bg=C["sidebar"])
        fav_ctrl.pack(fill="x", padx=12, pady=(0,6))
        mk_btn(fav_ctrl, "＋ Tambah Favorit (Folder Saat Ini)", C["accent2"], "white", C["accent_hover"], self.add_favorite, padx=8, pady=4, font=("Segoe UI",7,"bold")).pack(fill="x")

        self.fav_container = tk.Frame(left, bg=C["sidebar"])
        self.fav_container.pack(fill="x", padx=8, pady=4)

        self.lbl_no_fav = tk.Label(self.fav_container, text="Belum ada favorit.\nTambahkan folder yang sering dibuka.", bg=C["sidebar"], fg=C["text3"], font=("Segoe UI",7), justify="center")
        # will be shown if empty

        # Recent
        section("TERAKHIR DIBUKA", "🕘")
        self.recent_frame=tk.Frame(left, bg=C["sidebar"])
        self.recent_frame.pack(fill="x", padx=8, pady=(0,10))

        # ===== RIGHT CONTENT =====
        right = tk.Frame(paned, bg=C["bg"])
        self.right_frame = right
        paned.add(right, stretch="always", minsize=300)

        # breadcrumb card
        bc_card = tk.Frame(right, bg=C["card"], highlightbackground=C["border"], highlightthickness=1)
        bc_card.pack(fill="x", pady=(0,8))
        self.breadcrumb = tk.Frame(bc_card, bg=C["card"])
        self.breadcrumb.pack(fill="x", padx=10, pady=8, anchor="w")
        self.lbl_info = tk.Label(right, text="", bg=C["bg"], fg=C["text2"], font=("Segoe UI",7))
        self.lbl_info.pack(anchor="w", padx=2, pady=(0,4))

        # Tree card
        tree_card = tk.Frame(right, bg=C["card"], highlightbackground=C["border"], highlightthickness=1)
        tree_card.pack(fill="both", expand=True)

        cols=("name","type","modified")
        self.tree=ttk.Treeview(tree_card, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("name", text="  📂  Nama (Folder & File)", anchor="w")
        self.tree.heading("type", text="Tipe / Ukuran", anchor="center")
        self.tree.heading("modified", text="Dimodifikasi", anchor="center")
        self.tree.column("name", width=520, anchor="w")
        self.tree.column("type", width=110, anchor="center")
        self.tree.column("modified", width=150, anchor="center")

        vsb=ttk.Scrollbar(tree_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        vsb.pack(side="right", fill="y", padx=(0,2), pady=10)

        self.tree.tag_configure("even", background=C["card"])
        self.tree.tag_configure("odd", background=C["row_alt"])

        self.tree.bind("<Double-Button-1>", self.on_tree_double)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_context)

        # context menu - dinamis sesuai file/folder & IDE terpilih
        self.menu=tk.Menu(self, tearoff=0, bg=C["card"], fg=C["text"], activebackground=C["accent2"], activeforeground="white", font=("Segoe UI",9))
        self.menu.add_command(label="📂 Buka Folder", command=lambda: self.open_selected())
        self.menu.add_command(label="📄 Buka File di IDE", command=self.open_in_vscode)
        self.menu.add_separator()
        self.menu.add_command(label="💙 Buka di IDE", command=self.open_in_vscode)
        self.ide_submenu=tk.Menu(self.menu, tearoff=0, bg=C["card"], fg=C["text"], activebackground=C["accent2"], activeforeground="white", font=("Segoe UI",9))
        self.menu.add_cascade(label="🚀 Buka dengan IDE lain", menu=self.ide_submenu)
        self.menu.add_command(label="📂 Buka di Explorer", command=self.open_in_explorer_only)
        self.menu.add_command(label="💙+📂 IDE + Explorer", command=self.open_in_both)
        self.menu.add_separator()
        self.menu.add_command(label="⭐ Tambah ke Favorit", command=self.add_favorite)
        self.menu.add_command(label="📋 Copy Path", command=self.copy_path)
        self.menu.add_command(label="▶️ Jalankan File (default app)", command=self.open_with_default_app)

        # ===== ACTION BAR (Modern & Responsive) =====
        action = tk.Frame(right, bg=C["card"], highlightbackground=C["border"], highlightthickness=1)
        action.pack(fill="x", pady=(8,0))
        self._action_bar = action
        self._action_stacked = False

        a_left = tk.Frame(action, bg=C["card"])
        a_left.pack(side="left", fill="x", expand=True, padx=12, pady=10)
        self._action_left = a_left
        tk.Label(a_left, text="TERPILIH", bg=C["card"], fg=C["text3"], font=("Segoe UI",7,"bold")).pack(anchor="w")
        self.lbl_selected = tk.Label(a_left, text=str(self.current_path), bg=C["card"], fg=C["accent_fg"], font=("Consolas",8), anchor="w", wraplength=500, justify="left")
        self.lbl_selected.pack(anchor="w", fill="x", pady=(2,0))
        self.lbl_selected_sub = tk.Label(a_left, text="Folder saat ini", bg=C["card"], fg=C["text2"], font=("Segoe UI",7), anchor="w")
        self.lbl_selected_sub.pack(anchor="w")

        a_right = tk.Frame(action, bg=C["card"])
        a_right.pack(side="right", padx=12, pady=10)
        self._action_right = a_right

        # IDE Selector (auto-detected)
        ide_box = tk.Frame(a_right, bg=C["card"])
        ide_box.pack(side="left", padx=(0,8))
        tk.Label(ide_box, text="IDE", bg=C["card"], fg=C["text3"], font=("Segoe UI",7,"bold")).pack(anchor="w")
        self.ide_var = tk.StringVar()
        self.ide_combo = ttk.Combobox(ide_box, textvariable=self.ide_var, state="readonly", width=18, font=("Segoe UI",8,"bold"))
        self.ide_combo.pack(anchor="w")
        self.ide_combo.bind("<<ComboboxSelected>>", self.on_ide_selected)

        self.btn_vscode = mk_btn(a_right, "  💙  Buka di IDE  ", C["accent2"], "white", C["accent_hover"], self.open_in_vscode, padx=14, pady=8, font=("Segoe UI",9,"bold"))
        self.btn_vscode.pack(side="left", padx=4)
        self.btn_both = mk_btn(a_right, " IDE + Explorer ", C["card"], C["accent_fg"], C["accent_soft"], self.open_in_both, padx=12, pady=8, font=("Segoe UI",9,"bold"))
        self.btn_both.config(highlightbackground=C["accent"], highlightthickness=1, bd=0, relief="flat")
        self.btn_both.pack(side="left", padx=4)
        # explorer only
        mk_btn(a_right, "📂", C["btn_sec"], C["text"], C["btn_sec_hover"], self.open_in_explorer_only, padx=10, pady=8).pack(side="left", padx=4)

        self._sync_ide_ui()

        # STATUS BAR
        self.status_var=tk.StringVar(value="✨ Siap — pilih folder lalu klik buka")
        status = tk.Label(self, textvariable=self.status_var, anchor="w", bg=C["surface2"], fg=C["text2"], font=("Segoe UI",7), bd=1, relief="flat", padx=10, pady=4)
        status.pack(fill="x", side="bottom")

        # after build, refresh lists
        self.refresh_fav_list()
        self.refresh_recent_list()

        # ===== RESPONSIVE: resize + shortcuts =====
        self.bind("<Configure>", self.on_window_resize)
        self.bind("<F9>", lambda e: self.toggle_sidebar())
        self.bind("<Control-b>", lambda e: self.toggle_sidebar())  # VS Code style
        # simpan lebar awal untuk proporsi
        self.after(300, self._init_sash)

    def _pick_active_ide(self, preferred_id):
        if not self.installed_ides:
            return None
        for ide in self.installed_ides:
            if ide["id"] == preferred_id or ide["name"] == preferred_id:
                return ide
        return self.installed_ides[0]

    def _sync_ide_ui(self):
        ide_cnt = len(self.installed_ides)
        if hasattr(self, "lbl_vs_header"):
            if ide_cnt > 0:
                self.lbl_vs_header.config(text=f"●  {ide_cnt} IDE Terdeteksi", fg="#4ADE80")
            else:
                self.lbl_vs_header.config(text="●  IDE Tidak Ditemukan", fg="#F87171")
        if hasattr(self, "ide_combo"):
            if self.installed_ides:
                labels = [f"{i['icon']}  {i['name']}" for i in self.installed_ides]
                self.ide_combo["values"] = labels
                idx = 0
                if self.active_ide:
                    for k, item in enumerate(self.installed_ides):
                        if item["id"] == self.active_ide["id"]:
                            idx = k
                            break
                self.ide_combo.current(idx)
            else:
                self.ide_combo["values"] = ["(Tidak ada IDE)"]
                self.ide_combo.current(0)

        if self.active_ide:
            name = self.active_ide["name"]
            short = self.active_ide["short"]
            icon = self.active_ide["icon"]
            self.btn_vscode.config(text=f"  {icon}  Buka di {name}  ")
            self.btn_both.config(text=f" {short} + Explorer ")
            try:
                self.menu.entryconfig(1, label=f"📄 Buka File di {name}")
                self.menu.entryconfig(3, label=f"{icon} Buka di {name}")
                self.menu.entryconfig(6, label=f"{icon}+📂 {name} + Explorer")
            except Exception:
                pass
        else:
            self.btn_vscode.config(text="  ⚠️  IDE Tidak Ditemukan  ")
            self.btn_both.config(text=" IDE + Explorer ")

        if hasattr(self, "ide_submenu"):
            self.ide_submenu.delete(0, "end")
            if self.installed_ides:
                for ide in self.installed_ides:
                    self.ide_submenu.add_command(
                        label=f"{ide['icon']}  {ide['name']}",
                        command=lambda _ide=ide: self._open_vscode(str(self.get_target()), False, ide=_ide),
                    )
            else:
                self.ide_submenu.add_command(label="(Tidak ada IDE terdeteksi)", state="disabled")

    def on_ide_selected(self, event=None):
        if not self.installed_ides:
            return
        idx = self.ide_combo.current()
        if 0 <= idx < len(self.installed_ides):
            self.active_ide = self.installed_ides[idx]
            self.vscode_path = self.active_ide["path"]
            self.cfg["selected_ide"] = self.active_ide["id"]
            save_config(self.cfg)
            self._sync_ide_ui()
            self.refresh_fav_list()
            self.refresh_recent_list()
            self.status(f"{self.active_ide['icon']} IDE aktif: {self.active_ide['name']}")

    def rescan_ides(self):
        self.installed_ides = detect_installed_ides()
        cur_id = self.active_ide["id"] if self.active_ide else self.cfg.get("selected_ide", "")
        self.active_ide = self._pick_active_ide(cur_id)
        self.vscode_path = self.active_ide["path"] if self.active_ide else None
        self._sync_ide_ui()
        self.refresh_fav_list()
        self.refresh_recent_list()
        if self.installed_ides:
            names = ", ".join(i["name"] for i in self.installed_ides)
            self.status(f"🔄 {len(self.installed_ides)} IDE terdeteksi: {names}")
        else:
            self.status("⚠️ Tidak ada IDE terdeteksi di perangkat ini")

    def _is_unc(self, s): return s.startswith("\\\\") or s.startswith("//")
    # ---------- Navigation ----------
    def navigate_to(self, path_str, add_history=True):
        raw = path_str.strip().strip('"').strip()
        # normalisasi UNC: \\it-4 atau \\192.168.x.x\share
        is_unc = self._is_unc(raw)
        # ganti / jadi \ untuk UNC agar konsisten Windows
        if is_unc:
            raw = raw.replace("/", "\\")
            # normalisasi tapi JANGAN pakai os.path.normpath karena '\\it-4' -> '\it-4' (hilang 1 slash)
            # cukup rapikan trailing slash & double slash
            # // -> \\
            if raw.startswith("//"):
                raw = "\\" + raw[1:]
                raw = raw.replace("/", "\\")
                # pastikan tetap \\
                if not raw.startswith("\\\\"):
                    raw = "\\" + raw
            # hapus trailing \ berlebih tapi jangan potong \\server
            while len(raw) > 3 and raw.endswith("\\"):
                raw = raw[:-1]
        p=Path(raw)
        # untuk lokal, tetap cek exists ketat; untuk UNC jangan blok - biarkan coba load
        # karena Explorer bisa akses dengan konteks user yang kadang Path.exists() False di Python
        if not is_unc:
            if not p.exists():
                log(f"navigate_to gagal exists: {p}", "ERROR")
                messagebox.showerror("Tidak ditemukan", f"Path tidak ditemukan:\n{p}\n\nLihat terminal untuk detail."); return
            if p.is_file(): p=p.parent
            try: p=p.resolve()
            except: pass
            # clear UNC raw saat pindah ke lokal agar tidak nyangkut
            self._unc_raw = None
        else:
            # UNC: jangan check exists di sini, langsung coba navigasi
            try:
                if os.path.isfile(raw):
                    p=Path(raw).parent
                    raw=str(p)
                    p=Path(raw)
                else:
                    p=Path(raw)
            except: p=Path(raw)
            if self._is_unc_server_root(raw):
                self._unc_raw = raw
            else:
                self._unc_raw = None
        self.current_path=p
        log(f"navigate_to: raw={raw} | is_unc={is_unc} | _unc_raw={getattr(self,'_unc_raw',None)} | current_path={self.current_path} | str={str(self.current_path)}", "INFO")
        # untuk UNC, pakai raw double-slash agar tidak jadi \it-4
        if is_unc:
            self.path_var.set(raw)
            if self._is_unc_server_root(raw):
                # paksa current_path display pakai raw (biar \\it-4)
                # simpan juga sebagai atribut untuk load_folders
                self.current_path = Path(raw)  # tetap Path tapi string salah, jadi kita override str via _unc_raw
                self.path_var.set(raw)
        else:
            self.path_var.set(str(p))
        if add_history:
            if self.history_idx < len(self.history)-1:
                self.history=self.history[:self.history_idx+1]
            if not self.history or self.history[-1]!=p:
                # untuk UNC server root, history simpan raw string agar tidak jadi \it-4
                hist_p = Path(self._unc_raw) if is_unc and self._is_unc_server_root(raw) else p
                self.history.append(hist_p); self.history_idx=len(self.history)-1
        # simpan last_path pakai raw untuk UNC server root
        save_p = self._unc_raw if is_unc and self._is_unc_server_root(raw) else str(p)
        self.cfg["last_path"]=save_p; save_config(self.cfg)
        log(f"history now: {[str(x) for x in self.history]} idx={self.history_idx} | last_path={save_p}", "INFO")
        self._refresh_all()

    def go_back(self):
        if self.history_idx>0:
            self.history_idx-=1; self.navigate_to(str(self.history[self.history_idx]), add_history=False)
        else: self.status("Sudah di awal history")
    def go_forward(self):
        if self.history_idx < len(self.history)-1:
            self.history_idx+=1; self.navigate_to(str(self.history[self.history_idx]), add_history=False)
        else: self.status("Sudah di akhir history")
    def go_up(self):
        # handle UNC server root via _unc_raw
        cur_display = getattr(self, '_unc_raw', None) or str(self.current_path)
        if cur_display.startswith("\\\\"):
            if self._is_unc_server_root(cur_display):
                self.status("Sudah di root server (\\it-4)"); return
            # untuk UNC share, parent adalah server
            par_str = cur_display.rsplit("\\", 1)[0] if "\\" in cur_display[2:] else cur_display
            # jika sudah di share root, naik ke server
            if cur_display.count("\\") <= 3:  # \\server\share
                self.navigate_to("\\\\" + cur_display[2:].split("\\")[0])
                return
        par=self.current_path.parent
        if str(self.current_path).startswith("\\\\"):
            if str(par) == str(self.current_path):
                self.status("Sudah di root sharing"); return
        if par!=self.current_path and par.exists(): self.navigate_to(str(par))
        elif cur_display.startswith("\\\\"):
            self.navigate_to(str(par) if str(par).startswith("\\\\") else cur_display.rsplit("\\",1)[0])
    def refresh(self): self._refresh_all(); self.status(f"↻ Refresh: {self.current_path}")
    def browse_dialog(self):
        d=filedialog.askdirectory(initialdir=str(self.current_path), title="Pilih Folder")
        if d: self.navigate_to(d)

    # ---------- Refresh ----------
    def _refresh_all(self):
        self.build_breadcrumb()
        self.load_folders()
        self.update_selection_label()

    def build_breadcrumb(self):
        for w in self.breadcrumb.winfo_children(): w.destroy()
        # pakai _unc_raw untuk server root agar \\it-4 tidak jadi \it-4
        cur_str = getattr(self, '_unc_raw', None) or str(self.current_path)
        # fallback: jika current_path single tapi path_var double, pakai path_var
        if cur_str.startswith("\\") and not cur_str.startswith("\\\\") and self.path_var.get().startswith("\\\\"):
            cur_str = self.path_var.get()
        is_unc = cur_str.startswith("\\\\")
        # untuk UNC, pecah manual karena Path.parts bug di beberapa Python
        if is_unc:
            # \\it-4\share\folder\sub -> ["\\it-4", "share", "folder", "sub"]
            clean = cur_str.rstrip("\\")
            # hapus \\ awal lalu split
            without = clean[2:]
            comps = without.split("\\")
            # rebuild incremental: \\it-4, \\it-4\share, \\it-4\share\folder...
            parts = []
            for i in range(len(comps)):
                parts.append("\\\\" + "\\".join(comps[:i+1]))
        else:
            parts = list(self.current_path.parts)
        # Home icon beda untuk jaringan
        icon_bc = "🌐" if is_unc else "📍"
        tk.Label(self.breadcrumb, text=icon_bc, bg=C["card"], font=("Segoe UI",9)).pack(side="left", padx=(0,4))

        # Jika path terlalu panjang (> 5 segmen), ringkas bagian tengah agar tidak overflow
        if len(parts) > 5:
            display_indices = [0, -4, len(parts)-3, len(parts)-2, len(parts)-1]
        else:
            display_indices = list(range(len(parts)))

        for pos, idx in enumerate(display_indices):
            if idx == -4:
                ellipsis_target = parts[len(parts)-4]
                b = tk.Button(self.breadcrumb, text="…", bg=C["card"], fg=C["text2"], font=("Segoe UI",8,"bold"),
                              relief="flat", bd=0, padx=7, pady=4, cursor="hand2", takefocus=0,
                              highlightbackground=C["border"], highlightthickness=1,
                              command=lambda _p=str(ellipsis_target): self.navigate_to(_p))
                b.pack(side="left", padx=1)
                tk.Label(self.breadcrumb, text="›", bg=C["card"], fg=C["text3"], font=("Segoe UI",9,"bold")).pack(side="left", padx=2)
                continue
            part = parts[idx]
            disp = part if not is_unc else part.split("\\")[-1] if "\\" in part else part
            if is_unc and idx == 0:
                disp = "\\\\" + disp
            is_last = idx == len(parts) - 1
            bg = C["accent_soft"] if is_last else C["card"]
            fg = C["accent_fg"] if is_last else C["text"]
            hl = C["accent"] if is_last else C["border"]
            p = parts[idx] if is_unc else str(Path(*parts[:idx+1]))
            b = tk.Button(self.breadcrumb, text=disp, bg=bg, fg=fg, font=("Segoe UI",8,"bold" if is_last else "normal"),
                          relief="flat", bd=0, padx=8, pady=4, cursor="hand2", takefocus=0,
                          highlightbackground=hl, highlightthickness=1,
                          command=lambda _p=str(p): self.navigate_to(_p))
            b.pack(side="left", padx=1)
            if pos < len(display_indices) - 1:
                tk.Label(self.breadcrumb, text="›", bg=C["card"], fg=C["text3"], font=("Segoe UI",9,"bold")).pack(side="left", padx=2)

    def _is_unc_server_root(self, p):
        s=str(p).rstrip("\\") if isinstance(p, (str, Path)) else str(p)
        # handle single slash bug: \it-4 -> treat as \\it-4
        if s.startswith("\\") and not s.startswith("\\\\"):
            s = "\\" + s
        if not s.startswith("\\\\"): return False
        rest=s[2:]
        return "\\" not in rest

    def _display_name(self, p):
        """Ambil nama display yang benar untuk UNC share (Path.name kosong untuk \\server\share)"""
        try:
            n = p.name
            if n:
                return n
        except: pass
        s = str(p).rstrip("\\/")
        # UNC: \\server\share\folder -> folder
        if s.startswith("\\\\"):
            rest = s[2:].replace("/", "\\")
            parts = [x for x in rest.split("\\") if x]
            return parts[-1] if parts else s
        # lokal
        return s.split("\\")[-1].split("/")[-1] if s else str(p)

    def _list_unc_shares(self, server_path):
        """List shares di \\server via 'net view' (karena iterdir tidak bisa untuk root)"""
        log(f"Mencoba net view {server_path} ...", "INFO")
        try:
            out = subprocess.check_output(f'net view "{server_path}"', shell=True, text=True, encoding='utf-8', errors='ignore', timeout=8)
            shares=[]
            seen=set()
            lines=out.splitlines()
            in_section=False
            for line in lines:
                if "----" in line:
                    in_section=True
                    continue
                if in_section:
                    if not line.strip() or "command completed" in line.lower():
                        break
                    parts=line.strip().split()
                    if parts:
                        name=parts[0]
                        if name and name not in seen and not name.startswith("-"):
                            seen.add(name)
                            # skip IPC$ dan hidden share berakhir $
                            # tapi tetap tampilkan jika user butuh
                            shares.append(Path(server_path.rstrip("\\/") + "\\" + name))
            if shares:
                log(f"net view {server_path} -> {len(shares)} shares: {shares}", "INFO")
                return shares
            else:
                log(f"net view {server_path} tidak ada share / kosong. Output: {out[:300]}", "WARN")
        except Exception as e:
            log(f"net view {server_path} failed: {e}\n{traceback.format_exc()}", "ERROR")
        return None

    def _format_item_meta(self, path_obj, dname, is_dir, st=None, is_unc=False):
        mt = "-"
        sz_s = ""
        if st is not None:
            try:
                mt = datetime.fromtimestamp(st.st_mtime).strftime("%d %b %Y %H:%M")
            except Exception:
                mt = "-"
            if not is_dir:
                try:
                    sz = st.st_size
                    if sz < 1024: sz_s = f"{sz} B"
                    elif sz < 1024*1024: sz_s = f"{sz/1024:.1f} KB"
                    else: sz_s = f"{sz/1024/1024:.1f} MB"
                except Exception:
                    sz_s = ""
        path_str = str(path_obj)
        if is_dir:
            has_code = False
            if not is_unc or (path_str.count("\\") > 3):
                try:
                    has_code = any(os.path.exists(os.path.join(path_str, x)) for x in _PROJECT_MARKERS)
                except Exception:
                    has_code = False
            typ = "📦 Project" if has_code else "📁 Folder"
        else:
            ext = path_obj.suffix.lower()
            icon = _ICON_MAP.get(ext, "📄")
            typ = f"{icon} {ext[1:].upper() if ext else 'File'}" + (f" • {sz_s}" if sz_s else "")
        return {
            "path": path_obj,
            "path_str": path_str,
            "name": dname,
            "name_lower": dname.lower(),
            "is_dir": is_dir,
            "typ": typ,
            "mt": mt,
        }

    def load_folders(self):
        self._load_seq += 1
        seq = self._load_seq
        target_path = self.current_path
        show_hidden = self.show_hidden
        cur_str = getattr(self, '_unc_raw', None) or str(target_path)
        if cur_str.startswith("\\") and not cur_str.startswith("\\\\") and self.path_var.get().startswith("\\\\"):
            cur_str = self.path_var.get()
        is_unc_root = self._is_unc_server_root(cur_str)
        is_unc = cur_str.startswith("\\\\")

        self.lbl_info.config(text=f"⏳ Memuat {cur_str}...")

        def _worker():
            items_meta = None
            last_err = None
            entries_raw = None  # list of (Path, dname, is_dir, stat_result)

            if is_unc_root:
                shares = self._list_unc_shares(cur_str)
                if shares is not None:
                    entries_raw = [(s, self._display_name(s), True, None) for s in shares]
                else:
                    last_err = OSError("[WinError 3] The system cannot find the path specified: '" + cur_str + "' (server root butuh net view)")

            if entries_raw is None:
                # 1. os.scandir paling cepat di Windows karena cache stat dari FindFirstFile
                try:
                    temp = []
                    with os.scandir(str(target_path)) as it:
                        for entry in it:
                            dname = entry.name
                            if not show_hidden and dname.startswith("."):
                                continue
                            try:
                                st = entry.stat(follow_symlinks=False)
                            except Exception:
                                st = None
                            if not show_hidden:
                                hidden = False
                                if st is not None and hasattr(st, "st_file_attributes"):
                                    hidden = bool(st.st_file_attributes & _FILE_ATTR_HIDDEN)
                                else:
                                    hidden = self.is_hidden(entry.path)
                                if hidden:
                                    continue
                            try:
                                is_dir = entry.is_dir(follow_symlinks=True)
                            except Exception:
                                is_dir = is_unc
                            temp.append((Path(entry.path), dname, is_dir, st))
                    entries_raw = temp
                except Exception as e:
                    last_err = e

            if entries_raw is None:
                # 2. Fallback iterdir / listdir untuk UNC atau kasus khusus
                for attempt in ("iterdir", "listdir"):
                    try:
                        if attempt == "iterdir":
                            paths = list(target_path.iterdir())
                        else:
                            paths = [Path(os.path.join(str(target_path), n)) for n in os.listdir(str(target_path))]
                        temp = []
                        for p in paths:
                            dname = self._display_name(p)
                            if not show_hidden and (dname.startswith(".") or self.is_hidden(p)):
                                continue
                            try:
                                st = p.stat()
                            except Exception:
                                st = None
                            try:
                                is_dir = p.is_dir()
                            except Exception:
                                is_dir = True
                            if str(p).startswith("\\\\") and p.name == "":
                                is_dir = True
                            temp.append((p, dname, is_dir, st))
                        entries_raw = temp
                        break
                    except Exception as e:
                        last_err = e
                        continue

            if entries_raw is not None:
                items_meta = [
                    self._format_item_meta(p, dname, is_dir, st, is_unc=is_unc)
                    for (p, dname, is_dir, st) in entries_raw
                ]
                items_meta.sort(key=lambda x: (0 if x["is_dir"] else 1, x["name_lower"]))

            self.after(0, lambda: self._on_folders_loaded(seq, target_path, items_meta, last_err))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_folders_loaded(self, seq, target_path, items_meta, last_err):
        if seq != self._load_seq:
            return
        if items_meta is None:
            self.all_items = []
            self.tree.delete(*self.tree.get_children())
            err_msg = str(last_err) if last_err else "Unknown"
            is_unc = str(target_path).startswith("\\\\")
            log(f"load_folders GAGAL: {target_path} | {err_msg}", "ERROR")
            if is_unc:
                is_root = self._is_unc_server_root(target_path)
                extra = ""
                if is_root:
                    extra = "\n\nKamu akses ROOT SERVER (\\\\it-4) - ini daftar SHARE, bukan folder.\nCoba klik salah satu share di bawah atau ketik lengkap:\n\\\\it-4\\NamaShare\n\nJika tetap gagal, jalankan di CMD:\nnet view \\\\it-4"
                if messagebox.askyesno("Sharing butuh akses",
                    f"Gagal membaca sharing:\n{target_path}\n\nError: {err_msg}{extra}\n\n"
                    f"Padahal Explorer bisa? Coba:\n"
                    f"• Klik YA untuk buka di Explorer dulu (agar koneksi cache)\n"
                    f"• Pastikan ketik lengkap: \\\\it-4\\ShareName (bukan cuma \\\\it-4)\n"
                    f"• Atau jalankan:  net use \\\\it-4  (di CMD)\n\n"
                    f"Buka di Explorer sekarang? (lihat log terminal untuk detail)"):
                    try:
                        log(f"Membuka di Explorer: {target_path}", "INFO")
                        subprocess.Popen(["explorer", str(target_path)])
                    except Exception as e:
                        log(f"Gagal buka Explorer: {e}", "ERROR")
                self.status(f"⚠️ UNC: {err_msg} (lihat terminal)")
            else:
                messagebox.showerror("Akses Ditolak", f"Tidak bisa membaca:\n{target_path}\n\n{err_msg}\n\nLihat log terminal untuk detail.")
            return
        self.all_items = items_meta
        self.apply_filter()

    def is_hidden(self, path):
        if _GetFileAttributesW is None:
            return False
        try:
            a = _GetFileAttributesW(str(path))
            return a != -1 and bool(a & 2)
        except Exception:
            return False

    def _recursive_search_meta(self, query, base_path, max_results=200, max_depth=4):
        """Cari rekursif di base_path untuk file/folder yang match query (berjalan di background thread)"""
        ignore_dirs = {".git", ".svn", "node_modules", "vendor", "__pycache__", ".vscode", ".idea", "storage", "bootstrap/cache"}
        results = []
        q = query.lower()
        base_str = str(base_path)
        is_unc = base_str.startswith("\\\\")
        try:
            for root, dirs, files in os.walk(base_str, topdown=True):
                rel = os.path.relpath(root, base_str)
                depth = 0 if rel == "." else rel.count(os.sep) + 1
                if depth > max_depth:
                    dirs[:] = []
                    continue
                dirs[:] = [d for d in dirs if d.lower() not in ignore_dirs and not d.startswith(".")]
                for d in dirs:
                    if q in d.lower():
                        if not self.show_hidden and d.startswith("."): continue
                        p = Path(root) / d
                        try: st = p.stat()
                        except Exception: st = None
                        results.append(self._format_item_meta(p, d, True, st, is_unc=is_unc))
                        if len(results) >= max_results: break
                if len(results) >= max_results: break
                for f in files:
                    if q in f.lower():
                        if not self.show_hidden and f.startswith("."): continue
                        p = Path(root) / f
                        try: st = p.stat()
                        except Exception: st = None
                        results.append(self._format_item_meta(p, f, False, st, is_unc=is_unc))
                        if len(results) >= max_results: break
                if len(results) >= max_results: break
        except Exception as e:
            log(f"recursive search error: {e}", "ERROR")
        results.sort(key=lambda x: (0 if x["is_dir"] else 1, x["name_lower"]))
        return results

    def _schedule_filter(self, *_):
        if self._filter_after_id is not None:
            try: self.after_cancel(self._filter_after_id)
            except Exception: pass
        self._filter_after_id = self.after(180, self.apply_filter)

    def apply_filter(self):
        self._filter_after_id = None
        q = self.search_var.get().lower().strip()
        is_recursive = bool(getattr(self, 'recursive_var', None) and self.recursive_var.get() and q and len(q) >= 2)
        if is_recursive:
            self._search_seq += 1
            seq = self._search_seq
            base_path = self.current_path
            log(f"recursive search: '{q}' di {base_path} depth=4", "INFO")
            self.lbl_info.config(text=f"🔍 Mencari '{q}' secara rekursif di {base_path}...")
            self.lbl_count.config(text="...")
            self.status(f"🔍 Mencari '{q}' secara rekursif...")

            def _search_worker():
                res = self._recursive_search_meta(q, base_path)
                self.after(0, lambda: self._render_recursive_results(seq, q, base_path, res))

            threading.Thread(target=_search_worker, daemon=True).start()
            return

        # Cancel any pending recursive search result
        self._search_seq += 1
        self.tree.delete(*self.tree.get_children())
        filt = [item for item in self.all_items if q in item["name_lower"]] if q else self.all_items
        folder_ct = sum(1 for item in filt if item["is_dir"])
        file_ct = len(filt) - folder_ct

        insert = self.tree.insert
        for idx, item in enumerate(filt):
            insert("", "end", values=(f"  {item['name']}", item["typ"], item["mt"]),
                   tags=(item["path_str"], "odd" if idx % 2 else "even"))

        self.lbl_info.config(text=f"Menampilkan {len(filt)} item ({folder_ct} folder, {file_ct} file) dari {len(self.all_items)}  •  {self.current_path}")
        self.lbl_count.config(text=f"{len(filt)} item")
        self.current_selection = self.current_path
        self.update_selection_label()

    def _render_recursive_results(self, seq, q, base_path, filt):
        if seq != self._search_seq:
            return
        self.tree.delete(*self.tree.get_children())
        if not filt:
            self.lbl_info.config(text=f"Tidak ada hasil untuk '{q}' di {base_path} (rekursif 4 level, coba perpendek kata kunci)")
            self.lbl_count.config(text="0 item")
            return

        base_str = str(base_path)
        insert = self.tree.insert
        for item in filt:
            dname = item["name"]
            typ = item["typ"]
            try:
                rel = os.path.relpath(item["path_str"], base_str)
                rel_dir = os.path.dirname(rel)
            except Exception:
                rel_dir = ""
            if rel_dir and rel_dir != ".":
                name_disp = f"  {dname}  →  {rel_dir}"
                typ_disp = f"{typ} {'•' if item['is_dir'] else '@'} {rel_dir}"
            else:
                name_disp = f"  {dname}"
                typ_disp = typ
            insert("", "end", values=(name_disp, typ_disp, item["mt"]),
                   tags=(item["path_str"], "odd" if len(self.tree.get_children()) % 2 else "even"))

        self.lbl_info.config(text=f"🔍 Rekursif '{q}' → {len(filt)} hasil di {base_path} (max 200, depth 4, skip node_modules/vendor/.git)")
        self.lbl_count.config(text=f"{len(filt)} item")
        self.current_selection = self.current_path
        self.update_selection_label()

    def on_tree_select(self, e):
        sel=self.tree.selection()
        if sel:
            # pakai full path dari tags, bukan reconstruct via name (agar UNC //it-4/share work)
            try:
                tags=self.tree.item(sel[0], "tags")
                if tags:
                    self.current_selection=Path(tags[0])
                else:
                    name=self.tree.item(sel[0], "values")[0].strip()
                    self.current_selection=self.current_path/name
            except:
                name=self.tree.item(sel[0], "values")[0].strip()
                self.current_selection=self.current_path/name
        else:
            self.current_selection=self.current_path
        self.update_selection_label()

    def on_tree_double(self, e):
        sel=self.tree.selection()
        if sel:
            # ambil full path dari tags
            tags=self.tree.item(sel[0], "tags")
            full = tags[0] if tags else None
            if full:
                target=Path(full)
                # file vs folder via is_dir, tapi untuk UNC pakai fallback
                try: isd=target.is_dir()
                except: isd=True
                if full.startswith("\\\\") and target.name=="":
                    isd=True
                if isd:
                    self.navigate_to(full)
                else:
                    # cek file
                    try: isf=target.is_file()
                    except: isf=False
                    if isf:
                        self._open_vscode(full, False)
                    else:
                        # jika stat gagal tapi path adalah file share, coba buka sebagai folder
                        self.navigate_to(full)
                return
            # fallback lama
            name=self.tree.item(sel[0], "values")[0].strip()
            target = self.current_path/name
            if target.is_dir():
                self.navigate_to(str(target))
            elif target.is_file():
                self._open_vscode(str(target), False)
            else:
                self.navigate_to(str(target))
        else:
            self.open_in_vscode()

    def open_selected(self):
        if self.current_selection and self.current_selection.exists() and self.current_selection.is_dir():
            self.navigate_to(str(self.current_selection))

    def update_selection_label(self):
        p=self.current_selection
        self.lbl_selected.config(text=str(p))
        is_cur = p==self.current_path
        self.lbl_selected_sub.config(text="📂 Folder saat ini — akan dibuka" if is_cur else f"📁 Subfolder dari {self.current_path.name}")

    def show_context(self, e):
        iid=self.tree.identify_row(e.y)
        if iid:
            self.tree.selection_set(iid); self.on_tree_select(None)
        self.menu.tk_popup(e.x_root, e.y_root)

    def toggle_hidden(self):
        self.show_hidden=self.hidden_var.get()
        self.cfg["show_hidden"]=self.show_hidden; save_config(self.cfg); self.load_folders()

    # ---------- Favorites Modern ----------
    def refresh_fav_list(self):
        self._last_sidebar_w = 0
        for w in self.fav_container.winfo_children(): w.destroy()
        favs=self.cfg.get("favorites", [])
        if not favs:
            self.lbl_no_fav = tk.Label(self.fav_container, text="Belum ada favorit.\nTambahkan folder yang sering dibuka.", bg=C["sidebar"], fg=C["text3"], font=("Segoe UI",7), justify="center")
            self.lbl_no_fav.pack(pady=10)
            return
        ide_short = self.active_ide["short"] if self.active_ide else "IDE"
        for path in favs:
            card=FavCard(self.fav_container, path,
                         on_vs=self.open_fav_vscode,
                         on_exp=self.open_fav_explorer,
                         on_both=self.open_fav_both,
                         on_del=self.remove_favorite_path,
                         on_nav=self.navigate_to,
                         drag_start=self.fav_drag_start,
                         drag_motion=self.fav_drag_motion,
                         drag_end=self.fav_drag_end,
                         ide_short=ide_short)
            card.pack(fill="x", pady=4)

    def refresh_recent_list(self):
        self._last_sidebar_w = 0
        for w in self.recent_frame.winfo_children(): w.destroy()
        rec=self.cfg.get("recent", [])[:8]
        if not rec:
            tk.Label(self.recent_frame, text="Belum ada history", bg=C["sidebar"], fg=C["text3"], font=("Segoe UI",7)).pack(anchor="w")
            return
        ide_short = self.active_ide["short"] if self.active_ide else "IDE"
        for path in rec:
            row=tk.Frame(self.recent_frame, bg=C["card"], highlightbackground=C["border"], highlightthickness=1)
            row.pack(fill="x", pady=2)
            p=Path(path)
            tk.Label(row, text="🕘", bg=C["card"], fg=C["text2"], font=("Segoe UI",7)).pack(side="left", padx=6)
            lbl=tk.Label(row, text=p.name or path, bg=C["card"], fg=C["text"], font=("Segoe UI",7,"bold"), anchor="w", cursor="hand2")
            lbl.pack(side="left", fill="x", expand=True)
            lbl.bind("<Button-1>", lambda e, pp=path: self.navigate_to(pp))
            # quick IDE button
            mk_btn(row, ide_short, C["accent_soft"], C["accent_fg"], C["accent_soft_hover"], lambda pp=path: self._open_vscode(pp, False), padx=6, pady=2, font=("Segoe UI",6,"bold")).pack(side="right", padx=2, pady=3)
            mk_btn(row, "📂", C["btn_sec"], C["text"], C["btn_sec_hover"], lambda pp=path: self._open_explorer(pp), padx=4, pady=2, font=("Segoe UI",7)).pack(side="right", padx=2, pady=3)

    def add_favorite(self):
        target=str(self.current_selection) if self.current_selection else str(self.current_path)
        favs=self.cfg.get("favorites", [])
        if target not in favs:
            favs.insert(0, target); self.cfg["favorites"]=favs; save_config(self.cfg)
            self.refresh_fav_list(); self.status(f"⭐ Ditambah ke favorit: {Path(target).name}")
        else: self.status("Sudah ada di favorit")

    def remove_favorite_path(self, path):
        favs=self.cfg.get("favorites", [])
        if path in favs:
            favs.remove(path); self.cfg["favorites"]=favs; save_config(self.cfg)
            self.refresh_fav_list(); self.status(f"🗑 Dihapus: {Path(path).name}")

    def open_fav_vscode(self, path): self._open_vscode(path, False)
    def open_fav_explorer(self, path): self._open_explorer(path)
    def open_fav_both(self, path): self._open_vscode(path, True)

    # ---------- Drag & Drop Favorit ----------
    def fav_drag_start(self, event, path, card):
        self._drag_path = path
        self._drag_card = card
        try:
            idx = self.cfg.get("favorites", []).index(path)
        except: idx = 0
        self._drag_start_idx = idx
        self._drag_current_idx = idx
        card.config(highlightbackground=C["accent2"], highlightthickness=2, bg=C["accent_soft"])
        # buat indikator drop line
        self._drop_indicator = tk.Frame(self.fav_container, bg=C["accent2"], height=3)
        self.status(f"⠿ Drag: {Path(path).name} — geser ke posisi baru lalu lepas")

    def fav_drag_motion(self, event):
        if not hasattr(self, "_drag_path") or not self._drag_path: return
        # posisi mouse relatif ke fav_container
        try:
            y_root = event.y_root
            cont_y = self.fav_container.winfo_rooty()
            y = y_root - cont_y
        except: return
        # cari index target berdasarkan posisi y
        children = [c for c in self.fav_container.winfo_children() if isinstance(c, FavCard)]
        if not children: return
        target_idx = len(children)  # default akhir
        for i, child in enumerate(children):
            cy = child.winfo_y()
            ch = child.winfo_height()
            mid = cy + ch//2
            if y < mid:
                target_idx = i
                break
        # koreksi jika drag card sendiri ikut dihitung
        if target_idx > self._drag_start_idx:
            # karena card masih di list, visual offset
            pass
        self._drag_current_idx = target_idx
        # highlight target
        for c in children:
            c.config(highlightbackground=C["border"], highlightthickness=1)
        if 0 <= target_idx < len(children):
            children[target_idx].config(highlightbackground=C["accent"], highlightthickness=2)
            # tampilkan indikator garis di atas target
            try:
                self._drop_indicator.place_forget()
                cx = children[target_idx].winfo_x()
                cy = children[target_idx].winfo_y()
                self._drop_indicator.place(x=cx, y=cy, width=children[target_idx].winfo_width(), height=3)
            except: pass
        else:
            # di akhir
            try:
                last = children[-1]
                self._drop_indicator.place(x=last.winfo_x(), y=last.winfo_y()+last.winfo_height()+2, width=last.winfo_width(), height=3)
            except: pass
        # visual feedback card yang didrag
        if hasattr(self, "_drag_card") and self._drag_card:
            self._drag_card.config(highlightbackground=C["accent2"], highlightthickness=2)

    def fav_drag_end(self, event):
        if not hasattr(self, "_drag_path") or not self._drag_path: return
        # hapus indikator
        try: self._drop_indicator.place_forget(); self._drop_indicator.destroy()
        except: pass
        try: del self._drop_indicator
        except: pass
        start = getattr(self, "_drag_start_idx", 0)
        target = getattr(self, "_drag_current_idx", start)
        path = self._drag_path
        # cleanup highlight
        for c in self.fav_container.winfo_children():
            if isinstance(c, FavCard):
                c.config(highlightbackground=C["border"], highlightthickness=1, bg=C["card"])

        favs = self.cfg.get("favorites", [])
        if path in favs:
            favs.remove(path)
            # clamp target
            target = max(0, min(target, len(favs)))
            # jika drag ke bawah, index perlu adjust karena remove sudah terjadi
            favs.insert(target, path)
            self.cfg["favorites"] = favs
            save_config(self.cfg)
            self.refresh_fav_list()
            if start != target:
                self.status(f"↕ Dipindah: {Path(path).name}  {start+1} → {target+1}")
            else:
                self.status(f"↔ Tetap: {Path(path).name} di posisi {target+1}")
        # reset
        self._drag_path = None
        self._drag_card = None
        self._drag_start_idx = None
        self._drag_current_idx = None

    def push_recent(self, path_str):
        rec=self.cfg.get("recent", [])
        if path_str in rec: rec.remove(path_str)
        rec.insert(0, path_str); self.cfg["recent"]=rec[:20]; save_config(self.cfg); self.refresh_recent_list()

    # ---------- Open actions ----------
    def get_target(self):
        sel=self.tree.selection()
        if sel:
            tags=self.tree.item(sel[0],"tags")
            if tags:
                p=Path(tags[0])
                if p.exists(): return p
            name=self.tree.item(sel[0],"values")[0].strip()
            p=self.current_path/name
            if p.exists(): return p
        if self.current_selection and self.current_selection.exists(): return self.current_selection
        return self.current_path

    def open_in_vscode(self): self._open_vscode(str(self.get_target()), False)
    def open_in_both(self): self._open_vscode(str(self.get_target()), True)
    def open_in_explorer_only(self): self._open_explorer(str(self.get_target()))
    def copy_path(self):
        t=self.get_target(); self.clipboard_clear(); self.clipboard_append(str(t)); self.status(f"📋 Disalin: {t}")

    def _open_vscode(self, target, explorer, ide=None):
        if not os.path.exists(target):
            messagebox.showerror("Error", f"Path tidak ada:\n{target}"); return
        chosen = ide or self.active_ide
        if not chosen:
            self.rescan_ides()
            chosen = self.active_ide
            if not chosen:
                messagebox.showerror(
                    "IDE tidak ditemukan",
                    "Tidak ada IDE yang terdeteksi di perangkat ini.\n\n"
                    "Pastikan IDE (VS Code, Cursor, Antigravity, Windsurf, JetBrains, dll.) sudah terinstall atau klik '🔄 Scan IDE'."
                )
                return
        exe_path = chosen["path"]
        ide_name = chosen["name"]
        # recent simpan parent folder jika file
        recent_path = target if Path(target).is_dir() else str(Path(target).parent)
        self.push_recent(recent_path)
        def run():
            try:
                no_win = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                if exe_path.lower().endswith((".cmd", ".bat")):
                    subprocess.Popen(f'"{exe_path}" "{target}"', shell=True, creationflags=no_win)
                else:
                    subprocess.Popen([exe_path, target])
                if explorer:
                    # jika file, select file di explorer; jika folder buka folder
                    if Path(target).is_file():
                        subprocess.Popen(["explorer", "/select,", target])
                    else:
                        subprocess.Popen(["explorer", target])
                self.after(0, lambda: self.status(f"🚀 Membuka di {ide_name}: {Path(target).name} {'+ Explorer' if explorer else ''}"))
            except Exception as e:
                self.after(0, lambda err=str(e): messagebox.showerror("Gagal", err))
        threading.Thread(target=run, daemon=True).start()

    def _open_explorer(self, target):
        try:
            if Path(target).is_file():
                subprocess.Popen(["explorer", "/select,", target])
            else:
                subprocess.Popen(["explorer", target])
            recent_path = target if Path(target).is_dir() else str(Path(target).parent)
            self.push_recent(recent_path)
            self.status(f"📂 Explorer: {Path(target).name}")
        except Exception as e: messagebox.showerror("Gagal", str(e))

    def open_with_default_app(self):
        target = self.get_target()
        try:
            os.startfile(str(target))
            self.status(f"▶️ Buka dengan app default: {Path(target).name}")
        except Exception as e: messagebox.showerror("Gagal", str(e))

    def _get_sash_pos(self):
        # kompatibel: tk.PanedWindow pakai sash_coord, ttk pakai sashpos
        try:
            if hasattr(self.paned, "sashpos"):
                v = self.paned.sashpos(0)
                return v[0] if isinstance(v, (tuple, list)) else v
        except: pass
        try:
            if hasattr(self.paned, "sash_coord"):
                x, y = self.paned.sash_coord(0)
                return x
        except: pass
        return self.sidebar_width

    def _set_sash_pos(self, pos):
        # kompatibel tk vs ttk
        try:
            if hasattr(self.paned, "sashpos"):
                self.paned.sashpos(0, pos)
                return
        except: pass
        try:
            if hasattr(self.paned, "sash_place"):
                self.paned.sash_place(0, pos, 0)
                return
        except: pass

    def _init_sash(self):
        try:
            w = self.winfo_width()
            if w > 600:
                target = int(w * 0.28)
                target = max(220, min(target, 380))
                self._set_sash_pos(target)
                self.sidebar_width = target
        except Exception as e:
            log(f"_init_sash error: {e}\n{traceback.format_exc()}", "ERROR")

    def log_error(self, ctx, err):
        msg = f"{ctx}: {err}\n{traceback.format_exc()}"
        log(msg, "ERROR")
        self.status(f"❌ {ctx}: {err}")

    def toggle_sidebar(self):
        """Toggle sidebar visible / hidden - responsive"""
        if self.sidebar_visible:
            try: self.sidebar_width = self._get_sash_pos()
            except: pass
            self.paned.forget(self.sidebar_wrap)
            self.sidebar_visible = False
            self.btn_toggle_sidebar.config(text="☰  Tampilkan Sidebar")
            self.status("◀ Sidebar disembunyikan — tekan F9 / Ctrl+B untuk tampilkan")
        else:
            try:
                try: self.paned.forget(self.right_frame)
                except: pass
                try: self.paned.forget(self.sidebar_wrap)
                except: pass
                self.paned.add(self.sidebar_wrap, minsize=220, width=self.sidebar_width, stretch="never")
                self.paned.add(self.right_frame, stretch="always", minsize=400)
                self.after(20, lambda: self._set_sash_pos(self.sidebar_width))
            except Exception as e:
                try: self.paned.add(self.sidebar_wrap, minsize=220, width=self.sidebar_width)
                except: pass
                print("toggle show error:", e)
            self.sidebar_visible = True
            self._auto_collapsed = False
            self.btn_toggle_sidebar.config(text="☰  Sembunyikan Sidebar")
            self.status("▶ Sidebar ditampilkan di kiri")

    def _schedule_sidebar_resize(self):
        if self._sidebar_resize_after is not None:
            try: self.after_cancel(self._sidebar_resize_after)
            except Exception: pass
        self._sidebar_resize_after = self.after(70, self.on_sidebar_resize)

    def on_sidebar_resize(self, event=None):
        """Isi sidebar ikut lebar sidebar saat drag sash / resize"""
        self._sidebar_resize_after = None
        try:
            sw = self.sidebar_wrap.winfo_width()
            if sw < 50:
                sw = self.sidebar_width
            if abs(sw - self._last_sidebar_w) < 4:
                return
            self._last_sidebar_w = sw
            usable = max(120, sw - 140)
            name_w = max(100, sw - 80)
            for card in self.fav_container.winfo_children():
                if hasattr(card, 'lbl_path'):
                    card.lbl_path.config(wraplength=usable)
                if hasattr(card, 'lbl_name'):
                    card.lbl_name.config(wraplength=name_w)
            for row in self.recent_frame.winfo_children():
                for child in row.winfo_children():
                    if isinstance(child, tk.Label) and child.cget("font") and "bold" in str(child.cget("font")):
                        child.config(wraplength=max(100, sw - 90))
            items = self.sidebar_canvas.find_all()
            if items:
                self.sidebar_canvas.itemconfig(items[0], width=sw-16)
        except Exception as e:
            log(f"on_sidebar_resize: {e}", "WARN")

    def on_window_resize(self, event):
        if event.widget != self: return
        w = event.width
        if abs(w - self._last_win_w) < 4:
            return
        self._last_win_w = w
        if w < 850 and self.sidebar_visible and not self._auto_collapsed:
            self._auto_collapsed = True
            self.toggle_sidebar()
            self.status("📱 Auto-hide sidebar (jendela < 850px) — tekan F9 untuk tampilkan")
        elif w >= 950 and not self.sidebar_visible and self._auto_collapsed:
            self.toggle_sidebar()
            self._auto_collapsed = False
        if self._win_resize_after is not None:
            try: self.after_cancel(self._win_resize_after)
            except Exception: pass
        self._win_resize_after = self.after(60, lambda: self._apply_window_resize(w))

    def _apply_window_resize(self, w):
        self._win_resize_after = None
        # 1. Treeview kolom responsif sesuai lebar area kanan
        try:
            right_w = max(320, self.right_frame.winfo_width() or (w - (self.sidebar_width if self.sidebar_visible else 0) - 40))
            type_w = 105 if w >= 800 else 90
            mod_w = 135 if w >= 820 else 105
            name_w = max(200, right_w - type_w - mod_w - 36)
            self.tree.column("name", width=name_w)
            self.tree.column("type", width=type_w)
            self.tree.column("modified", width=mod_w)
        except Exception:
            pass
        # 2. Sembunyikan hint sekunder saat jendela sempit agar bar tetap rapi
        try:
            if w < 980:
                self._search_hint_lbl.pack_forget()
                self._ctrl_hint_lbl.pack_forget()
            else:
                if not self._search_hint_lbl.winfo_ismapped():
                    self._search_hint_lbl.pack(side="left", padx=4, before=self.lbl_count)
                if not self._ctrl_hint_lbl.winfo_ismapped():
                    self._ctrl_hint_lbl.pack(side="left", padx=8, after=self.btn_toggle_sidebar)
        except Exception:
            pass
        # 3. Action bar otomatis bertumpuk (2 baris) saat jendela sempit (< 900px)
        try:
            should_stack = w < 900
            if should_stack != self._action_stacked:
                self._action_stacked = should_stack
                self._action_left.pack_forget()
                self._action_right.pack_forget()
                if should_stack:
                    self._action_left.pack(side="top", fill="x", padx=12, pady=(10,4))
                    self._action_right.pack(side="top", fill="x", padx=12, pady=(0,10))
                else:
                    self._action_left.pack(side="left", fill="x", expand=True, padx=12, pady=10)
                    self._action_right.pack(side="right", padx=12, pady=10)
        except Exception:
            pass
        try:
            self.lbl_selected.config(wraplength=max(260, int(w * (0.75 if self._action_stacked else 0.42))))
        except Exception:
            pass
        self._schedule_sidebar_resize()

    def prompt_network_path(self):
        # dialog input IP / server name untuk sharing
        import tkinter.simpledialog as sd
        val = sd.askstring("Buka Sharing Jaringan", "Masukkan path sharing:\n\nContoh:\n\\\\it-4\n\\\\it-4\\share\n\\\\192.168.1.10\\data\n\n(akan dibuka & bisa di-favoritkan)", initialvalue="\\\\it-4")
        if val:
            self.navigate_to(val.strip())

    def show_logs(self):
        log_path = Path(__file__).parent / "app.log"
        win = tk.Toplevel(self)
        win.title("📋 Application Logs")
        win.geometry("900x600")
        win.transient(self)
        try: win.iconbitmap(str(Path(__file__).parent / "logo.ico"))
        except: pass
        win.configure(bg=C["bg"])

        # header
        hdr = tk.Frame(win, bg=C["card"], highlightbackground=C["border"], highlightthickness=1)
        hdr.pack(fill="x", padx=10, pady=10)
        tk.Label(hdr, text="📋  Application Logs", bg=C["card"], fg=C["text"], font=("Segoe UI",11,"bold")).pack(side="left", padx=10, pady=10)
        tk.Label(hdr, text=str(log_path), bg=C["card"], fg=C["text2"], font=("Consolas",7)).pack(side="left", padx=10)
        # file info
        try:
            sz = log_path.stat().st_size if log_path.exists() else 0
            cnt = len(log_path.read_text(encoding="utf-8", errors="ignore").splitlines()) if log_path.exists() else 0
            info = f"{cnt} baris • {sz/1024:.1f} KB"
        except: info = "-"
        tk.Label(hdr, text=info, bg=C["card"], fg=C["text3"], font=("Segoe UI",7)).pack(side="right", padx=10)

        # text area
        txt_frame = tk.Frame(win, bg=C["card"], highlightbackground=C["border"], highlightthickness=1)
        txt_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))
        txt = tk.Text(txt_frame, wrap="none", font=("Consolas",8), bg=C["input_bg"], fg=C["text"], insertbackground=C["text"], bd=0, padx=8, pady=8, undo=False)
        vsb = ttk.Scrollbar(txt_frame, orient="vertical", command=txt.yview)
        hsb = ttk.Scrollbar(txt_frame, orient="horizontal", command=txt.xview)
        txt.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        txt.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        txt_frame.grid_rowconfigure(0, weight=1)
        txt_frame.grid_columnconfigure(0, weight=1)

        def load():
            txt.config(state="normal")
            txt.delete("1.0", "end")
            if log_path.exists():
                try:
                    content = log_path.read_text(encoding="utf-8", errors="ignore")
                    txt.insert("1.0", content)
                    # color by level
                    for i, line in enumerate(content.splitlines(), 1):
                        if "[ERROR]" in line:
                            txt.tag_add("err", f"{i}.0", f"{i}.end")
                        elif "[WARN]" in line:
                            txt.tag_add("warn", f"{i}.0", f"{i}.end")
                    txt.tag_config("err", foreground=C["danger"], font=("Consolas",8,"bold"))
                    txt.tag_config("warn", foreground=C["warning"])
                    txt.see("end")
                    log(f"Buka logs: {cnt} baris", "INFO")
                except Exception as e:
                    txt.insert("1.0", f"Gagal baca log: {e}")
            else:
                txt.insert("1.0", "Belum ada log.\nLog akan muncul setelah aktivitas (navigasi, error, dsb).")
            txt.config(state="disabled")
        load()

        # buttons
        btns = tk.Frame(win, bg=C["bg"])
        btns.pack(fill="x", padx=10, pady=(0,10))
        def refresh():
            load()
            self.status("📋 Logs di-refresh")
        def clear():
            if messagebox.askyesno("Hapus Logs", "Yakin hapus semua logs?\n\nFile: app.log akan dikosongkan.", parent=win):
                try:
                    log_path.write_text("", encoding="utf-8")
                    load()
                    log("Logs dihapus user", "INFO")
                    self.status("🗑 Logs dihapus")
                except Exception as e:
                    messagebox.showerror("Gagal", str(e), parent=win)
                    log(f"Gagal hapus log: {e}", "ERROR")
        def open_folder():
            try: subprocess.Popen(["explorer", str(log_path.parent)])
            except: webbrowser.open(str(log_path.parent))
        def copy_all():
            txt.config(state="normal")
            content = txt.get("1.0", "end")
            win.clipboard_clear(); win.clipboard_append(content)
            txt.config(state="disabled")
            self.status("📋 Logs disalin ke clipboard")

        mk_btn(btns, "🔄 Refresh", C["accent2"], "white", C["accent_hover"], refresh, padx=12, pady=6).pack(side="left", padx=4)
        mk_btn(btns, "🗑  Hapus Logs", "#FEE2E2", C["danger"], "#FECACA", clear, padx=12, pady=6, font=("Segoe UI",8,"bold")).pack(side="left", padx=4)
        mk_btn(btns, "📋 Copy", "#F1F5F9", C["text"], "#E2E8F0", copy_all, padx=10, pady=6).pack(side="left", padx=4)
        mk_btn(btns, "📂 Buka Folder", "#F1F5F9", C["text"], "#E2E8F0", open_folder, padx=10, pady=6).pack(side="left", padx=4)
        mk_btn(btns, "✕ Tutup", "#FFFFFF", C["text"], "#F1F5F9", win.destroy, padx=12, pady=6).pack(side="right", padx=4)
        # shortcut
        win.bind("<Escape>", lambda e: win.destroy())
        win.bind("<F5>", lambda e: refresh())

    def show_settings(self):
        messagebox.showinfo("Settings", f"Config: {CONFIG_FILE}\nLog: {Path(__file__).parent / 'app.log'}\n\nEdit manual jika perlu.\nHapus file untuk reset.\n\nShortcut:\nF9 / Ctrl+B = Toggle Sidebar\nDrag garis tengah = Atur lebar sidebar\n\nJaringan:\n• Ketik \\\\it-4 atau \\\\IP di Lokasi lalu Enter\n• Tombol 🌐 di atas untuk shortcut")

    def status(self, msg):
        self.status_var.set(f"{datetime.now().strftime('%H:%M:%S')}  •  {msg}")
        # juga log ke terminal (INFO level)
        log(msg, "INFO")

if __name__=="__main__":
    App().mainloop()
