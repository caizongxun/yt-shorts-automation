"""Manual Content Provider - Read pre-written stories from TXT files.

This module allows you to manually provide stories instead of scraping Reddit or using LLM.
Simply create TXT files in the content/ directory and the system will automatically process them.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ManualContentProvider:
    """Read and manage manually-provided content from TXT files."""

    def __init__(self, content_dir: str = "content"):
        """Initialize content provider.
        
        Args:
            content_dir: Directory containing story TXT files
        """
        self.content_dir = Path(content_dir)
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir = self.content_dir / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
        logger.info(f"ManualContentProvider initialized")
        logger.info(f"  Content directory: {self.content_dir}")
        logger.info(f"  Processed directory: {self.processed_dir}")

    def list_available_stories(self) -> List[Path]:
        """List all unprocessed story files.
        
        Returns:
            List of Path objects to TXT files
        """
        txt_files = list(self.content_dir.glob("*.txt"))
        # Filter out already processed files
        txt_files = [f for f in txt_files if not f.name.startswith(".")]
        
        logger.info(f"Found {len(txt_files)} unprocessed story files")
        return sorted(txt_files)

    def read_story(self, file_path: Path) -> Dict:
        """Read and parse a story TXT file.
        
        Expected format:
        ```
        Title: Story Title Here
        
        Story content goes here...
        Can be multiple paragraphs.
        Will be read as-is.
        ```
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Dictionary with 'title' and 'content'
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                full_text = f.read()
            
            # Try to extract title if it starts with "Title:"
            lines = full_text.split('\n')
            title = "Story"
            content_start = 0
            
            if lines[0].startswith("Title:"):
                title = lines[0].replace("Title:", "").strip()
                content_start = 1
            
            # Skip empty lines after title
            while content_start < len(lines) and not lines[content_start].strip():
                content_start += 1
            
            content = '\n'.join(lines[content_start:]).strip()
            
            logger.info(f"Read story: {file_path.name}")
            logger.info(f"  Title: {title}")
            logger.info(f"  Content length: {len(content)} characters")
            
            return {
                'source': 'manual',
                'title': title,
                'content': content,
                'file': str(file_path),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reading story file {file_path}: {e}")
            raise

    def fetch_stories(self, count: int = 3) -> List[Dict]:
        """Fetch the specified number of story files.
        
        Args:
            count: Number of stories to fetch
            
        Returns:
            List of story dictionaries
        """
        available_files = self.list_available_stories()
        
        if not available_files:
            logger.error(f"No story files found in {self.content_dir}")
            logger.info("Please create TXT files in the content/ directory")
            logger.info("Example filename: story_1.txt, story_2.txt, etc.")
            return []
        
        if len(available_files) < count:
            logger.warning(
                f"Only {len(available_files)} story files available, "
                f"but {count} requested. Using all available."
            )
            count = len(available_files)
        
        stories = []
        for i, file_path in enumerate(available_files[:count]):
            try:
                story = self.read_story(file_path)
                stories.append(story)
            except Exception as e:
                logger.error(f"Skipping file {file_path}: {e}")
                continue
        
        logger.info(f"Fetched {len(stories)} stories")
        return stories

    def mark_processed(self, file_path: Path):
        """Move a story file to processed directory.
        
        Args:
            file_path: Path to file that was processed
        """
        try:
            new_path = self.processed_dir / file_path.name
            file_path.rename(new_path)
            logger.info(f"Marked as processed: {file_path.name}")
        except Exception as e:
            logger.error(f"Error marking file as processed: {e}")

    def prepare_scripts(self, stories: List[Dict]) -> List[str]:
        """Prepare stories for TTS processing.
        
        Args:
            stories: List of story dictionaries
            
        Returns:
            List of text scripts ready for audio generation
        """
        scripts = []
        for story in stories:
            # Combine title and content for narration
            script = f"{story['title']}. {story['content']}"
            
            # Clean up: remove extra whitespace and line breaks
            script = ' '.join(script.split())
            
            scripts.append(script)
        
        return scripts

    def create_example_files(self):
        """Create example story files for reference."""
        examples = [
            {
                'filename': 'example_story_1.txt',
                'content': """Title: The Ancient Honey Discovery

Did you know that honey never spoils? Archaeologists have discovered jars of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible! The honey remains unchanged due to its low moisture content and acidic properties that prevent bacterial growth. This incredible natural preservative has been used by civilizations for thousands of years, not just as food, but also for medicinal purposes and wound healing."""
            },
            {
                'filename': 'example_story_2.txt',
                'content': """Title: The Mystery of Flamingo Pink Feathers

Flamingos aren't born pink! When baby flamingos hatch, they have grey or white feathers. Their iconic pink color actually comes from their diet. They eat algae and crustaceans called krill that contain a pigment called carotenoid. As they consume more of these food sources, the carotenoid accumulates in their feathers, turning them pink. The more they eat, the more vibrant their color becomes!"""
            },
            {
                'filename': 'example_story_3.txt',
                'content': """Title: Your Body's Cellular Wonder

Your body is constantly renewing itself. Every single second, your body produces approximately 330 billion new cells to replace old ones. Over the course of a year, you essentially have a completely new body! This means that the atoms and cells that make up your body today are constantly being replaced. This incredible process is one of the reasons why our bodies can heal from injuries and fight off infections."""
            }
        ]
        
        for example in examples:
            file_path = self.content_dir / example['filename']
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(example['content'])
                logger.info(f"Created example file: {example['filename']}")
            else:
                logger.info(f"Example file already exists: {example['filename']}")


if __name__ == "__main__":
    # Test usage
    provider = ManualContentProvider()
    
    # Create example files
    print("\n=== Creating Example Files ===")
    provider.create_example_files()
    
    # List available stories
    print("\n=== Available Stories ===")
    stories = provider.fetch_stories(count=3)
    
    if stories:
        print(f"\nFetched {len(stories)} stories:")
        for i, story in enumerate(stories, 1):
            print(f"\n{i}. {story['title']}")
            print(f"   Content length: {len(story['content'])} chars")
    else:
        print("No stories available. Please create TXT files in the content/ directory.")
