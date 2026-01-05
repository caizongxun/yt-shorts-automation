#!/usr/bin/env python3
"""Easy Video Downloader - Paste URL in PyCharm and download 720p videos.

Supports:
- YouTube (youtube-dl alternative: yt-dlp)
- Pexels
- Pixabay
- Any video URL

Usage:
    python tools/download_background.py
    
Then enter:
    [URL]: https://www.pexels.com/video/123456/
    
Or:
    python tools/download_background.py "https://youtube.com/watch?v=..."
"""

import os
import sys
import logging
from pathlib import Path
import subprocess
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoDownloader:
    """Download videos from various sources to 720p MP4."""

    def __init__(self, output_dir: str = "assets/gameplay"):
        """Initialize downloader.
        
        Args:
            output_dir: Output directory for downloaded videos
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {self.output_dir}")

    def _check_yt_dlp(self) -> bool:
        """Check if yt-dlp is installed.
        
        Returns:
            True if installed, False otherwise
        """
        try:
            import yt_dlp
            logger.info(f"yt-dlp version: {yt_dlp.__version__}")
            return True
        except ImportError:
            logger.error("yt-dlp not installed!")
            logger.info("Install with: pip install yt-dlp")
            return False

    def download(self, url: str, quality: str = "720") -> Optional[Path]:
        """Download video from URL.
        
        Args:
            url: Video URL (YouTube, Pexels, Pixabay, etc.)
            quality: Video quality (default: 720)
            
        Returns:
            Path to downloaded file or None if failed
        """
        if not self._check_yt_dlp():
            return None

        # Validate URL
        if not url.startswith(("http://", "https://")):
            logger.error("Invalid URL. Must start with http:// or https://")
            return None

        logger.info(f"[START] Downloading video...")
        logger.info(f"  URL: {url}")
        logger.info(f"  Quality: {quality}p")
        logger.info(f"  Format: MP4")
        logger.info(f"  Output: {self.output_dir}")
        logger.info("")

        try:
            import yt_dlp

            # yt-dlp options
            ydl_opts = {
                'format': f'best[height<=720]/best',  # 720p or best available
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'progress_hooks': [self._progress_hook],
                'socket_timeout': 30,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info("[PROCESSING] Extracting video info...")
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                logger.info(f"  Title: {info.get('title', 'Unknown')}")
                logger.info(f"  Duration: {info.get('duration', 'N/A')} seconds")
                logger.info("")

                logger.info("[DOWNLOADING] Starting download...")
                ydl.download([url])

            output_file = Path(filename)
            if output_file.exists():
                logger.info("")
                logger.info("[SUCCESS] Download completed!")
                logger.info(f"  File: {output_file}")
                logger.info(f"  Size: {output_file.stat().st_size / 1024 / 1024:.2f} MB")
                logger.info("")
                logger.info("You can now run:")
                logger.info(f"  python scripts/manual_daily_pipeline.py --count 3")
                return output_file
            else:
                logger.error("[ERROR] File not found after download")
                return None

        except Exception as e:
            logger.error(f"[ERROR] Download failed: {e}")
            logger.info("")
            logger.info("Troubleshooting:")
            logger.info("  1. Check your internet connection")
            logger.info("  2. Make sure the URL is valid")
            logger.info("  3. Try a different URL")
            logger.info("  4. Update yt-dlp: pip install --upgrade yt-dlp")
            return None

    def _progress_hook(self, d):
        """Progress hook for yt-dlp."""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"\r  Progress: {percent} at {speed} ETA: {eta}", end='', flush=True)
        elif d['status'] == 'finished':
            print("\n  [OK] Download finished, now converting...")

    def interactive_mode(self):
        """Interactive download mode."""
        print("")
        print("=" * 60)
        print("YouTube/Pexels/Pixabay Video Downloader (720p)")
        print("=" * 60)
        print("")
        print("Supported sources:")
        print("  - YouTube: youtube.com/watch?v=...")
        print("  - Pexels: pexels.com/video/...")
        print("  - Pixabay: pixabay.com/videos/...")
        print("  - Any video URL")
        print("")

        while True:
            try:
                url = input("[INPUT] Paste video URL (or 'quit' to exit): ").strip()

                if url.lower() == 'quit':
                    print("")
                    print("[EXIT] Goodbye!")
                    break

                if not url:
                    print("[ERROR] URL cannot be empty")
                    continue

                quality = input("[INPUT] Quality (default 720, or enter custom): ").strip()
                if not quality:
                    quality = "720"

                result = self.download(url, quality)

                if result:
                    print("")
                    another = input("[INPUT] Download another video? (y/n): ").strip().lower()
                    if another != 'y':
                        print("")
                        print("[EXIT] All done! Your videos are in: assets/gameplay/")
                        break
                    print("")

            except KeyboardInterrupt:
                print("\n")
                print("[CANCELLED] Download cancelled by user")
                break
            except Exception as e:
                logger.error(f"[ERROR] Unexpected error: {e}")
                continue


def main():
    """Main entry point."""
    downloader = VideoDownloader(output_dir="assets/gameplay")

    # If URL provided as argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
        quality = sys.argv[2] if len(sys.argv) > 2 else "720"
        result = downloader.download(url, quality)
        return 0 if result else 1

    # Interactive mode
    downloader.interactive_mode()
    return 0


if __name__ == "__main__":
    sys.exit(main())
