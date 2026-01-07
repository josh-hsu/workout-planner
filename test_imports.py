#!/usr/bin/env python3
"""
測試所有模組是否可以正確導入
"""

import sys

def test_imports():
    """測試所有模組導入"""
    print("測試模組導入...")

    tests = []

    # 測試核心模組
    try:
        import config_manager
        print("✓ config_manager")
        tests.append(True)
    except Exception as e:
        print(f"✗ config_manager: {e}")
        tests.append(False)

    try:
        import track_manager
        print("✓ track_manager")
        tests.append(True)
    except Exception as e:
        print(f"✗ track_manager: {e}")
        tests.append(False)

    try:
        import xspf_generator
        print("✓ xspf_generator")
        tests.append(True)
    except Exception as e:
        print(f"✗ xspf_generator: {e}")
        tests.append(False)

    try:
        import utils
        print("✓ utils")
        tests.append(True)
    except Exception as e:
        print(f"✗ utils: {e}")
        tests.append(False)

    try:
        import video_player
        print("✓ video_player")
        tests.append(True)
    except Exception as e:
        print(f"✗ video_player: {e}")
        tests.append(False)

    # 測試 GUI 模組
    try:
        from gui import main_window
        print("✓ gui.main_window")
        tests.append(True)
    except Exception as e:
        print(f"✗ gui.main_window: {e}")
        tests.append(False)

    try:
        from gui import track_editor
        print("✓ gui.track_editor")
        tests.append(True)
    except Exception as e:
        print(f"✗ gui.track_editor: {e}")
        tests.append(False)

    try:
        from gui import playlist_builder
        print("✓ gui.playlist_builder")
        tests.append(True)
    except Exception as e:
        print(f"✗ gui.playlist_builder: {e}")
        tests.append(False)

    # 測試 tkinter
    try:
        import tkinter as tk
        print("✓ tkinter")
        tests.append(True)
    except Exception as e:
        print(f"✗ tkinter: {e}")
        tests.append(False)

    # 測試 cv2 和 PIL
    try:
        import cv2
        print("✓ cv2 (opencv-python)")
        tests.append(True)
    except Exception as e:
        print(f"✗ cv2 (opencv-python): {e}")
        print("  請執行: pip install opencv-python")
        tests.append(False)

    try:
        from PIL import Image, ImageTk
        print("✓ PIL (Pillow)")
        tests.append(True)
    except Exception as e:
        print(f"✗ PIL (Pillow): {e}")
        print("  請執行: pip install Pillow")
        tests.append(False)

    # 結果統計
    print("\n" + "="*50)
    total = len(tests)
    passed = sum(tests)
    failed = total - passed

    print(f"總計: {total} 個測試")
    print(f"通過: {passed}")
    print(f"失敗: {failed}")

    if failed == 0:
        print("\n所有模組導入成功！可以啟動應用程式。")
        return 0
    else:
        print("\n有模組導入失敗，請檢查依賴套件是否已安裝。")
        print("執行以下命令安裝依賴套件:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(test_imports())
