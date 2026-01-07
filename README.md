# Workout Planner

健身影片片段編排應用程式 - 自由編排健身影片片段成為課程播放清單

## 功能特色

- **建立分段描述檔**: 為健身影片建立時間戳記，標記每個訓練片段
- **建立課程播放清單**: 從不同影片中選擇片段，組合成個人化的訓練課程
- **XSPF 格式支援**: 生成 VLC 播放器可直接播放的播放清單
- **最愛管理**: 標記常用的訓練片段
- **跨平台**: 支援 Windows、macOS、Linux

## 系統需求

- Python 3.7+
- tkinter (通常隨 Python 安裝)
- OpenCV (opencv-python)
- Pillow (PIL)

## 安裝

1. 克隆或下載此專案
2. 安裝依賴套件:

```bash
pip install -r requirements.txt
```

## 檔案結構

```
WORK_DIR/
├── .workout-planner          # 配置檔案（自動生成）
├── playlists/                # 播放清單目錄（自動生成）
│   └── *.xspf
├── BodyCombat/               # 課程種類資料夾
│   ├── BC64.mp4
│   ├── BC64.json             # 分段描述檔
│   └── ...
├── BodyPump/
│   └── ...
└── ...
```

## 使用方法

### 啟動應用程式

```bash
cd /path/to/workout-planner
python main.py
```

### 功能一：建立分段描述檔

1. 點擊「建立分段描述檔」按鈕
2. 選擇要建立描述檔的影片檔案 (.mp4)
3. 使用影片播放器找到每個片段的開始和結束位置
4. 點擊「標記開始」和「標記結束」來標記片段
5. 輸入歌名和訓練名稱（可選）
6. 重複步驟 3-5 標記所有片段
7. 點擊「匯出描述檔」儲存為 .json 檔案

### 功能二：建立課程播放清單

1. 點擊「建立課程播放清單」按鈕
2. 選擇課程種類（如 BodyCombat）
3. 在左側的分段項目上：
   - **雙擊**：直接加入到播放清單
   - **右鍵點擊**：顯示選單
     - **選擇分段**：加入到播放清單（等同雙擊）
     - **預覽**：彈出視窗預覽該分段內容
     - **加入最愛/取消最愛**：標記常用分段（★/☆）
4. 右側播放清單可以刪除不需要的項目
5. 點擊「匯出播放清單」並輸入名稱
6. 播放清單會儲存到 `playlists/` 目錄

### 播放播放清單

使用 VLC Media Player 開啟生成的 .xspf 檔案即可播放。

## 檔案格式說明

### .workout-planner (JSON)

配置檔案，記錄播放統計和最愛片段:

```json
{
  "playlists": {
    "my_workout.xspf": {
      "play_count": 5,
      "last_played": "2026-01-07"
    }
  },
  "favorites": {
    "BodyCombat/BC64.mp4": [1, 3, 5]
  },
  "preferences": {
    "default_playlist_dir": "playlists"
  }
}
```

### *.json (分段描述檔)

影片分段資訊:

```json
{
  "video": "BC64.mp4",
  "tracks": [
    {
      "serial": 1,
      "name": "Warm Up",
      "training": "Warm Up",
      "start": 0,
      "end": 332
    }
  ]
}
```

### *.xspf (播放清單)

VLC 支援的播放清單格式，包含影片路徑和時間戳記。

## 專案結構

```
workout-planner/
├── main.py                    # 主程式進入點
├── config_manager.py          # 配置檔案管理
├── track_manager.py           # 分段描述檔管理
├── xspf_generator.py          # XSPF 播放清單生成
├── video_player.py            # 影片播放器元件
├── utils.py                   # 工具函數
├── gui/
│   ├── __init__.py
│   ├── main_window.py         # 主視窗
│   ├── track_editor.py        # 時間戳編輯器
│   └── playlist_builder.py    # 播放清單建立器
├── requirements.txt           # 依賴套件
└── README.md                  # 說明文件
```

## 注意事項

- 影片檔案必須是 .mp4 格式
- 建議先建立課程種類資料夾（如 BodyCombat、BodyPump）再放入影片
- 分段描述檔 (.json) 會自動儲存在影片檔案的同一目錄
- 播放清單會儲存在 `playlists/` 目錄下

## 授權

MIT License
