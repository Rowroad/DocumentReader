"""Main application entry point."""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui import MainWindow


def main():
    """Main application entry point."""
    try:
        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Document Reader")
        app.setOrganizationName("DocumentReader")
        app.setApplicationVersion("1.0.0")

        # Create and show main window
        window = MainWindow()
        window.show()

        # Run application
        sys.exit(app.exec())
    except Exception as e:
        import traceback
        print(f"\n{'='*60}")
        print("FATAL ERROR:")
        print(f"{'='*60}")
        print(f"{str(e)}")
        print(f"\n{traceback.format_exc()}")
        print(f"{'='*60}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
