#!/bin/bash

# --- KONFIGURASI BASE ---
SOURCE_BASE_DIR="/home/ilham/dms33/uploads/backup-folders"
BACKUP_HDD_DIR="/mnt/backup"
LOG_FILE="/home/ilham/dms33/dms33_backup.log"

# Pengecekan awal: Pastikan folder sumber ada
if [ ! -d "$SOURCE_BASE_DIR" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR (Compress): Folder $SOURCE_BASE_DIR tidak ditemukan!" >> $LOG_FILE
    exit 1
fi

# Pengecekan awal: Pastikan HDD External (/backup) ter-mount dengan benar
if [ ! -d "$BACKUP_HDD_DIR" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR (Compress): HDD External di $BACKUP_HDD_DIR tidak aktif/ter-mount!" >> $LOG_FILE
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === MEMULAI PROSES KOMPRESI KE HDD ===" >> $LOG_FILE

# Loop 1: Mencari folder Divisi (Finance, IT, HR, dll.)
for DIVISI_DIR in "$SOURCE_BASE_DIR"/*; do
    if [ -d "$DIVISI_DIR" ]; then
        DIVISI_NAME=$(basename "$DIVISI_DIR")

        # Loop 2: Mencari folder bulanan (Juli-2026-Finance, dll.)
        for BULANAN_DIR in "$DIVISI_DIR"/*; do
            if [ -d "$BULANAN_DIR" ]; then
                BULANAN_NAME=$(basename "$BULANAN_DIR")
                
                # Folder tujuan di HDD: /backup/NAMA_DIVISI
                TARGET_HDD_FOLDER="$BACKUP_HDD_DIR/$DIVISI_NAME"
                # Nama file hasil compress: /backup/NAMA_DIVISI/TANGGAL-DIVISI.tar.gz
                OUTPUT_TAR_FILE="$TARGET_HDD_FOLDER/$BULANAN_NAME.tar.gz"

                # Cek apakah folder sumber ada isinya agar tidak mengompres folder kosong
                if [ "$(ls -A "$BULANAN_DIR")" ]; then
                    
                    # 1. Pastikan folder tujuan di HDD sudah dibuat
                    if [ ! -d "$TARGET_HDD_FOLDER" ]; then
                        mkdir -p "$TARGET_HDD_FOLDER"
                        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Membuat folder baru di HDD: $TARGET_HDD_FOLDER" >> $LOG_FILE
                    fi

                    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Mengompres $BULANAN_NAME ke HDD..." >> $LOG_FILE
                    
                    # 2. Proses Kompresi menggunakan tar
                    # -c: create, -z: gzip, -f: file
                    # -C: pindah direktori sementara agar struktur di dalam tar tidak full path panjang
                    tar -czf "$OUTPUT_TAR_FILE" -C "$DIVISI_DIR" "$BULANAN_NAME"

                    if [ $? -eq 0 ]; then
                        echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: Kompresi $BULANAN_NAME.tar.gz berhasil disimpan." >> $LOG_FILE
                    else
                        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Gagal mengompres folder $BULANAN_NAME" >> $LOG_FILE
                    fi
                else
                    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Skip compress $BULANAN_NAME karena folder kosong." >> $LOG_FILE
                fi
            fi
        done
    fi
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === PROSES KOMPRESI SELESAI ===" >> $LOG_FILE
