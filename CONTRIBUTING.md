# Contributing to Document Reader

Thank you for your interest in contributing to Document Reader! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on accessibility and usability
- Provide constructive feedback
- Help make the project better for blind and visually impaired users

## How to Contribute

### Reporting Bugs

When reporting bugs, please include:
1. **Clear description** of the issue
2. **Steps to reproduce** the problem
3. **Expected behavior** vs actual behavior
4. **System information** (OS version, Python version, screen reader if applicable)
5. **Error messages** or screenshots if relevant

### Accessibility Issues

Accessibility is our top priority. When reporting accessibility barriers:
1. Specify the screen reader and version you're using
2. Describe the exact interaction that's problematic
3. Suggest a preferred behavior if possible
4. Note if this affects keyboard-only navigation

### Suggesting Features

Feature requests are welcome! Please include:
1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Accessibility considerations**: How does it work with screen readers?
4. **Alternatives considered**: Other approaches you've thought of

### Code Contributions

#### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/DocumentReader.git
   cd DocumentReader
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest  # For testing
   ```

5. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Coding Standards

- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Write **docstrings** for all public functions and classes
- Keep functions **focused and small**
- Prioritize **readability** over cleverness

#### Accessibility Guidelines

All UI changes must:
1. Be **fully keyboard accessible** (no mouse required)
2. Have **proper ARIA labels** and accessible names
3. Maintain **logical tab order**
4. Work with **screen readers** (test with NVDA or Narrator)
5. Support **high contrast mode**
6. Follow **Microsoft UI Automation** standards

#### Testing

- Write **unit tests** for new functionality
- Test with **screen readers** for UI changes
- Verify **keyboard navigation** works properly
- Test with **different input formats**

Run tests:
```bash
pytest tests/
```

#### Commit Messages

Use clear, descriptive commit messages:
```
Add OCR support for manga panels

- Implement panel detection algorithm
- Extract dialogue in reading order
- Generate visual descriptions for accessibility
- Add tests for manga processing
```

#### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update README** if adding user-facing features
5. **Test accessibility** thoroughly
6. Submit pull request with clear description

### Documentation Contributions

Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples or tutorials
- Improve accessibility documentation
- Translate to other languages

## Priority Areas

We especially welcome contributions in:
1. **Additional input formats** support
2. **Output format** improvements
3. **Accessibility** enhancements
4. **Performance** optimizations
5. **Error handling** improvements
6. **Documentation** and examples
7. **Testing** coverage

## Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Check existing issues and discussions
- Review the README and documentation

## Recognition

All contributors will be acknowledged in the README and release notes.

Thank you for helping make Document Reader more accessible!
