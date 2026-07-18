#!/bin/bash

# --- KONFIGURASI --
SOURCE_DIR="/home/ilham/dms33/uploads/temp"
REMOTE_NAME="dms33"
REMOTE_PATH="backup_dms33"
AIRGAP_DIR="/backup"

# Arahkan log ke folder home Anda, bukan /var/log
LOG_FILE="/home/ilham/dms33/dms33_backup.log"

# --- PROSES UPLOAD ---
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Uploading to cloud..." >> $LOG_FILE

rclone copy "$SOURCE_DIR" "$REMOTE_NAME:$REMOTE_PATH" --log-file="$LOG_FILE" --log-level INFO

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Upload success,now deleting file..." >> $LOG_FILE
    find "$SOURCE_DIR" -type f -delete
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Failed upload" >> $LOG_FILE
fi
