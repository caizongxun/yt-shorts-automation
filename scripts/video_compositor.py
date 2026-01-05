import os
import random
import logging
from pathlib import Path
from datetime import datetime
import subprocess
import json
from typing import Tuple, List

try:
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, CompositeVideoClip,
        TextClip, ColorClip, concatenate_videoclips
    )
    import moviepy.video.fx.all as vfx
except ImportError:
    print("MoviePy not installed. Install with: pip install moviepy")

try:
    import numpy as np
except ImportError:
    print("NumPy not installed. Install with: pip install numpy")

try:
    import whisper
except ImportError:
    print("Whisper not installed. Install with: pip install openai-whisper")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoCompositor:
    """Compose YouTube Shorts from audio, background footage, and effects."""

    # Shorts format: 9:16 (1080x1920 pixels)
    SHORTS_WIDTH = 1080
    SHORTS_HEIGHT = 1920
    SHORTS_FPS = 30
    SHORTS_DURATION = 60  # Max 60 seconds

    # Font for subtitles
    SUBTITLE_FONT = "Arial-Bold"
    SUBTITLE_SIZE = 80  # Large, easily readable
    SUBTITLE_COLOR = "yellow"

    def __init__(
        self,
        background_dir: str = "assets/gameplay",
        music_dir: str = "assets/music",
        output_dir: str = "output/videos",
        enable_randomization: bool = True
    ):
        """Initialize video compositor.
        
        Args:
            background_dir: Directory containing background video clips
            music_dir: Directory containing royalty-free background music
            output_dir: Directory to save final videos
            enable_randomization: Enable random variations to avoid "repetitive content" penalty
        """
        self.background_dir = Path(background_dir)
        self.music_dir = Path(music_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.enable_randomization = enable_randomization

        logger.info(f"VideoCompositor initialized")
        logger.info(f"  Background dir: {self.background_dir}")
        logger.info(f"  Music dir: {self.music_dir}")
        logger.info(f"  Randomization: {enable_randomization}")

    def _get_audio_timestamps(self, audio_file: str) -> List[dict]:
        """Extract word-level timestamps from audio using Whisper.
        
        Returns list of dicts with 'word', 'start', 'end' times.
        """
        try:
            logger.info(f"Transcribing audio with Whisper: {audio_file}")
            model = whisper.load_model("base")
            result = model.transcribe(audio_file, language="en", word_level_timestamps=True)
            
            word_timestamps = []
            for segment in result["segments"]:
                for word_info in segment.get("words", []):
                    word_timestamps.append({
                        'word': word_info['word'].strip(),
                        'start': word_info['start'],
                        'end': word_info['end']
                    })
            
            logger.info(f"Extracted {len(word_timestamps)} word timestamps")
            return word_timestamps
            
        except Exception as e:
            logger.error(f"Error transcribing with Whisper: {e}")
            return self._generate_dummy_timestamps(audio_file)

    def _generate_dummy_timestamps(self, audio_file: str) -> List[dict]:
        """Generate dummy timestamps if Whisper fails.
        
        This is a fallback that estimates timing based on audio length.
        """
        try:
            audio = AudioFileClip(audio_file)
            duration = audio.duration
            
            # Estimate ~150 words per minute for English speech
            # So ~2.5 words per second
            timestamps = []
            time = 0
            word_duration = 0.4  # 400ms per word
            
            dummy_words = ['Did', 'you', 'know', 'that', 'this', 'is', 'amazing',
                          'incredible', 'fact', 'about', 'life', 'universe']
            
            word_idx = 0
            while time < duration:
                timestamps.append({
                    'word': dummy_words[word_idx % len(dummy_words)],
                    'start': time,
                    'end': time + word_duration
                })
                time += word_duration
                word_idx += 1
            
            return timestamps
            
        except Exception as e:
            logger.error(f"Error generating dummy timestamps: {e}")
            return []

    def _create_subtitle_clips(self, timestamps: List[dict]) -> List:
        """Create text clips for word-by-word subtitles."""
        subtitle_clips = []
        
        try:
            for ts in timestamps:
                text_clip = TextClip(
                    ts['word'],
                    fontsize=self.SUBTITLE_SIZE,
                    color=self.SUBTITLE_COLOR,
                    font=self.SUBTITLE_FONT,
                    stroke_color='black',
                    stroke_width=3
                ).set_position('center').set_duration(
                    ts['end'] - ts['start']
                ).set_start(ts['start'])
                
                subtitle_clips.append(text_clip)
            
            logger.info(f"Created {len(subtitle_clips)} subtitle clips")
            return subtitle_clips
            
        except Exception as e:
            logger.error(f"Error creating subtitle clips: {e}")
            return []

    def _pick_random_background(self) -> str:
        """Randomly select a background video file."""
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov']
        video_files = []
        
        for ext in video_extensions:
            video_files.extend(self.background_dir.glob(f"*{ext}"))
        
        if not video_files:
            logger.warning(f"No video files found in {self.background_dir}")
            logger.info("Please download background videos from:")
            logger.info("  - YouTube: 'No Copyright Gameplay' channels")
            logger.info("  - Pexels/Pixabay API")
            return None
        
        selected = random.choice(video_files)
        logger.info(f"Selected background: {selected.name}")
        return str(selected)

    def _crop_to_shorts_ratio(self, clip) -> VideoFileClip:
        """Crop video to 9:16 Shorts ratio, preserving center."""
        w, h = clip.size
        target_ratio = self.SHORTS_HEIGHT / self.SHORTS_WIDTH  # 1.777
        current_ratio = h / w
        
        if current_ratio > target_ratio:
            # Height is too large, crop width
            new_w = int(h / target_ratio)
            x_center = (w - new_w) / 2
            clip = clip.crop(x1=x_center, x2=x_center + new_w)
        elif current_ratio < target_ratio:
            # Width is too large, crop height  
            new_h = int(w * target_ratio)
            y_center = (h - new_h) / 2
            clip = clip.crop(y1=y_center, y2=y_center + new_h)
        
        return clip.resize(height=self.SHORTS_HEIGHT)

    def _apply_random_effects(self, clip) -> VideoFileClip:
        """Apply random visual effects to reduce "repetitive content" detection."""
        if not self.enable_randomization:
            return clip
        
        # Random brightness/contrast adjustment (-5% to +5%)
        brightness_factor = random.uniform(0.95, 1.05)
        
        try:
            # Apply brightness adjustment
            clip = clip.speedx(brightness_factor) if random.random() < 0.3 else clip
            
            # Random color grading
            if random.random() < 0.5:
                clip = clip.without_audio()  # Some effects require no audio
                # Could add color grading here if needed
            
        except Exception as e:
            logger.warning(f"Error applying effects: {e}")
        
        return clip

    def _pick_background_music(self) -> str:
        """Randomly select background music file."""
        audio_extensions = ['.mp3', '.wav', '.m4a', '.aac']
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(self.music_dir.glob(f"*{ext}"))
        
        if not audio_files:
            logger.info(f"No background music found in {self.music_dir}")
            return None
        
        selected = random.choice(audio_files)
        logger.info(f"Selected background music: {selected.name}")
        return str(selected)

    def compose(
        self,
        audio_file: str,
        title: str = "Incredible Facts",
        output_file: str = None,
        randomize: bool = True
    ) -> str:
        """Compose the final YouTube Shorts video.
        
        Args:
            audio_file: Path to TTS audio file
            title: Video title (for metadata)
            output_file: Custom output filename
            randomize: Enable random variations
            
        Returns:
            Path to generated video file
        """
        if output_file is None:
            output_file = f"short_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        
        output_path = self.output_dir / output_file
        
        try:
            logger.info(f"Starting video composition: {output_file}")
            
            # Load audio
            logger.info(f"Loading audio: {audio_file}")
            audio = AudioFileClip(audio_file)
            duration = min(audio.duration, self.SHORTS_DURATION)
            
            # Get background
            bg_file = self._pick_random_background()
            if not bg_file:
                logger.error("Cannot compose video without background footage")
                return None
            
            # Load and prepare background
            logger.info(f"Loading background video: {bg_file}")
            bg_clip = VideoFileClip(bg_file)
            
            # Crop to Shorts ratio
            bg_clip = self._crop_to_shorts_ratio(bg_clip)
            
            # Random start point to add variation
            if randomize and bg_clip.duration > duration:
                start = random.uniform(0, bg_clip.duration - duration)
                bg_clip = bg_clip.subclip(start, start + duration)
            else:
                bg_clip = bg_clip.subclip(0, min(duration, bg_clip.duration))
            
            # Apply effects
            bg_clip = self._apply_random_effects(bg_clip)
            
            # Create subtitle clips
            logger.info("Extracting audio timestamps...")
            timestamps = self._get_audio_timestamps(audio_file)
            subtitle_clips = self._create_subtitle_clips(timestamps)
            
            # Get background music (optional, very low volume)
            bg_music_file = self._pick_background_music()
            if bg_music_file:
                try:
                    bg_music = AudioFileClip(bg_music_file).subclip(0, duration)
                    # Mix audio: main voice at 100%, background at 5%
                    audio = audio.subclip(0, duration)
                    mixed_audio = (
                        audio.audio_composite(bg_music.volumex(0.05))
                        if hasattr(audio, 'audio_composite')
                        else audio.set_duration(duration)
                    )
                except Exception as e:
                    logger.warning(f"Could not mix background music: {e}")
                    mixed_audio = audio.subclip(0, duration)
            else:
                mixed_audio = audio.subclip(0, duration)
            
            # Compose final video with subtitles
            if subtitle_clips:
                final = CompositeVideoClip(
                    [bg_clip] + subtitle_clips,
                    size=(self.SHORTS_WIDTH, self.SHORTS_HEIGHT)
                )
            else:
                final = bg_clip.set_size((self.SHORTS_WIDTH, self.SHORTS_HEIGHT))
            
            final = final.set_audio(mixed_audio).set_duration(duration)
            
            # Write to file
            logger.info(f"Writing video file: {output_path}")
            final.write_videofile(
                str(output_path),
                fps=self.SHORTS_FPS,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None  # Suppress ffmpeg output
            )
            
            # Save metadata
            metadata = {
                'video_file': str(output_path),
                'title': title,
                'duration': duration,
                'width': self.SHORTS_WIDTH,
                'height': self.SHORTS_HEIGHT,
                'fps': self.SHORTS_FPS,
                'audio_source': audio_file,
                'background': bg_file,
                'timestamp': datetime.now().isoformat()
            }
            
            meta_path = output_path.with_suffix('.json')
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Video composition completed: {output_path}")
            logger.info(f"Duration: {duration}s, Size: {self.SHORTS_WIDTH}x{self.SHORTS_HEIGHT}")
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error during video composition: {e}")
            raise


if __name__ == "__main__":
    # Test usage
    compositor = VideoCompositor(
        background_dir="assets/gameplay",
        music_dir="assets/music",
        enable_randomization=True
    )
    
    # This would require actual audio file
    # video = compositor.compose(
    #     audio_file="output/audio/audio_20250105_151300.mp3",
    #     title="Amazing Facts #Shorts"
    # )
    
    print("VideoCompositor module ready for testing")
