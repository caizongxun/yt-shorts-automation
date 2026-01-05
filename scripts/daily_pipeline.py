#!/usr/bin/env python3
"""Daily YouTube Shorts automation pipeline.

This script orchestrates the entire process:
1. Fetch/generate content from Reddit or LLM
2. Convert to speech with Edge-TTS
3. Compose video with effects
4. Upload to YouTube with scheduling

Run this daily via cron or scheduler.
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime

from content_scraper import ContentScraper
from audio_generator import AudioGenerator
from video_compositor import VideoCompositor
from youtube_uploader import UploadScheduler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DailyPipeline:
    """Orchestrate the daily YouTube Shorts generation pipeline."""
    
    def __init__(
        self,
        content_count: int = 3,
        voice: str = 'en-male',
        randomize_videos: bool = True,
        upload: bool = False
    ):
        """Initialize pipeline.
        
        Args:
            content_count: Number of shorts to generate per day
            voice: TTS voice to use
            randomize_videos: Apply random effects to reduce pattern detection
            upload: Actually upload to YouTube (vs just generating files)
        """
        self.content_count = content_count
        self.voice = voice
        self.randomize_videos = randomize_videos
        self.upload = upload
        
        self.scraper = ContentScraper()
        self.audio_gen = AudioGenerator(voice=voice, rate='+10%')
        self.compositor = VideoCompositor(
            background_dir="assets/gameplay",
            music_dir="assets/music",
            enable_randomization=randomize_videos
        )
        
        if self.upload:
            self.uploader = UploadScheduler()
        
        logger.info(f"Daily Pipeline initialized:")
        logger.info(f"  Content count: {content_count}")
        logger.info(f"  Voice: {voice}")
        logger.info(f"  Randomization: {randomize_videos}")
        logger.info(f"  Upload mode: {upload}")
    
    def run(self) -> bool:
        """Execute the full pipeline.
        
        Returns:
            True if successful, False if any step failed
        """
        logger.info("=" * 60)
        logger.info(f"STARTING DAILY PIPELINE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        try:
            # Step 1: Fetch content
            logger.info("\n[STEP 1/4] Fetching content...")
            stories = self.scraper.fetch_stories(count=self.content_count)
            if not stories:
                logger.error("Failed to fetch stories")
                return False
            
            logger.info(f"Fetched {len(stories)} stories")
            scripts = self.scraper.prepare_scripts(stories)
            
            # Step 2: Generate audio
            logger.info("\n[STEP 2/4] Generating audio...")
            audio_files = []
            for i, script in enumerate(scripts):
                logger.info(f"Generating audio {i+1}/{len(scripts)}...")
                try:
                    audio_file = self.audio_gen.generate(script, f"audio_{i:02d}.mp3")
                    audio_files.append(audio_file)
                except Exception as e:
                    logger.error(f"Failed to generate audio {i+1}: {e}")
                    continue
            
            if not audio_files:
                logger.error("No audio files generated")
                return False
            
            logger.info(f"Generated {len(audio_files)} audio files")
            
            # Step 3: Compose videos
            logger.info("\n[STEP 3/4] Composing videos...")
            video_files = []
            metadata = []
            
            for i, (audio_file, story) in enumerate(zip(audio_files, stories)):
                logger.info(f"Composing video {i+1}/{len(audio_files)}...")
                try:
                    title = story.get('title', f'Shorts #{i+1}')
                    video_file = self.compositor.compose(
                        audio_file=audio_file,
                        title=title,
                        randomize=self.randomize_videos
                    )
                    video_files.append(video_file)
                    
                    metadata.append({
                        'title': f"{title} #Shorts",
                        'description': f"{story.get('content', '')[:100]}...\n\n#Shorts #Facts #Viral",
                        'tags': ['Shorts', 'Facts', 'Viral', 'Amazing']
                    })
                except Exception as e:
                    logger.error(f"Failed to compose video {i+1}: {e}")
                    continue
            
            if not video_files:
                logger.error("No videos composed")
                return False
            
            logger.info(f"Composed {len(video_files)} videos")
            
            # Step 4: Schedule uploads (or just generate files if not uploading)
            logger.info("\n[STEP 4/4] Scheduling uploads...")
            if self.upload:
                try:
                    self.uploader.queue_uploads(video_files, metadata)
                    logger.info(f"Scheduled {len(video_files)} videos for upload")
                except Exception as e:
                    logger.error(f"Failed to schedule uploads: {e}")
                    # Don't fail the pipeline if upload scheduling fails
                    logger.info("Continuing without upload...")
            else:
                logger.info(f"Generated {len(video_files)} videos (upload disabled)")
                logger.info("Videos ready for manual upload or scheduling")
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info(f"  Generated videos: {len(video_files)}")
            logger.info(f"  Audio files: {len(audio_files)}")
            logger.info(f"  Output directory: {self.compositor.output_dir}")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"\nPipeline failed with error: {e}", exc_info=True)
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="YouTube Shorts daily automation pipeline"
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
        default='en-male',
        choices=['en-male', 'en-female', 'en-casual', 'en-male-old'],
        help='TTS voice to use (default: en-male)'
    )
    parser.add_argument(
        '--no-randomize',
        action='store_true',
        help='Disable random effects and variations'
    )
    parser.add_argument(
        '--upload',
        action='store_true',
        help='Enable YouTube upload (requires manual login first)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test mode: just show what would be generated'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("DRY RUN MODE: No files will be actually generated")
        logger.info(f"Would generate {args.count} shorts with voice {args.voice}")
        return True
    
    pipeline = DailyPipeline(
        content_count=args.count,
        voice=args.voice,
        randomize_videos=not args.no_randomize,
        upload=args.upload
    )
    
    success = pipeline.run()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
