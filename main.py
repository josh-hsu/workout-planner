#!/usr/bin/env python3
"""
Workout Planner - 健身影片片段編排應用程式
主程式進入點
"""

import tkinter as tk
from gui.main_window import MainWindow


def main():
    """主程式進入點"""
    root = tk.Tk()
    root.title("Workout Planner")
    root.geometry("600x400")

    # 建立主視窗
    app = MainWindow(root)

    # 啟動事件循環
    root.mainloop()


if __name__ == "__main__":
    main()
