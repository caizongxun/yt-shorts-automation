#!/usr/bin/env python3
"""Simplified Daily Pipeline for Manual Content.

Use this script when you provide stories manually via TXT files.
No Reddit API or LLM needed - just your own content!

Workflow:
1. Create story files in content/ directory
2. Run this script
3. It generates 3 YouTube Shorts automatically
4. Profits!

Usage:
    python scripts/manual_daily_pipeline.py --count 3 --voice en-male-excited
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime
import sys
import os

# Auto-create logs directory
log_dir = Path("logs")
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"manual_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manual_content_provider import ManualContentProvider
from audio_generator import AudioGenerator
from video_compositor import VideoCompositor

# Available voice options
AVAILABLE_VOICES = {
    'en-male-excited': 'High-energy, upbeat male voice',
    'en-male-calm': 'Deep, calm male voice',
    'en-male-casual': 'Warm, friendly male voice',
    'en-male-friendly': 'Bright, engaging voice',
    'en-female-natural': 'Natural, friendly female voice',
    'en-female-warm': 'Warm and engaging female voice',
    'en-female-professional': 'Professional, clear female voice',
    # Legacy options
    'en-male': 'Default male voice (mapped to en-male-calm)',
    'en-female': 'Default female voice (mapped to en-female-natural)',
    'en-casual': 'Casual voice (mapped to en-male-casual)',
    'en-male-old': 'Older male voice (mapped to en-male-calm)',
}


class ManualDailyPipeline:
    """Orchestrate video generation from manually-provided stories."""

    def __init__(
        self,
        story_count: int = 3,
        voice: str = 'en-male-excited',
        randomize_videos: bool = True,
        upload: bool = False
    ):
        """Initialize pipeline.
        
        Args:
            story_count: Number of stories to process
            voice: TTS voice to use
            randomize_videos: Apply random effects
            upload: Upload to YouTube
        """
        self.story_count = story_count
        self.voice = voice
        self.randomize_videos = randomize_videos
        self.upload = upload

        self.content_provider = ManualContentProvider(content_dir="content")
        # Use higher rate for excited voices, normal for calm
        rate = '+15%' if 'excited' in voice else '+10%'
        self.audio_gen = AudioGenerator(voice=voice, rate=rate)
        self.compositor = VideoCompositor(
            background_dir="assets/gameplay",
            music_dir="assets/music",
            enable_randomization=randomize_videos
        )

        if self.upload:
            try:
                from youtube_uploader import UploadScheduler
                self.uploader = UploadScheduler()
            except ImportError:
                logger.warning("YouTube uploader not available, upload disabled")
                self.upload = False

        logger.info(f"Manual Daily Pipeline initialized:")
        logger.info(f"  Story count: {story_count}")
        logger.info(f"  Voice: {voice} ({AVAILABLE_VOICES.get(voice, 'custom')})")
        logger.info(f"  Speech rate: {rate}")
        logger.info(f"  Randomization: {randomize_videos}")
        logger.info(f"  Upload: {upload}")

    def run(self) -> bool:
        """Execute the full pipeline.
        
        Returns:
            True if successful, False if failed
        """
        logger.info("=" * 60)
        logger.info(f"STARTING MANUAL DAILY PIPELINE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        try:
            # Step 1: Fetch manual stories
            logger.info("\n[STEP 1/4] Loading stories from content/ directory...")
            stories = self.content_provider.fetch_stories(count=self.story_count)

            if not stories:
                logger.error("[ERROR] No stories found!")
                logger.info("\n[INFO] How to add stories:")
                logger.info("   1. Create a file: content/story_1.txt")
                logger.info("   2. Format:")
                logger.info("      Title: Your Story Title")
                logger.info("      ")
                logger.info("      Your story content here...")
                logger.info("   3. Run this script again")
                logger.info("\n[TIP] Run this to create example files:")
                logger.info("   python scripts/manual_daily_pipeline.py --create-examples")
                return False

            logger.info(f"[SUCCESS] Loaded {len(stories)} stories")

            # Step 2: Generate audio
            logger.info("\n[STEP 2/4] Generating audio files...")
            audio_files = []

            for i, story in enumerate(stories):
                logger.info(f"  Generating audio {i+1}/{len(stories)}: {story['title']}")
                try:
                    script = self.content_provider.prepare_scripts([story])[0]
                    audio_file = self.audio_gen.generate(
                        script,
                        f"manual_audio_{i:02d}.mp3"
                    )
                    audio_files.append(audio_file)
                    logger.info(f"    [OK] Generated: {Path(audio_file).name}")
                except Exception as e:
                    logger.error(f"    [SKIP] Failed: {e}")
                    continue

            if not audio_files:
                logger.error("[ERROR] No audio files generated")
                return False

            logger.info(f"[SUCCESS] Generated {len(audio_files)} audio files")

            # Step 3: Compose videos
            logger.info("\n[STEP 3/4] Composing videos...")
            video_files = []
            metadata = []

            for i, (audio_file, story) in enumerate(zip(audio_files, stories)):
                logger.info(f"  Composing video {i+1}/{len(audio_files)}: {story['title']}")
                try:
                    title = story.get('title', f'Story #{i+1}')
                    video_file = self.compositor.compose(
                        audio_file=audio_file,
                        title=title,
                        output_file=f"manual_short_{i:02d}.mp4",
                        randomize=self.randomize_videos
                    )
                    video_files.append(video_file)

                    metadata.append({
                        'title': f"{title} #Shorts",
                        'description': f"{story.get('content', '')[:100]}...\n\n#Shorts #Facts #Viral",
                        'tags': ['Shorts', 'Facts', 'Viral', 'Amazing']
                    })
                    logger.info(f"    [OK] Composed: {Path(video_file).name}")
                except Exception as e:
                    logger.error(f"    [SKIP] Failed: {e}")
                    continue

            if not video_files:
                logger.error("[ERROR] No videos composed")
                return False

            logger.info(f"[SUCCESS] Composed {len(video_files)} videos")

            # Step 4: Schedule uploads
            logger.info("\n[STEP 4/4] Scheduling uploads...")
            if self.upload:
                try:
                    self.uploader.queue_uploads(video_files, metadata)
                    logger.info(f"[SUCCESS] Scheduled {len(video_files)} videos for upload")
                except Exception as e:
                    logger.error(f"[ERROR] Upload scheduling failed: {e}")
                    logger.info("   Videos are ready for manual upload")
            else:
                logger.info(f"[SUCCESS] Generated {len(video_files)} videos (upload disabled)")
                logger.info("   Videos ready in: output/videos/")

            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("[SUCCESS] PIPELINE COMPLETED SUCCESSFULLY")
            logger.info(f"   Generated videos: {len(video_files)}")
            logger.info(f"   Audio files: {len(audio_files)}")
            logger.info(f"   Output directory: {self.compositor.output_dir}")
            logger.info(f"   Process time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"\n[ERROR] Pipeline failed: {e}", exc_info=True)
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manual YouTube Shorts generation pipeline (no Reddit/LLM needed)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Available voices:
  Excited (best for Shorts):  en-male-excited, en-female-warm
  Calm & storytelling:        en-male-calm, en-female-professional
  Casual & friendly:          en-male-casual, en-female-natural
  Legacy options:             en-male, en-female, en-casual, en-male-old

Examples:
  python scripts/manual_daily_pipeline.py --count 3 --voice en-male-excited
  python scripts/manual_daily_pipeline.py --count 5 --voice en-female-warm
  python scripts/manual_daily_pipeline.py --count 2 --voice en-male-calm
        """
    )
    parser.add_argument(
        '--count',
        type=int,
        default=3,
        help='Number of shorts to generate (default: 3)'
    )
    parser.add_argument(
        '--voice',
        type=str,
        default='en-male-excited',
        choices=list(AVAILABLE_VOICES.keys()),
        help='TTS voice to use (default: en-male-excited)'
    )
    parser.add_argument(
        '--no-randomize',
        action='store_true',
        help='Disable random effects'
    )
    parser.add_argument(
        '--upload',
        action='store_true',
        help='Enable YouTube upload (requires manual login first)'
    )
    parser.add_argument(
        '--create-examples',
        action='store_true',
        help='Create example story files and exit'
    )

    args = parser.parse_args()

    # Create example files if requested
    if args.create_examples:
        logger.info("Creating example story files...")
        provider = ManualContentProvider()
        provider.create_example_files()
        logger.info("[SUCCESS] Example files created in content/ directory")
        logger.info("   You can now edit them or create your own!")
        return 0

    pipeline = ManualDailyPipeline(
        story_count=args.count,
        voice=args.voice,
        randomize_videos=not args.no_randomize,
        upload=args.upload
    )

    success = pipeline.run()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
