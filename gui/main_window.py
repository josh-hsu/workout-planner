"""
主視窗模組
顯示功能選擇介面
"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path


class MainWindow:
    """主視窗類別"""

    def __init__(self, root, workspace_dir, on_workdir_change=None):
        """
        初始化主視窗

        Args:
            root: Tkinter 根視窗
            workspace_dir: 工作目錄路徑 (Path 物件)
            on_workdir_change: 工作目錄變更時的回呼函式
        """
        self.root = root
        self.work_dir = workspace_dir
        self._on_workdir_change = on_workdir_change

        # 設定視窗
        self._setup_ui()

    def _setup_ui(self):
        """設定使用者介面"""
        # 設定按鈕樣式
        style = ttk.Style()
        style.configure('Large.TButton', font=('Arial', 20))

        # 標題
        title_label = ttk.Label(
            self.root,
            text="Workout Planner",
            font=('Arial', 48, 'bold')
        )
        title_label.pack(pady=20)

        # 副標題
        subtitle_label = ttk.Label(
            self.root,
            text="健身影片片段編排應用程式",
            font=('Arial', 24)
        )
        subtitle_label.pack(pady=10)

        # 按鈕框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=40)

        # 建立分段描述檔按鈕
        create_track_btn = ttk.Button(
            button_frame,
            text="建立分段描述檔",
            command=self._open_track_editor,
            width=25,
            style='Large.TButton'
        )
        create_track_btn.pack(pady=10)

        # 建立課程播放清單按鈕
        create_playlist_btn = ttk.Button(
            button_frame,
            text="建立課程播放清單",
            command=self._open_playlist_builder,
            width=25,
            style='Large.TButton'
        )
        create_playlist_btn.pack(pady=10)

        # 變更工作目錄按鈕
        change_workdir_btn = ttk.Button(
            button_frame,
            text="變更工作目錄",
            command=self._change_workdir,
            width=25,
            style='Large.TButton'
        )
        change_workdir_btn.pack(pady=10)

        # 底部資訊
        self.info_label = ttk.Label(
            self.root,
            text=f"工作目錄: {self.work_dir}",
            font=('Arial', 18),
            foreground='gray'
        )
        self.info_label.pack(side=tk.BOTTOM, pady=10)

    def _open_track_editor(self):
        """開啟時間戳編輯器視窗"""
        from .track_editor import TrackEditorWindow

        # 建立新視窗
        editor_window = tk.Toplevel(self.root)
        TrackEditorWindow(editor_window, self.work_dir)

    def _open_playlist_builder(self):
        """開啟播放清單建立器視窗"""
        from .playlist_builder import PlaylistBuilderWindow

        # 建立新視窗
        builder_window = tk.Toplevel(self.root)
        PlaylistBuilderWindow(builder_window, self.work_dir)

    def _change_workdir(self):
        """變更工作目錄"""
        new_workdir = filedialog.askdirectory(
            title="選擇新的工作目錄",
            initialdir=self.work_dir
        )

        if new_workdir:
            self.work_dir = Path(new_workdir)
            self.info_label.config(text=f"工作目錄: {self.work_dir}")

            # 呼叫回呼函式儲存新的工作目錄
            if self._on_workdir_change:
                self._on_workdir_change(self.work_dir)
