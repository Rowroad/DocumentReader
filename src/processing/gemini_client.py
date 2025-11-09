"""Gemini API client for document processing and TTS."""

import os
import base64
import time
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import google.generativeai as genai
from PIL import Image
import io

from ..models import Document, DocumentStructure, ImageData, Settings


class GeminiClient:
    """Client for interacting with Google's Gemini API."""

    def __init__(self, api_key: str, settings: Settings):
        """Initialize the Gemini client.

        Args:
            api_key: Google AI API key
            settings: Application settings
        """
        self.api_key = api_key
        self.settings = settings
        genai.configure(api_key=api_key)

        # Model selection based on processing mode
        # Using latest stable model names (as of Jan 2025)
        if settings.processing.accuracy_mode == "speed":
            self.model_name = "gemini-1.5-flash-latest"
        else:
            self.model_name = "gemini-1.5-pro-latest"

        self.model = genai.GenerativeModel(self.model_name)
        self.vision_model = genai.GenerativeModel('gemini-1.5-pro-latest')

    def extract_text_from_image(self, image_path: Path) -> Tuple[str, str]:
        """Extract text and generate alt text from an image.

        Args:
            image_path: Path to the image file

        Returns:
            Tuple of (ocr_text, alt_text)
        """
        try:
            img = Image.open(image_path)

            # OCR prompt
            ocr_prompt = """Extract ALL text from this image with perfect accuracy.
            Preserve any formatting, layout, or structure.
            If there is no text, return an empty string."""

            # Alt text prompt
            alt_prompt = """Generate a detailed, accessible description of this image for blind and visually impaired users.
            Include:
            - Main subject and context
            - Important details, colors, and composition
            - Any text visible in the image
            - Emotional tone or atmosphere
            Be concise but thorough (2-4 sentences)."""

            # Get OCR text
            ocr_response = self.vision_model.generate_content([ocr_prompt, img])
            ocr_text = ocr_response.text.strip()

            # Small delay to respect rate limits
            time.sleep(0.5)

            # Get alt text
            alt_response = self.vision_model.generate_content([alt_prompt, img])
            alt_text = alt_response.text.strip()

            return ocr_text, alt_text

        except Exception as e:
            raise Exception(f"Error processing image {image_path}: {str(e)}")

    def process_document_content(self, content: str, file_path: Path,
                                 custom_instructions: str = "") -> Dict:
        """Process document content to extract structure and metadata.

        Args:
            content: Raw document content
            file_path: Path to the original file
            custom_instructions: Additional user instructions

        Returns:
            Dictionary with processed content, structure, and metadata
        """
        # Build the prompt
        system_prompt = self.settings.system_prompt

        if self.settings.processing.accuracy_mode == "speed":
            # Simplified prompt for speed mode
            system_prompt = """Extract all text content from this document and identify:
            - Main title
            - Major headings
            - Language
            Output as JSON."""

        if custom_instructions and self.settings.processing.accuracy_mode != "speed":
            system_prompt += f"\n\nAdditional instructions: {custom_instructions}"

        prompt = f"""{system_prompt}

Document to process:
---
{content[:50000]}  # Limit to avoid token limits
---

Return a JSON object with this structure:
{{
    "title": "Document title",
    "language": "detected language code",
    "metadata": {{
        "author": "author if found",
        "description": "brief description"
    }},
    "structure": [
        {{
            "id": "unique_id",
            "title": "heading text",
            "level": 1,
            "content": "section content",
            "children": []
        }}
    ],
    "processed_content": "full processed content with preserved formatting"
}}
"""

        try:
            response = self.model.generate_content(prompt)

            # Parse JSON response
            result_text = response.text

            # Extract JSON from markdown code blocks if present
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()

            result = json.loads(result_text)
            return result

        except json.JSONDecodeError as e:
            # Fallback: return raw content
            return {
                "title": file_path.stem,
                "language": self.settings.processing.detect_language and "en" or "",
                "metadata": {},
                "structure": [],
                "processed_content": content
            }
        except Exception as e:
            raise Exception(f"Error processing document with Gemini: {str(e)}")

    def detect_language(self, text: str) -> str:
        """Detect the language of text.

        Args:
            text: Text to analyze

        Returns:
            ISO language code
        """
        if not self.settings.processing.detect_language:
            return "en"

        prompt = f"""Detect the primary language of this text and return ONLY the ISO 639-1 language code (e.g., 'en', 'es', 'fr', 'de').

Text: {text[:1000]}

Language code:"""

        try:
            response = self.model.generate_content(prompt)
            lang_code = response.text.strip().lower()[:2]
            return lang_code if len(lang_code) == 2 else "en"
        except:
            return "en"

    def generate_tts_audio(self, text: str, output_path: Path,
                          chapter_title: str = "") -> bool:
        """Generate TTS audio using Google AI Studio TTS.

        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            chapter_title: Optional chapter title for metadata

        Returns:
            True if successful
        """
        try:
            # Note: As of Jan 2025, Gemini API doesn't have direct TTS.
            # This would need to use Google Cloud Text-to-Speech API
            # For now, we'll create a placeholder that would integrate with that API

            from google.cloud import texttospeech

            client = texttospeech.TextToSpeechClient()

            synthesis_input = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code=self.settings.tts.language,
                name=self.settings.tts.voice
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=self.settings.tts.speed,
                pitch=self.settings.tts.pitch
            )

            response = client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as out:
                out.write(response.audio_content)

            return True

        except ImportError:
            # Fallback: Create a placeholder for TTS
            # In production, this would require google-cloud-texttospeech
            raise NotImplementedError(
                "TTS requires google-cloud-texttospeech package. "
                "Install with: pip install google-cloud-texttospeech"
            )
        except Exception as e:
            raise Exception(f"Error generating TTS audio: {str(e)}")

    def process_manga_page(self, image_path: Path) -> Dict:
        """Process a manga/comic page with panel detection and dialogue extraction.

        Args:
            image_path: Path to manga page image

        Returns:
            Dictionary with panel data and dialogue
        """
        try:
            img = Image.open(image_path)

            prompt = """Analyze this manga/comic page and extract:
            1. Reading order of panels (right-to-left for Japanese manga, left-to-right for Western comics)
            2. All dialogue and text in each panel
            3. Sound effects
            4. Visual descriptions of each panel for accessibility

            Return as JSON:
            {
                "reading_order": "rtl" or "ltr",
                "panels": [
                    {
                        "panel_number": 1,
                        "description": "visual description",
                        "dialogue": ["text1", "text2"],
                        "sound_effects": ["effect1"]
                    }
                ]
            }"""

            response = self.vision_model.generate_content([prompt, img])
            result_text = response.text

            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()

            return json.loads(result_text)

        except Exception as e:
            raise Exception(f"Error processing manga page: {str(e)}")

    def cleanup_cloud_data(self):
        """Request deletion of cloud-processed data (best effort)."""
        # Note: Gemini API doesn't store data persistently by default
        # This is a placeholder for compliance documentation
        pass
