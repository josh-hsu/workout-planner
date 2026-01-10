#!/usr/bin/env python3
"""
Workout Planner - 健身影片片段編排應用程式
主程式進入點
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from gui.main_window import MainWindow


def select_workspace():
    """
    提示使用者選擇工作目錄

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
        initialdir=Path.home()
    )

    temp_root.destroy()

    if workspace_path:
        return Path(workspace_path)
    return None


def main():
    """主程式進入點"""
    # 先選擇工作目錄
    workspace = select_workspace()

    if workspace is None:
        # 使用者取消選擇，結束程式
        return

    # 建立主視窗
    root = tk.Tk()
    root.title("Workout Planner")
    root.geometry("600x400")

    # 傳入選擇的工作目錄
    app = MainWindow(root, workspace)

    # 啟動事件循環
    root.mainloop()


if __name__ == "__main__":
    main()
