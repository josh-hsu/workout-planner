"""
影片播放器模組
提供簡單的影片播放器元件
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional, Callable
import threading
import time

try:
    import cv2
    from PIL import Image, ImageTk
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("警告: 無法導入 cv2 或 PIL，影片播放功能將不可用")


class VideoPlayer(ttk.Frame):
    """影片播放器元件"""

    def __init__(self, parent, width=640, height=480):
        """
        初始化影片播放器

        Args:
            parent: 父元件
            width: 播放器寬度
            height: 播放器高度
        """
        super().__init__(parent)

        self.width = width
        self.height = height
        self.video_path: Optional[Path] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_playing = False
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.duration = 0  # 總時長（秒）
        self.play_thread: Optional[threading.Thread] = None
        self.on_position_changed: Optional[Callable[[float], None]] = None

        self._setup_ui()

    def _setup_ui(self):
        """設定使用者介面"""
        # 影片顯示區域
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg='black')
        self.canvas.pack(pady=10)

        # 控制列框架
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)

        # 播放/暫停按鈕
        self.play_pause_btn = ttk.Button(
            control_frame,
            text="播放",
            command=self._toggle_play_pause,
            state=tk.DISABLED
        )
        self.play_pause_btn.pack(side=tk.LEFT, padx=5)

        # 停止按鈕
        self.stop_btn = ttk.Button(
            control_frame,
            text="停止",
            command=self._stop,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # 時間標籤
        self.time_label = ttk.Label(control_frame, text="00:00:00 / 00:00:00")
        self.time_label.pack(side=tk.LEFT, padx=20)

        # 進度條框架
        progress_frame = ttk.Frame(self)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)

        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_scale = ttk.Scale(
            progress_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.progress_var,
            command=self._on_scale_change
        )
        self.progress_scale.pack(fill=tk.X)
        self.progress_scale.config(state=tk.DISABLED)

    def load_video(self, video_path: Path) -> bool:
        """
        載入影片

        Args:
            video_path: 影片檔案路徑

        Returns:
            是否載入成功
        """
        if not CV2_AVAILABLE:
            return False

        if not video_path.exists():
            return False

        # 釋放舊的影片
        self._release_video()

        # 載入新影片
        self.video_path = video_path
        self.cap = cv2.VideoCapture(str(video_path))

        if not self.cap.isOpened():
            return False

        # 取得影片資訊
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0

        # 顯示第一幀
        self._show_frame(0)

        # 啟用控制按鈕
        self.play_pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_scale.config(state=tk.NORMAL)

        # 更新時間標籤
        self._update_time_label()

        return True

    def _show_frame(self, frame_number: int) -> None:
        """
        顯示指定幀

        Args:
            frame_number: 幀號
        """
        if not self.cap:
            return

        # 設定影片位置
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()

        if ret:
            # 轉換顏色空間 (BGR -> RGB)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 調整大小
            frame = cv2.resize(frame, (self.width, self.height))

            # 轉換為 PIL Image
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image)

            # 顯示在 Canvas 上
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.canvas.image = photo  # 保持引用

            self.current_frame = frame_number

            # 更新進度條
            progress = (frame_number / self.total_frames * 100) if self.total_frames > 0 else 0
            self.progress_var.set(progress)

            # 更新時間標籤
            self._update_time_label()

            # 觸發位置變更回調
            if self.on_position_changed:
                current_time = self.get_current_time()
                self.on_position_changed(current_time)

    def _toggle_play_pause(self):
        """切換播放/暫停"""
        if self.is_playing:
            self._pause()
        else:
            self._play()

    def _play(self):
        """播放影片"""
        if not self.cap or self.is_playing:
            return

        self.is_playing = True
        self.play_pause_btn.config(text="暫停")

        # 在新執行緒中播放
        self.play_thread = threading.Thread(target=self._play_loop, daemon=True)
        self.play_thread.start()

    def _pause(self):
        """暫停播放"""
        self.is_playing = False
        self.play_pause_btn.config(text="播放")

    def _stop(self):
        """停止播放"""
        self.is_playing = False
        self.play_pause_btn.config(text="播放")
        self._show_frame(0)

    def _play_loop(self):
        """播放循環（在背景執行緒中執行）"""
        frame_delay = 1.0 / self.fps if self.fps > 0 else 0.033

        while self.is_playing and self.current_frame < self.total_frames - 1:
            start_time = time.time()

            # 顯示下一幀
            next_frame = self.current_frame + 1
            self.after(0, lambda f=next_frame: self._show_frame(f))

            # 控制播放速度
            elapsed = time.time() - start_time
            sleep_time = max(0, frame_delay - elapsed)
            time.sleep(sleep_time)

        # 播放結束
        self.after(0, self._pause)

    def _on_scale_change(self, value):
        """
        進度條變更事件

        Args:
            value: 進度條數值 (0-100)
        """
        if not self.cap:
            return

        # 計算對應的幀號
        frame_number = int(float(value) / 100 * self.total_frames)
        frame_number = max(0, min(frame_number, self.total_frames - 1))

        # 如果不是播放中，則顯示該幀
        if not self.is_playing:
            self._show_frame(frame_number)

    def _update_time_label(self):
        """更新時間標籤"""
        current_time = self.current_frame / self.fps if self.fps > 0 else 0
        total_time = self.duration

        current_str = self._format_time(current_time)
        total_str = self._format_time(total_time)

        self.time_label.config(text=f"{current_str} / {total_str}")

    @staticmethod
    def _format_time(seconds: float) -> str:
        """
        格式化時間

        Args:
            seconds: 秒數

        Returns:
            格式化的時間字串 (HH:MM:SS)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_current_time(self) -> float:
        """
        取得當前播放時間

        Returns:
            當前時間（秒）
        """
        return self.current_frame / self.fps if self.fps > 0 else 0

    def get_duration(self) -> float:
        """
        取得影片總時長

        Returns:
            總時長（秒）
        """
        return self.duration

    def seek_to(self, seconds: float) -> None:
        """
        跳轉到指定時間

        Args:
            seconds: 時間（秒）
        """
        if not self.cap:
            return

        frame_number = int(seconds * self.fps)
        frame_number = max(0, min(frame_number, self.total_frames - 1))
        self._show_frame(frame_number)

    def _release_video(self):
        """釋放影片資源"""
        self.is_playing = False

        if self.cap:
            self.cap.release()
            self.cap = None

        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30
        self.duration = 0

    def destroy(self):
        """銷毀元件"""
        self._release_video()
        super().destroy()
