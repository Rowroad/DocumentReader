"""Document model for representing processed documents."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from pathlib import Path
from datetime import datetime


class DocumentFormat(Enum):
    """Supported document formats."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    EPUB = "epub"
    MOBI = "mobi"
    HTML = "html"
    MARKDOWN = "md"
    IMAGE = "image"
    WEBPAGE = "webpage"


class OutputFormat(Enum):
    """Supported output formats."""
    PDF = "pdf"
    EPUB = "epub"
    TXT = "txt"
    DAISY_TEXT = "daisy_text"
    DAISY_AUDIO = "daisy_audio"
    M4B = "m4b"
    HTML = "html"
    MARKDOWN = "md"
    DOCX = "docx"


@dataclass
class DocumentStructure:
    """Represents the hierarchical structure of a document."""
    id: str
    title: str
    level: int
    page_number: Optional[int] = None
    children: List['DocumentStructure'] = field(default_factory=list)
    content: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "page_number": self.page_number,
            "children": [child.to_dict() for child in self.children],
            "content": self.content
        }


@dataclass
class ImageData:
    """Represents an image within a document."""
    id: str
    path: Optional[str]
    alt_text: str
    ocr_text: Optional[str] = None
    position: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "path": self.path,
            "alt_text": self.alt_text,
            "ocr_text": self.ocr_text,
            "position": self.position
        }


@dataclass
class Document:
    """Main document model."""
    file_path: Path
    title: str
    format: DocumentFormat
    content: str = ""
    structure: List[DocumentStructure] = field(default_factory=list)
    images: List[ImageData] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    language: str = "en"
    created_at: datetime = field(default_factory=datetime.now)
    processed: bool = False

    def get_flat_structure(self) -> List[DocumentStructure]:
        """Get a flattened list of all structure elements."""
        def flatten(items: List[DocumentStructure]) -> List[DocumentStructure]:
            result = []
            for item in items:
                result.append(item)
                if item.children:
                    result.extend(flatten(item.children))
            return result
        return flatten(self.structure)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "file_path": str(self.file_path),
            "title": self.title,
            "format": self.format.value,
            "content": self.content,
            "structure": [s.to_dict() for s in self.structure],
            "images": [img.to_dict() for img in self.images],
            "metadata": self.metadata,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "processed": self.processed
        }
