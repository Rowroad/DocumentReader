"""Processing options dialog."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QRadioButton, QButtonGroup, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt

from ..utils import AccessibleButton, AccessibleLabel


class ProcessingOptionsDialog(QDialog):
    """Dialog to choose document processing method."""

    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.use_gemini = True  # Default to Gemini processing

        self.setWindowTitle("Processing Options")
        self.setModal(True)
        self.setMinimumWidth(500)

        # Accessibility
        self.setAccessibleName("Processing Options Dialog")
        self.setAccessibleDescription("Choose how to process the document")

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)

        # Title
        title_label = AccessibleLabel(f"How would you like to open '{self.filename}'?")
        title_label.setWordWrap(True)
        font = title_label.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)

        layout.addSpacing(10)

        # Radio button group
        option_group = QGroupBox("Processing Method")
        option_layout = QVBoxLayout()

        self.button_group = QButtonGroup(self)

        # Option 1: Process with Gemini AI
        self.gemini_radio = QRadioButton("Process with AI (Recommended)")
        self.gemini_radio.setAccessibleName("Process with AI")
        self.gemini_radio.setAccessibleDescription(
            "Use Gemini AI to extract structure, detect chapters, generate alt text for images, "
            "and improve accessibility. Uses API tokens."
        )
        self.gemini_radio.setChecked(True)
        self.button_group.addButton(self.gemini_radio)
        option_layout.addWidget(self.gemini_radio)

        gemini_desc = QLabel(
            "• Detects chapter structure and headings\n"
            "• Generates alt text for images (if present)\n"
            "• Extracts text from images with OCR\n"
            "• Improves formatting and accessibility\n"
            "• Uses Gemini API tokens"
        )
        gemini_desc.setStyleSheet("margin-left: 25px; color: #666;")
        gemini_desc.setWordWrap(True)
        option_layout.addWidget(gemini_desc)

        option_layout.addSpacing(15)

        # Option 2: Direct reading
        self.direct_radio = QRadioButton("Read directly (No AI)")
        self.direct_radio.setAccessibleName("Read directly")
        self.direct_radio.setAccessibleDescription(
            "Extract text directly from the file without AI processing. "
            "No API tokens used, but less structure and no image descriptions."
        )
        self.button_group.addButton(self.direct_radio)
        option_layout.addWidget(self.direct_radio)

        direct_desc = QLabel(
            "• Extracts text as-is from the document\n"
            "• No AI processing or structure detection\n"
            "• No image alt text generation\n"
            "• Faster and uses no API tokens\n"
            "• Good for simple text documents"
        )
        direct_desc.setStyleSheet("margin-left: 25px; color: #666;")
        direct_desc.setWordWrap(True)
        option_layout.addWidget(direct_desc)

        option_group.setLayout(option_layout)
        layout.addWidget(option_group)

        layout.addSpacing(10)

        # Note
        note_label = QLabel(
            "Note: For pure text documents (TXT, EPUB, etc.), "
            "direct reading is often sufficient and saves API tokens."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("font-style: italic; color: #444;")
        layout.addWidget(note_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = AccessibleButton(
            "OK",
            description="Confirm processing choice"
        )
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)

        self.cancel_button = AccessibleButton(
            "Cancel",
            description="Cancel opening document"
        )
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def accept(self):
        """Accept dialog and save choice."""
        self.use_gemini = self.gemini_radio.isChecked()
        super().accept()

    def get_use_gemini(self) -> bool:
        """Get whether to use Gemini processing.

        Returns:
            True if Gemini processing should be used
        """
        return self.use_gemini
