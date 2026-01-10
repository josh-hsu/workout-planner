"""
工具函數模組
提供通用的工具函數
"""

import os
from pathlib import Path
from typing import List, Tuple


def seconds_to_time_str(seconds: float) -> str:
    """
    將秒數轉換為時間字串 (HH:MM:SS)

    Args:
        seconds: 秒數

    Returns:
        時間字串 (HH:MM:SS)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def time_str_to_seconds(time_str: str) -> float:
    """
    將時間字串轉換為秒數
    支援格式: HH:MM:SS, MM:SS, SS

    Args:
        time_str: 時間字串

    Returns:
        秒數

    Raises:
        ValueError: 時間格式錯誤
    """
    parts = time_str.strip().split(':')

    try:
        if len(parts) == 3:  # HH:MM:SS
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        elif len(parts) == 2:  # MM:SS
            minutes, seconds = map(int, parts)
            return minutes * 60 + seconds
        elif len(parts) == 1:  # SS
            return int(parts[0])
        else:
            raise ValueError("時間格式錯誤")
    except ValueError:
        raise ValueError(f"無法解析時間字串: {time_str}")


def get_video_files(directory: Path) -> List[Path]:
    """
    取得目錄下所有的影片檔案 (.mp4, .m4v)

    Args:
        directory: 目錄路徑

    Returns:
        影片檔案路徑列表
    """
    if not directory.exists() or not directory.is_dir():
        return []

    video_files = []
    video_files.extend(directory.glob("*.mp4"))
    video_files.extend(directory.glob("*.m4v"))
    return sorted(video_files)


def get_workout_categories(work_dir: Path) -> List[str]:
    """
    取得所有的課程種類（第一層資料夾）

    Args:
        work_dir: 工作目錄路徑

    Returns:
        課程種類名稱列表
    """
    if not work_dir.exists():
        return []

    categories = []
    for item in work_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.') and item.name != 'playlists':
            categories.append(item.name)

    return sorted(categories)


def ensure_dir_exists(directory: Path) -> None:
    """
    確保目錄存在，不存在則建立

    Args:
        directory: 目錄路徑
    """
    directory.mkdir(parents=True, exist_ok=True)


def get_relative_path(path: Path, base: Path) -> str:
    """
    取得相對於基準路徑的相對路徑

    Args:
        path: 檔案路徑
        base: 基準路徑

    Returns:
        相對路徑字串
    """
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def validate_video_file(file_path: Path) -> Tuple[bool, str]:
    """
    驗證影片檔案

    Args:
        file_path: 影片檔案路徑

    Returns:
        (是否有效, 錯誤訊息)
    """
    if not file_path.exists():
        return False, "檔案不存在"

    if not file_path.is_file():
        return False, "不是檔案"

    if file_path.suffix.lower() not in ['.mp4', '.m4v']:
        return False, "檔案格式必須為 .mp4 或 .m4v"

    return True, ""
