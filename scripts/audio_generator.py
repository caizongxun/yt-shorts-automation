import asyncio
import edge_tts
import logging
from pathlib import Path
from datetime import datetime
import json
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioGenerator:
    """Generate speech audio from text using Edge-TTS (free, high quality)."""

    # Available voices with good quality
    VOICES = {
        'en-male': 'en-US-ChristopherNeural',      # Deep male voice
        'en-female': 'en-US-AvaNeural',            # Natural female voice
        'en-casual': 'en-US-GuyNeural',            # Casual male
        'en-male-old': 'en-US-ArthurNeural',       # Older male voice
    }

    def __init__(self, voice: str = 'en-male', rate: str = '+10%', output_dir: str = 'output/audio'):
        """Initialize audio generator.
        
        Args:
            voice: Voice selection (key from VOICES dict or direct voice name)
            rate: Speech rate adjustment (e.g., '+10%', '-5%', '0%')
            output_dir: Directory to save audio files
        """
        self.voice = self.VOICES.get(voice, voice)  # Allow both preset and custom voice names
        self.rate = rate
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
        logger.info(f"AudioGenerator initialized with voice: {self.voice}, rate: {rate}")

    async def generate_async(self, text: str, output_file: str = None, retry_count: int = 0) -> str:
        """Generate audio from text asynchronously with retry logic.
        
        Args:
            text: Text to convert to speech
            output_file: Custom output filename (without path)
            retry_count: Current retry attempt
            
        Returns:
            Path to generated audio file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"audio_{timestamp}.mp3"
        
        output_path = self.output_dir / output_file
        
        try:
            logger.info(f"Generating audio: {output_file}")
            
            # Initialize TTS communicator
            communicate = edge_tts.Communicate(
                text, 
                self.voice, 
                rate=self.rate
            )
            
            # Save to file with timeout
            try:
                await asyncio.wait_for(
                    communicate.save(str(output_path)),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"Timeout generating audio, retrying...")
                if retry_count < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                    return await self.generate_async(text, output_file, retry_count + 1)
                raise Exception("Audio generation timeout after retries")
            
            logger.info(f"Audio generated successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating audio (attempt {retry_count + 1}/{self.max_retries}): {error_msg}")
            
            # Retry on network errors or 403
            if retry_count < self.max_retries and any(x in error_msg for x in ['403', '401', 'Connection', 'timeout', 'connection reset']):
                logger.info(f"Retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)
                return await self.generate_async(text, output_file, retry_count + 1)
            
            raise

    def generate(self, text: str, output_file: str = None) -> str:
        """Generate audio synchronously (wrapper around async function).
        
        Args:
            text: Text to convert to speech
            output_file: Custom output filename
            
        Returns:
            Path to generated audio file
        """
        try:
            # Create new event loop if needed (Windows compatibility)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(self.generate_async(text, output_file))
        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            raise

    async def generate_batch_async(self, texts: list, output_files: list = None) -> list:
        """Generate multiple audio files with rate limiting to avoid 403.
        
        Args:
            texts: List of texts to convert
            output_files: List of output filenames (optional)
            
        Returns:
            List of generated audio file paths
        """
        if output_files is None:
            output_files = [f"audio_batch_{i}_{datetime.now().strftime('%H%M%S')}.mp3" 
                          for i in range(len(texts))]
        
        results = []
        for text, filename in zip(texts, output_files):
            try:
                # Generate with delay between requests
                result = await self.generate_async(text, filename)
                results.append(result)
                # Add delay between requests to avoid rate limiting
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error generating {filename}: {e}")
                results.append(None)
        
        return [r for r in results if r is not None]

    def generate_batch(self, texts: list, output_files: list = None) -> list:
        """Generate multiple audio files (synchronous wrapper).
        
        Args:
            texts: List of texts to convert
            output_files: List of output filenames
            
        Returns:
            List of generated audio file paths
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.generate_batch_async(texts, output_files))

    async def generate_with_metadata(self, text: str, metadata: dict = None) -> dict:
        """Generate audio and save metadata about the audio.
        
        Args:
            text: Text to convert
            metadata: Additional metadata to store
            
        Returns:
            Dictionary with audio info and metadata
        """
        output_file = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        audio_path = await self.generate_async(text, output_file)
        
        info = {
            'audio_file': str(audio_path),
            'text': text,
            'voice': self.voice,
            'rate': self.rate,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        # Save metadata
        meta_file = self.output_dir / output_file.replace('.mp3', '_meta.json')
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        return info

    def get_available_voices(self) -> dict:
        """Return available voice presets."""
        return self.VOICES.copy()

    def list_voices(self):
        """Print available voice options."""
        print("\n=== Available Voice Presets ===")
        for key, voice_name in self.VOICES.items():
            print(f"  {key:15} -> {voice_name}")
        print("\nOr use any valid Edge-TTS voice name directly.")
        print("For full list, visit: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support\n")


if __name__ == "__main__":
    import time
    
    # Test usage
    print("Testing AudioGenerator...\n")
    
    generator = AudioGenerator(voice='en-male', rate='+10%')
    
    # Show available voices
    generator.list_voices()
    
    # Test single generation
    print("Generating single audio...")
    text = "Did you know? Honey never spoils. Archaeologists found ancient Egyptian honey that's 3000 years old and still edible!"
    audio_file = generator.generate(text)
    print(f"Generated: {audio_file}\n")
    
    # Test batch generation
    print("Generating batch audio...")
    texts = [
        "Fact one: Your body contains 37 trillion cells.",
        "Fact two: Flamingos are born with grey feathers, not pink.",
        "Fact three: A group of flamingos is called a flamboyance."
    ]
    files = generator.generate_batch(texts)
    print(f"Generated {len(files)} audio files")
