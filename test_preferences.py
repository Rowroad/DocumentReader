"""Debug script to test preferences dialog in isolation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from src.models import Settings
from src.ui.preferences_dialog import PreferencesDialog

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)

    print("Loading settings...")
    settings = Settings()

    print("Creating PreferencesDialog...")
    try:
        dialog = PreferencesDialog(settings, None)
        print("Dialog created successfully!")

        print("Showing dialog...")
        dialog.show()

        print("Running event loop...")
        sys.exit(app.exec())

    except Exception as e:
        import traceback
        print(f"\n{'='*60}")
        print("ERROR creating or showing dialog:")
        print(f"{'='*60}")
        print(f"{str(e)}")
        print(f"\n{traceback.format_exc()}")
        print(f"{'='*60}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
