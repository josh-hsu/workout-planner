"""
影片分段描述檔管理模組
管理 *.json 影片分段描述檔
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class Track:
    """影片分段資料類別"""

    def __init__(self, serial: int, start: float, end: float,
                 name: str = "", training: str = ""):
        """
        初始化分段

        Args:
            serial: 序號（從1開始）
            start: 開始時間戳（秒）
            end: 結束時間戳（秒）
            name: 歌名
            training: 訓練名稱
        """
        self.serial = serial
        self.start = start
        self.end = end
        self.name = name
        self.training = training

    @property
    def duration(self) -> float:
        """取得分段時長（秒）"""
        return self.end - self.start

    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            "serial": self.serial,
            "name": self.name,
            "training": self.training,
            "start": self.start,
            "end": self.end
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Track':
        """從字典建立 Track 物件"""
        return Track(
            serial=data["serial"],
            start=data["start"],
            end=data["end"],
            name=data.get("name", ""),
            training=data.get("training", "")
        )

    def __repr__(self):
        return f"Track(serial={self.serial}, start={self.start}, end={self.end}, name={self.name})"


class TrackManager:
    """影片分段描述檔管理器"""

    def __init__(self, video_path: str):
        """
        初始化分段管理器

        Args:
            video_path: 影片檔案路徑（.mp4）
        """
        self.video_path = Path(video_path)
        self.json_path = self.video_path.with_suffix('.json')
        self.tracks: List[Track] = []
        self._load_tracks()

    def _load_tracks(self) -> None:
        """載入分段描述檔"""
        if not self.json_path.exists():
            self.tracks = []
            return

        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tracks = [Track.from_dict(t) for t in data.get("tracks", [])]
                # 按 serial 排序
                self.tracks.sort(key=lambda t: t.serial)
        except (json.JSONDecodeError, IOError, KeyError) as e:
            print(f"分段描述檔載入失敗: {e}")
            self.tracks = []

    def save_tracks(self) -> bool:
        """
        儲存分段描述檔

        Returns:
            是否儲存成功
        """
        # 按 serial 排序
        self.tracks.sort(key=lambda t: t.serial)

        data = {
            "video": self.video_path.name,
            "tracks": [t.to_dict() for t in self.tracks]
        }

        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"分段描述檔儲存失敗: {e}")
            return False

    def add_track(self, track: Track) -> None:
        """新增分段"""
        self.tracks.append(track)
        self.tracks.sort(key=lambda t: t.serial)

    def remove_track(self, serial: int) -> bool:
        """
        移除指定分段

        Args:
            serial: 分段序號

        Returns:
            是否移除成功
        """
        original_len = len(self.tracks)
        self.tracks = [t for t in self.tracks if t.serial != serial]
        return len(self.tracks) < original_len

    def update_track(self, track: Track) -> bool:
        """
        更新指定分段

        Args:
            track: 更新後的分段物件

        Returns:
            是否更新成功
        """
        for i, t in enumerate(self.tracks):
            if t.serial == track.serial:
                self.tracks[i] = track
                return True
        return False

    def get_track(self, serial: int) -> Optional[Track]:
        """取得指定分段"""
        for track in self.tracks:
            if track.serial == serial:
                return track
        return None

    def has_description_file(self) -> bool:
        """檢查是否有描述檔"""
        return self.json_path.exists() and len(self.tracks) > 0

    def get_all_tracks(self) -> List[Track]:
        """取得所有分段（已排序）"""
        return sorted(self.tracks, key=lambda t: t.serial)

    def validate_track(self, track: Track, video_duration: float) -> tuple[bool, str]:
        """
        驗證分段資料

        Args:
            track: 要驗證的分段
            video_duration: 影片總長度（秒）

        Returns:
            (是否有效, 錯誤訊息)
        """
        if track.start < 0:
            return False, "開始時間不能為負數"

        if track.end <= track.start:
            return False, "結束時間必須大於開始時間"

        if track.end > video_duration:
            return False, f"結束時間超出影片長度 ({video_duration}秒)"

        if track.serial < 1:
            return False, "序號必須從1開始"

        return True, ""
