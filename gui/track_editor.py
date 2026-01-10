"""
時間戳編輯器模組
建立影片分段描述檔功能
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from video_player import VideoPlayer
from track_manager import Track, TrackManager
from utils import seconds_to_time_str, validate_video_file


class TrackEditorWindow:
    """時間戳編輯器視窗"""

    def __init__(self, window, work_dir: Path):
        """
        初始化時間戳編輯器視窗

        Args:
            window: Tkinter 視窗
            work_dir: 工作目錄路徑
        """
        self.window = window
        self.work_dir = work_dir
        self.video_path: Path = None
        self.track_manager: TrackManager = None
        self.tracks = []  # Track 物件列表
        self.mark_start_time = None  # 標記的開始時間

        # 設定視窗
        self.window.title("建立分段描述檔")
        self.window.geometry("900x800")

        self._setup_ui()
        self._prompt_select_video()

    def _setup_ui(self):
        """設定使用者介面"""
        # 主容器
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 影片資訊標籤
        self.video_info_label = ttk.Label(
            main_container,
            text="未載入影片",
            font=('Arial', 10)
        )
        self.video_info_label.pack(pady=5)

        # 影片播放器
        self.video_player = VideoPlayer(main_container, width=640, height=360)
        self.video_player.pack(pady=10)

        # 時間戳標記區域
        mark_frame = ttk.LabelFrame(main_container, text="時間戳標記", padding=10)
        mark_frame.pack(fill=tk.X, pady=10)

        # 標記按鈕列
        button_row = ttk.Frame(mark_frame)
        button_row.pack(fill=tk.X, pady=5)

        self.mark_start_btn = ttk.Button(
            button_row,
            text="標記開始",
            command=self._mark_start,
            state=tk.DISABLED
        )
        self.mark_start_btn.pack(side=tk.LEFT, padx=5)

        self.mark_end_btn = ttk.Button(
            button_row,
            text="標記結束",
            command=self._mark_end,
            state=tk.DISABLED
        )
        self.mark_end_btn.pack(side=tk.LEFT, padx=5)

        self.mark_info_label = ttk.Label(
            button_row,
            text="請先標記開始時間",
            foreground='gray'
        )
        self.mark_info_label.pack(side=tk.LEFT, padx=20)

        # 匯出按鈕（先 pack，固定在底部）
        export_frame = ttk.Frame(main_container)
        export_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        ttk.Button(
            export_frame,
            text="匯出描述檔",
            command=self._export_tracks
        ).pack(side=tk.RIGHT, padx=5)

        # 分段列表區域（後 pack，填充剩餘空間）
        list_frame = ttk.LabelFrame(main_container, text="分段列表", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 建立 Treeview 表格
        columns = ('serial', 'start', 'end', 'duration', 'name', 'training')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        # 定義欄位
        self.tree.heading('serial', text='序號')
        self.tree.heading('start', text='開始時間')
        self.tree.heading('end', text='結束時間')
        self.tree.heading('duration', text='時長')
        self.tree.heading('name', text='歌名')
        self.tree.heading('training', text='訓練名稱')

        # 設定欄位寬度
        self.tree.column('serial', width=50, anchor=tk.CENTER)
        self.tree.column('start', width=100, anchor=tk.CENTER)
        self.tree.column('end', width=100, anchor=tk.CENTER)
        self.tree.column('duration', width=80, anchor=tk.CENTER)
        self.tree.column('name', width=150)
        self.tree.column('training', width=150)

        # 滾動條
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 編輯按鈕列
        edit_button_row = ttk.Frame(list_frame)
        edit_button_row.pack(fill=tk.X, pady=5)

        ttk.Button(
            edit_button_row,
            text="編輯選中項",
            command=self._edit_selected_track
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            edit_button_row,
            text="刪除選中項",
            command=self._delete_selected_track
        ).pack(side=tk.LEFT, padx=5)

    def _prompt_select_video(self):
        """提示選擇影片檔案"""
        file_path = filedialog.askopenfilename(
            title="選擇影片檔案",
            initialdir=self.work_dir,
            filetypes=[("影片檔案", "*.mp4 *.m4v"), ("所有檔案", "*.*")]
        )

        if not file_path:
            self.window.destroy()
            return

        self._load_video(Path(file_path))

    def _load_video(self, video_path: Path):
        """載入影片"""
        # 驗證影片檔案
        is_valid, error_msg = validate_video_file(video_path)
        if not is_valid:
            messagebox.showerror("錯誤", f"無法載入影片: {error_msg}")
            self.window.destroy()
            return

        # 載入影片
        if not self.video_player.load_video(video_path):
            messagebox.showerror("錯誤", "無法載入影片檔案")
            self.window.destroy()
            return

        self.video_path = video_path
        self.video_info_label.config(
            text=f"影片: {video_path.name} | 時長: {seconds_to_time_str(self.video_player.get_duration())}"
        )

        # 載入現有的分段描述檔（如果存在）
        self.track_manager = TrackManager(str(video_path))
        if self.track_manager.has_description_file():
            self.tracks = self.track_manager.get_all_tracks()
            self._refresh_track_list()
            messagebox.showinfo("提示", "已載入現有的分段描述檔")

        # 啟用標記按鈕
        self.mark_start_btn.config(state=tk.NORMAL)

    def _mark_start(self):
        """標記開始時間"""
        self.mark_start_time = self.video_player.get_current_time()
        self.mark_info_label.config(
            text=f"開始時間: {seconds_to_time_str(self.mark_start_time)} | 請標記結束時間",
            foreground='blue'
        )
        self.mark_end_btn.config(state=tk.NORMAL)

    def _mark_end(self):
        """標記結束時間並新增分段"""
        if self.mark_start_time is None:
            return

        mark_end_time = self.video_player.get_current_time()

        # 驗證時間
        if mark_end_time <= self.mark_start_time:
            messagebox.showerror("錯誤", "結束時間必須大於開始時間")
            return

        # 開啟編輯對話框
        self._show_track_edit_dialog(self.mark_start_time, mark_end_time)

        # 重置標記
        self.mark_start_time = None
        self.mark_info_label.config(
            text="請先標記開始時間",
            foreground='gray'
        )
        self.mark_end_btn.config(state=tk.DISABLED)

    def _show_track_edit_dialog(self, start_time: float, end_time: float, track: Track = None):
        """
        顯示分段編輯對話框

        Args:
            start_time: 開始時間
            end_time: 結束時間
            track: 要編輯的 Track（None 表示新增）
        """
        dialog = tk.Toplevel(self.window)
        dialog.title("編輯分段資訊")
        dialog.transient(self.window)
        dialog.grab_set()

        # 設置對話框大小
        dialog_width = 400
        dialog_height = 300

        # 更新視窗以獲取正確的尺寸
        dialog.update_idletasks()

        # 計算母視窗的中心位置
        parent_x = self.window.winfo_x()
        parent_y = self.window.winfo_y()
        parent_width = self.window.winfo_width()
        parent_height = self.window.winfo_height()

        # 計算對話框應該放置的位置（置中）
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        # 設置對話框位置和大小
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

        # 序號
        ttk.Label(dialog, text="序號:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        serial_var = tk.IntVar(value=track.serial if track else len(self.tracks) + 1)
        serial_entry = ttk.Entry(dialog, textvariable=serial_var, width=10)
        serial_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # 開始時間
        ttk.Label(dialog, text="開始時間:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        start_label = ttk.Label(dialog, text=seconds_to_time_str(start_time))
        start_label.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # 結束時間
        ttk.Label(dialog, text="結束時間:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        end_label = ttk.Label(dialog, text=seconds_to_time_str(end_time))
        end_label.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)

        # 時長
        duration = end_time - start_time
        ttk.Label(dialog, text="時長:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        duration_label = ttk.Label(dialog, text=seconds_to_time_str(duration))
        duration_label.grid(row=3, column=1, padx=10, pady=10, sticky=tk.W)

        # 歌名
        ttk.Label(dialog, text="歌名:").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        name_var = tk.StringVar(value=track.name if track else "")
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)

        # 訓練名稱
        ttk.Label(dialog, text="訓練名稱:").grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        training_var = tk.StringVar(value=track.training if track else "")
        training_entry = ttk.Entry(dialog, textvariable=training_var, width=30)
        training_entry.grid(row=5, column=1, padx=10, pady=10, sticky=tk.W)

        # 按鈕
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)

        def save_track():
            new_track = Track(
                serial=serial_var.get(),
                start=start_time,
                end=end_time,
                name=name_var.get(),
                training=training_var.get()
            )

            # 驗證
            is_valid, error_msg = self.track_manager.validate_track(
                new_track,
                self.video_player.get_duration()
            )

            if not is_valid:
                messagebox.showerror("錯誤", error_msg)
                return

            # 新增或更新
            if track:
                # 更新現有分段
                for i, t in enumerate(self.tracks):
                    if t.serial == track.serial:
                        self.tracks[i] = new_track
                        break
            else:
                # 新增分段
                self.tracks.append(new_track)

            # 按序號排序
            self.tracks.sort(key=lambda t: t.serial)

            self._refresh_track_list()
            dialog.destroy()

        ttk.Button(button_frame, text="儲存", command=save_track).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        # 綁定 Enter 鍵到儲存功能（主鍵盤和數字鍵盤）
        dialog.bind('<Return>', lambda event: save_track())
        dialog.bind('<KP_Enter>', lambda event: save_track())

    def _refresh_track_list(self):
        """刷新分段列表"""
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 重新填入
        for track in self.tracks:
            self.tree.insert('', tk.END, values=(
                track.serial,
                seconds_to_time_str(track.start),
                seconds_to_time_str(track.end),
                seconds_to_time_str(track.duration),
                track.name,
                track.training
            ))

    def _edit_selected_track(self):
        """編輯選中的分段"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "請先選擇要編輯的分段")
            return

        # 取得選中的項目
        item = selection[0]
        values = self.tree.item(item, 'values')
        serial = int(values[0])

        # 找到對應的 Track
        track = next((t for t in self.tracks if t.serial == serial), None)
        if track:
            self._show_track_edit_dialog(track.start, track.end, track)

    def _delete_selected_track(self):
        """刪除選中的分段"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "請先選擇要刪除的分段")
            return

        # 確認刪除
        if not messagebox.askyesno("確認", "確定要刪除選中的分段嗎？"):
            return

        # 取得選中的項目
        item = selection[0]
        values = self.tree.item(item, 'values')
        serial = int(values[0])

        # 刪除 Track
        self.tracks = [t for t in self.tracks if t.serial != serial]

        self._refresh_track_list()

    def _export_tracks(self):
        """匯出分段描述檔"""
        if not self.tracks:
            messagebox.showwarning("警告", "沒有分段可以匯出")
            return

        # 確認匯出
        if not messagebox.askyesno("確認", f"確定要匯出到 {self.video_path.with_suffix('.json')} 嗎？"):
            return

        # 更新 TrackManager
        self.track_manager.tracks = self.tracks

        # 儲存
        if self.track_manager.save_tracks():
            messagebox.showinfo("成功", f"分段描述檔已匯出至\n{self.track_manager.json_path}")
        else:
            messagebox.showerror("錯誤", "匯出失敗")
