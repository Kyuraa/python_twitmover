# Twitter File Auto-Mover

A simple Python script that automatically moves files starting with "twit_" from your Downloads folder to a dedicated "twit" subfolder.

## What it does

- Monitors your Downloads folder for new files
- Automatically moves any file starting with "twit_" to a subfolder called "twit"
- Handles duplicate filenames by adding a counter suffix
- Works with existing files at startup and new downloads in real-time

## Requirements

- Python 3.x
- watchdog library (`pip install watchdog`)

## Usage

Run the script and it will continuously monitor your Downloads folder:

```bash
python twit_mover.py
```

Press Ctrl+C to stop the monitoring.

## Note

This tool is for personal usage only.