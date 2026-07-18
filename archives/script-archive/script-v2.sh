#!/bin/bash

# --- KONFIGURASI BASE ---
BASE_DIR="/home/ilham/dms33/uploads/backup-folders"
REMOTE_NAME="dms33"
REMOTE_BASE_PATH="backup_dms33"
LOG_FILE="/home/ilham/dms33/dms33_backup.log"

# Pengecekan awal: Pastikan folder base ada
if [ ! -d "$BASE_DIR" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Base folder $BASE_DIR tidak ditemukan!" >> $LOG_FILE
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === MEMULAI PROSES BACKUP DINAMIS ===" >> $LOG_FILE

# Loop 1: Mencari semua subfolder Divisi (Finance, IT, HR, dll.)
for DIVISI_DIR in "$BASE_DIR"/*; do
    # Pastikan ini adalah sebuah direktori/folder
    if [ -d "$DIVISI_DIR" ]; then
        DIVISI_NAME=$(basename "$DIVISI_DIR")

        # Loop 2: Mencari folder bulanan di dalam folder Divisi (Juli-2026-Finance, Agustus-2029-IT, dll.)
        for BULANAN_DIR in "$DIVISI_DIR"/*; do
            if [ -d "$BULANAN_DIR" ]; then
                BULANAN_NAME=$(basename "$BULANAN_DIR")
                
                # Definisikan path tujuan di cloud secara dinamis
                # Hasilnya akan menjadi: backup_dms33/Finance/Juli-2026-Finance
                REMOTE_PATH="$REMOTE_BASE_PATH/$DIVISI_NAME/$BULANAN_NAME"

                # Cek apakah folder tersebut kosong atau ada filenya
                if [ "$(ls -A "$BULANAN_DIR")" ]; then
                    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Memproses folder: $DIVISI_NAME -> $BULANAN_NAME" >> $LOG_FILE
                    
                    # Jalankan rclone copy
                    rclone copy "$BULANAN_DIR" "$REMOTE_NAME:$REMOTE_PATH" --log-file="$LOG_FILE" --log-level INFO

                    if [ $? -eq 0 ]; then
                        echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $BULANAN_NAME berhasil diupload. Menghapus file lokal..." >> $LOG_FILE
                        # Menghapus file di dalam folder tersebut setelah sukses
                        find "$BULANAN_DIR" -type f -delete
                    else
                        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Gagal upload folder $BULANAN_NAME" >> $LOG_FILE
                    fi
                else
                    # Log opsional jika folder kosong (bisa dihapus jika terlalu penuh memenuhi log)
                    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Skip $BULANAN_NAME karena folder kosong." >> $LOG_FILE
                fi
            fi
        done
    fi
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === PROSES BACKUP SELESAI ===" >> $LOG_FILE
