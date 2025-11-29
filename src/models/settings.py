"""Application settings model."""

from dataclasses import dataclass, field, asdict
from typing import Dict, Optional
from pathlib import Path
import json
import os


@dataclass
class TTSSettings:
    """Text-to-speech settings."""
    engine: str = "google"  # "google" or "sapi5"
    voice: str = "en-US-Neural2-A"  # For Google TTS
    sapi5_voice: str = ""  # For SAPI5 (empty = default voice)
    speed: float = 1.0
    language: str = "en-US"
    pitch: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ProcessingSettings:
    """Document processing settings."""
    accuracy_mode: str = "high"  # high, balanced, speed
    preserve_formatting: bool = True
    extract_images: bool = True
    ocr_images: bool = True
    detect_language: bool = True
    custom_instructions: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SecuritySettings:
    """Security and privacy settings."""
    auto_delete_days: int = 7
    delete_cloud_data: bool = True
    encrypt_local_storage: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class UISettings:
    """UI preferences."""
    theme: str = "system"
    font_size: int = 12
    high_contrast: bool = False
    keyboard_shortcuts: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Settings:
    """Main application settings."""
    gemini_api_key: str = ""
    system_prompt: str = ""
    tts: TTSSettings = field(default_factory=TTSSettings)
    processing: ProcessingSettings = field(default_factory=ProcessingSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    ui: UISettings = field(default_factory=UISettings)
    output_directory: str = ""
    temp_directory: str = ""

    def __post_init__(self):
        """Initialize directories."""
        if not self.output_directory:
            self.output_directory = str(Path.home() / "Documents" / "DocumentReader" / "Output")
        if not self.temp_directory:
            self.temp_directory = str(Path(os.getenv('APPDATA', '')) / "DocumentReader" / "Temp")
        if not self.system_prompt:
            self.system_prompt = self.get_default_system_prompt()

        # Create directories
        Path(self.output_directory).mkdir(parents=True, exist_ok=True)
        Path(self.temp_directory).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_default_system_prompt() -> str:
        """Get the default system prompt for Gemini."""
        return """You are an expert document processing assistant optimized for accessibility. Your task is to:

1. Extract ALL text content from documents with perfect accuracy
2. Preserve document structure including:
   - Headings hierarchy (H1, H2, H3, etc.)
   - Paragraphs and line breaks
   - Lists (ordered and unordered)
   - Tables with proper row/column structure
   - Quotes and special formatting
3. For images:
   - Extract any embedded text using OCR
   - Generate detailed, accessible alt text descriptions
   - Note the position and context of images
4. Detect and preserve:
   - Language(s) used in the document
   - Chapter/section boundaries
   - Page numbers and references
   - Footnotes and endnotes
5. For structured documents (books, reports):
   - Identify title, author, and metadata
   - Detect table of contents
   - Recognize chapter/section divisions
   - Preserve semantic structure

Output should be in a structured format that preserves all accessibility features for blind and visually impaired users."""

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "gemini_api_key": self.gemini_api_key,
            "system_prompt": self.system_prompt,
            "tts": self.tts.to_dict(),
            "processing": self.processing.to_dict(),
            "security": self.security.to_dict(),
            "ui": self.ui.to_dict(),
            "output_directory": self.output_directory,
            "temp_directory": self.temp_directory
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Settings':
        """Create Settings from dictionary."""
        return cls(
            gemini_api_key=data.get("gemini_api_key", ""),
            system_prompt=data.get("system_prompt", cls.get_default_system_prompt()),
            tts=TTSSettings(**data.get("tts", {})),
            processing=ProcessingSettings(**data.get("processing", {})),
            security=SecuritySettings(**data.get("security", {})),
            ui=UISettings(**data.get("ui", {})),
            output_directory=data.get("output_directory", ""),
            temp_directory=data.get("temp_directory", "")
        )

    def save(self, file_path: Path):
        """Save settings to file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            # Don't save API key to file for security
            data = self.to_dict()
            data["gemini_api_key"] = ""
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, file_path: Path) -> 'Settings':
        """Load settings from file."""
        if not file_path.exists():
            return cls()

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return cls.from_dict(data)
