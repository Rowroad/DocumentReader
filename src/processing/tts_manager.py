"""Text-to-Speech manager supporting multiple TTS engines."""

import os
import platform
from pathlib import Path
from typing import Optional, List
import subprocess

from ..models import Settings


class TTSManager:
    """Manager for text-to-speech conversion with multiple engine support."""

    def __init__(self, settings: Settings, gemini_client=None):
        """Initialize the TTS manager.

        Args:
            settings: Application settings
            gemini_client: Optional Gemini client for Google TTS
        """
        self.settings = settings
        self.gemini_client = gemini_client

    def generate_audio(self, text: str, output_path: Path,
                      chapter_title: str = "") -> bool:
        """Generate TTS audio using the configured engine.

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            chapter_title: Optional chapter title for metadata

        Returns:
            True if successful

        Raises:
            NotImplementedError: If TTS engine is not available
            Exception: If TTS generation fails
        """
        engine = self.settings.tts.engine.lower()

        if engine == "google":
            return self._generate_google_tts(text, output_path, chapter_title)
        elif engine == "sapi5":
            return self._generate_sapi5_tts(text, output_path, chapter_title)
        else:
            raise ValueError(f"Unknown TTS engine: {engine}")

    def _generate_google_tts(self, text: str, output_path: Path,
                            chapter_title: str = "") -> bool:
        """Generate TTS using Google Cloud Text-to-Speech.

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            chapter_title: Optional chapter title

        Returns:
            True if successful
        """
        if not self.gemini_client:
            raise NotImplementedError(
                "Google TTS requires Gemini client to be initialized"
            )

        return self.gemini_client.generate_tts_audio(text, output_path, chapter_title)

    def _generate_sapi5_tts(self, text: str, output_path: Path,
                           chapter_title: str = "") -> bool:
        """Generate TTS using Microsoft SAPI 5.

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            chapter_title: Optional chapter title

        Returns:
            True if successful
        """
        # Check if running on Windows
        if platform.system() != "Windows":
            raise NotImplementedError(
                "SAPI 5 TTS is only available on Windows"
            )

        try:
            import win32com.client
            from pydub import AudioSegment
            import tempfile
        except ImportError:
            raise NotImplementedError(
                "SAPI 5 TTS requires pywin32 and pydub packages. "
                "Install with: pip install pywin32 pydub"
            )

        try:
            # Initialize SAPI 5
            speaker = win32com.client.Dispatch("SAPI.SpVoice")

            # Set voice if specified
            if self.settings.tts.sapi5_voice:
                voices = speaker.GetVoices()
                for i in range(voices.Count):
                    voice = voices.Item(i)
                    if self.settings.tts.sapi5_voice in voice.GetDescription():
                        speaker.Voice = voice
                        break

            # Set rate (SAPI range is -10 to 10, our speed is 0.5 to 2.0)
            # Convert: speed 1.0 = rate 0, speed 0.5 = rate -5, speed 2.0 = rate 5
            rate = int((self.settings.tts.speed - 1.0) * 5)
            rate = max(-10, min(10, rate))
            speaker.Rate = rate

            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # SAPI speaks to WAV file
            temp_wav = output_path.with_suffix('.wav')

            # Create a file stream for audio output
            from win32com.client import constants
            stream = win32com.client.Dispatch("SAPI.SpFileStream")

            # Set output format to 44.1kHz, 16-bit, mono
            stream.Format.Type = 39  # SAFT44kHz16BitMono

            # Open the stream
            stream.Open(str(temp_wav), 3)  # SSFMCreateForWrite

            # Set the output stream
            speaker.AudioOutputStream = stream

            # Speak the text
            speaker.Speak(text)

            # Close the stream
            stream.Close()

            # Convert WAV to MP3 if requested
            if output_path.suffix.lower() == '.mp3':
                audio = AudioSegment.from_wav(str(temp_wav))
                audio.export(str(output_path), format='mp3', bitrate='128k')
                temp_wav.unlink()  # Remove temporary WAV
            else:
                # If output is WAV, just rename
                if temp_wav != output_path:
                    temp_wav.rename(output_path)

            return True

        except Exception as e:
            raise Exception(f"Error generating SAPI 5 TTS audio: {str(e)}")

    def get_available_sapi5_voices(self) -> List[str]:
        """Get list of available SAPI 5 voices.

        Returns:
            List of voice names

        Raises:
            NotImplementedError: If SAPI 5 is not available
        """
        if platform.system() != "Windows":
            return []

        try:
            import win32com.client

            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            voices = speaker.GetVoices()

            voice_list = []
            for i in range(voices.Count):
                try:
                    voice = voices.Item(i)
                    # Try different methods to get the voice name
                    try:
                        name = voice.GetDescription()
                    except:
                        # Fallback: try accessing the name attribute directly
                        name = str(voice.GetAttribute("Name"))

                    if name:
                        voice_list.append(name)
                except Exception as voice_error:
                    print(f"Error getting voice {i}: {voice_error}")
                    continue

            print(f"Found {len(voice_list)} SAPI 5 voices: {voice_list}")
            return voice_list

        except ImportError:
            print("Error: pywin32 not installed")
            return []
        except Exception as e:
            import traceback
            print(f"Error getting SAPI 5 voices: {e}")
            print(traceback.format_exc())
            return []

    def is_sapi5_available(self) -> bool:
        """Check if SAPI 5 is available on this system.

        Returns:
            True if SAPI 5 is available
        """
        if platform.system() != "Windows":
            return False

        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            return True
        except:
            return False
