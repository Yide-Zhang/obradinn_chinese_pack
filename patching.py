import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.style import Style
from pathlib import Path

# ===== 从 main.py 引入函数（它们已支持传入自定义路径 custom_path） =====
from main import (
    get_steam_game_data_path,
    check_obra_dinn_files,
    backup_obra_dinn_files,
    patch_obra_dinn_files,
)

# ===== Overlay Entry：提示文字不占位 =====
class OverlayEntry(ttk.Frame):
    def __init__(self, master=None, placeholder="选择路径", width=40, *args, **kwargs):
        super().__init__(master)
        self.var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.var, width=width, *args, **kwargs)
        self.entry.pack(fill="x")
        self.placeholder = ttk.Label(self, text=placeholder, foreground="grey", anchor="w")
        self.placeholder.place(x=8, y=2)
        self.var.trace_add("write", self._toggle_placeholder)
        self.entry.bind("<FocusIn>", lambda e: self._toggle_placeholder())
        self.entry.bind("<FocusOut>", lambda e: self._toggle_placeholder())
        self._toggle_placeholder()

    def _toggle_placeholder(self, *args):
        if self.var.get().strip():
            self.placeholder.place_forget()
        else:
            self.placeholder.place(x=8, y=2)

    def get(self):
        return self.var.get().strip()

    def set(self, value):
        self.var.set(value)


# ===== 页面基类 =====
class Page(ttk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.option_add("*Font", ("Microsoft YaHei UI", 10))

    def show(self):
        self.lift()


# ===== 第1步：选择游戏目录 =====
class PageSelectDir(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        ttk.Label(self, text="游戏目录选择", font=("Microsoft YaHei UI", 14, "bold")).pack(pady=10)

        row = ttk.Frame(self)
        row.pack(pady=10, anchor="center")

        self.path_entry = OverlayEntry(row, placeholder="选择路径", width=40)
        self.path_entry.pack(side="left", padx=5)

        ttk.Button(
            row, text="浏览...", style="Win11.TButton", width=8, command=self.manual_select
        ).pack(side="left", padx=5)

        ttk.Button(
            self, text="自动获取", style="Win11.TButton", width=8, command=self.auto_get
        ).pack(pady=5)

        ttk.Button(
            self, text="下一步", style="Win11.TButton", width=8, command=self.next_page
        ).pack(pady=20)

    def auto_get(self):
        ok, path = get_steam_game_data_path()
        if ok and path:
            self.path_entry.set(path)
            # 立即同步 app 路径（可选）
            self.app.game_path = Path(path)
        else:
            messagebox.showerror("错误", "自动获取失败，请手动选择目录。")

    def manual_select(self):
        path = filedialog.askdirectory(title="选择游戏数据目录")
        if path:
            self.path_entry.set(path)

    def next_page(self):
        path = self.path_entry.get()
        if not path:
            messagebox.showerror("错误", "必须选择有效的目录！")
            return

        # 记录用户自定义路径（核心）
        self.app.game_path = Path(path)

        # 用用户路径进行原文件检测（核心）
        if not check_obra_dinn_files(str(self.app.game_path)):
            messagebox.showerror("错误", "缺少原文件，请在 Steam 中验证游戏完整性。")
            return

        self.app.page_backup.show()


# ===== 第2步：备份选择 =====
class PageBackup(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        ttk.Label(self, text="是否备份原始文件？", font=("Microsoft YaHei UI", 14, "bold")).pack(pady=10)

        row = ttk.Frame(self)
        row.pack(pady=10, anchor="center")

        self.backup_entry = OverlayEntry(row, placeholder="选择路径", width=40)
        self.backup_entry.pack(side="left", padx=5)

        ttk.Button(
            row, text="浏览...", style="Win11.TButton", width=8, command=self.select_dir
        ).pack(side="left", padx=5)

        ttk.Button(
            self, text="执行备份", style="Win11.TButton", width=8, command=self.do_backup
        ).pack(pady=5)

        ttk.Button(
            self, text="跳过备份", style="Win11.TButton", width=8, command=self.skip_backup
        ).pack(pady=5)

        ttk.Button(
            self, text="上一步", style="Win11.TButton", width=8,
            command=lambda: self.app.page_select.show()
        ).pack(pady=5)

    def select_dir(self):
        path = filedialog.askdirectory(title="选择备份目录")
        if path:
            self.backup_entry.set(path)

    def do_backup(self):
        backup_dir = self.backup_entry.get()
        if not backup_dir:
            messagebox.showerror("错误", "请先输入或选择备份目录")
            return
        # 使用用户目录（核心）
        success = backup_obra_dinn_files(backup_dir, str(self.app.game_path) if self.app.game_path else None)
        if success:
            messagebox.showinfo("提示", "备份完成")
            self.app.page_patch.show()
        else:
            messagebox.showerror("错误", "部分文件备份失败")

    def skip_backup(self):
        self.app.page_patch.show()


# ===== 第3步：选择补丁 =====
class PagePatch(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        ttk.Label(self, text="安装补丁", font=("Microsoft YaHei UI", 14, "bold")).pack(pady=20)

        self.var_text = tk.BooleanVar()
        self.var_font = tk.BooleanVar()

        center_frame = ttk.Frame(self)
        center_frame.pack(expand=True)

        ttk.Checkbutton(
            center_frame, text="文本补丁", variable=self.var_text,
            style="Win11.TCheckbutton", bootstyle="round-toggle"
        ).pack(pady=10)

        ttk.Checkbutton(
            center_frame, text="字体补丁", variable=self.var_font,
            style="Win11.TCheckbutton", bootstyle="round-toggle"
        ).pack(pady=10)

        btn_row = ttk.Frame(self)
        btn_row.pack(pady=20)

        ttk.Button(
            btn_row, text="上一步", style="Win11.TButton", width=8,
            command=lambda: self.app.page_backup.show()
        ).pack(side="left", padx=10)

        ttk.Button(
            btn_row, text="执行安装", style="Win11.TButton", width=8,
            command=self.do_patch
        ).pack(side="left", padx=10)

    def do_patch(self):
        text = self.var_text.get()
        font = self.var_font.get()
        if not text and not font:
            messagebox.showerror("错误", "请选择至少一个补丁！")
            return
        # 使用用户目录（核心）
        success = patch_obra_dinn_files(text, font, str(self.app.game_path) if self.app.game_path else None)
        if success:
            self.app.page_done.show()
        else:
            messagebox.showerror("错误", "补丁安装失败，请检查补丁文件是否存在。")


# ===== 第4步：完成 =====
class PageDone(Page):
    def __init__(self, master, app):
        super().__init__(master, app)
        ttk.Label(self, text="安装完成！", font=("Microsoft YaHei UI", 14, "bold")).pack(pady=20)
        ttk.Button(self, text="退出", style="Win11.TButton", width=8, command=app.quit).pack(pady=20)


# ===== 主应用 =====
class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("Return of the Obra Dinn 补丁安装器")
        self.geometry("800x300")

        self.option_add("*Font", ("Microsoft YaHei UI", 10))

        style = Style()
        style.configure(
            "Win11.TButton",
            font=("Microsoft YaHei UI", 10),
            padding=4,
            relief="flat",
            borderwidth=1,
            focusthickness=2,
            focuscolor="blue",
            background="#f2f2f2",
            foreground="black",
        )
        style.map(
            "Win11.TButton",
            background=[("active", "#e6f0fa"), ("pressed", "#d0e7ff")],
        )
        style.configure("Win11.TCheckbutton", font=("Microsoft YaHei UI", 12))

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.game_path: Path | None = None  # 保存用户选择的路径

        self.page_select = PageSelectDir(container, self)
        self.page_backup = PageBackup(container, self)
        self.page_patch = PagePatch(container, self)
        self.page_done = PageDone(container, self)

        for page in (self.page_select, self.page_backup, self.page_patch, self.page_done):
            page.place(relwidth=1, relheight=1)

        self.page_select.show()


if __name__ == "__main__":
    app = App()
    app.mainloop()
