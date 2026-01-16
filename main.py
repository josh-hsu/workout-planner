#!/usr/bin/env python3
"""
Workout Planner - 健身影片片段編排應用程式
主程式進入點
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from gui.main_window import MainWindow

# 儲存上次工作目錄的檔案路徑
LAST_WORKDIR_FILE = Path(__file__).parent / ".last_workdir"


def load_last_workdir() -> Path | None:
    """
    載入上次使用的工作目錄

    Returns:
        Path: 上次使用的工作目錄，如果不存在或無效則返回 None
    """
    if not LAST_WORKDIR_FILE.exists():
        return None

    try:
        workdir = Path(LAST_WORKDIR_FILE.read_text().strip())
        if workdir.exists() and workdir.is_dir():
            return workdir
    except Exception:
        pass

    return None


def save_last_workdir(workdir: Path):
    """
    儲存工作目錄到檔案

    Args:
        workdir: 要儲存的工作目錄路徑
    """
    try:
        LAST_WORKDIR_FILE.write_text(str(workdir))
    except Exception:
        pass


def select_workspace(initial_dir: Path = None) -> Path | None:
    """
    提示使用者選擇工作目錄

    Args:
        initial_dir: 初始目錄，如果為 None 則使用 home 目錄

    Returns:
        Path: 使用者選擇的工作目錄，如果取消則返回 None
    """
    # 建立一個隱藏的根視窗用於顯示對話框
    temp_root = tk.Tk()
    temp_root.withdraw()

    # 顯示資訊對話框
    messagebox.showinfo(
        "選擇工作目錄",
        "請選擇一個資料夾作為 Workout Planner 的工作目錄。\n\n"
        "所有的設定檔和資料將會儲存在此目錄中。"
    )

    # 開啟資料夾選擇對話框
    workspace_path = filedialog.askdirectory(
        title="選擇工作目錄",
        initialdir=initial_dir or Path.home()
    )

    temp_root.destroy()

    if workspace_path:
        return Path(workspace_path)
    return None


def main():
    """主程式進入點"""
    # 嘗試載入上次的工作目錄
    workspace = load_last_workdir()

    # 如果沒有上次的工作目錄，提示選擇
    if workspace is None:
        workspace = select_workspace()

    if workspace is None:
        # 使用者取消選擇，結束程式
        return

    # 儲存工作目錄
    save_last_workdir(workspace)

    # 建立主視窗
    root = tk.Tk()
    root.title("Workout Planner")
    root.geometry("600x450")

    # 傳入選擇的工作目錄和儲存回呼函式
    app = MainWindow(root, workspace, on_workdir_change=save_last_workdir)

    # 啟動事件循環
    root.mainloop()


if __name__ == "__main__":
    main()
