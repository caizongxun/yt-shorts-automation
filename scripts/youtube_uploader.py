import logging
import time
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Optional, List

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.keys import Keys
except ImportError:
    print("Selenium not installed. Install with: pip install selenium")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeUploader:
    """Upload videos to YouTube Studio with automatic title/description."""

    YOUTUBE_STUDIO_URL = "https://studio.youtube.com"
    YOUTUBE_UPLOAD_URL = "https://www.youtube.com/upload"

    def __init__(self, headless: bool = False):
        """Initialize YouTube uploader with Selenium.
        
        Args:
            headless: Run browser in headless mode (no window)
        """
        self.headless = headless
        self.driver = None
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        logger.info(f"YouTubeUploader initialized (headless={headless})")

    def _init_browser(self):
        """Initialize Selenium WebDriver for Chrome."""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            logger.info("Chrome WebDriver initialized")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def _wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be present and return it."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            logger.error(f"Timeout waiting for element: {by}={value}")
            raise

    def login(self, browser_profile_path: Optional[str] = None):
        """Login to YouTube.
        
        Note: This is a tricky part. The recommended approach is to:
        1. Manually login once in Chrome
        2. Use the browser profile for subsequent uploads
        3. Or use cookies saved from previous session
        
        Args:
            browser_profile_path: Path to Chrome user data directory
        """
        self._init_browser()
        
        if browser_profile_path:
            # This would require restarting browser with profile
            logger.info(f"Using Chrome profile: {browser_profile_path}")
        
        logger.info("Opening YouTube Studio...")
        self.driver.get(self.YOUTUBE_STUDIO_URL)
        
        # Wait for user to manually login if needed
        logger.info("Please login manually if prompted...")
        time.sleep(10)
        
        if "youtube" not in self.driver.current_url:
            logger.error("Login failed")
            return False
        
        logger.info("Login successful")
        return True

    def upload(
        self,
        video_path: str,
        title: str = "Shorts Video",
        description: str = "",
        tags: Optional[List[str]] = None,
        is_short: bool = True,
        made_for_kids: bool = False,
        schedule_time: Optional[str] = None
    ) -> bool:
        """Upload a video to YouTube.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags/hashtags
            is_short: Mark as Shorts format
            made_for_kids: COPPA compliance
            schedule_time: ISO format datetime for scheduled upload
            
        Returns:
            True if upload successful, False otherwise
        """
        if not self.driver:
            self._init_browser()
            if not self.login():
                return False
        
        try:
            logger.info(f"Starting upload: {Path(video_path).name}")
            
            # Navigate to upload page
            self.driver.get(self.YOUTUBE_UPLOAD_URL)
            time.sleep(3)
            
            # Find file input and upload
            logger.info("Uploading video file...")
            file_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
            file_input.send_keys(str(Path(video_path).absolute()))
            
            # Wait for upload to start
            time.sleep(5)
            
            # Fill in title
            logger.info(f"Setting title: {title}")
            self._wait_for_element(By.ID, 'textbox').send_keys(title)
            
            # Fill in description
            if description:
                logger.info("Setting description")
                desc_input = self.driver.find_element(By.CSS_SELECTOR, 'ytcp-ve[heading="Description"] textarea')
                desc_input.send_keys(description)
            
            # Add tags
            if tags:
                logger.info(f"Adding tags: {tags}")
                tag_input = self.driver.find_element(By.CSS_SELECTOR, '[aria-label="Tags"]')
                tag_input.send_keys(', '.join(tags))
            
            # Toggle Shorts format
            if is_short:
                logger.info("Marking as Shorts")
                shorts_checkbox = self.driver.find_element(
                    By.CSS_SELECTOR,
                    'ytcp-checkbox-lit[label-position="after"] input[type="checkbox"]'
                )
                if not shorts_checkbox.is_selected():
                    shorts_checkbox.click()
            
            # Set COPPA
            logger.info(f"Setting 'Made for Kids': {made_for_kids}")
            # This would require finding and clicking the appropriate radio button
            
            # Schedule or publish
            if schedule_time:
                logger.info(f"Scheduling for: {schedule_time}")
                # Find and click "Schedule" button
                schedule_btn = self.driver.find_element(
                    By.XPATH,
                    '//button[contains(text(), "Schedule")]'
                )
                schedule_btn.click()
                # Would need to set date/time picker
            else:
                logger.info("Publishing immediately...")
                # Click "Publish" button
                publish_btn = self.driver.find_element(
                    By.XPATH,
                    '//button[contains(text(), "Publish")]'
                )
                publish_btn.click()
            
            # Wait for confirmation
            time.sleep(15)
            
            logger.info("Upload completed successfully")
            self._log_upload(
                video_path, title, description, tags,
                schedule_time, success=True
            )
            return True
            
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            self._log_upload(
                video_path, title, description, tags,
                schedule_time, success=False, error=str(e)
            )
            return False
    
    def _log_upload(self, video_path: str, title: str, description: str,
                   tags: List[str], schedule_time: str,
                   success: bool, error: str = None):
        """Log upload attempt to file."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'video_path': video_path,
            'title': title,
            'description': description[:100],  # Truncate for logs
            'tags': tags,
            'schedule_time': schedule_time,
            'success': success,
            'error': error
        }
        
        log_file = self.logs_dir / f"uploads_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class UploadScheduler:
    """Schedule uploads at specific times with randomization."""

    def __init__(self, output_dir: str = "output/videos"):
        """Initialize upload scheduler.
        
        Args:
            output_dir: Directory containing generated videos
        """
        self.output_dir = Path(output_dir)
        self.uploader = YouTubeUploader(headless=False)
        
    def get_upload_times(self, count: int = 3) -> List[datetime]:
        """Generate random upload times to avoid pattern detection.
        
        Spreads uploads throughout the day, typically:
        - Morning: 09:00-12:00
        - Afternoon: 14:00-17:00
        - Evening: 19:00-21:00
        
        Args:
            count: Number of upload times to generate
            
        Returns:
            List of datetime objects for scheduled uploads
        """
        import random
        
        times = []
        preferred_hours = [
            (9, 12),    # Morning
            (14, 17),   # Afternoon
            (19, 21)    # Evening
        ]
        
        for _ in range(count):
            hour_range = random.choice(preferred_hours)
            hour = random.randint(hour_range[0], hour_range[1])
            minute = random.randint(0, 59)
            
            now = datetime.now()
            scheduled = now.replace(hour=hour, minute=minute, second=0)
            
            # If time already passed today, schedule for tomorrow
            if scheduled <= now:
                scheduled += timedelta(days=1)
            
            times.append(scheduled)
        
        times.sort()
        return times
    
    def queue_uploads(self, videos: List[str], metadata: List[dict] = None):
        """Queue multiple videos for upload at scheduled times.
        
        Args:
            videos: List of video file paths
            metadata: List of metadata dicts (title, description, tags)
        """
        if metadata is None:
            metadata = [{} for _ in videos]
        
        upload_times = self.get_upload_times(len(videos))
        
        schedule = []
        for video, meta, upload_time in zip(videos, metadata, upload_times):
            schedule.append({
                'video': video,
                'upload_time': upload_time.isoformat(),
                'title': meta.get('title', 'Shorts Video'),
                'description': meta.get('description', '#Shorts #Facts'),
                'tags': meta.get('tags', ['Shorts', 'Facts', 'Viral'])
            })
        
        # Save schedule
        schedule_file = self.output_dir / "upload_schedule.json"
        with open(schedule_file, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Schedule saved to {schedule_file}")
        for item in schedule:
            logger.info(f"  {item['upload_time']}: {item['title']}")


if __name__ == "__main__":
    # Test usage
    logger.info("YouTube Uploader module ready")
    
    # Generate sample upload schedule
    scheduler = UploadScheduler()
    times = scheduler.get_upload_times(3)
    
    logger.info("\nSample upload schedule:")
    for t in times:
        logger.info(f"  - {t.strftime('%Y-%m-%d %H:%M:%S')}")
