# CLAUDE.md

## Project Overview

**Workout Planner** is a Python GUI application for creating timestamped segment descriptions for fitness videos and building custom workout playlists (XSPF format) compatible with VLC Media Player.

## Tech Stack

- **Language:** Python 3.7+
- **GUI:** tkinter
- **Dependencies:** opencv-python (video frame extraction), Pillow (image processing)
- **Data formats:** JSON (config/metadata), XML (XSPF playlists)

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Test imports
python test_imports.py

# Run application
python main.py
```

## Project Structure

```
workout-planner/
├── main.py                    # Entry point - workspace selection
├── config_manager.py          # Configuration file management (.workout-planner)
├── track_manager.py           # Video segment metadata (Track, TrackManager)
├── xspf_generator.py          # XSPF playlist generation for VLC
├── video_player.py            # Tkinter video player component using CV2
├── utils.py                   # Utilities (time conversion, path handling)
├── gui/
│   ├── main_window.py         # Main menu interface
│   ├── track_editor.py        # Timestamp editor window
│   └── playlist_builder.py    # Playlist builder with preview
└── requirements.txt
```

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point, workspace selection, remembers last workspace |
| `config_manager.py` | Handles `.workout-planner` JSON config (favorites, playlists, preferences) |
| `track_manager.py` | CRUD for video segments stored as `{video}.json` alongside video files |
| `xspf_generator.py` | Generates VLC-compatible XSPF playlists |
| `video_player.py` | Embedded video player using CV2 + threading |
| `gui/track_editor.py` | UI for marking timestamps in videos |
| `gui/playlist_builder.py` | UI for building playlists from segments |

## Coding Conventions

- **Documentation language:** Traditional Chinese (comments, docstrings, UI text)
- **Path handling:** Use `pathlib.Path` for cross-platform compatibility
- **File paths:** Stored as relative paths in configuration
- **Time values:** Stored in seconds as floats
- **Segment IDs:** Serial numbers starting at 1
- **Type hints:** Used for method signatures

## Data Storage

- **Config:** `{workspace}/.workout-planner` (JSON)
- **Track metadata:** `{video_file}.json` alongside each video
- **Playlists:** Exported to `{workspace}/playlists/` directory
- **Video formats:** `.mp4`, `.m4v` only

## Architecture Patterns

- **Separation of concerns:** Core logic (managers) separated from GUI
- **Manager classes:** `ConfigManager`, `TrackManager`, `XSPFGenerator` handle domain logic
- **Window classes:** Each GUI window is a separate class with its own state
- **Threading:** Background video playback to prevent UI freezing
- **Change tracking:** Unsaved changes detection with confirmation dialogs

## Platform Notes

- Cross-platform via tkinter and pathlib
- macOS VLC path hardcoded: `/Applications/VLC.app/Contents/MacOS/VLC`
- Preview functionality currently macOS-specific
