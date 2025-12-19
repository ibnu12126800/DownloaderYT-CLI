### Cara Menginstal `ffmpeg`

Untuk sebagian besar distribusi Linux, Anda bisa menginstalnya melalui package manager:

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

## Fitur

- **Input URL:** Mendukung URL video YouTube tunggal dan URL playlist.
- **Pilihan Output:** Unduh sebagai Video atau Audio.
- **Pilihan Kualitas:** Pilih resolusi video atau format audio (MP3, M4A, FLAC, WAV).
- **Output Terstruktur:** Secara otomatis membuat folder terpisah untuk setiap video/playlist yang berisi:
  - File media (video/audio)
  - Thumbnail
  - Metadata dalam format JSON
- **Progress Bar Interaktif:** Menampilkan progress download secara real-time.
- **Penanganan Error:** Memberikan pesan error yang informatif untuk URL yang tidak valid atau masalah koneksi.

## Instalasi

1. **Clone repositori ini:**

   ```bash
   git clone https://github.com/yourusername/DownloaderYT.git
   cd DownloaderYT
   ```

   _(Catatan: Anda mungkin perlu membuat repositori ini nanti jika belum ada.)_

2. **Buat Virtual Environment (Disarankan):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instal Dependensi:**

   ```bash
   pip install -r requirements.txt
   ```

## Cara Menggunakan

1. **Jalankan Aplikasi:**

   ```bash
   ./run.sh
   ```

   Atau, jika `run.sh` tidak bisa dieksekusi atau Anda tidak ingin menggunakannya:

   ```bash
   python main.py
   ```

2. **Ikuti Petunjuk:**
   Aplikasi akan memandu Anda melalui langkah-langkah berikut:

   - Memasukkan URL YouTube.
   - Menampilkan informasi video.
   - Memilih tipe unduhan (Video atau Audio).
   - Memilih kualitas/format.
   - Menampilkan progress download.

3. **Lokasi Unduhan:**
   Semua file yang diunduh (video/audio, thumbnail, metadata JSON) akan disimpan di dalam folder `downloads/` di direktori proyek. Untuk video tunggal, akan ada sub-folder terpisah per video. Untuk playlist, akan ada sub-folder dengan nama playlist, di dalamnya berisi sub-folder untuk setiap video dalam playlist tersebut.

## Struktur Proyek

```text
.
├── main.py            # Logika utama aplikasi CLI dan interaksi pengguna
├── downloader.py      # Wrapper untuk fungsionalitas yt-dlp
├── requirements.txt   # Daftar dependensi Python
├── .gitignore         # File yang diabaikan oleh Git
├── README.md          # Dokumentasi proyek
└── run.sh             # Script sederhana untuk menjalankan aplikasi
└── downloads/         # Folder tempat hasil unduhan disimpan
```
