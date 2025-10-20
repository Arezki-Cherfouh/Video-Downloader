#!/bin/bash
cd "$(dirname "$0")"
echo "Running run_video-downloader..."
wine "run_video-downloader" || ./"run_video-downloader" "$@"
