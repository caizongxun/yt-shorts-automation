import praw
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentScraper:
    """Scrape content from Reddit or generate using LLM."""

    def __init__(self, config_path: str = "configs/reddit_config.json"):
        """Initialize content scraper with Reddit API or LLM config."""
        self.config = self._load_config(config_path)
        self.reddit = self._init_reddit()
        self.output_dir = Path("output/content")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict:
        """Create default configuration for setup."""
        return {
            "client_id": "YOUR_CLIENT_ID",
            "client_secret": "YOUR_CLIENT_SECRET",
            "user_agent": "yt-shorts-bot/1.0",
            "subreddits": ["AskReddit", "NoSleep", "Confessions"],
            "sort_by": "top",
            "time_filter": "day",
            "limit": 5,
            "min_length": 100,
            "use_llm": False,
            "llm_model": "llama2"  # For local Ollama
        }

    def _init_reddit(self):
        """Initialize Reddit API client."""
        try:
            if self.config.get('client_id') == "YOUR_CLIENT_ID":
                logger.info("Reddit API not configured, will use LLM fallback")
                return None
            return praw.Reddit(
                client_id=self.config['client_id'],
                client_secret=self.config['client_secret'],
                user_agent=self.config['user_agent']
            )
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API: {e}")
            return None

    def fetch_stories(self, count: int = 3) -> List[Dict]:
        """Fetch stories from Reddit or generate with LLM."""
        if self.reddit:
            return self._fetch_from_reddit(count)
        else:
            logger.info("Falling back to LLM content generation")
            return self._generate_with_llm(count)

    def _fetch_from_reddit(self, count: int) -> List[Dict]:
        """Fetch top stories from configured subreddits."""
        stories = []
        subreddits = self.config.get('subreddits', ['AskReddit'])
        
        for subreddit_name in subreddits:
            if len(stories) >= count:
                break
            
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                posts = subreddit.top(
                    time_filter=self.config.get('time_filter', 'day'),
                    limit=self.config.get('limit', 5)
                )
                
                for post in posts:
                    if len(stories) >= count:
                        break
                    
                    if len(post.selftext) >= self.config.get('min_length', 100):
                        stories.append({
                            'source': 'reddit',
                            'title': post.title,
                            'content': post.selftext,
                            'subreddit': subreddit_name,
                            'url': f"https://reddit.com{post.permalink}",
                            'timestamp': datetime.now().isoformat()
                        })
            except Exception as e:
                logger.error(f"Error fetching from r/{subreddit_name}: {e}")
                continue
        
        logger.info(f"Fetched {len(stories)} stories from Reddit")
        return stories

    def _generate_with_llm(self, count: int) -> List[Dict]:
        """Generate content using local LLM (Ollama)."""
        try:
            import requests
            
            stories = []
            prompts = [
                "Generate a short, engaging story about an unusual life event. Keep it under 300 words.",
                "Write a surprising fact about science or nature that would amaze people.",
                "Generate a funny or awkward social situation story for Reddit.",
                "Create an interesting historical fact that most people don't know.",
                "Write a mysterious or creepy short story for Reddit's NoSleep."
            ]
            
            for i, prompt in enumerate(prompts[:count]):
                try:
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": self.config.get('llm_model', 'llama2'),
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        content = response.json().get('response', '')
                        stories.append({
                            'source': 'llm',
                            'title': f"Generated Story #{i+1}",
                            'content': content,
                            'model': self.config.get('llm_model', 'llama2'),
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception as e:
                    logger.error(f"Error generating with LLM: {e}")
                    # Fallback to dummy story
                    stories.append(self._create_dummy_story(i))
            
            logger.info(f"Generated {len(stories)} stories with LLM")
            return stories
            
        except ImportError:
            logger.error("Requests library not found. Please install it.")
            return [self._create_dummy_story(i) for i in range(count)]

    def _create_dummy_story(self, index: int) -> Dict:
        """Create a dummy story for testing."""
        dummy_stories = [
            "Did you know? Your body contains about 37.2 trillion cells. Each second, your body produces approximately 330 billion cells.",
            "Fun fact: Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible!",
            "Interesting: A group of flamingos is called a 'flamboyance'. And when baby flamingos are born, they have grey or white feathers, not pink!",
        ]
        return {
            'source': 'dummy',
            'title': f"Fact #{index+1}",
            'content': dummy_stories[index % len(dummy_stories)],
            'timestamp': datetime.now().isoformat()
        }

    def save_stories(self, stories: List[Dict], filename: str = None) -> str:
        """Save scraped stories to JSON file."""
        if filename is None:
            filename = f"stories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stories, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(stories)} stories to {filepath}")
        return str(filepath)

    def prepare_scripts(self, stories: List[Dict]) -> List[str]:
        """Prepare stories for TTS processing."""
        scripts = []
        for story in stories:
            # Clean up the content
            content = story['content']
            title = story['title']
            
            # Combine title and content for narration
            script = f"{title}. {content}"
            
            # Remove line breaks and extra spaces
            script = ' '.join(script.split())
            
            scripts.append(script)
        
        return scripts


if __name__ == "__main__":
    # Test usage
    scraper = ContentScraper()
    stories = scraper.fetch_stories(count=3)
    scraper.save_stories(stories)
    scripts = scraper.prepare_scripts(stories)
    for i, script in enumerate(scripts):
        print(f"Script {i+1}: {script[:100]}...")
