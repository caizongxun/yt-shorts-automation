"""YouTube Shorts automation pipeline package"""

__version__ = "1.0.0"
__author__ = "caizongxun"

from .content_scraper import ContentScraper
from .audio_generator import AudioGenerator
from .video_compositor import VideoCompositor
from .youtube_uploader import YouTubeUploader

__all__ = [
    "ContentScraper",
    "AudioGenerator",
    "VideoCompositor",
    "YouTubeUploader",
]
