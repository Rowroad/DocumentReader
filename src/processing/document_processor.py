"""Document processor for extracting content from various formats."""

import os
import re
from pathlib import Path
from typing import Optional, List, Dict
import uuid

import PyPDF2
import fitz  # PyMuPDF
from docx import Document as DocxDocument
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
from PIL import Image
import requests

from ..models import Document, DocumentFormat, DocumentStructure, ImageData, Settings
from .gemini_client import GeminiClient


class DocumentProcessor:
    """Processes various document formats."""

    def __init__(self, settings: Settings, gemini_client: Optional[GeminiClient] = None):
        """Initialize the document processor.

        Args:
            settings: Application settings
            gemini_client: Gemini API client (optional, required only for AI processing)
        """
        self.settings = settings
        self.gemini = gemini_client

    def process_file(self, file_path: Path,
                    custom_instructions: str = "",
                    use_gemini: bool = True) -> Document:
        """Process a file and extract its content.

        Args:
            file_path: Path to the file
            custom_instructions: Optional custom processing instructions
            use_gemini: Whether to use Gemini AI for processing (default True)

        Returns:
            Processed Document object
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()

        # Determine format
        format_map = {
            '.pdf': DocumentFormat.PDF,
            '.docx': DocumentFormat.DOCX,
            '.txt': DocumentFormat.TXT,
            '.epub': DocumentFormat.EPUB,
            '.mobi': DocumentFormat.MOBI,
            '.html': DocumentFormat.HTML,
            '.htm': DocumentFormat.HTML,
            '.md': DocumentFormat.MARKDOWN,
            '.jpg': DocumentFormat.IMAGE,
            '.jpeg': DocumentFormat.IMAGE,
            '.png': DocumentFormat.IMAGE,
            '.gif': DocumentFormat.IMAGE,
            '.bmp': DocumentFormat.IMAGE,
        }

        doc_format = format_map.get(suffix, DocumentFormat.TXT)

        # Extract raw content
        if doc_format == DocumentFormat.PDF:
            content, images = self._extract_pdf(file_path)
        elif doc_format == DocumentFormat.DOCX:
            content, images = self._extract_docx(file_path)
        elif doc_format == DocumentFormat.EPUB:
            content, images = self._extract_epub(file_path)
        elif doc_format == DocumentFormat.MOBI:
            content, images = self._extract_mobi(file_path)
        elif doc_format == DocumentFormat.HTML:
            content, images = self._extract_html(file_path)
        elif doc_format == DocumentFormat.MARKDOWN:
            content, images = self._extract_markdown(file_path)
        elif doc_format == DocumentFormat.IMAGE:
            content, images = self._extract_image(file_path)
        else:  # TXT
            content, images = self._extract_txt(file_path)

        # Create initial document
        doc = Document(
            file_path=file_path,
            title=file_path.stem,
            format=doc_format,
            content=content,
            images=images
        )

        # Process with Gemini for structure and enhancement (if enabled)
        if content and use_gemini:
            if not self.gemini:
                # Gemini client not available, fall back to direct reading
                print("Warning: Gemini client not available, using direct reading mode")
                use_gemini = False
            else:
                try:
                    processed = self.gemini.process_document_content(
                        content, file_path, custom_instructions
                    )

                    doc.title = processed.get('title', doc.title)
                    doc.language = processed.get('language', 'en')
                    doc.metadata = processed.get('metadata', {})
                    doc.content = processed.get('processed_content', content)

                    # Convert structure
                    structure_data = processed.get('structure', [])
                    doc.structure = self._convert_structure(structure_data)

                    # Detect language if needed
                    if not doc.language:
                        doc.language = self.gemini.detect_language(content[:1000])

                except Exception as e:
                    print(f"Warning: Gemini processing failed: {e}")
                    # Continue with raw content
                    use_gemini = False

        if content and not use_gemini:
            # Direct reading mode - try to detect basic structure from content
            doc.language = 'en'  # Default language
            doc.structure = self._detect_simple_structure(content)

        doc.processed = True
        return doc

    def _extract_pdf(self, file_path: Path) -> tuple[str, List[ImageData]]:
        """Extract text and images from PDF."""
        content = []
        images = []

        try:
            # Use PyMuPDF for better extraction
            pdf_document = fitz.open(file_path)

            for page_num, page in enumerate(pdf_document):
                # Extract text
                text = page.get_text()
                content.append(text)

                # Extract images if enabled
                if self.settings.processing.extract_images:
                    image_list = page.get_images()

                    for img_index, img in enumerate(image_list):
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]

                        # Save image temporarily
                        img_id = f"img_{page_num}_{img_index}"
                        img_path = Path(self.settings.temp_directory) / f"{img_id}.png"

                        with open(img_path, "wb") as img_file:
                            img_file.write(image_bytes)

                        # OCR and alt text if enabled
                        ocr_text = ""
                        alt_text = ""

                        if self.settings.processing.ocr_images:
                            try:
                                ocr_text, alt_text = self.gemini.extract_text_from_image(img_path)
                            except Exception as e:
                                print(f"Warning: Image processing failed: {e}")
                                alt_text = f"Image on page {page_num + 1}"

                        images.append(ImageData(
                            id=img_id,
                            path=str(img_path),
                            alt_text=alt_text,
                            ocr_text=ocr_text,
                            position=page_num
                        ))

            pdf_document.close()
            return '\n\n'.join(content), images

        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")

    def _extract_docx(self, file_path: Path) -> tuple[str, List[ImageData]]:
        """Extract text and images from DOCX."""
        content = []
        images = []

        try:
            doc = DocxDocument(file_path)

            # Extract paragraphs
            for para in doc.paragraphs:
                content.append(para.text)

            # Extract tables
            for table in doc.tables:
                table_text = []
                for row in table.rows:
                    row_text = [cell.text for cell in row.cells]
                    table_text.append(' | '.join(row_text))
                content.append('\n'.join(table_text))

            # Extract images if enabled
            if self.settings.processing.extract_images:
                # Note: python-docx doesn't directly support image extraction
                # Would need additional processing with zipfile
                pass

            return '\n\n'.join(content), images

        except Exception as e:
            raise Exception(f"Error extracting DOCX: {str(e)}")

    def _extract_epub(self, file_path: Path) -> tuple[str, List[ImageData]]:
        """Extract text and images from EPUB."""
        content = []
        images = []

        try:
            book = epub.read_epub(file_path)

            for item in book.get_items():
                if item.get_type() == ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text = soup.get_text()
                    content.append(text)

                    # Extract images
                    if self.settings.processing.extract_images:
                        for img_tag in soup.find_all('img'):
                            alt_text = img_tag.get('alt', 'Image')
                            images.append(ImageData(
                                id=f"img_{len(images)}",
                                path=None,
                                alt_text=alt_text
                            ))

            return '\n\n'.join(content), images

        except Exception as e:
            raise Exception(f"Error extracting EPUB: {str(e)}")

    def _extract_mobi(self, file_path: Path) -> tuple[str, List[ImageData]]:
        """Extract text from MOBI (using external tools if available)."""
        # MOBI extraction requires external tools like calibre
        # For now, attempt basic text extraction
        try:
            with open(file_path, 'rb') as f:
                # This is a placeholder - proper MOBI parsing requires mobi package
                content = "MOBI format requires additional dependencies. Please convert to EPUB."
            return content, []
        except Exception as e:
            raise Exception(f"Error extracting MOBI: {str(e)}")

    def _extract_html(self, file_path: Path) -> tuple[str, List[ImageData]]:
        """Extract text from HTML."""
        images = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')

            # Extract images
            if self.settings.processing.extract_images:
                for img_tag in soup.find_all('img'):
                    alt_text = img_tag.get('alt', 'Image')
                    images.append(ImageData(
                        id=f"img_{len(images)}",
                        path=img_tag.get('src'),
                        alt_text=alt_text
                    ))

            content = soup.get_text(separator='\n')
            return content, images

        except Exception as e:
            raise Exception(f"Error extracting HTML: {str(e)}")

    def _extract_markdown(self, file_path: Path) -> tuple[str, List[ImageData]]:
        """Extract text from Markdown."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, []
        except Exception as e:
            raise Exception(f"Error extracting Markdown: {str(e)}")

    def _extract_image(self, file_path: Path) -> tuple[str, List[ImageData]]:
        """Extract text from image using OCR."""
        try:
            ocr_text, alt_text = self.gemini.extract_text_from_image(file_path)

            image_data = ImageData(
                id="img_0",
                path=str(file_path),
                alt_text=alt_text,
                ocr_text=ocr_text
            )

            return ocr_text, [image_data]

        except Exception as e:
            raise Exception(f"Error extracting image: {str(e)}")

    def _extract_txt(self, file_path: Path) -> tuple[str, List[ImageData]]:
        """Extract text from plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, []
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            return content, []
        except Exception as e:
            raise Exception(f"Error extracting text: {str(e)}")

    def process_webpage(self, url: str, custom_instructions: str = "") -> Document:
        """Process a webpage.

        Args:
            url: URL of the webpage
            custom_instructions: Optional custom processing instructions

        Returns:
            Processed Document object
        """
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title = soup.title.string if soup.title else url

            # Extract images
            images = []
            if self.settings.processing.extract_images:
                for img_tag in soup.find_all('img'):
                    alt_text = img_tag.get('alt', 'Image')
                    images.append(ImageData(
                        id=f"img_{len(images)}",
                        path=img_tag.get('src'),
                        alt_text=alt_text
                    ))

            # Extract text
            content = soup.get_text(separator='\n')

            # Create document
            doc = Document(
                file_path=Path(url),
                title=title,
                format=DocumentFormat.WEBPAGE,
                content=content,
                images=images
            )

            # Process with Gemini
            if content:
                processed = self.gemini.process_document_content(
                    content, Path(url), custom_instructions
                )
                doc.title = processed.get('title', doc.title)
                doc.language = processed.get('language', 'en')
                doc.metadata = processed.get('metadata', {})
                doc.content = processed.get('processed_content', content)
                structure_data = processed.get('structure', [])
                doc.structure = self._convert_structure(structure_data)

            doc.processed = True
            return doc

        except Exception as e:
            raise Exception(f"Error processing webpage: {str(e)}")

    def _convert_structure(self, structure_data: List[Dict]) -> List[DocumentStructure]:
        """Convert structure data from Gemini to DocumentStructure objects."""
        result = []

        for item in structure_data:
            struct = DocumentStructure(
                id=item.get('id', str(uuid.uuid4())),
                title=item.get('title', ''),
                level=item.get('level', 1),
                page_number=item.get('page_number'),
                content=item.get('content', '')
            )

            # Recursively process children
            if 'children' in item and item['children']:
                struct.children = self._convert_structure(item['children'])

            result.append(struct)

        return result

    def _detect_simple_structure(self, content: str) -> List[DocumentStructure]:
        """Detect basic structure from content without AI.

        Uses simple heuristics to find headings:
        - Lines that are all caps
        - Lines followed by ===== or -----
        - Lines starting with Chapter, Part, Section, etc.
        - Markdown-style # headings

        Args:
            content: Document content

        Returns:
            List of DocumentStructure objects
        """
        result = []
        lines = content.split('\n')

        i = 0
        section_counter = 0

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Check for underlined headings (next line is ==== or ----)
            is_heading = False
            level = 2

            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and all(c == '=' for c in next_line) and len(next_line) >= 3:
                    is_heading = True
                    level = 1
                    i += 1  # Skip the underline
                elif next_line and all(c == '-' for c in next_line) and len(next_line) >= 3:
                    is_heading = True
                    level = 2
                    i += 1  # Skip the underline

            # Check for markdown headings
            if line.startswith('#'):
                is_heading = True
                level = len(line) - len(line.lstrip('#'))
                line = line.lstrip('#').strip()

            # Check for chapter/section markers
            if re.match(r'^(Chapter|CHAPTER|Part|PART|Section|SECTION)\s+\d+', line):
                is_heading = True
                level = 1

            # Check for all-caps lines (potential headings)
            elif len(line) > 3 and line.isupper() and not line.endswith('.'):
                is_heading = True
                level = 2

            if is_heading and line:
                section_counter += 1
                struct = DocumentStructure(
                    id=f"section_{section_counter}",
                    title=line,
                    level=min(level, 6),
                    content=""
                )
                result.append(struct)

            i += 1

        return result
