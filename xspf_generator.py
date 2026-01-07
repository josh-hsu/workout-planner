"""
XSPF 播放清單生成模組
生成 VLC 播放器支援的 XSPF 格式播放清單
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple
from xml.dom import minidom


class PlaylistItem:
    """播放清單項目"""

    def __init__(self, video_path: str, track_serial: int, track_name: str,
                 start_time: float, end_time: float, training: str = ""):
        """
        初始化播放清單項目

        Args:
            video_path: 影片檔案路徑
            track_serial: 分段序號
            track_name: 分段名稱
            start_time: 開始時間（秒）
            end_time: 結束時間（秒）
            training: 訓練名稱
        """
        self.video_path = video_path
        self.track_serial = track_serial
        self.track_name = track_name
        self.start_time = start_time
        self.end_time = end_time
        self.training = training

    @property
    def duration(self) -> float:
        """取得時長（秒）"""
        return self.end_time - self.start_time

    @property
    def title(self) -> str:
        """取得顯示標題"""
        video_name = Path(self.video_path).stem
        title_parts = [video_name, f"Track {self.track_serial}"]

        if self.track_name:
            title_parts.append(self.track_name)

        if self.training:
            title_parts.append(f"({self.training})")

        return " - ".join(title_parts)


class XSPFGenerator:
    """XSPF 播放清單生成器"""

    NAMESPACE = "http://xspf.org/ns/0/"
    VLC_NAMESPACE = "http://www.videolan.org/vlc/playlist/0"

    def __init__(self, work_dir: str = "."):
        """
        初始化生成器

        Args:
            work_dir: 工作目錄路徑
        """
        self.work_dir = Path(work_dir)

    def generate_xspf(self, playlist_name: str, items: List[PlaylistItem]) -> str:
        """
        生成 XSPF 格式的播放清單

        Args:
            playlist_name: 播放清單名稱
            items: 播放清單項目列表

        Returns:
            XSPF 檔案路徑
        """
        # 建立 XML 根元素
        playlist = ET.Element("playlist", {
            "version": "1",
            "xmlns": self.NAMESPACE,
            "xmlns:vlc": self.VLC_NAMESPACE
        })

        # 標題
        title = ET.SubElement(playlist, "title")
        title.text = playlist_name

        # trackList
        track_list = ET.SubElement(playlist, "trackList")

        for idx, item in enumerate(items, start=1):
            self._add_track(track_list, item, idx)

        # 轉換為字串並格式化
        xml_str = ET.tostring(playlist, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ", encoding='utf-8')

        # 儲存檔案
        output_dir = self.work_dir / "playlists"
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f"{playlist_name}.xspf"
        with open(output_file, 'wb') as f:
            f.write(pretty_xml)

        return str(output_file)

    def _add_track(self, track_list: ET.Element, item: PlaylistItem, track_id: int) -> None:
        """
        新增一個 track 到 trackList

        Args:
            track_list: trackList 元素
            item: 播放清單項目
            track_id: track ID（從1開始）
        """
        track = ET.SubElement(track_list, "track")

        # location (使用絕對路徑)
        location = ET.SubElement(track, "location")
        video_abs_path = (self.work_dir / item.video_path).resolve()
        location.text = video_abs_path.as_uri()

        # title
        title = ET.SubElement(track, "title")
        title.text = item.title

        # duration (毫秒)
        duration = ET.SubElement(track, "duration")
        duration.text = str(int(item.duration * 1000))

        # extension for VLC options
        extension = ET.SubElement(track, "extension", {
            "application": self.VLC_NAMESPACE
        })

        # VLC options for start and stop time
        vlc_id = ET.SubElement(extension, "vlc:id")
        vlc_id.text = str(track_id - 1)  # VLC uses 0-based index

        vlc_option_start = ET.SubElement(extension, "vlc:option")
        vlc_option_start.text = f"start-time={item.start_time:.2f}"

        vlc_option_stop = ET.SubElement(extension, "vlc:option")
        vlc_option_stop.text = f"stop-time={item.end_time:.2f}"

    @staticmethod
    def calculate_total_duration(items: List[PlaylistItem]) -> float:
        """
        計算播放清單總時長

        Args:
            items: 播放清單項目列表

        Returns:
            總時長（秒）
        """
        return sum(item.duration for item in items)

    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        格式化時長為 HH:MM:SS

        Args:
            seconds: 秒數

        Returns:
            格式化的時長字串
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
