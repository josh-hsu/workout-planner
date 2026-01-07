"""
配置檔案管理模組
管理 .workout-planner 配置檔案
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class ConfigManager:
    """配置檔案管理器"""

    DEFAULT_CONFIG = {
        "playlists": {},
        "favorites": {},
        "preferences": {
            "default_playlist_dir": "playlists"
        }
    }

    def __init__(self, work_dir: str = "."):
        """
        初始化配置管理器

        Args:
            work_dir: 工作目錄路徑
        """
        self.work_dir = Path(work_dir)
        self.config_file = self.work_dir / ".workout-planner"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """載入配置檔案，若不存在則建立預設配置"""
        if not self.config_file.exists():
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"配置檔案載入失敗: {e}, 使用預設配置")
            return self.DEFAULT_CONFIG.copy()

    def _save_config(self, config: Optional[Dict] = None) -> None:
        """儲存配置檔案"""
        if config is None:
            config = self.config

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"配置檔案儲存失敗: {e}")

    def get_favorites(self, video_path: str) -> List[int]:
        """
        取得指定影片的最愛分段

        Args:
            video_path: 影片路徑（相對於工作目錄）

        Returns:
            最愛的分段序號列表
        """
        return self.config.get("favorites", {}).get(video_path, [])

    def toggle_favorite(self, video_path: str, track_serial: int) -> bool:
        """
        切換指定分段的最愛狀態

        Args:
            video_path: 影片路徑（相對於工作目錄）
            track_serial: 分段序號

        Returns:
            切換後的狀態 (True=已加入最愛, False=已移除)
        """
        if "favorites" not in self.config:
            self.config["favorites"] = {}

        if video_path not in self.config["favorites"]:
            self.config["favorites"][video_path] = []

        favorites = self.config["favorites"][video_path]

        if track_serial in favorites:
            favorites.remove(track_serial)
            is_favorite = False
        else:
            favorites.append(track_serial)
            is_favorite = True

        self._save_config()
        return is_favorite

    def is_favorite(self, video_path: str, track_serial: int) -> bool:
        """
        檢查指定分段是否為最愛

        Args:
            video_path: 影片路徑
            track_serial: 分段序號

        Returns:
            是否為最愛
        """
        return track_serial in self.get_favorites(video_path)

    def update_playlist_stats(self, playlist_name: str, last_played: str = None) -> None:
        """
        更新播放清單統計資訊

        Args:
            playlist_name: 播放清單名稱
            last_played: 最後播放日期 (YYYY-MM-DD 格式)
        """
        if "playlists" not in self.config:
            self.config["playlists"] = {}

        if playlist_name not in self.config["playlists"]:
            self.config["playlists"][playlist_name] = {
                "play_count": 0,
                "last_played": None
            }

        # 更新播放次數
        self.config["playlists"][playlist_name]["play_count"] += 1

        # 更新最後播放日期
        if last_played:
            self.config["playlists"][playlist_name]["last_played"] = last_played

        self._save_config()

    def get_preference(self, key: str, default=None):
        """取得偏好設定"""
        return self.config.get("preferences", {}).get(key, default)

    def set_preference(self, key: str, value) -> None:
        """設定偏好設定"""
        if "preferences" not in self.config:
            self.config["preferences"] = {}

        self.config["preferences"][key] = value
        self._save_config()
