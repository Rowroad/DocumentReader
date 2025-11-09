"""Accessibility utilities for Windows UI Automation."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTextEdit
from PyQt6.QtGui import QKeySequence, QAction


class AccessibleWidget:
    """Mixin for making widgets accessible."""

    def setup_accessibility(self, name: str, description: str = "",
                          role: str = ""):
        """Setup accessibility properties for a widget.

        Args:
            name: Accessible name
            description: Accessible description
            role: ARIA role equivalent
        """
        self.setAccessibleName(name)
        if description:
            self.setAccessibleDescription(description)

        # Ensure keyboard focus is possible
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def announce(self, text: str):
        """Announce text to screen readers.

        Args:
            text: Text to announce
        """
        # Set accessible description which triggers screen reader notification
        self.setAccessibleDescription(text)


class AccessibleButton(QPushButton, AccessibleWidget):
    """Accessible button with proper ARIA attributes."""

    def __init__(self, text: str, parent=None, description: str = ""):
        super().__init__(text, parent)
        self.setup_accessibility(
            name=text,
            description=description or f"{text} button",
            role="button"
        )

        # Ensure button is keyboard accessible
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


class AccessibleLabel(QLabel, AccessibleWidget):
    """Accessible label."""

    def __init__(self, text: str, parent=None, for_widget=None):
        super().__init__(text, parent)
        self.setup_accessibility(
            name=text,
            role="label"
        )

        if for_widget:
            self.setBuddy(for_widget)


class AccessibleLineEdit(QLineEdit, AccessibleWidget):
    """Accessible line edit with label association."""

    def __init__(self, parent=None, label: str = "", placeholder: str = ""):
        super().__init__(parent)

        if placeholder:
            self.setPlaceholderText(placeholder)

        self.setup_accessibility(
            name=label,
            description=f"{label} input field",
            role="textbox"
        )


class AccessibleTextEdit(QTextEdit, AccessibleWidget):
    """Accessible multi-line text edit."""

    def __init__(self, parent=None, label: str = "", read_only: bool = False):
        super().__init__(parent)

        self.setReadOnly(read_only)

        self.setup_accessibility(
            name=label,
            description=f"{label} {'view' if read_only else 'edit'} area",
            role="textbox" if not read_only else "document"
        )


def create_accessible_action(text: str, shortcut: QKeySequence = None,
                            description: str = "", parent=None) -> QAction:
    """Create an accessible menu action.

    Args:
        text: Action text
        shortcut: Keyboard shortcut
        description: Status tip / accessible description
        parent: Parent widget

    Returns:
        QAction with accessibility properties set
    """
    action = QAction(text, parent)

    if shortcut:
        action.setShortcut(shortcut)

    if description:
        action.setStatusTip(description)
        action.setToolTip(description)

    return action


def setup_focus_chain(widgets: list):
    """Setup explicit focus chain for keyboard navigation.

    Args:
        widgets: List of widgets in desired tab order
    """
    for i in range(len(widgets) - 1):
        QWidget.setTabOrder(widgets[i], widgets[i + 1])


def announce_to_screen_reader(widget: QWidget, message: str):
    """Announce a message to screen readers.

    Args:
        widget: Widget to announce from
        message: Message to announce
    """
    # Update accessible description to trigger announcement
    current_desc = widget.accessibleDescription()
    widget.setAccessibleDescription(message)

    # Restore original description after a delay
    # (In production, use QTimer for this)
    widget.setAccessibleDescription(current_desc)


class KeyboardShortcuts:
    """Standard keyboard shortcuts for accessibility."""

    # File operations
    NEW = QKeySequence.StandardKey.New
    OPEN = QKeySequence.StandardKey.Open
    SAVE = QKeySequence.StandardKey.Save
    QUIT = QKeySequence.StandardKey.Quit

    # Editing
    COPY = QKeySequence.StandardKey.Copy
    CUT = QKeySequence.StandardKey.Cut
    PASTE = QKeySequence.StandardKey.Paste
    SELECT_ALL = QKeySequence.StandardKey.SelectAll

    # Navigation
    FIND = QKeySequence.StandardKey.Find
    FIND_NEXT = QKeySequence.StandardKey.FindNext
    FIND_PREVIOUS = QKeySequence.StandardKey.FindPrevious

    # Custom shortcuts
    PREFERENCES = QKeySequence("Ctrl+,")
    NEXT_TAB = QKeySequence("Ctrl+Tab")
    PREVIOUS_TAB = QKeySequence("Ctrl+Shift+Tab")
    CLOSE_TAB = QKeySequence("Ctrl+W")
    CONVERT = QKeySequence("Ctrl+Shift+C")
    BATCH_CONVERT = QKeySequence("Ctrl+Shift+B")


def set_high_contrast_mode(widget: QWidget, enabled: bool):
    """Enable or disable high contrast mode.

    Args:
        widget: Widget to apply mode to
        enabled: Whether to enable high contrast
    """
    if enabled:
        # Apply high contrast stylesheet
        widget.setStyleSheet("""
            QWidget {
                background-color: black;
                color: white;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #333;
                color: white;
                border: 2px solid white;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:focus {
                border: 3px solid yellow;
            }
            QLineEdit, QTextEdit {
                background-color: black;
                color: white;
                border: 2px solid white;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 3px solid yellow;
            }
            QMenuBar {
                background-color: #222;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #555;
            }
            QMenu {
                background-color: #222;
                color: white;
                border: 2px solid white;
            }
            QMenu::item:selected {
                background-color: #555;
            }
        """)
    else:
        # Remove custom stylesheet
        widget.setStyleSheet("")
