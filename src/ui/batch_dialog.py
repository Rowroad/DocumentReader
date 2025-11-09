"""Batch conversion dialog."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton,
    QComboBox, QLabel, QProgressBar, QFileDialog, QListWidgetItem,
    QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
from typing import List, Tuple

from ..models import Settings, Document, OutputFormat
from ..processing import DocumentProcessor, FormatConverter
from ..utils import AccessibleButton, AccessibleLabel, ErrorHandler


class BatchProcessingThread(QThread):
    """Thread for batch processing."""

    progress_update = pyqtSignal(int, int, str)  # current, total, message
    file_complete = pyqtSignal(str, bool, str)  # filename, success, error
    batch_complete = pyqtSignal(int, int)  # successful, failed

    def __init__(self, files: List[Path], output_format: OutputFormat,
                 output_directory: Path, processor: DocumentProcessor,
                 converter: FormatConverter):
        super().__init__()
        self.files = files
        self.output_format = output_format
        self.output_directory = output_directory
        self.processor = processor
        self.converter = converter

    def run(self):
        """Run batch processing."""
        successful = 0
        failed = 0
        total = len(self.files)

        for i, file_path in enumerate(self.files):
            try:
                self.progress_update.emit(i + 1, total, f"Processing {file_path.name}...")

                # Process document
                document = self.processor.process_file(file_path)

                # Convert
                format_extensions = {
                    OutputFormat.TXT: ".txt",
                    OutputFormat.HTML: ".html",
                    OutputFormat.MARKDOWN: ".md",
                    OutputFormat.DOCX: ".docx",
                    OutputFormat.EPUB: ".epub",
                    OutputFormat.PDF: ".pdf",
                    OutputFormat.DAISY_TEXT: ".ncc.html",
                    OutputFormat.DAISY_AUDIO: ".ncc.html",
                    OutputFormat.M4B: ".m4b",
                }

                ext = format_extensions.get(self.output_format, ".txt")
                output_path = self.output_directory / (file_path.stem + ext)

                self.converter.convert(document, self.output_format, output_path)

                self.file_complete.emit(file_path.name, True, "")
                successful += 1

            except Exception as e:
                self.file_complete.emit(file_path.name, False, str(e))
                failed += 1

        self.batch_complete.emit(successful, failed)


class BatchConvertDialog(QDialog):
    """Dialog for batch document conversion."""

    def __init__(self, settings: Settings, processor: DocumentProcessor,
                 converter: FormatConverter, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.processor = processor
        self.converter = converter
        self.files = []

        self.setWindowTitle("Batch Convert Documents")
        self.setModal(True)
        self.resize(600, 500)

        # Accessibility
        self.setAccessibleName("Batch Convert Dialog")
        self.setAccessibleDescription("Convert multiple documents at once")

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)

        # Instructions
        instructions = QLabel(
            "Select multiple documents to convert them all to the same format."
        )
        instructions.setWordWrap(True)
        instructions.setAccessibleName("Instructions")
        layout.addWidget(instructions)

        # File list
        list_group = QGroupBox("Files to Convert")
        list_layout = QVBoxLayout()

        self.file_list = QListWidget()
        self.file_list.setAccessibleName("Files to Convert List")
        self.file_list.setAccessibleDescription(
            "List of files selected for batch conversion"
        )
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        list_layout.addWidget(self.file_list)

        # File list buttons
        file_buttons = QHBoxLayout()

        add_files_btn = AccessibleButton(
            "Add Files...",
            description="Add files to conversion list"
        )
        add_files_btn.clicked.connect(self.add_files)
        file_buttons.addWidget(add_files_btn)

        remove_files_btn = AccessibleButton(
            "Remove Selected",
            description="Remove selected files from list"
        )
        remove_files_btn.clicked.connect(self.remove_selected_files)
        file_buttons.addWidget(remove_files_btn)

        clear_files_btn = AccessibleButton(
            "Clear All",
            description="Clear all files from list"
        )
        clear_files_btn.clicked.connect(self.clear_files)
        file_buttons.addWidget(clear_files_btn)

        file_buttons.addStretch()

        list_layout.addLayout(file_buttons)
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # Output settings
        output_group = QGroupBox("Output Settings")
        output_layout = QFormLayout()

        # Format
        format_label = AccessibleLabel("Output Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Plain Text",
            "HTML",
            "Markdown",
            "DOCX",
            "EPUB",
            "PDF",
            "DAISY (Text)",
            "DAISY (Audio + Text)",
            "M4B Audiobook"
        ])
        self.format_combo.setAccessibleName("Output Format")
        self.format_combo.setAccessibleDescription("Select output format for all files")
        format_label.setBuddy(self.format_combo)
        output_layout.addRow(format_label, self.format_combo)

        # Output directory
        dir_label = AccessibleLabel("Output Directory:")
        dir_layout = QHBoxLayout()

        self.output_dir_label = QLabel(self.settings.output_directory)
        self.output_dir_label.setAccessibleName("Output Directory Path")
        dir_layout.addWidget(self.output_dir_label)

        browse_dir_btn = AccessibleButton(
            "Browse...",
            description="Browse for output directory"
        )
        browse_dir_btn.clicked.connect(self.browse_output_directory)
        dir_layout.addWidget(browse_dir_btn)

        output_layout.addRow(dir_label, dir_layout)

        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setAccessibleName("Batch Processing Progress")
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAccessibleName("Status")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.convert_button = AccessibleButton(
            "Convert All",
            description="Start batch conversion"
        )
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setDefault(True)

        self.close_button = AccessibleButton(
            "Close",
            description="Close dialog"
        )
        self.close_button.clicked.connect(self.reject)

        button_layout.addWidget(self.convert_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def add_files(self):
        """Add files to the list."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Documents",
            "",
            "All Supported Files (*.pdf *.docx *.txt *.epub *.mobi *.html *.md *.jpg *.jpeg *.png);;PDF Files (*.pdf);;Word Documents (*.docx);;Text Files (*.txt);;EPUB Files (*.epub);;All Files (*.*)"
        )

        for file_path in file_paths:
            path = Path(file_path)
            if path not in self.files:
                self.files.append(path)
                item = QListWidgetItem(path.name)
                item.setData(Qt.ItemDataRole.UserRole, str(path))
                self.file_list.addItem(item)

    def remove_selected_files(self):
        """Remove selected files from the list."""
        for item in self.file_list.selectedItems():
            file_path = Path(item.data(Qt.ItemDataRole.UserRole))
            if file_path in self.files:
                self.files.remove(file_path)
            self.file_list.takeItem(self.file_list.row(item))

    def clear_files(self):
        """Clear all files from the list."""
        self.files = []
        self.file_list.clear()

    def browse_output_directory(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_dir_label.text()
        )

        if directory:
            self.output_dir_label.setText(directory)

    def start_conversion(self):
        """Start batch conversion."""
        if not self.files:
            ErrorHandler.show_info_dialog(
                self,
                "No Files",
                "Please add files to convert."
            )
            return

        # Get output format
        format_map = {
            0: OutputFormat.TXT,
            1: OutputFormat.HTML,
            2: OutputFormat.MARKDOWN,
            3: OutputFormat.DOCX,
            4: OutputFormat.EPUB,
            5: OutputFormat.PDF,
            6: OutputFormat.DAISY_TEXT,
            7: OutputFormat.DAISY_AUDIO,
            8: OutputFormat.M4B,
        }

        output_format = format_map[self.format_combo.currentIndex()]
        output_directory = Path(self.output_dir_label.text())

        # Disable UI
        self.convert_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.files))
        self.progress_bar.setValue(0)
        self.status_label.setVisible(True)

        # Start processing thread
        self.processing_thread = BatchProcessingThread(
            self.files,
            output_format,
            output_directory,
            self.processor,
            self.converter
        )
        self.processing_thread.progress_update.connect(self.on_progress_update)
        self.processing_thread.file_complete.connect(self.on_file_complete)
        self.processing_thread.batch_complete.connect(self.on_batch_complete)
        self.processing_thread.start()

        self.errors = []

    def on_progress_update(self, current: int, total: int, message: str):
        """Handle progress update."""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"{current}/{total}: {message}")

    def on_file_complete(self, filename: str, success: bool, error: str):
        """Handle file completion."""
        if not success:
            self.errors.append(f"{filename}: {error}")

    def on_batch_complete(self, successful: int, failed: int):
        """Handle batch completion."""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
        self.convert_button.setEnabled(True)

        ErrorHandler.handle_batch_errors(self, successful, failed, self.errors)

        if failed == 0:
            # All successful, close dialog
            self.accept()
