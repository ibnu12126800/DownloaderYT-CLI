import os
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.table import Table
import questionary
from downloader import YouTubeHandler

console = Console()
handler = YouTubeHandler()

# Quality mapping for CLI arguments
VIDEO_QUALITY_MAP = {
    'best': 'bestvideo+bestaudio/best',
    '4k': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
    '2160p': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
    '1440p': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
    '2k': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
    '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
    '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
    '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
    '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
}

AUDIO_QUALITY_MAP = {
    'mp3': 'mp3',
    'm4a': 'm4a',
    'flac': 'flac',
    'wav': 'wav',
}

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='YouTube Downloader CLI - Download video/audio dari YouTube',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Contoh penggunaan:
  %(prog)s                                    # Mode interactive
  %(prog)s "URL" -t video -q 1080p            # Download video 1080p
  %(prog)s "URL" -t audio -q mp3              # Download audio MP3
  %(prog)s "URL" -t video -q best -o ./media  # Download ke folder custom
        '''
    )
    
    parser.add_argument('url', nargs='?', help='URL YouTube (video atau playlist)')
    parser.add_argument('-t', '--type', choices=['video', 'audio'], 
                        help='Tipe download: video atau audio')
    parser.add_argument('-q', '--quality', 
                        help='Kualitas (video: best/4k/1080p/720p/480p/360p, audio: mp3/m4a/flac/wav)')
    parser.add_argument('-o', '--output', default='downloads',
                        help='Direktori output (default: downloads)')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Force mode interactive')
    
    return parser.parse_args()


def run_non_interactive(args):
    """Jalankan download dalam mode non-interactive."""
    url = args.url
    download_type = args.type or 'video'
    quality = args.quality or ('best' if download_type == 'video' else 'mp3')
    output_dir = args.output
    
    # Validasi quality
    if download_type == 'video':
        if quality.lower() not in VIDEO_QUALITY_MAP:
            console.print(f"[bold red]Error:[/bold red] Kualitas video tidak valid: {quality}")
            console.print(f"Pilihan: {', '.join(VIDEO_QUALITY_MAP.keys())}")
            sys.exit(1)
        format_str = VIDEO_QUALITY_MAP[quality.lower()]
    else:
        if quality.lower() not in AUDIO_QUALITY_MAP:
            console.print(f"[bold red]Error:[/bold red] Format audio tidak valid: {quality}")
            console.print(f"Pilihan: {', '.join(AUDIO_QUALITY_MAP.keys())}")
            sys.exit(1)
        audio_format = AUDIO_QUALITY_MAP[quality.lower()]
    
    # Ambil metadata
    console.print(f"[bold cyan]🔗 URL:[/bold cyan] {url}")
    with console.status("[bold green]Mengambil metadata...[/bold green]", spinner="dots"):
        info, error = handler.get_video_info(url)
    
    if error:
        console.print(f"[bold red]Gagal mengambil info:[/bold red] {error}")
        sys.exit(1)
    
    # Tampilkan info singkat
    is_playlist = info.get('_type') == 'playlist'
    if is_playlist:
        console.print(f"[bold cyan]📋 Playlist:[/bold cyan] {info.get('title', 'N/A')}")
        count = info.get('playlist_count') or len(info.get('entries', []))
        console.print(f"[bold cyan]📊 Jumlah Video:[/bold cyan] {count}")
    else:
        console.print(f"[bold cyan]🎬 Judul:[/bold cyan] {info.get('title', 'N/A')}")
        console.print(f"[bold cyan]📺 Channel:[/bold cyan] {info.get('uploader', 'N/A')}")
    
    console.print(f"[bold cyan]📁 Output:[/bold cyan] {output_dir}/")
    console.print(f"[bold cyan]🎯 Tipe:[/bold cyan] {download_type.capitalize()}")
    console.print(f"[bold cyan]⚡ Kualitas:[/bold cyan] {quality}")
    console.print()
    
    # Siapkan opsi download
    dl_options = {}
    
    if is_playlist:
        playlist_title = info.get('title', 'Playlist')
        safe_title = "".join(x for x in playlist_title if x.isalnum() or x in " -_").strip()
        dl_options['outtmpl'] = os.path.join(output_dir, safe_title, '%(title)s [%(id)s]', '%(title)s [%(id)s].%(ext)s')
    else:
        dl_options['outtmpl'] = os.path.join(output_dir, '%(title)s [%(id)s]', '%(title)s [%(id)s].%(ext)s')
    
    if download_type == 'video':
        dl_options['format'] = format_str
        dl_options['merge_output_format'] = 'mp4'
    else:
        dl_options['format'] = 'bestaudio/best'
        dl_options['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '192',
        }]
    
    # Download dengan progress bar
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console
    )
    
    task_id = progress.add_task("Downloading...", total=None)
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            try:
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                
                info_dict = d.get('info_dict', {})
                title = info_dict.get('title', '')
                if not title and 'filename' in d:
                    title = os.path.basename(d['filename'])
                
                display_title = (title[:30] + '...') if len(title) > 30 else title
                
                p_index = info_dict.get('playlist_index')
                p_count = info_dict.get('playlist_count')
                
                if p_index and p_count:
                    desc = f"[cyan][{p_index}/{p_count}] {display_title}[/cyan]"
                else:
                    desc = f"[cyan]{display_title}[/cyan]" if display_title else "Downloading..."
                
                if total:
                    progress.update(task_id, total=total, completed=downloaded, description=desc)
            except Exception:
                pass
        elif d['status'] == 'finished':
            progress.update(task_id, description="[bold green]Processing...[/bold green]")
    
    console.print("[bold green]⬇️  Mulai download...[/bold green]")
    with progress:
        success, msg = handler.download(url, dl_options, progress_hook)
    
    if success:
        console.print(f"\n[bold green]✅ {msg}[/bold green]")
        console.print(f"[dim]File tersimpan di folder '{output_dir}'[/dim]")
        sys.exit(0)
    else:
        console.print(f"\n[bold red]❌ Error:[/bold red] {msg}")
        sys.exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    title = Text("YouTube Downloader CLI", style="bold magenta", justify="center")
    subtitle = Text("Powered by yt-dlp & Python", style="italic white", justify="center")
    panel = Panel(Text.assemble(title, "\n", subtitle), border_style="cyan", expand=False)
    console.print(panel, justify="center")
    console.print("\n")

def format_seconds(seconds):
    if not seconds: return "N/A"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{int(h)}:{int(m):02d}:{int(s):02d}"
    return f"{int(m)}:{int(s):02d}"

def get_quality_options(type_choice):
    if type_choice == 'Video':
        return [
            {"name": "🌟 Best Available (Max)", "value": "bestvideo+bestaudio/best"},
            {"name": "📺 4K (2160p)", "value": "bestvideo[height<=2160]+bestaudio/best[height<=2160]"},
            {"name": "🖥️ 2K (1440p)", "value": "bestvideo[height<=1440]+bestaudio/best[height<=1440]"},
            {"name": "📀 Full HD (1080p)", "value": "bestvideo[height<=1080]+bestaudio/best[height<=1080]"},
            {"name": "💿 HD (720p)", "value": "bestvideo[height<=720]+bestaudio/best[height<=720]"},
            {"name": "📼 SD (480p)", "value": "bestvideo[height<=480]+bestaudio/best[height<=480]"},
            {"name": "📱 Low (360p)", "value": "bestvideo[height<=360]+bestaudio/best[height<=360]"},
        ]
    else: # Audio
        return [
            {"name": "🎧 Best Quality (MP3)", "value": "mp3"},
            {"name": "🎼 M4A (AAC)", "value": "m4a"},
            {"name": "🎹 FLAC (Lossless)", "value": "flac"},
            {"name": "🔉 WAV", "value": "wav"},
        ]

def main():
    while True:
        clear_screen()
        print_header()

        # 1. Input URL
        url = questionary.text(
            "🔗 Masukkan URL YouTube (atau tekan Enter untuk keluar):",
            validate=lambda text: True if len(text) > 0 or text == "" else "URL tidak boleh kosong"
        ).ask()
        if not url:
            break

        # 2. Get Metadata
        with console.status("[bold green]Sedang mengambil metadata...[/bold green]", spinner="dots"):
            info, error = handler.get_video_info(url)

        if error:
            console.print(f"[bold red]Gagal mengambil info: {error}[/bold red]")
            if not questionary.confirm("Coba lagi?").ask():
                break
            continue

        # 3. Tampilkan Info
        is_playlist = info.get('_type') == 'playlist'
        
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold cyan")
        table.add_column("Value")
        
        if is_playlist:
            table.add_row("Tipe", "Playlist")
            table.add_row("Judul", info.get('title', 'N/A'))
            table.add_row("Uploader", info.get('uploader', 'N/A'))
            count = info.get('playlist_count')
            if count is None and 'entries' in info:
                # Try to estimate if possible, or just say 'Unknown'
                try:
                    count = len(info['entries'])
                except:
                    count = "Unknown"
            table.add_row("Jumlah Video", str(count))
        else:
            table.add_row("Judul", info.get('title', 'N/A'))
            table.add_row("Channel", info.get('uploader', 'N/A'))
            table.add_row("Durasi", format_seconds(info.get('duration')))
            table.add_row("Views", f"{info.get('view_count', 0):,}")
        
        console.print(Panel(table, title="Video/Playlist Info", border_style="blue", expand=False))
        console.print("\n")

        # 4. Pilih Tipe Output
        type_choice = questionary.select(
            "Pilih tipe download:",
            choices=["🎥 Video", "🎵 Audio", "🔙 Kembali"]
        ).ask()

        if not type_choice or "Kembali" in type_choice: 
            continue
            
        # Clean type choice for logic (remove emoji)
        clean_type = "Video" if "Video" in type_choice else "Audio"

        # 5. Pilih Kualitas
        quality_opts = get_quality_options(clean_type)
        # Tambahkan opsi kembali
        quality_opts.append({"name": "🔙 Kembali", "value": "back"})

        quality_choice = questionary.select(
            f"Pilih kualitas {clean_type}:",
            choices=[q['name'] for q in quality_opts]
        ).ask()
        
        if not quality_choice or "Kembali" in quality_choice: 
            continue

        # Map choice name back to value
        selected_format_str = next(q['value'] for q in quality_opts if q['name'] == quality_choice)

        if selected_format_str == "back": continue

        # Siapkan opsi download
        dl_options = {}
        
        if is_playlist:
            # Use playlist title for folder
            playlist_title = info.get('title', 'Playlist')
            # Simple sanitization
            safe_title = "".join(x for x in playlist_title if x.isalnum() or x in " -_").strip()
            dl_options['outtmpl'] = os.path.join('downloads', safe_title, '%(title)s [%(id)s]', '%(title)s [%(id)s].%(ext)s')
        
        if clean_type == 'Video':
            dl_options['format'] = selected_format_str
            # Kita ingin memastikan video digabung menjadi container umum seperti mp4 atau mkv jika perlu
            dl_options['merge_output_format'] = 'mp4'
        else:
            # Audio extraction options
            dl_options['format'] = 'bestaudio/best'
            dl_options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': selected_format_str,
                'preferredquality': '192',
            }]

        # 6. Download dengan Progress Bar
        console.print(f"\n[bold green]Mulai mendownload: {clean_type} - {quality_choice}[/bold green]")
        
        # Setup Rich Progress Bar
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
            console=console
        )

        task_id = progress.add_task("Downloading...", total=None)

        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    total = d.get('total_bytes') or d.get('total_bytes_estimate')
                    downloaded = d.get('downloaded_bytes', 0)
                    
                    # Try to get title info
                    info_dict = d.get('info_dict', {})
                    title = info_dict.get('title', '')
                    if not title and 'filename' in d:
                        title = os.path.basename(d['filename'])
                    
                    # Shorten title
                    display_title = (title[:30] + '...') if len(title) > 30 else title
                    
                    # Playlist info
                    p_index = info_dict.get('playlist_index')
                    p_count = info_dict.get('playlist_count')
                    
                    if p_index and p_count:
                        desc = f"[cyan][{p_index}/{p_count}] {display_title}[/cyan]"
                    else:
                        desc = f"[cyan]{display_title}[/cyan]" if display_title else "Downloading..."

                    if total:
                        progress.update(task_id, total=total, completed=downloaded, description=desc)
                except Exception as e:
                    pass
            elif d['status'] == 'finished':
                progress.update(task_id, description="[bold green]Processing...[/bold green]")

        with progress:
            success, msg = handler.download(url, dl_options, progress_hook)

        if success:
            console.print(Panel(f"[bold green]{msg}[/bold green]\nFile tersimpan di folder 'downloads'", title="Sukses", border_style="green"))
        else:
            console.print(Panel(f"[bold red]Error:[/bold red] {msg}", title="Gagal", border_style="red"))

        # Tanya user apakah ingin lanjut
        console.print("\n")
        if not questionary.confirm("Download video lain?").ask():
            console.print("[bold cyan]Terima kasih telah menggunakan YouTube Downloader CLI![/bold cyan]")
            break

if __name__ == "__main__":
    try:
        args = parse_arguments()
        
        # Tentukan mode: interactive atau non-interactive
        if args.url and not args.interactive:
            # Mode non-interactive jika URL diberikan
            run_non_interactive(args)
        else:
            # Mode interactive (default)
            main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Operasi dibatalkan oleh pengguna.[/bold yellow]")
        sys.exit(0)
