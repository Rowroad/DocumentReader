# Document Reader - Accessible Document Converter

A comprehensive Windows desktop application that uses Google's Gemini API to process, extract, and transcribe documents for blind and visually impaired users. The application focuses on strict adherence to accessibility standards and flexible output conversion.

## Features

### Input Formats Supported
- **Documents**: PDF, DOCX, TXT, EPUB, MOBI, HTML, Markdown
- **Images**: JPEG, PNG, GIF, BMP (with OCR)
- **Web Pages**: Direct URL processing
- **Graphic Novels & Manga**: Specialized panel detection and dialogue extraction

### Output Formats
- **Text-based**: Plain Text, HTML, Markdown, DOCX
- **E-books**: EPUB, accessible PDF
- **Accessible Formats**:
  - DAISY (Text only)
  - DAISY (Audio + Text with TTS)
  - M4B Audiobook (single file with chapters)

### Core Capabilities
- **AI-Powered Processing**: Uses Gemini API for OCR, structure detection, and text extraction
- **Multi-language Support**: Automatic language detection and processing
- **Structure Preservation**: Maintains headings, tables, lists, and document hierarchy
- **Image Processing**: OCR for images, automatic alt text generation
- **Text-to-Speech**: Generate audio versions with Google Cloud TTS
- **Batch Processing**: Convert multiple documents in parallel
- **Accessibility First**: Full Microsoft UI Automation compliance

### Accessibility Features
- **Full Keyboard Navigation**: Every feature accessible without mouse
- **Screen Reader Support**: Complete NVDA/JAWS compatibility
- **Logical Tab Order**: Intuitive navigation flow
- **Accessible Dialogs**: Clear feedback and error messages
- **High Contrast Mode**: Optional for better visibility
- **Customizable Font Sizes**: Adjustable for low vision users
- **Keyboard Shortcuts**: Standard Windows shortcuts throughout

## System Requirements

- **Operating System**: Windows 10 or later
- **Python**: 3.9 or later
- **Internet Connection**: Required for Gemini API access
- **Screen Reader** (Optional): NVDA, JAWS, or Windows Narrator

## Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/DocumentReader.git
cd DocumentReader
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Optional: Install Additional Components

For **PDF conversion** (HTML to PDF):
```bash
pip install pdfkit
# Also install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html
```

For **Text-to-Speech** (DAISY Audio & M4B):
```bash
pip install google-cloud-texttospeech
# Configure Google Cloud credentials (see TTS Setup below)
```

### 4. Get a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key

### 5. Configure the Application

On first run, the application will prompt you to enter your API key in Preferences.

Alternatively, create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API key
```

## Usage

### Running the Application

```bash
python run.py
```

Or:
```bash
python src/main.py
```

### Quick Start Guide

#### 1. Opening a Document

**Via Menu**:
- Press `Alt + F` to open File menu
- Press `O` for Open (or `Ctrl+O`)
- Select your document

**Keyboard Navigation**:
- `Ctrl+O`: Open document
- `Ctrl+Shift+B`: Batch convert multiple documents
- `Ctrl+W`: Close current tab
- `Ctrl+Tab`: Next tab
- `Ctrl+Shift+Tab`: Previous tab

#### 2. Converting a Document

After opening a document:
1. Press `Alt + C` to open Convert menu
2. Select desired output format
3. Choose save location
4. Wait for conversion to complete

**Supported Conversions**:
- `Plain Text`: Simple .txt file
- `HTML`: Web-accessible format
- `Markdown`: .md format
- `DOCX`: Microsoft Word format
- `EPUB`: E-book format
- `PDF`: Accessible PDF
- `DAISY (Text)`: DAISY text-only format
- `DAISY (Audio + Text)`: DAISY with TTS audio
- `M4B Audiobook`: Single audiobook file with chapters

#### 3. Batch Conversion

1. Press `Ctrl+Shift+B` (or File → Batch Convert)
2. Click "Add Files..." to select multiple documents
3. Choose output format
4. Select output directory
5. Click "Convert All"

#### 4. Configuring Preferences

Press `Ctrl+,` (or Edit → Preferences) to access:

**General Tab**:
- Gemini API Key
- Output directory
- System prompt (advanced)

**Processing Tab**:
- Accuracy mode (High/Balanced/Speed)
- Preserve formatting
- Extract images
- OCR images
- Auto-detect language

**Text-to-Speech Tab**:
- Voice selection
- Speech speed
- Speech pitch
- Language

**Security & Privacy Tab**:
- Auto-delete days (default: 7)
- Cloud data deletion
- Local encryption

**Interface Tab**:
- Theme (System/Light/Dark)
- Font size
- High contrast mode

### Document Navigation

When viewing a document:
- **Tree View** (left): Document structure with headings
- **Content View** (right): Full document content
- Click headings in tree to jump to sections
- Use keyboard arrows to navigate tree
- Tab key moves between tree and content

## Keyboard Shortcuts

### File Operations
- `Ctrl+O`: Open document
- `Ctrl+W`: Close current tab
- `Ctrl+Shift+B`: Batch convert
- `Ctrl+Q`: Quit application

### Navigation
- `Ctrl+Tab`: Next tab
- `Ctrl+Shift+Tab`: Previous tab
- `Tab`: Move forward through controls
- `Shift+Tab`: Move backward through controls
- `Arrow Keys`: Navigate tree view

### Other
- `Ctrl+,`: Preferences
- `Alt`: Access menu bar
- `F1`: Help (if implemented)

## Text-to-Speech Setup

For DAISY Audio and M4B audiobook generation:

### 1. Install Google Cloud Text-to-Speech

```bash
pip install google-cloud-texttospeech
```

### 2. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Text-to-Speech API
4. Create a service account
5. Download the JSON key file

### 3. Configure Credentials

Set the environment variable:

**Windows Command Prompt**:
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account-key.json
```

**Windows PowerShell**:
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

**Permanent (System Environment Variables)**:
1. Right-click "This PC" → Properties
2. Advanced system settings → Environment Variables
3. Add new system variable:
   - Variable name: `GOOGLE_APPLICATION_CREDENTIALS`
   - Variable value: `C:\path\to\service-account-key.json`

## Privacy & Security

### Data Handling
- **Encrypted Transmission**: All data sent to Gemini API is encrypted (HTTPS)
- **Cloud Data Deletion**: Gemini doesn't persistently store data by default
- **Local Storage**: Files stored in `%APPDATA%\DocumentReader\Temp`
- **Auto-Cleanup**: Local files deleted after 7 days (configurable)
- **Encryption**: Optional local file encryption

### Manual Data Management
- **Tools → Cleanup Old Files**: Remove old temporary files
- **Tools → Storage Information**: View stored data statistics
- Preferences → Security: Configure auto-delete settings

## Troubleshooting

### "API Key Required" Error
- Open Preferences (`Ctrl+,`)
- Enter valid Gemini API key
- Get key from: https://makersuite.google.com/app/apikey

### "TTS Not Available" Error
- Install `google-cloud-texttospeech` package
- Configure Google Cloud credentials
- Alternative: Use text-only DAISY format

### Document Processing Errors
- Check file isn't corrupted
- Verify file isn't password-protected
- Try reducing accuracy mode (Preferences → Processing → Speed)
- Check internet connection

### Network Errors
- Verify internet connection
- Check firewall settings
- Ensure Gemini API service is available
- Wait and retry

### Conversion Errors
- Ensure document is fully processed first
- Check write permissions to output directory
- Verify required dependencies are installed
- Try different output format

## Accessibility Notes

### Screen Reader Compatibility
Tested with:
- NVDA (recommended)
- JAWS
- Windows Narrator

### Best Practices
- Use keyboard shortcuts for efficiency
- Enable "Speak command keys" in screen reader settings
- Use high contrast mode if needed
- Adjust font size in Preferences

### Reporting Accessibility Issues
If you encounter accessibility barriers, please report them so we can improve the application.

## Advanced Features

### Custom System Prompts
The system prompt controls how Gemini processes documents. Advanced users can:
1. Open Preferences → General
2. Edit the "System Prompt" field
3. Add specific instructions for your use case
4. Click "Reset to Default" to restore

### Custom Processing Instructions
When opening a document, you can add custom per-file instructions in the processing dialog (if enabled).

### Manga/Graphic Novel Processing
The application automatically detects and processes:
- Panel reading order (RTL for Japanese, LTR for Western)
- Dialogue extraction
- Sound effects
- Visual descriptions for accessibility

## Project Structure

```
DocumentReader/
├── src/
│   ├── models/           # Data models
│   ├── processing/       # Document processing & conversion
│   ├── ui/              # User interface
│   ├── utils/           # Utilities (accessibility, errors, security)
│   └── main.py          # Application entry point
├── config/              # Configuration files
├── tests/              # Unit tests
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── run.py             # Convenience runner
└── README.md          # This file
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
The project follows PEP 8 style guidelines.

### Contributing
Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Specify your license here]

## Credits

- **Google Gemini AI**: Document processing and OCR
- **Google Cloud TTS**: Text-to-speech generation
- **PyQt6**: UI framework
- **Contributors**: [List contributors]

## Support

For issues, questions, or feature requests:
- GitHub Issues: [Your GitHub repository]
- Email: [Your support email]
- Documentation: [Your documentation site]

## Version History

### Version 1.0.0 (Current)
- Initial release
- Full input format support
- All output formats implemented
- Complete accessibility compliance
- Batch processing
- Security features

## Acknowledgments

Built for the blind and visually impaired community with a focus on accessibility, usability, and independence.

## Disclaimer

This application requires internet connectivity and API credits for Google's Gemini AI and Text-to-Speech services. Users are responsible for their own API usage and associated costs.