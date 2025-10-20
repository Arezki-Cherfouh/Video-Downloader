#!/bin/bash
cd "$(dirname "$0")"
echo "Running run_video_downloader_gui..."
wine "run_video_downloader_gui" || ./"run_video_downloader_gui" "$@"
