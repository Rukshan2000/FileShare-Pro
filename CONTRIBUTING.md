# Contributing to FileShare Pro

Thank you for your interest in contributing to FileShare Pro! We welcome contributions from everyone and are grateful for every contribution, be it a bug report, feature request, documentation improvement, or code enhancement.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## 🚀 Getting Started

### Development Environment Setup

1. **Fork the repository**
   - Click the "Fork" button at the top right of the repository page
   - Clone your fork: `git clone https://github.com/YOUR_USERNAME/FileShare-Pro.git`

2. **Set up the development environment**
   ```bash
   cd FileShare-Pro
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Install development tools
   ```

3. **Set up pre-commit hooks** (recommended)
   ```bash
   pre-commit install
   ```
   This will automatically format your code and run checks before each commit.

4. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/Rukshan2000/FileShare-Pro.git
   ```

5. **Run the application**
   ```bash
   python3 app.py
   ```
   - Access the application at `http://localhost:8000`
   - Default login: Username: `admin`, Password: `admin`

## 🎯 How to Contribute

### 1. Bug Fixes
- Look for issues labeled with `bug` or `good first issue`
- Comment on the issue to let others know you're working on it
- Fork the repository and create a feature branch
- Fix the bug and add tests if applicable
- Submit a pull request

### 2. New Features
- Check existing issues for requested features
- Create a new issue to discuss the feature before implementing
- Wait for maintainer approval before starting work
- Implement the feature following our coding standards
- Add tests and update documentation

### 3. Documentation Improvements
Documentation is crucial for project success! We welcome contributions to:

- **README files**: Improve setup instructions, usage examples, troubleshooting
- **API documentation**: Update `API_DOCUMENTATION.md` with new endpoints
- **Code comments**: Add inline documentation for complex code sections
- **Examples**: Add integration examples in the `examples/` directory
- **Tutorials**: Create step-by-step guides for common use cases
- **Translations**: Help translate documentation to other languages

#### Documentation Style Guidelines:
- Use clear, concise language
- Include code examples where applicable
- Update table of contents when adding new sections
- Use consistent markdown formatting
- Test all code examples to ensure they work
- Add screenshots for UI-related documentation

#### Building Documentation (if using MkDocs):
```bash
# Install documentation dependencies
pip install mkdocs mkdocs-material

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

### 4. Code Reviews
- Review open pull requests
- Provide constructive feedback
- Test changes locally when possible

## ⚙️ Development Setup

### Project Structure
```
FileShare-Pro/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── static/               # CSS, JavaScript, assets
│   ├── script.js         # Frontend JavaScript
│   └── style.css         # Styles
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── upload.html       # Upload page
│   ├── files.html        # File browser
│   └── chat.html         # Chat interface
├── uploads/              # File storage (created at runtime)
├── thumbnails/           # Generated thumbnails
└── examples/             # Integration examples
    └── laravel/          # Laravel/PHP examples
```

### Environment Configuration
- The application uses Flask development mode by default
- File uploads are limited to 100MB
- Automatic cleanup removes files older than 7 days
- Authentication is required for all routes except login

### Running Tests
The project includes a comprehensive test suite using pytest:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app.py

# Run tests in watch mode (requires pytest-watch)
pytest-watch
```

Test files are located in the `tests/` directory and follow the naming convention `test_*.py`.

## 📝 Coding Standards

### Python Code Style
- Follow **PEP 8** guidelines using automated tools
- Code formatting is handled by **Black** (line length: 88 characters)
- Import sorting is managed by **isort**
- Code quality is enforced by **flake8**
- Security scanning with **bandit**
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions focused and small
- Use type hints where appropriate

#### Automated Code Formatting
The project uses several tools to maintain code quality:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check code quality with flake8
flake8 .

# Run security scan with bandit
bandit -r . -x tests

# Or run all checks at once with pre-commit
pre-commit run --all-files
```

#### Configuration Files
- **pyproject.toml**: Configuration for Black, isort, pytest, and bandit
- **.editorconfig**: Editor settings for consistent coding style
- **.pre-commit-config.yaml**: Pre-commit hooks configuration

```python
def create_user(username: str, password: str, role: str = 'user') -> tuple[bool, str]:
    """Create a new user account.

    Args:
        username: The username for the new account
        password: The password for the new account
        role: The role for the user (default: 'user')

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Implementation here
```

### Frontend Code Style
- Use consistent indentation (2 spaces)
- Write semantic HTML
- Use CSS custom properties for theming
- Add comments for complex JavaScript logic
- Follow existing naming conventions

### Git Commit Messages
Use clear, descriptive commit messages:

```
feat: add user authentication system
fix: resolve file upload progress bar issue
docs: update API documentation for new endpoints
refactor: improve file organization logic
test: add unit tests for user management
```

### Code Review Checklist
- [ ] Code follows the project's style guidelines
- [ ] Self-review of the code has been performed
- [ ] Code is well-commented, particularly complex areas
- [ ] Tests have been added for new features
- [ ] All tests pass
- [ ] Documentation has been updated if necessary

## 🔄 Pull Request Process

### Before Submitting
1. **Update your fork** with the latest changes from upstream
   ```bash
   git checkout main
   git fetch upstream
   git merge upstream/main
   git push origin main
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, well-documented code
   - Test your changes thoroughly
   - Update documentation if needed

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   git push origin feature/your-feature-name
   ```

### Submitting the Pull Request
1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your feature branch
4. Fill out the pull request template
5. Link any related issues

### Pull Request Template
Please include:
- **Description**: What changes were made and why
- **Type of Change**: Bug fix, new feature, documentation, etc.
- **Testing**: How the changes were tested
- **Screenshots**: If applicable, especially for UI changes
- **Checklist**: Confirm code follows guidelines

### Review Process
- Maintainers will review your pull request
- You may be asked to make changes
- Once approved, your PR will be merged
- Thank you for your contribution! 🎉

## 🐛 Issue Reporting

### Bug Reports
When reporting bugs, please include:
- **Description**: Clear description of the issue
- **Steps to Reproduce**: Detailed steps to recreate the bug
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, browser (if applicable)
- **Screenshots**: If applicable
- **Additional Context**: Any other relevant information

### Bug Report Template
```markdown
**Bug Description**
A clear and concise description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g., Ubuntu 20.04, Windows 10]
- Python Version: [e.g., 3.9.7]
- Browser: [e.g., Chrome 96.0.4664.110]

**Additional Context**
Add any other context about the problem here.
```

## 💡 Feature Requests

### Suggesting Features
We love hearing your ideas! When suggesting features:
- **Check existing issues** to avoid duplicates
- **Describe the problem** the feature would solve
- **Propose a solution** or approach
- **Consider alternatives** you've thought of
- **Provide examples** of how it would be used

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of alternative solutions or features.

**Additional context**
Add any other context or screenshots about the feature request.
```

## 🏷️ Labels and Issues

### Issue Labels
Understanding our labeling system helps you find the right issues to work on:

#### Type Labels
- `bug` - Something isn't working correctly
- `enhancement` - New feature requests or improvements
- `documentation` - Improvements or additions to docs
- `question` - General questions about the project
- `refactor` - Code improvements without changing functionality

#### Difficulty Labels
- `good first issue` - Perfect for newcomers to the project
- `easy` - Can be completed in a few hours
- `medium` - Requires moderate experience and time
- `hard` - Complex issues requiring significant expertise

#### Status Labels
- `help wanted` - Maintainers are looking for community help
- `needs discussion` - Requires community input before implementation
- `blocked` - Cannot proceed due to dependencies
- `wontfix` - Will not be implemented (with explanation)
- `duplicate` - Already reported elsewhere

#### Priority Labels
- `priority: critical` - Security issues, major bugs affecting all users
- `priority: high` - Important features, bugs affecting many users
- `priority: medium` - Standard improvements and fixes
- `priority: low` - Nice-to-have improvements

### Finding Issues to Work On

**New Contributors:**
- Start with `good first issue` labels
- Look for `help wanted` combined with `easy`
- Check `documentation` issues for non-code contributions

**Experienced Contributors:**
- `help wanted` + `medium` or `hard`
- `enhancement` issues for new features
- `refactor` issues for code improvements

### Issue Lifecycle
1. **Reported** - New issues are triaged by maintainers
2. **Labeled** - Appropriate labels are added
3. **Assigned** - Contributors can self-assign or request assignment
4. **In Progress** - Work begins (comment to let others know)
5. **PR Submitted** - Pull request linked to the issue
6. **Reviewed** - Code review process
7. **Merged** - Issue closed when PR is merged

## 🏆 Recognition

Contributors will be recognized in:
- The project's README file
- Release notes for significant contributions
- GitHub's contributor statistics

## 📞 Getting Help

- **Documentation**: Check the README and API documentation
- **Issues**: Search existing issues for your question
- **Discussions**: Use GitHub Discussions for general questions
- **Direct Contact**: Reach out to maintainers for urgent matters

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Socket.IO Documentation](https://socket.io/docs/)
- [Python PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Git Documentation](https://git-scm.com/doc)

---

Thank you for contributing to FileShare Pro! Your efforts help make this project better for everyone. 🚀
