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
   git clone https://github.com/ibnu12126800/DownloaderYT-CLI.git
   cd DownloaderYT-CLI
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

### Mode Interactive (Default)

1. **Jalankan Aplikasi:**

   ```bash
   ./run.sh
   ```

   Atau:

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

### Mode CLI (Non-Interactive)

Untuk scripting atau penggunaan cepat:

```bash
# Download video kualitas terbaik
python main.py "https://youtube.com/watch?v=xxx"

# Download video 1080p
python main.py "https://youtube.com/watch?v=xxx" -t video -q 1080p

# Download audio MP3
python main.py "https://youtube.com/watch?v=xxx" -t audio -q mp3

# Download ke folder custom
python main.py "https://youtube.com/watch?v=xxx" -t video -q 720p -o ./media

# Lihat bantuan
python main.py --help
```

**Opsi CLI yang tersedia:**

| Opsi | Deskripsi |
|------|-----------|
| `url` | URL YouTube (video atau playlist) |
| `-t, --type` | Tipe download: `video` atau `audio` |
| `-q, --quality` | Kualitas video: `best`, `4k`, `1080p`, `720p`, `480p`, `360p`<br>Format audio: `mp3`, `m4a`, `flac`, `wav` |
| `-o, --output` | Direktori output (default: `downloads`) |
| `-i, --interactive` | Force mode interactive |

### Mode Desktop GUI (PyQt6)

Untuk tampilan grafis modern:

```bash
python gui.py
```

**Fitur GUI:**
- 🎨 Dark theme modern
- 🔍 Fetch info video dengan satu klik
- ⚡ Progress bar real-time dengan speed indicator
- 📁 Browse folder output
- ❌ Tombol cancel download

3. **Lokasi Unduhan:**
   Semua file yang diunduh (video/audio, thumbnail, metadata JSON) akan disimpan di dalam folder `downloads/` di direktori proyek. Untuk video tunggal, akan ada sub-folder terpisah per video. Untuk playlist, akan ada sub-folder dengan nama playlist, di dalamnya berisi sub-folder untuk setiap video dalam playlist tersebut.

## Struktur Proyek

```text
.
├── main.py            # CLI - interaksi pengguna via terminal
├── gui.py             # Desktop GUI - antarmuka grafis PyQt6
├── downloader.py      # Wrapper untuk fungsionalitas yt-dlp
├── requirements.txt   # Daftar dependensi Python
├── .gitignore         # File yang diabaikan oleh Git
├── README.md          # Dokumentasi proyek
├── run.sh             # Script sederhana untuk menjalankan aplikasi
└── downloads/         # Folder tempat hasil unduhan disimpan
```
