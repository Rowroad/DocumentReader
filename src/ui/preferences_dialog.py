"""Preferences dialog for application settings."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QComboBox, QSpinBox,
    QDoubleSpinBox, QCheckBox, QTextEdit, QGroupBox,
    QFileDialog, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path

from ..models import Settings, TTSSettings, ProcessingSettings, SecuritySettings, UISettings
from ..utils import (
    AccessibleButton, AccessibleLabel, AccessibleLineEdit,
    AccessibleTextEdit, setup_focus_chain, KeyboardShortcuts
)


class PreferencesDialog(QDialog):
    """Accessible preferences dialog."""

    settings_changed = pyqtSignal(Settings)

    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Preferences")
        self.setModal(True)
        self.resize(700, 600)

        # Accessibility
        self.setAccessibleName("Preferences Dialog")
        self.setAccessibleDescription("Configure application settings")

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)

        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setAccessibleName("Settings Categories")

        # Create tabs
        self.general_tab = self.create_general_tab()
        self.processing_tab = self.create_processing_tab()
        self.tts_tab = self.create_tts_tab()
        self.security_tab = self.create_security_tab()
        self.ui_tab = self.create_ui_tab()

        self.tab_widget.addTab(self.general_tab, "General")
        self.tab_widget.addTab(self.processing_tab, "Processing")
        self.tab_widget.addTab(self.tts_tab, "Text-to-Speech")
        self.tab_widget.addTab(self.security_tab, "Security && Privacy")
        self.tab_widget.addTab(self.ui_tab, "Interface")

        layout.addWidget(self.tab_widget)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = AccessibleButton(
            "Save",
            description="Save settings and close dialog"
        )
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setDefault(True)

        self.cancel_button = AccessibleButton(
            "Cancel",
            description="Cancel changes and close dialog"
        )
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Setup focus chain
        setup_focus_chain([self.tab_widget, self.save_button, self.cancel_button])

    def create_general_tab(self) -> QWidget:
        """Create general settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # API Key
        api_key_label = AccessibleLabel("Gemini API Key:")
        self.api_key_input = AccessibleLineEdit(
            label="Gemini API Key",
            placeholder="Enter your Google AI API key"
        )
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_key_label.setBuddy(self.api_key_input)
        layout.addRow(api_key_label, self.api_key_input)

        # Show API key button
        show_key_btn = AccessibleButton(
            "Show/Hide API Key",
            description="Toggle API key visibility"
        )
        show_key_btn.clicked.connect(self.toggle_api_key_visibility)
        layout.addRow("", show_key_btn)

        # Output directory
        output_label = AccessibleLabel("Output Directory:")
        output_layout = QHBoxLayout()
        self.output_dir_input = AccessibleLineEdit(
            label="Output Directory",
            placeholder="Select output directory"
        )
        output_layout.addWidget(self.output_dir_input)

        browse_output_btn = AccessibleButton(
            "Browse...",
            description="Browse for output directory"
        )
        browse_output_btn.clicked.connect(self.browse_output_directory)
        output_layout.addWidget(browse_output_btn)

        layout.addRow(output_label, output_layout)

        # System prompt
        prompt_label = AccessibleLabel("System Prompt:")
        self.system_prompt_input = AccessibleTextEdit(
            label="System Prompt",
            read_only=False
        )
        self.system_prompt_input.setMinimumHeight(200)
        prompt_label.setBuddy(self.system_prompt_input)
        layout.addRow(prompt_label, self.system_prompt_input)

        # Reset to default button
        reset_prompt_btn = AccessibleButton(
            "Reset to Default",
            description="Reset system prompt to default"
        )
        reset_prompt_btn.clicked.connect(self.reset_system_prompt)
        layout.addRow("", reset_prompt_btn)

        layout.addStretch()
        return widget

    def create_processing_tab(self) -> QWidget:
        """Create processing settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Accuracy mode
        mode_group = QGroupBox("Processing Mode")
        mode_layout = QFormLayout()

        mode_label = AccessibleLabel("Accuracy Mode:")
        self.accuracy_combo = QComboBox()
        self.accuracy_combo.addItems(["High", "Balanced", "Speed"])
        self.accuracy_combo.setAccessibleName("Accuracy Mode")
        self.accuracy_combo.setAccessibleDescription(
            "Choose between accuracy and processing speed"
        )
        mode_label.setBuddy(self.accuracy_combo)
        mode_layout.addRow(mode_label, self.accuracy_combo)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # Options
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()

        self.preserve_formatting_check = QCheckBox("Preserve Formatting")
        self.preserve_formatting_check.setAccessibleName("Preserve Formatting")
        self.preserve_formatting_check.setAccessibleDescription(
            "Maintain document structure and formatting"
        )

        self.extract_images_check = QCheckBox("Extract Images")
        self.extract_images_check.setAccessibleName("Extract Images")
        self.extract_images_check.setAccessibleDescription(
            "Extract images from documents"
        )

        self.ocr_images_check = QCheckBox("OCR Images")
        self.ocr_images_check.setAccessibleName("OCR Images")
        self.ocr_images_check.setAccessibleDescription(
            "Extract text from images using OCR"
        )

        self.detect_language_check = QCheckBox("Auto-detect Language")
        self.detect_language_check.setAccessibleName("Auto-detect Language")
        self.detect_language_check.setAccessibleDescription(
            "Automatically detect document language"
        )

        options_layout.addWidget(self.preserve_formatting_check)
        options_layout.addWidget(self.extract_images_check)
        options_layout.addWidget(self.ocr_images_check)
        options_layout.addWidget(self.detect_language_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        layout.addStretch()
        return widget

    def create_tts_tab(self) -> QWidget:
        """Create TTS settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # TTS Engine
        engine_label = AccessibleLabel("TTS Engine:")
        self.tts_engine_combo = QComboBox()
        self.tts_engine_combo.addItems(["Google TTS", "SAPI 5 (Windows)"])
        self.tts_engine_combo.setAccessibleName("TTS Engine")
        self.tts_engine_combo.setAccessibleDescription("Select text-to-speech engine")
        self.tts_engine_combo.currentIndexChanged.connect(self.on_tts_engine_changed)
        engine_label.setBuddy(self.tts_engine_combo)
        layout.addRow(engine_label, self.tts_engine_combo)

        # Google TTS Voice
        self.google_voice_label = AccessibleLabel("Google Voice:")
        self.voice_combo = QComboBox()
        self.voice_combo.addItems([
            "en-US-Neural2-A",
            "en-US-Neural2-C",
            "en-US-Neural2-D",
            "en-US-Neural2-E",
            "en-GB-Neural2-A",
            "en-GB-Neural2-B"
        ])
        self.voice_combo.setAccessibleName("Google TTS Voice")
        self.voice_combo.setAccessibleDescription("Select Google text-to-speech voice")
        self.google_voice_label.setBuddy(self.voice_combo)
        layout.addRow(self.google_voice_label, self.voice_combo)

        # SAPI5 Voice
        self.sapi5_voice_label = AccessibleLabel("SAPI 5 Voice:")
        self.sapi5_voice_combo = QComboBox()
        self.sapi5_voice_combo.setAccessibleName("SAPI 5 Voice")
        self.sapi5_voice_combo.setAccessibleDescription("Select SAPI 5 voice")
        self.sapi5_voice_label.setBuddy(self.sapi5_voice_combo)
        layout.addRow(self.sapi5_voice_label, self.sapi5_voice_combo)

        # Load SAPI5 voices
        self.load_sapi5_voices()

        # Language
        lang_label = AccessibleLabel("Language:")
        self.tts_language_input = AccessibleLineEdit(
            label="TTS Language",
            placeholder="e.g., en-US"
        )
        lang_label.setBuddy(self.tts_language_input)
        layout.addRow(lang_label, self.tts_language_input)

        # Speed
        speed_label = AccessibleLabel("Speed:")
        self.speed_spinner = QDoubleSpinBox()
        self.speed_spinner.setRange(0.5, 2.0)
        self.speed_spinner.setSingleStep(0.1)
        self.speed_spinner.setValue(1.0)
        self.speed_spinner.setAccessibleName("Speech Speed")
        self.speed_spinner.setAccessibleDescription("Speech speed multiplier")
        speed_label.setBuddy(self.speed_spinner)
        layout.addRow(speed_label, self.speed_spinner)

        # Pitch
        pitch_label = AccessibleLabel("Pitch:")
        self.pitch_spinner = QDoubleSpinBox()
        self.pitch_spinner.setRange(-20.0, 20.0)
        self.pitch_spinner.setSingleStep(1.0)
        self.pitch_spinner.setValue(0.0)
        self.pitch_spinner.setAccessibleName("Speech Pitch")
        self.pitch_spinner.setAccessibleDescription("Speech pitch adjustment")
        pitch_label.setBuddy(self.pitch_spinner)
        layout.addRow(pitch_label, self.pitch_spinner)

        # Note
        note_label = QLabel(
            "Note: Google TTS requires Google Cloud Text-to-Speech API. "
            "SAPI 5 is available on Windows without additional setup."
        )
        note_label.setWordWrap(True)
        layout.addRow(note_label)

        return widget

    def create_security_tab(self) -> QWidget:
        """Create security settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Auto-delete days
        delete_label = AccessibleLabel("Auto-delete after (days):")
        self.delete_days_spinner = QSpinBox()
        self.delete_days_spinner.setRange(1, 365)
        self.delete_days_spinner.setValue(7)
        self.delete_days_spinner.setAccessibleName("Auto-delete Days")
        self.delete_days_spinner.setAccessibleDescription(
            "Automatically delete local files after this many days"
        )
        delete_label.setBuddy(self.delete_days_spinner)
        layout.addRow(delete_label, self.delete_days_spinner)

        # Options
        self.delete_cloud_check = QCheckBox("Request cloud data deletion")
        self.delete_cloud_check.setAccessibleName("Delete Cloud Data")
        self.delete_cloud_check.setAccessibleDescription(
            "Request deletion of data from Gemini servers after processing"
        )
        layout.addRow("", self.delete_cloud_check)

        self.encrypt_storage_check = QCheckBox("Encrypt local storage")
        self.encrypt_storage_check.setAccessibleName("Encrypt Local Storage")
        self.encrypt_storage_check.setAccessibleDescription(
            "Encrypt files stored locally"
        )
        layout.addRow("", self.encrypt_storage_check)

        return widget

    def create_ui_tab(self) -> QWidget:
        """Create UI settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Theme
        theme_label = AccessibleLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        self.theme_combo.setAccessibleName("Application Theme")
        theme_label.setBuddy(self.theme_combo)
        layout.addRow(theme_label, self.theme_combo)

        # Font size
        font_label = AccessibleLabel("Font Size:")
        self.font_size_spinner = QSpinBox()
        self.font_size_spinner.setRange(8, 24)
        self.font_size_spinner.setValue(12)
        self.font_size_spinner.setAccessibleName("Font Size")
        font_label.setBuddy(self.font_size_spinner)
        layout.addRow(font_label, self.font_size_spinner)

        # High contrast
        self.high_contrast_check = QCheckBox("High Contrast Mode")
        self.high_contrast_check.setAccessibleName("High Contrast Mode")
        self.high_contrast_check.setAccessibleDescription(
            "Enable high contrast mode for better visibility"
        )
        layout.addRow("", self.high_contrast_check)

        return widget

    def load_settings(self):
        """Load settings into UI."""
        # General
        self.api_key_input.setText(self.settings.gemini_api_key)
        self.output_dir_input.setText(self.settings.output_directory)
        self.system_prompt_input.setPlainText(self.settings.system_prompt)

        # Processing
        mode_map = {"high": 0, "balanced": 1, "speed": 2}
        self.accuracy_combo.setCurrentIndex(
            mode_map.get(self.settings.processing.accuracy_mode, 0)
        )
        self.preserve_formatting_check.setChecked(
            self.settings.processing.preserve_formatting
        )
        self.extract_images_check.setChecked(
            self.settings.processing.extract_images
        )
        self.ocr_images_check.setChecked(
            self.settings.processing.ocr_images
        )
        self.detect_language_check.setChecked(
            self.settings.processing.detect_language
        )

        # TTS
        # Set TTS engine
        engine_index = 0 if self.settings.tts.engine == "google" else 1
        self.tts_engine_combo.setCurrentIndex(engine_index)

        # Set Google voice
        voice_index = self.voice_combo.findText(self.settings.tts.voice)
        if voice_index >= 0:
            self.voice_combo.setCurrentIndex(voice_index)

        # Set SAPI5 voice
        if self.settings.tts.sapi5_voice:
            sapi5_index = self.sapi5_voice_combo.findData(self.settings.tts.sapi5_voice)
            if sapi5_index >= 0:
                self.sapi5_voice_combo.setCurrentIndex(sapi5_index)

        self.tts_language_input.setText(self.settings.tts.language)
        self.speed_spinner.setValue(self.settings.tts.speed)
        self.pitch_spinner.setValue(self.settings.tts.pitch)

        # Update visibility based on engine
        self.on_tts_engine_changed(engine_index)

        # Security
        self.delete_days_spinner.setValue(self.settings.security.auto_delete_days)
        self.delete_cloud_check.setChecked(self.settings.security.delete_cloud_data)
        self.encrypt_storage_check.setChecked(
            self.settings.security.encrypt_local_storage
        )

        # UI
        theme_map = {"system": 0, "light": 1, "dark": 2}
        self.theme_combo.setCurrentIndex(
            theme_map.get(self.settings.ui.theme, 0)
        )
        self.font_size_spinner.setValue(self.settings.ui.font_size)
        self.high_contrast_check.setChecked(self.settings.ui.high_contrast)

    def save_settings(self):
        """Save settings from UI."""
        # General
        self.settings.gemini_api_key = self.api_key_input.text()
        self.settings.output_directory = self.output_dir_input.text()
        self.settings.system_prompt = self.system_prompt_input.toPlainText()

        # Processing
        mode_map = {0: "high", 1: "balanced", 2: "speed"}
        self.settings.processing.accuracy_mode = mode_map[
            self.accuracy_combo.currentIndex()
        ]
        self.settings.processing.preserve_formatting = \
            self.preserve_formatting_check.isChecked()
        self.settings.processing.extract_images = \
            self.extract_images_check.isChecked()
        self.settings.processing.ocr_images = \
            self.ocr_images_check.isChecked()
        self.settings.processing.detect_language = \
            self.detect_language_check.isChecked()

        # TTS
        self.settings.tts.engine = "google" if self.tts_engine_combo.currentIndex() == 0 else "sapi5"
        self.settings.tts.voice = self.voice_combo.currentText()
        self.settings.tts.sapi5_voice = self.sapi5_voice_combo.currentData() or ""
        self.settings.tts.language = self.tts_language_input.text()
        self.settings.tts.speed = self.speed_spinner.value()
        self.settings.tts.pitch = self.pitch_spinner.value()

        # Security
        self.settings.security.auto_delete_days = self.delete_days_spinner.value()
        self.settings.security.delete_cloud_data = self.delete_cloud_check.isChecked()
        self.settings.security.encrypt_local_storage = \
            self.encrypt_storage_check.isChecked()

        # UI
        theme_map = {0: "system", 1: "light", 2: "dark"}
        self.settings.ui.theme = theme_map[self.theme_combo.currentIndex()]
        self.settings.ui.font_size = self.font_size_spinner.value()
        self.settings.ui.high_contrast = self.high_contrast_check.isChecked()

        # Save to file
        settings_file = Path.home() / ".documentreader" / "settings.json"
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        self.settings.save(settings_file)

        # Emit signal
        self.settings_changed.emit(self.settings)

        self.accept()

    def toggle_api_key_visibility(self):
        """Toggle API key visibility."""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

    def browse_output_directory(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_dir_input.text()
        )

        if directory:
            self.output_dir_input.setText(directory)

    def reset_system_prompt(self):
        """Reset system prompt to default."""
        default_prompt = Settings.get_default_system_prompt()
        self.system_prompt_input.setPlainText(default_prompt)

    def on_tts_engine_changed(self, index: int):
        """Handle TTS engine selection change."""
        is_google = (index == 0)

        # Show/hide appropriate voice selection
        self.google_voice_label.setVisible(is_google)
        self.voice_combo.setVisible(is_google)
        self.sapi5_voice_label.setVisible(not is_google)
        self.sapi5_voice_combo.setVisible(not is_google)

    def load_sapi5_voices(self):
        """Load available SAPI 5 voices."""
        try:
            from ..processing.tts_manager import TTSManager
            tts_manager = TTSManager(self.settings, None)

            voices = tts_manager.get_available_sapi5_voices()

            if voices:
                self.sapi5_voice_combo.addItem("(Default Voice)", "")
                for voice in voices:
                    self.sapi5_voice_combo.addItem(voice, voice)
            else:
                self.sapi5_voice_combo.addItem("(No SAPI 5 voices available)", "")
        except Exception as e:
            self.sapi5_voice_combo.addItem("(SAPI 5 not available)", "")
            print(f"Could not load SAPI 5 voices: {e}")
