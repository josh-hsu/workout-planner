"""
播放清單建立器模組
建立課程播放清單功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config_manager import ConfigManager
from track_manager import Track, TrackManager
from xspf_generator import XSPFGenerator, PlaylistItem
from utils import get_workout_categories, get_video_files, get_relative_path, seconds_to_time_str


class PlaylistBuilderWindow:
    """播放清單建立器視窗"""

    def __init__(self, window, work_dir: Path):
        """
        初始化播放清單建立器視窗

        Args:
            window: Tkinter 視窗
            work_dir: 工作目錄路徑
        """
        self.window = window
        self.work_dir = work_dir
        self.config_manager = ConfigManager(str(work_dir))
        self.xspf_generator = XSPFGenerator(str(work_dir))

        self.selected_category = None
        self.playlist_items = []  # 已選擇的播放清單項目

        # 設定視窗
        self.window.title("建立課程播放清單")
        self.window.geometry("1000x700")

        self._setup_ui()

    def _setup_ui(self):
        """設定使用者介面"""
        # 主容器
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 上半部：課程種類選擇
        category_frame = ttk.LabelFrame(main_container, text="選擇課程種類", padding=10)
        category_frame.pack(fill=tk.X, pady=5)

        # 取得所有課程種類
        categories = get_workout_categories(self.work_dir)

        if not categories:
            ttk.Label(
                category_frame,
                text="工作目錄下沒有找到課程種類資料夾\n請在工作目錄下建立課程資料夾（如 BodyCombat, BodyPump 等）",
                foreground='red'
            ).pack()
        else:
            self.category_var = tk.StringVar()
            for category in categories:
                ttk.Radiobutton(
                    category_frame,
                    text=category,
                    variable=self.category_var,
                    value=category,
                    command=self._on_category_selected
                ).pack(side=tk.LEFT, padx=10)

        # 中間部分：分為左右兩欄
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # 左欄：課程分段資訊
        left_frame = ttk.LabelFrame(content_frame, text="課程分段資訊", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 篩選選項
        filter_frame = ttk.Frame(left_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 5))

        self.show_favorites_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame,
            text="只顯示最愛",
            variable=self.show_favorites_only,
            command=self._on_filter_changed
        ).pack(side=tk.LEFT)

        # 課程分段列表（使用 Treeview）
        self.video_tree = ttk.Treeview(left_frame, show='tree', height=20)
        video_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.video_tree.yview)
        self.video_tree.configure(yscrollcommand=video_scrollbar.set)
        self.video_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        video_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 綁定雙擊事件
        self.video_tree.bind('<Double-Button-1>', self._on_track_double_click)

        # 綁定右鍵點擊事件（支援 macOS 和其他平台）
        self.video_tree.bind('<Button-2>', self._on_track_right_click)  # macOS 右鍵
        self.video_tree.bind('<Button-3>', self._on_track_right_click)  # Windows/Linux 右鍵
        self.video_tree.bind('<Control-Button-1>', self._on_track_right_click)  # macOS Control+左鍵

        # 創建右鍵選單
        self.context_menu = tk.Menu(self.video_tree, tearoff=0)
        self.context_menu.add_command(label="新增至清單", command=self._add_to_playlist_from_menu)
        self.context_menu.add_command(label="預覽", command=self._preview_track)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="標記最愛 / 取消最愛", command=self._toggle_favorite)

        # 用於記錄右鍵點擊的項目
        self.right_clicked_item = None

        # 右欄：已選分段清單
        right_frame = ttk.LabelFrame(content_frame, text="已選分段清單", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # 總時長標籤
        self.duration_label = ttk.Label(right_frame, text="總時長: 00:00:00", font=('Arial', 10, 'bold'))
        self.duration_label.pack(pady=5)

        # 已選分段列表
        columns = ('index', 'video', 'track', 'name', 'duration')
        self.playlist_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=20)

        self.playlist_tree.heading('index', text='#')
        self.playlist_tree.heading('video', text='影片')
        self.playlist_tree.heading('track', text='分段')
        self.playlist_tree.heading('name', text='名稱')
        self.playlist_tree.heading('duration', text='時長')

        self.playlist_tree.column('index', width=40, anchor=tk.CENTER)
        self.playlist_tree.column('video', width=100)
        self.playlist_tree.column('track', width=60, anchor=tk.CENTER)
        self.playlist_tree.column('name', width=150)
        self.playlist_tree.column('duration', width=80, anchor=tk.CENTER)

        playlist_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.playlist_tree.yview)
        self.playlist_tree.configure(yscrollcommand=playlist_scrollbar.set)
        self.playlist_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        playlist_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 刪除按鈕
        delete_btn_frame = ttk.Frame(right_frame)
        delete_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            delete_btn_frame,
            text="刪除選中項",
            command=self._delete_selected_item
        ).pack(side=tk.LEFT)

        ttk.Button(
            delete_btn_frame,
            text="清空清單",
            command=self._clear_playlist
        ).pack(side=tk.LEFT, padx=5)

        # 底部：匯出按鈕
        export_frame = ttk.Frame(main_container)
        export_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            export_frame,
            text="匯出播放清單",
            command=self._export_playlist
        ).pack(side=tk.RIGHT, padx=5)

    def _on_category_selected(self):
        """當選擇課程種類時"""
        self.selected_category = self.category_var.get()
        self._load_videos()

    def _on_filter_changed(self):
        """當篩選條件改變時"""
        self._load_videos()

    def _load_videos(self):
        """載入選中課程種類的所有影片"""
        # 清空列表
        for item in self.video_tree.get_children():
            self.video_tree.delete(item)

        if not self.selected_category:
            return

        category_dir = self.work_dir / self.selected_category
        videos = get_video_files(category_dir)

        for video_path in videos:
            # 建立影片節點
            video_name = video_path.stem
            video_node = self.video_tree.insert('', tk.END, text=video_name, tags=('video',))

            # 載入分段描述檔
            track_manager = TrackManager(str(video_path))

            if not track_manager.has_description_file():
                # 沒有描述檔
                self.video_tree.insert(video_node, tk.END, text="(沒有描述檔)", tags=('no_desc',))
                self.video_tree.item(video_node, tags=('video', 'no_desc'))
            else:
                # 有描述檔，展開所有分段
                tracks = track_manager.get_all_tracks()
                video_rel_path = get_relative_path(video_path, self.work_dir)

                # 篩選 tracks（如果啟用了只顯示最愛）
                show_favorites_only = self.show_favorites_only.get()
                has_visible_tracks = False

                for track in tracks:
                    # 檢查是否為最愛
                    is_fav = self.config_manager.is_favorite(video_rel_path, track.serial)

                    # 如果啟用「只顯示最愛」且此 track 不是最愛，則跳過
                    if show_favorites_only and not is_fav:
                        continue

                    has_visible_tracks = True
                    fav_icon = "★" if is_fav else "☆"

                    track_text = f"{fav_icon} Track {track.serial}: {track.name or '(無名稱)'}"
                    if track.training:
                        track_text += f" [{track.training}]"

                    track_node = self.video_tree.insert(
                        video_node,
                        tk.END,
                        text=track_text,
                        tags=('track',),
                        values=(str(video_path), track.serial)
                    )

                # 如果沒有可見的 tracks，則不顯示這個影片節點
                if not has_visible_tracks:
                    self.video_tree.delete(video_node)
                else:
                    # 展開影片節點
                    self.video_tree.item(video_node, open=True)

    def _on_track_double_click(self, event):
        """當雙擊分段時，加入到播放清單"""
        selection = self.video_tree.selection()
        if not selection:
            return

        item = selection[0]
        tags = self.video_tree.item(item, 'tags')

        # 只處理 track 標籤的項目
        if 'track' not in tags:
            # 如果是影片節點，嘗試切換最愛狀態（未來功能）
            return

        # 取得 track 資訊
        values = self.video_tree.item(item, 'values')
        if not values:
            return

        video_path_str, track_serial = values
        video_path = Path(video_path_str)
        track_serial = int(track_serial)

        # 載入 track 資訊
        track_manager = TrackManager(video_path_str)
        track = track_manager.get_track(track_serial)

        if not track:
            return

        # 建立 PlaylistItem
        video_rel_path = get_relative_path(video_path, self.work_dir)
        playlist_item = PlaylistItem(
            video_path=video_rel_path,
            track_serial=track.serial,
            track_name=track.name,
            start_time=track.start,
            end_time=track.end,
            training=track.training
        )

        # 加入播放清單
        self.playlist_items.append(playlist_item)
        self._refresh_playlist()

        # 處理最愛圖示切換（點擊星星）
        # 這裡可以添加一個右鍵選單來切換最愛狀態

    def _refresh_playlist(self):
        """刷新播放清單"""
        # 清空列表
        for item in self.playlist_tree.get_children():
            self.playlist_tree.delete(item)

        # 重新填入
        for idx, item in enumerate(self.playlist_items, start=1):
            video_name = Path(item.video_path).stem
            self.playlist_tree.insert('', tk.END, values=(
                idx,
                video_name,
                f"Track {item.track_serial}",
                item.track_name or "(無名稱)",
                seconds_to_time_str(item.duration)
            ))

        # 更新總時長
        total_duration = XSPFGenerator.calculate_total_duration(self.playlist_items)
        self.duration_label.config(text=f"總時長: {seconds_to_time_str(total_duration)}")

    def _delete_selected_item(self):
        """刪除選中的播放清單項目"""
        selection = self.playlist_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "請先選擇要刪除的項目")
            return

        # 取得選中的項目
        item = selection[0]
        values = self.playlist_tree.item(item, 'values')
        index = int(values[0]) - 1  # 轉換為 0-based index

        # 刪除
        if 0 <= index < len(self.playlist_items):
            del self.playlist_items[index]
            self._refresh_playlist()

    def _clear_playlist(self):
        """清空播放清單"""
        if not self.playlist_items:
            return

        if messagebox.askyesno("確認", "確定要清空播放清單嗎？"):
            self.playlist_items.clear()
            self._refresh_playlist()

    def _export_playlist(self):
        """匯出播放清單"""
        if not self.playlist_items:
            messagebox.showwarning("警告", "播放清單是空的，無法匯出")
            return

        # 提示輸入播放清單名稱
        playlist_name = simpledialog.askstring(
            "匯出播放清單",
            "請輸入播放清單名稱:",
            parent=self.window
        )

        if not playlist_name:
            return

        # 移除可能的副檔名
        playlist_name = playlist_name.replace('.xspf', '')

        try:
            # 生成 XSPF 檔案
            output_file = self.xspf_generator.generate_xspf(playlist_name, self.playlist_items)
            messagebox.showinfo("成功", f"播放清單已匯出至:\n{output_file}")

            # 清空當前播放清單（可選）
            if messagebox.askyesno("提示", "是否要清空當前播放清單？"):
                self.playlist_items.clear()
                self._refresh_playlist()

        except Exception as e:
            messagebox.showerror("錯誤", f"匯出失敗: {str(e)}")

    def _on_track_right_click(self, event):
        """處理右鍵點擊事件"""
        # 取得點擊位置的項目
        item = self.video_tree.identify_row(event.y)
        if not item:
            return

        # 選中該項目
        self.video_tree.selection_set(item)
        self.right_clicked_item = item

        # 檢查是否為 track 項目
        tags = self.video_tree.item(item, 'tags')
        if 'track' in tags:
            # 顯示右鍵選單
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def _add_to_playlist_from_menu(self):
        """從右鍵選單添加到播放清單"""
        if not self.right_clicked_item:
            return

        # 模擬雙擊事件
        class FakeEvent:
            pass

        fake_event = FakeEvent()
        self._on_track_double_click(fake_event)

    def _preview_track(self):
        """預覽分段"""
        if not self.right_clicked_item:
            return

        tags = self.video_tree.item(self.right_clicked_item, 'tags')
        if 'track' not in tags:
            return

        # 取得 track 資訊
        values = self.video_tree.item(self.right_clicked_item, 'values')
        if not values:
            return

        video_path_str, track_serial = values
        video_path = Path(video_path_str)
        track_serial = int(track_serial)

        # 載入 track 資訊
        track_manager = TrackManager(video_path_str)
        track = track_manager.get_track(track_serial)

        if not track:
            messagebox.showerror("錯誤", "無法載入分段資訊")
            return

        # 開啟預覽視窗
        preview_window = tk.Toplevel(self.window)
        PreviewWindow(preview_window, video_path, track)

    def _toggle_favorite(self):
        """切換最愛狀態"""
        if not self.right_clicked_item:
            return

        tags = self.video_tree.item(self.right_clicked_item, 'tags')
        if 'track' not in tags:
            return

        # 取得 track 資訊
        values = self.video_tree.item(self.right_clicked_item, 'values')
        if not values:
            return

        video_path_str, track_serial = values
        video_path = Path(video_path_str)
        track_serial = int(track_serial)

        # 取得相對路徑
        video_rel_path = get_relative_path(video_path, self.work_dir)

        # 切換最愛狀態
        is_favorite = self.config_manager.toggle_favorite(video_rel_path, track_serial)

        # 重新載入影片列表以更新顯示（星星圖標會自動更新）
        self._load_videos()


class PreviewWindow:
    """預覽視窗"""

    def __init__(self, window, video_path: Path, track: Track):
        """
        初始化預覽視窗

        Args:
            window: Tkinter 視窗
            video_path: 影片路徑
            track: 要預覽的分段
        """
        self.window = window
        self.video_path = video_path
        self.track = track

        # 設定視窗
        self.window.title(f"預覽 - {video_path.stem} Track {track.serial}")
        self.window.geometry("700x650")

        self._setup_ui()
        self._load_and_play()

    def _setup_ui(self):
        """設定使用者介面"""
        # 標題
        title_text = f"{self.video_path.stem} - Track {self.track.serial}"
        if self.track.name:
            title_text += f": {self.track.name}"
        if self.track.training:
            title_text += f" [{self.track.training}]"

        title_label = ttk.Label(
            self.window,
            text=title_text,
            font=('Arial', 12, 'bold')
        )
        title_label.pack(pady=10)

        # 時間資訊
        from utils import seconds_to_time_str
        time_info = f"時間: {seconds_to_time_str(self.track.start)} - {seconds_to_time_str(self.track.end)} (時長: {seconds_to_time_str(self.track.duration)})"
        time_label = ttk.Label(self.window, text=time_info)
        time_label.pack(pady=5)

        # 影片播放器
        from video_player import VideoPlayer
        self.video_player = VideoPlayer(self.window, width=640, height=360)
        self.video_player.pack(pady=10)

        # 關閉按鈕
        close_btn = ttk.Button(
            self.window,
            text="關閉",
            command=self.window.destroy
        )
        close_btn.pack(pady=10)

    def _load_and_play(self):
        """載入並播放影片片段"""
        # 載入影片
        if not self.video_player.load_video(self.video_path):
            messagebox.showerror("錯誤", "無法載入影片")
            self.window.destroy()
            return

        # 跳轉到開始位置
        self.video_player.seek_to(self.track.start)

        # 自動播放
        self.video_player._play()

        # 設定定時器，在結束時間停止
        duration_ms = int((self.track.end - self.track.start) * 1000)
        self.window.after(duration_ms, self._stop_playback)

    def _stop_playback(self):
        """停止播放"""
        if hasattr(self, 'video_player'):
            self.video_player._pause()
