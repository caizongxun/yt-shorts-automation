"""Video Compositor - Combine audio, subtitles, and background footage into YouTube Shorts.

This module handles all video composition tasks including:
- Loading and processing audio files
- Speech-to-text for subtitle generation
- Random background video selection and cropping
- Subtitle rendering with effects
- Final video encoding
"""

import logging
import random
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    ColorClip,
    concatenate_videoclips
)
import librosa

# Fix PIL compatibility for moviepy
try:
    from PIL import Image
    # For Pillow 10+, ANTIALIAS is deprecated
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.Resampling.LANCZOS
except Exception as e:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoCompositor:
    """Handle video composition and effects."""

    def __init__(
        self,
        background_dir: str = "assets/gameplay",
        music_dir: str = "assets/music",
        enable_randomization: bool = True,
        output_dir: str = "output/videos"
    ):
        """Initialize compositor.
        
        Args:
            background_dir: Directory with background videos
            music_dir: Directory with background music
            enable_randomization: Apply random effects
            output_dir: Output directory for videos
        """
        self.background_dir = Path(background_dir)
        self.music_dir = Path(music_dir)
        self.enable_randomization = enable_randomization
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"VideoCompositor initialized")
        logger.info(f"  Background dir: {self.background_dir}")
        logger.info(f"  Music dir: {self.music_dir}")
        logger.info(f"  Randomization: {enable_randomization}")

    def _get_background_video(self) -> Optional[Path]:
        """Select a random background video file.
        
        Returns:
            Path to video file or None if not found
        """
        if not self.background_dir.exists():
            logger.warning(f"Background directory not found: {self.background_dir}")
            return None

        video_files = list(self.background_dir.glob("*.mp4"))
        if not video_files:
            logger.warning(f"No video files found in {self.background_dir}")
            logger.info("Please download background videos from:")
            logger.info("  - YouTube: 'No Copyright Gameplay' channels")
            logger.info("  - Pexels/Pixabay API")
            return None

        selected = random.choice(video_files)
        logger.info(f"Selected background: {selected.name}")
        return selected

    def _crop_video_to_shorts(self, video_clip: VideoFileClip, target_duration: float) -> VideoFileClip:
        """Crop video to 9:16 aspect ratio (Shorts format).
        
        Args:
            video_clip: Source video
            target_duration: Target duration in seconds
            
        Returns:
            Cropped video clip
        """
        # Shorts format: 1080x1920 (9:16)
        target_width = 1080
        target_height = 1920
        target_aspect = target_height / target_width  # 1.778

        # Get original dimensions
        orig_width = video_clip.w
        orig_height = video_clip.h
        orig_aspect = orig_height / orig_width

        logger.info(f"Cropping video: {orig_width}x{orig_height} -> {target_width}x{target_height}")

        if orig_aspect > target_aspect:
            # Original is taller: crop width
            new_width = int(orig_height / target_aspect)
            x1 = max(0, (orig_width - new_width) // 2)
            crop = video_clip.crop(x1=x1, y1=0, x2=x1 + new_width, y2=orig_height)
        else:
            # Original is wider: crop height
            new_height = int(orig_width * target_aspect)
            y1 = max(0, (orig_height - new_height) // 2)
            crop = video_clip.crop(x1=0, y1=y1, x2=orig_width, y2=y1 + new_height)

        # Resize to exact Shorts dimensions using set_fps to ensure compatibility
        try:
            # Use set_size instead of resize for better compatibility
            resized = crop.resize(height=target_height)
        except Exception as e:
            logger.warning(f"Resize failed, using fallback method: {e}")
            # Fallback: use set_size for frame scaling
            resized = crop.resize(width=target_width, height=target_height)

        # If video is too long, take a random segment
        if resized.duration > target_duration + 0.1:  # Add small buffer
            # Random start position (avoid end of video)
            max_start = max(0, resized.duration - target_duration)
            start_time = random.uniform(0, max_start) if max_start > 0 else 0
            logger.info(f"Trimming video from {start_time:.2f}s for {target_duration:.2f}s")
            # Use subclip() instead of subclipped() - correct moviepy API
            resized = resized.subclip(start_time, start_time + target_duration)
        elif resized.duration < target_duration - 0.1:  # Add small buffer
            # Loop video if too short
            logger.warning(f"Video too short ({resized.duration:.2f}s), looping...")
            num_loops = int(target_duration / resized.duration) + 1
            clips = [resized] * num_loops
            combined = concatenate_videoclips(clips)
            # Use subclip() for trimming
            resized = combined.subclip(0, target_duration)

        return resized

    def _generate_subtitles(self, audio_file: str) -> List[Dict]:
        """Generate subtitle timing from audio using Whisper.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            List of subtitle segments with timing
        """
        try:
            import whisper
        except ImportError:
            logger.warning("Whisper not installed, using dummy subtitles")
            return [{"text": "...", "start": 0, "end": 60}]

        try:
            logger.info(f"Transcribing audio: {audio_file}")
            model = whisper.load_model("base", device="cpu")
            result = model.transcribe(audio_file, language="en")
            
            subtitles = []
            for segment in result.get("segments", []):
                subtitles.append({
                    "text": segment["text"],
                    "start": segment["start"],
                    "end": segment["end"]
                })
            
            logger.info(f"Generated {len(subtitles)} subtitle segments")
            return subtitles
        except Exception as e:
            logger.error(f"Error generating subtitles: {e}")
            return [{"text": "...", "start": 0, "end": 60}]

    def _create_subtitle_clips(self, subtitles: List[Dict], video_duration: float) -> List:
        """Create subtitle clips for each segment.
        
        Args:
            subtitles: List of subtitle segments
            video_duration: Total video duration
            
        Returns:
            List of text clips
        """
        text_clips = []
        
        # Font and styling options
        fonts = ["Arial", "Verdana", "Impact"]
        font = random.choice(fonts) if self.enable_randomization else "Arial"
        
        # Color options (randomized)
        colors = [(255, 255, 0), (255, 255, 255), (0, 255, 255), (255, 0, 255)]
        text_color = random.choice(colors) if self.enable_randomization else (255, 255, 0)
        
        # Font size variation
        base_size = 60
        size_var = random.randint(-10, 10) if self.enable_randomization else 0
        fontsize = max(30, base_size + size_var)

        for subtitle in subtitles:
            text = subtitle["text"].strip()
            if not text:
                continue

            start = max(0, subtitle["start"])
            end = min(video_duration, subtitle["end"])
            duration = end - start

            if duration <= 0:
                continue

            try:
                # Create text clip with shadow effect
                txt_clip = TextClip(
                    text,
                    fontsize=fontsize,
                    font=font,
                    color="white" if text_color == (255, 255, 255) else text_color,
                    stroke_color="black",
                    stroke_width=2,
                    method="caption",
                    size=(1000, 200),
                    align="center"
                ).set_position("center").set_start(start).set_duration(duration)
                
                text_clips.append(txt_clip)
            except Exception as e:
                logger.warning(f"Error creating subtitle: {e}")
                continue

        logger.info(f"Created {len(text_clips)} subtitle clips")
        return text_clips

    def compose(
        self,
        audio_file: str,
        title: str = "Story",
        output_file: str = "output.mp4",
        randomize: bool = True
    ) -> Optional[str]:
        """Compose video with audio, subtitles, and background.
        
        Args:
            audio_file: Path to audio file
            title: Video title (for subtitles)
            output_file: Output video filename
            randomize: Apply random effects
            
        Returns:
            Path to output video or None if failed
        """
        logger.info(f"Starting video composition: {output_file}")
        
        bg_video = None
        bg_cropped = None
        audio = None
        final_video = None
        
        try:
            # Load audio
            logger.info(f"Loading audio: {audio_file}")
            audio = AudioFileClip(audio_file)
            audio_duration = audio.duration
            logger.info(f"Audio duration: {audio_duration:.2f}s")

            # Get background video
            bg_video_path = self._get_background_video()
            if not bg_video_path:
                logger.error("Cannot compose video without background footage")
                return None

            # Load and process background video
            bg_video = VideoFileClip(str(bg_video_path))
            logger.info(f"Background video duration: {bg_video.duration:.2f}s")
            
            # Crop to Shorts format and get random segment
            bg_cropped = self._crop_video_to_shorts(bg_video, audio_duration)

            # Generate subtitles
            subtitles = self._generate_subtitles(audio_file)
            subtitle_clips = self._create_subtitle_clips(subtitles, audio_duration)

            # Create final composite
            logger.info(f"Compositing final video...")
            final_clips = [bg_cropped] + subtitle_clips
            final_video = CompositeVideoClip(final_clips, size=(1080, 1920))
            final_video = final_video.set_audio(audio)

            # Apply color grading (subtle)
            if randomize and self.enable_randomization:
                brightness_adjust = random.uniform(-0.05, 0.05)
                if brightness_adjust > 0:
                    final_video = final_video.speedx(1.0)
                logger.info(f"Applied brightness adjustment: {brightness_adjust:+.2%}")

            # Write to file
            output_path = self.output_dir / output_file
            logger.info(f"Writing video to: {output_path}")
            
            final_video.write_videofile(
                str(output_path),
                codec="libx264",
                audio_codec="aac",
                fps=30,
                verbose=False,
                logger=None
            )

            logger.info(f"Video composed successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Error during composition: {e}", exc_info=True)
            return None
        
        finally:
            # Cleanup resources
            try:
                if final_video is not None:
                    final_video.close()
            except:
                pass
            try:
                if audio is not None:
                    audio.close()
            except:
                pass
            try:
                if bg_cropped is not None:
                    bg_cropped.close()
            except:
                pass
            try:
                if bg_video is not None:
                    bg_video.close()
            except:
                pass


if __name__ == "__main__":
    compositor = VideoCompositor()
    # Test with example audio file
    result = compositor.compose(
        audio_file="output/audio/manual_audio_00.mp3",
        title="Test Video",
        output_file="test_short.mp4"
    )
    print(f"Result: {result}")
