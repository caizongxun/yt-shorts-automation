import asyncio
import edge_tts
import logging
from pathlib import Path
from datetime import datetime
import json

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
        
        logger.info(f"AudioGenerator initialized with voice: {self.voice}, rate: {rate}")

    async def generate_async(self, text: str, output_file: str = None) -> str:
        """Generate audio from text asynchronously.
        
        Args:
            text: Text to convert to speech
            output_file: Custom output filename (without path)
            
        Returns:
            Path to generated audio file
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"audio_{timestamp}.mp3"
        
        output_path = self.output_dir / output_file
        
        try:
            # Initialize TTS communicator
            communicate = edge_tts.Communicate(text, self.voice, rate=self.rate)
            
            # Save to file
            await communicate.save(str(output_path))
            
            logger.info(f"Audio generated successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            raise

    def generate(self, text: str, output_file: str = None) -> str:
        """Generate audio synchronously (wrapper around async function).
        
        Args:
            text: Text to convert to speech
            output_file: Custom output filename
            
        Returns:
            Path to generated audio file
        """
        return asyncio.run(self.generate_async(text, output_file))

    async def generate_batch_async(self, texts: list, output_files: list = None) -> list:
        """Generate multiple audio files concurrently.
        
        Args:
            texts: List of texts to convert
            output_files: List of output filenames (optional)
            
        Returns:
            List of generated audio file paths
        """
        if output_files is None:
            output_files = [f"audio_batch_{i}_{datetime.now().strftime('%H%M%S')}.mp3" 
                          for i in range(len(texts))]
        
        tasks = [self.generate_async(text, filename) 
                for text, filename in zip(texts, output_files)]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Log any errors
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error generating audio batch item {i}: {result}")
        
        return [r for r in results if not isinstance(r, Exception)]

    def generate_batch(self, texts: list, output_files: list = None) -> list:
        """Generate multiple audio files (synchronous wrapper).
        
        Args:
            texts: List of texts to convert
            output_files: List of output filenames
            
        Returns:
            List of generated audio file paths
        """
        return asyncio.run(self.generate_batch_async(texts, output_files))

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
