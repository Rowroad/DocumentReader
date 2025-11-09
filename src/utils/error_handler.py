"""Error handling and user-friendly error dialogs."""

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from enum import Enum
from typing import Optional


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "Information"
    WARNING = "Warning"
    ERROR = "Error"
    CRITICAL = "Critical Error"


class ErrorHandler:
    """Centralized error handling with accessible dialogs."""

    @staticmethod
    def show_error_dialog(parent, title: str, message: str,
                         details: str = "",
                         severity: ErrorSeverity = ErrorSeverity.ERROR,
                         suggestions: list = None):
        """Show an accessible error dialog.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Main error message
            details: Detailed error information
            severity: Error severity level
            suggestions: List of suggested actions
        """
        # Create message box
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)

        # Set icon based on severity
        if severity == ErrorSeverity.INFO:
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif severity == ErrorSeverity.WARNING:
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif severity == ErrorSeverity.ERROR:
            msg_box.setIcon(QMessageBox.Icon.Critical)
        else:  # CRITICAL
            msg_box.setIcon(QMessageBox.Icon.Critical)

        # Add details
        full_details = details
        if suggestions:
            full_details += "\n\nSuggested actions:\n"
            for i, suggestion in enumerate(suggestions, 1):
                full_details += f"{i}. {suggestion}\n"

        if full_details:
            msg_box.setDetailedText(full_details)

        # Accessibility
        msg_box.setAccessibleName(f"{severity.value}: {title}")
        msg_box.setAccessibleDescription(message)

        # Standard buttons
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)

        msg_box.exec()

    @staticmethod
    def handle_file_not_found(parent, file_path: str):
        """Handle file not found error."""
        ErrorHandler.show_error_dialog(
            parent,
            "File Not Found",
            f"The file could not be found:\n{file_path}",
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Check that the file exists at the specified location",
                "Verify you have permission to access the file",
                "Try selecting the file again using the Open dialog"
            ]
        )

    @staticmethod
    def handle_permission_error(parent, file_path: str):
        """Handle permission denied error."""
        ErrorHandler.show_error_dialog(
            parent,
            "Permission Denied",
            f"You don't have permission to access:\n{file_path}",
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Check file permissions",
                "Try running the application as administrator",
                "Ensure the file is not open in another application"
            ]
        )

    @staticmethod
    def handle_network_error(parent, details: str = ""):
        """Handle network connectivity error."""
        ErrorHandler.show_error_dialog(
            parent,
            "Network Error",
            "Unable to connect to the internet or Gemini API.",
            details=details,
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Check your internet connection",
                "Verify your firewall settings",
                "Ensure the Gemini API service is available",
                "Try again in a few moments"
            ]
        )

    @staticmethod
    def handle_api_error(parent, error_message: str):
        """Handle Gemini API error."""
        ErrorHandler.show_error_dialog(
            parent,
            "API Error",
            "An error occurred while processing with Gemini API.",
            details=error_message,
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Check your API key in Preferences",
                "Verify you have API credits available",
                "Check if you've exceeded rate limits",
                "Try again with a smaller document"
            ]
        )

    @staticmethod
    def handle_conversion_error(parent, format_name: str, details: str = ""):
        """Handle document conversion error."""
        ErrorHandler.show_error_dialog(
            parent,
            "Conversion Error",
            f"Unable to convert document to {format_name} format.",
            details=details,
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Ensure the document is properly processed first",
                "Try a different output format",
                "Check that you have write permissions to the output directory",
                "Verify all required dependencies are installed"
            ]
        )

    @staticmethod
    def handle_unsupported_format(parent, file_path: str):
        """Handle unsupported file format."""
        ErrorHandler.show_error_dialog(
            parent,
            "Unsupported Format",
            f"The file format is not supported:\n{file_path}",
            severity=ErrorSeverity.WARNING,
            suggestions=[
                "Supported formats: PDF, DOCX, TXT, EPUB, MOBI, HTML, Markdown, Images (JPEG/PNG)",
                "Try converting the file to a supported format first",
                "Check the file extension is correct"
            ]
        )

    @staticmethod
    def handle_processing_error(parent, details: str = ""):
        """Handle general document processing error."""
        ErrorHandler.show_error_dialog(
            parent,
            "Processing Error",
            "An error occurred while processing the document.",
            details=details,
            severity=ErrorSeverity.ERROR,
            suggestions=[
                "Try reloading the document",
                "Check if the document is corrupted",
                "Verify the document isn't password protected",
                "Contact support if the problem persists"
            ]
        )

    @staticmethod
    def show_confirmation_dialog(parent, title: str, message: str,
                                details: str = "") -> bool:
        """Show a confirmation dialog.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Confirmation message
            details: Additional details

        Returns:
            True if user confirmed, False otherwise
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Question)

        if details:
            msg_box.setInformativeText(details)

        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        # Accessibility
        msg_box.setAccessibleName(title)
        msg_box.setAccessibleDescription(message)

        result = msg_box.exec()
        return result == QMessageBox.StandardButton.Yes

    @staticmethod
    def show_info_dialog(parent, title: str, message: str, details: str = ""):
        """Show an information dialog.

        Args:
            parent: Parent widget
            title: Dialog title
            message: Information message
            details: Additional details
        """
        ErrorHandler.show_error_dialog(
            parent,
            title,
            message,
            details=details,
            severity=ErrorSeverity.INFO
        )

    @staticmethod
    def handle_missing_api_key(parent):
        """Handle missing API key."""
        ErrorHandler.show_error_dialog(
            parent,
            "API Key Required",
            "Gemini API key is not configured.",
            severity=ErrorSeverity.WARNING,
            suggestions=[
                "Open Preferences (Ctrl+,)",
                "Enter your Gemini API key",
                "Get a free API key from https://makersuite.google.com/app/apikey"
            ]
        )

    @staticmethod
    def handle_tts_not_available(parent):
        """Handle TTS not available."""
        ErrorHandler.show_error_dialog(
            parent,
            "TTS Not Available",
            "Text-to-speech functionality requires additional setup.",
            severity=ErrorSeverity.WARNING,
            suggestions=[
                "Install Google Cloud Text-to-Speech library",
                "Run: pip install google-cloud-texttospeech",
                "Configure Google Cloud credentials",
                "Try using text-only DAISY format instead"
            ]
        )

    @staticmethod
    def handle_batch_errors(parent, successful: int, failed: int, errors: list):
        """Handle batch processing errors.

        Args:
            parent: Parent widget
            successful: Number of successful conversions
            failed: Number of failed conversions
            errors: List of error messages
        """
        message = f"Batch processing completed:\n"
        message += f"Successful: {successful}\n"
        message += f"Failed: {failed}"

        details = "\n".join(errors) if errors else ""

        severity = ErrorSeverity.INFO if failed == 0 else ErrorSeverity.WARNING

        ErrorHandler.show_error_dialog(
            parent,
            "Batch Processing Complete",
            message,
            details=details,
            severity=severity
        )
