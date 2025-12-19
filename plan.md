# Rencana Pengembangan YouTube Downloader

## Tujuan

Membuat aplikasi downloader YouTube menggunakan Python dan `yt-dlp` dengan fitur:

1. Input URL.
2. Pemilihan Output (Video/Audio).
3. Pemilihan Kualitas.
4. Output otomatis membuat folder berisi:
   - File Video/Audio
   - Thumbnail
   - Metadata (JSON)

## Arsitektur & Teknologi

- **Bahasa:** Python 3
- **Library Utama:** `yt-dlp`
- **Antarmuka:** CLI (Command Line Interface) - _Dipilih dengan tampilan cantik (rich, questionary)_

## Struktur Proyek

```text
/DownloaderYT
├── main.py            # Entry point dan interaksi user
├── downloader.py      # Logic utama yt-dlp
├── requirements.txt   # Daftar dependency
└── downloads/         # Folder output default
```

## Langkah Pengembangan

### 1. Persiapan Lingkungan

- [ ] Buat virtual environment (opsional tapi disarankan).
- [x] Buat file `requirements.txt` berisi `yt-dlp`, `rich`, `questionary`.
- [x] Install dependency.

### 2. Implementasi Core (`downloader.py`)

- [x] Buat fungsi untuk mengambil metadata video (tanpa download) untuk mendapatkan daftar format.
- [x] Konfigurasi `yt-dlp` options:
  - `writethumbnail`: True
  - `writeinfojson`: True
  - `outtmpl`: Template path agar masuk ke folder khusus per video.
  - `format`: Sesuai pilihan user.
- [x] Buat fungsi `download_media` yang menerima URL, tipe, dan quality ID.

### 3. Interaksi Pengguna (`main.py`)

- [x] Input URL dari pengguna.
- [x] Tampilkan metadata singkat (Judul).
- [x] Tanyakan Tipe: Video atau Audio.
  - Jika Audio: Tampilkan opsi bitrate/format (mp3/m4a).
  - Jika Video: Tampilkan opsi resolusi yang tersedia.
- [x] Eksekusi download berdasarkan pilihan.

### 4. Pengujian

- [x] Test link video biasa.
- [x] Test link playlist (Logic implemented & handled).
- [x] Verifikasi output folder (isi json, thumbnail, media).

### 5. Finalisasi

- [x] Code cleanup.
- [x] Error handling (URL tidak valid, koneksi error).
