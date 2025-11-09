"""Main application window."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTabWidget, QProgressBar,
    QFileDialog, QMenuBar, QMenu, QStatusBar, QLabel, QComboBox,
    QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QKeySequence, QAction, QTextCursor
from pathlib import Path
import os

from ..models import Document, OutputFormat, Settings
from ..processing import GeminiClient, DocumentProcessor, FormatConverter
from ..utils import (
    ErrorHandler, AccessibleButton, create_accessible_action,
    KeyboardShortcuts, set_high_contrast_mode, SecurityManager
)
from .preferences_dialog import PreferencesDialog


class ProcessingThread(QThread):
    """Background thread for document processing."""

    progress_update = pyqtSignal(int, str)
    processing_complete = pyqtSignal(Document)
    processing_error = pyqtSignal(str)

    def __init__(self, processor: DocumentProcessor, file_path: Path,
                 custom_instructions: str = ""):
        super().__init__()
        self.processor = processor
        self.file_path = file_path
        self.custom_instructions = custom_instructions

    def run(self):
        """Run the processing."""
        try:
            self.progress_update.emit(10, "Loading document...")

            document = self.processor.process_file(
                self.file_path,
                self.custom_instructions
            )

            self.progress_update.emit(100, "Complete")
            self.processing_complete.emit(document)

        except Exception as e:
            self.processing_error.emit(str(e))


class ConversionThread(QThread):
    """Background thread for format conversion."""

    progress_update = pyqtSignal(int, str)
    conversion_complete = pyqtSignal(Path)
    conversion_error = pyqtSignal(str)

    def __init__(self, converter: FormatConverter, document: Document,
                 output_format: OutputFormat, output_path: Path):
        super().__init__()
        self.converter = converter
        self.document = document
        self.output_format = output_format
        self.output_path = output_path

    def run(self):
        """Run the conversion."""
        try:
            self.progress_update.emit(10, f"Converting to {self.output_format.value}...")

            result_path = self.converter.convert(
                self.document,
                self.output_format,
                self.output_path
            )

            self.progress_update.emit(100, "Conversion complete")
            self.conversion_complete.emit(result_path)

        except Exception as e:
            self.conversion_error.emit(str(e))


class DocumentTab(QWidget):
    """Widget for a single document tab."""

    def __init__(self, document: Document, parent=None):
        super().__init__(parent)
        self.document = document
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Splitter for tree view and document view
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Document structure tree
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("Document Structure")
        self.tree_widget.setAccessibleName("Document Structure Tree")
        self.tree_widget.setAccessibleDescription(
            "Hierarchical view of document headings and sections"
        )
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)

        # Populate tree
        self.populate_tree()

        splitter.addWidget(self.tree_widget)

        # Document content view (read-only text edit for accessibility)
        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)
        self.content_view.setAccessibleName(f"{self.document.title} content")
        self.content_view.setAccessibleDescription("Document content view - read only")
        self.content_view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Load document content as text
        self.load_document_content()

        splitter.addWidget(self.content_view)

        # Set splitter sizes (30% tree, 70% content)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)

    def populate_tree(self):
        """Populate the tree widget with document structure."""
        self.tree_widget.clear()

        if not self.document.structure:
            # No structure, show placeholder
            item = QTreeWidgetItem(["No structure detected"])
            item.setDisabled(True)
            self.tree_widget.addTopLevelItem(item)
            return

        # Add structure items
        for section in self.document.structure:
            self.add_tree_item(section, self.tree_widget)

        # Expand first level
        self.tree_widget.expandToDepth(0)

    def add_tree_item(self, section, parent):
        """Add a structure item to the tree.

        Args:
            section: DocumentStructure object
            parent: Parent tree widget or item
        """
        item = QTreeWidgetItem([section.title])
        item.setData(0, Qt.ItemDataRole.UserRole, section.id)

        if isinstance(parent, QTreeWidget):
            parent.addTopLevelItem(item)
        else:
            parent.addChild(item)

        # Add children
        for child in section.children:
            self.add_tree_item(child, item)

    def load_document_content(self):
        """Load document content into text view."""
        # Generate formatted text with accessibility features
        text = self.generate_accessible_text()
        self.content_view.setPlainText(text)

        # Store section positions for navigation
        self.section_positions = {}
        if self.document.structure:
            self._calculate_section_positions()

    def generate_accessible_text(self) -> str:
        """Generate accessible plain text for document."""
        lines = []

        # Title
        lines.append("=" * 80)
        lines.append(self.document.title.upper())
        lines.append("=" * 80)
        lines.append("")

        # Metadata
        if self.document.metadata:
            if 'author' in self.document.metadata:
                lines.append(f"Author: {self.document.metadata['author']}")
            if 'description' in self.document.metadata:
                lines.append(f"Description: {self.document.metadata['description']}")
            lines.append("")
            lines.append("-" * 80)
            lines.append("")

        # Content with structure
        if self.document.structure:
            for section in self.document.structure:
                lines.extend(self._section_to_text(section, level=1))
        else:
            # Plain content
            lines.append(self.document.content)

        return '\n'.join(lines)

    def _section_to_text(self, section, level: int = 1) -> list:
        """Convert a section to text lines.

        Args:
            section: DocumentStructure object
            level: Heading level

        Returns:
            List of text lines
        """
        lines = []

        # Add heading with markers for the level
        if level == 1:
            lines.append("")
            lines.append("=" * 80)
            lines.append(section.title.upper())
            lines.append("=" * 80)
        elif level == 2:
            lines.append("")
            lines.append(section.title)
            lines.append("-" * len(section.title))
        else:
            lines.append("")
            prefix = "  " * (level - 2)
            lines.append(f"{prefix}{'*' * level} {section.title}")

        lines.append("")

        # Add content
        if section.content:
            # Indent content based on level
            indent = "  " * (level - 1)
            for line in section.content.split('\n'):
                if line.strip():
                    lines.append(f"{indent}{line}")
                else:
                    lines.append("")

        # Add children
        for child in section.children:
            lines.extend(self._section_to_text(child, level + 1))

        return lines

    def _calculate_section_positions(self):
        """Calculate text positions for each section for navigation."""
        text = self.content_view.toPlainText()
        lines = text.split('\n')

        def find_section(section, start_line=0):
            # Look for section title in the text
            for i in range(start_line, len(lines)):
                if section.title in lines[i]:
                    # Calculate character position
                    char_pos = sum(len(line) + 1 for line in lines[:i])
                    self.section_positions[section.id] = char_pos
                    # Recursively find children
                    for child in section.children:
                        find_section(child, i + 1)
                    break

        for section in self.document.structure:
            find_section(section)

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item click to navigate to section.

        Args:
            item: Clicked tree item
            column: Column index
        """
        section_id = item.data(0, Qt.ItemDataRole.UserRole)
        if section_id and section_id in self.section_positions:
            # Navigate to section in text view
            cursor = self.content_view.textCursor()
            cursor.setPosition(self.section_positions[section_id])
            self.content_view.setTextCursor(cursor)
            self.content_view.ensureCursorVisible()
            self.content_view.setFocus()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Document Reader - Accessible Document Converter")
        self.resize(1200, 800)

        # Accessibility
        self.setAccessibleName("Document Reader Main Window")

        # Settings
        self.load_settings()

        # Initialize components
        self.gemini_client = None
        self.processor = None
        self.converter = None
        self.security_manager = SecurityManager(self.settings.temp_directory)

        self.init_clients()

        # Document management
        self.current_document = None
        self.open_documents = {}  # tab_index -> Document

        # Menu actions (to enable/disable based on state)
        self.close_tab_action = None
        self.conversion_actions = []

        self.setup_ui()
        self.create_menus()
        self.apply_settings()

        # Update menu states initially (no documents open)
        self.update_menu_states()

    def load_settings(self):
        """Load application settings."""
        settings_file = Path.home() / ".documentreader" / "settings.json"
        self.settings = Settings.load(settings_file)

    def init_clients(self):
        """Initialize API clients."""
        if self.settings.gemini_api_key:
            try:
                self.gemini_client = GeminiClient(
                    self.settings.gemini_api_key,
                    self.settings
                )
                self.processor = DocumentProcessor(
                    self.settings,
                    self.gemini_client
                )
                self.converter = FormatConverter(
                    self.settings,
                    self.gemini_client
                )
            except Exception as e:
                ErrorHandler.handle_api_error(self, str(e))

    def setup_ui(self):
        """Setup the UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Tab widget for multiple documents
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setAccessibleName("Open Documents")
        self.tab_widget.setAccessibleDescription("Tabs for open documents")
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.tab_widget)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setAccessibleName("Processing Progress")
        self.progress_bar.setAccessibleDescription("Shows processing progress")
        self.progress_bar.setVisible(False)

        layout.addWidget(self.progress_bar)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setAccessibleName("Status")
        self.status_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.status_bar.addWidget(self.status_label)

    def create_menus(self):
        """Create application menus."""
        menubar = self.menuBar()
        menubar.setAccessibleName("Main Menu")

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.setAccessibleName("File Menu")

        open_action = create_accessible_action(
            "&Open Document...",
            KeyboardShortcuts.OPEN,
            "Open a document file",
            self
        )
        open_action.triggered.connect(self.open_document)
        file_menu.addAction(open_action)

        batch_action = create_accessible_action(
            "&Batch Convert...",
            KeyboardShortcuts.BATCH_CONVERT,
            "Convert multiple documents",
            self
        )
        batch_action.triggered.connect(self.batch_convert)
        file_menu.addAction(batch_action)

        file_menu.addSeparator()

        self.close_tab_action = create_accessible_action(
            "&Close Tab",
            KeyboardShortcuts.CLOSE_TAB,
            "Close current tab",
            self
        )
        self.close_tab_action.triggered.connect(self.close_current_tab)
        file_menu.addAction(self.close_tab_action)

        file_menu.addSeparator()

        quit_action = create_accessible_action(
            "&Quit",
            KeyboardShortcuts.QUIT,
            "Quit application",
            self
        )
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Convert menu
        convert_menu = menubar.addMenu("&Convert")
        convert_menu.setAccessibleName("Convert Menu")

        self.create_conversion_actions(convert_menu)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.setAccessibleName("Edit Menu")

        prefs_action = create_accessible_action(
            "&Preferences...",
            KeyboardShortcuts.PREFERENCES,
            "Open preferences",
            self
        )
        prefs_action.triggered.connect(self.show_preferences)
        edit_menu.addAction(prefs_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.setAccessibleName("Tools Menu")

        cleanup_action = create_accessible_action(
            "Cleanup Old Files...",
            None,
            "Clean up old temporary files",
            self
        )
        cleanup_action.triggered.connect(self.cleanup_old_files)
        tools_menu.addAction(cleanup_action)

        storage_action = create_accessible_action(
            "Storage Information...",
            None,
            "View storage information",
            self
        )
        storage_action.triggered.connect(self.show_storage_info)
        tools_menu.addAction(storage_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.setAccessibleName("Help Menu")

        about_action = create_accessible_action(
            "&About",
            None,
            "About Document Reader",
            self
        )
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_conversion_actions(self, menu: QMenu):
        """Create conversion menu actions.

        Args:
            menu: Convert menu
        """
        formats = [
            ("Plain Text", OutputFormat.TXT),
            ("HTML", OutputFormat.HTML),
            ("Markdown", OutputFormat.MARKDOWN),
            ("DOCX", OutputFormat.DOCX),
            ("EPUB", OutputFormat.EPUB),
            ("PDF", OutputFormat.PDF),
            ("DAISY (Text)", OutputFormat.DAISY_TEXT),
            ("DAISY (Audio + Text)", OutputFormat.DAISY_AUDIO),
            ("M4B Audiobook", OutputFormat.M4B),
        ]

        for name, fmt in formats:
            action = create_accessible_action(
                f"Convert to {name}",
                None,
                f"Convert current document to {name}",
                self
            )
            action.triggered.connect(lambda checked, f=fmt: self.convert_document(f))
            menu.addAction(action)
            self.conversion_actions.append(action)  # Store for enabling/disabling

    def open_document(self):
        """Open a document file."""
        if not self.gemini_client:
            ErrorHandler.handle_missing_api_key(self)
            self.show_preferences()
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            "",
            "All Supported Files (*.pdf *.docx *.txt *.epub *.mobi *.html *.md *.jpg *.jpeg *.png);;PDF Files (*.pdf);;Word Documents (*.docx);;Text Files (*.txt);;EPUB Files (*.epub);;MOBI Files (*.mobi);;HTML Files (*.html *.htm);;Markdown Files (*.md);;Images (*.jpg *.jpeg *.png)"
        )

        if file_path:
            self.process_document(Path(file_path))

    def process_document(self, file_path: Path, custom_instructions: str = ""):
        """Process a document file.

        Args:
            file_path: Path to document
            custom_instructions: Optional custom instructions
        """
        self.status_label.setText(f"Processing {file_path.name}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create processing thread
        self.processing_thread = ProcessingThread(
            self.processor,
            file_path,
            custom_instructions
        )
        self.processing_thread.progress_update.connect(self.on_processing_progress)
        self.processing_thread.processing_complete.connect(self.on_processing_complete)
        self.processing_thread.processing_error.connect(self.on_processing_error)
        self.processing_thread.start()

    def on_processing_progress(self, value: int, message: str):
        """Handle processing progress update.

        Args:
            value: Progress percentage
            message: Status message
        """
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def on_processing_complete(self, document: Document):
        """Handle processing completion.

        Args:
            document: Processed document
        """
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Loaded: {document.title}")

        # Create tab for document
        tab = DocumentTab(document)
        tab_index = self.tab_widget.addTab(tab, document.title)
        self.tab_widget.setCurrentIndex(tab_index)

        self.open_documents[tab_index] = document
        self.current_document = document

        # Update menu states now that we have a document
        self.update_menu_states()

    def on_processing_error(self, error: str):
        """Handle processing error.

        Args:
            error: Error message
        """
        self.progress_bar.setVisible(False)
        self.status_label.setText("Error processing document")

        ErrorHandler.handle_processing_error(self, error)

    def convert_document(self, output_format: OutputFormat):
        """Convert current document to specified format.

        Args:
            output_format: Target output format
        """
        if not self.current_document:
            ErrorHandler.show_info_dialog(
                self,
                "No Document",
                "Please open a document first."
            )
            return

        # Get output file name
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

        ext = format_extensions.get(output_format, ".txt")
        default_name = self.current_document.file_path.stem + ext

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Converted Document",
            str(Path(self.settings.output_directory) / default_name),
            f"Output Files (*{ext})"
        )

        if output_path:
            self.run_conversion(output_format, Path(output_path))

    def run_conversion(self, output_format: OutputFormat, output_path: Path):
        """Run document conversion.

        Args:
            output_format: Target format
            output_path: Output file path
        """
        self.status_label.setText(f"Converting to {output_format.value}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Create conversion thread
        self.conversion_thread = ConversionThread(
            self.converter,
            self.current_document,
            output_format,
            output_path
        )
        self.conversion_thread.progress_update.connect(self.on_conversion_progress)
        self.conversion_thread.conversion_complete.connect(self.on_conversion_complete)
        self.conversion_thread.conversion_error.connect(self.on_conversion_error)
        self.conversion_thread.start()

    def on_conversion_progress(self, value: int, message: str):
        """Handle conversion progress."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def on_conversion_complete(self, output_path: Path):
        """Handle conversion completion."""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Saved: {output_path.name}")

        ErrorHandler.show_info_dialog(
            self,
            "Conversion Complete",
            f"Document converted successfully:\n{output_path}"
        )

    def on_conversion_error(self, error: str):
        """Handle conversion error."""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Conversion error")

        ErrorHandler.handle_conversion_error(self, "output format", error)

    def batch_convert(self):
        """Batch convert multiple documents."""
        if not self.gemini_client:
            ErrorHandler.handle_missing_api_key(self)
            return

        # Import batch dialog here to avoid circular imports
        from .batch_dialog import BatchConvertDialog

        dialog = BatchConvertDialog(self.settings, self.processor, self.converter, self)
        dialog.exec()

    def close_tab(self, index: int):
        """Close a tab.

        Args:
            index: Tab index
        """
        self.tab_widget.removeTab(index)
        if index in self.open_documents:
            del self.open_documents[index]

        # Update current document
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0 and current_index in self.open_documents:
            self.current_document = self.open_documents[current_index]
        else:
            self.current_document = None

        # Update menu states after closing tab
        self.update_menu_states()

    def close_current_tab(self):
        """Close the current tab."""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)

    def on_tab_changed(self, index: int):
        """Handle tab change.

        Args:
            index: New tab index
        """
        if index >= 0 and index in self.open_documents:
            self.current_document = self.open_documents[index]
            self.status_label.setText(f"Viewing: {self.current_document.title}")
        else:
            self.current_document = None
            self.status_label.setText("Ready")

    def update_menu_states(self):
        """Update menu item enabled/disabled states based on current document."""
        has_document = self.current_document is not None

        # Enable/disable close tab action
        if self.close_tab_action:
            self.close_tab_action.setEnabled(has_document)

        # Enable/disable all conversion actions
        for action in self.conversion_actions:
            action.setEnabled(has_document)

    def show_preferences(self):
        """Show preferences dialog."""
        try:
            dialog = PreferencesDialog(self.settings, self)
            dialog.settings_changed.connect(self.on_settings_changed)
            dialog.exec()
        except Exception as e:
            import traceback
            error_msg = f"Error opening preferences:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(error_msg)
            ErrorHandler.show_error_dialog(
                self,
                "Preferences Error",
                "Failed to open preferences dialog.",
                details=error_msg
            )

    def on_settings_changed(self, settings: Settings):
        """Handle settings change.

        Args:
            settings: Updated settings
        """
        self.settings = settings
        self.init_clients()
        self.apply_settings()

    def apply_settings(self):
        """Apply UI settings."""
        # High contrast mode
        set_high_contrast_mode(self, self.settings.ui.high_contrast)

        # Font size
        font = self.font()
        font.setPointSize(self.settings.ui.font_size)
        self.setFont(font)

    def cleanup_old_files(self):
        """Clean up old files."""
        files_to_delete = self.security_manager.get_files_for_cleanup(
            self.settings.security.auto_delete_days
        )

        if not files_to_delete:
            ErrorHandler.show_info_dialog(
                self,
                "No Files to Clean",
                "No files found for cleanup."
            )
            return

        total_size = sum(size for _, _, size in files_to_delete)
        message = f"Found {len(files_to_delete)} files to delete\n"
        message += f"Total size: {total_size / (1024*1024):.2f} MB\n\n"
        message += "Delete these files?"

        if ErrorHandler.show_confirmation_dialog(self, "Cleanup Files", message):
            count, _ = self.security_manager.cleanup_old_files(
                self.settings.security.auto_delete_days,
                auto=True
            )

            ErrorHandler.show_info_dialog(
                self,
                "Cleanup Complete",
                f"Deleted {count} files."
            )

    def show_storage_info(self):
        """Show storage information."""
        info = self.security_manager.get_storage_info()

        message = f"Stored files: {info['file_count']}\n"
        message += f"Total size: {info['total_size_mb']:.2f} MB\n"

        if info['oldest_file']:
            message += f"\nOldest file: {info['oldest_file']}\n"
            message += f"Stored on: {info['oldest_date']}"

        ErrorHandler.show_info_dialog(
            self,
            "Storage Information",
            message
        )

    def show_about(self):
        """Show about dialog."""
        message = """Document Reader - Accessible Document Converter

A Windows desktop application for processing and converting documents
for blind and visually impaired users.

Features:
• Multiple input formats (PDF, DOCX, EPUB, images, etc.)
• Accessible output formats (DAISY, audiobooks, etc.)
• OCR and text extraction with Gemini AI
• Full keyboard navigation and screen reader support
• Text-to-speech generation

Version: 1.0.0
"""

        ErrorHandler.show_info_dialog(
            self,
            "About Document Reader",
            message
        )
