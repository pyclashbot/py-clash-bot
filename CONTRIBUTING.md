# Contributing to py-clash-bot

Welcome to the py-clash-bot project! We appreciate your interest in contributing. This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting up Development Environment](#setting-up-development-environment)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Additional Guidelines](#additional-guidelines)
- [Licensing](#licensing)

## Prerequisites

Before contributing, ensure you have the following tools installed:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) - Fast Python package installer and resolver
- [Make](https://www.gnu.org/software/make/) (or equivalent like `nmake` on Windows) - For running project commands
- [Git](https://git-scm.com/) - Version control

## Setting up Development Environment

1. **Clone the repository**

   ```bash
   git clone https://github.com/pyclashbot/py-clash-bot.git
   cd py-clash-bot
   ```

2. **Install dependencies**

   ```bash
   make setup
   ```

3. **Run development script**

   ```bash
   make dev
   ```

## Development Workflow

### Running the Application

- **Development mode**: `make dev`
- **Build Windows installer**: `make build-msi`

### Available Make Commands

- `make setup` - Install project dependencies
- `make dev` - Run the application in development mode
- `make lint` - Run all pre-commit checks on all files
- `make build-msi` - Build Windows MSI installer

## Testing Your Changes

Before submitting changes, ensure your code works correctly:

1. **Run the application** and verify it starts without errors
2. **Test your specific changes** thoroughly
3. **Check for any linting issues** (the project uses ruff for code formatting)

## Submitting Changes

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Set up Pre-commit Hooks

```bash
uvx pre-commit install
```

### 3. Make Your Changes

- Write clear, well-documented code
- Follow the existing code style
- Add tests if applicable
- Update documentation as needed

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add your feature description"
```

Use conventional commit messages:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:

- Clear description of changes
- Any relevant screenshots or examples
- Reference to related issues (if applicable)

## Code Style

The project uses several tools to maintain code quality:

- **ruff** - Code linting and formatting
- **isort** - Import sorting
- **pre-commit** - Automated code quality checks

### Running Code Quality Checks

```bash
# Run all pre-commit checks on all files
make lint
```

## Additional Guidelines

### Communication

- Be respectful and constructive in discussions
- Ask questions if something is unclear
- Provide context when reporting issues

### Documentation

- Update documentation for any API changes
- Add comments to complex code sections
- Include examples for new features

### Testing

- Test your changes thoroughly
- Consider edge cases and error conditions
- Verify the application still works as expected

### Performance

- Consider the impact of your changes on performance
- Profile code if making significant changes
- Follow existing patterns for optimization

## Getting Help

If you need help or have questions:

1. Check existing issues and pull requests
2. Search the documentation
3. Create a new issue with clear details
4. Join our community discussions

## Licensing

### Contributor License Agreement

By contributing to py-clash-bot, you agree that:

1. **Your contributions are your original work** or you have the right to submit them under the project's licenses.

2. **You grant a license** to your contributions under the same terms as the project:
   - Source code contributions are licensed under the py-clash-bot Non-Commercial Copyleft License 1.0 (NC-CL-1.0)
   - Asset contributions (images, documentation) are licensed under CC BY-NC-SA 4.0

3. **You understand the non-commercial restriction** - your contributions, along with the project, may not be used commercially without separate agreement with the maintainers.

4. **Your contributions become part of the project** - From the moment your contribution is merged, it is included under the project's dual-license and may be distributed accordingly.

### Guidelines

- Do not include proprietary or commercially-licensed content
- Clearly attribute any third-party content and ensure license compatibility
- Game assets from Clash Royale are property of Supercell - reference images are used for detection purposes only

### Commercial Inquiries

If you're interested in using py-clash-bot commercially, please contact the maintainers to discuss licensing options.

Thank you for contributing to py-clash-bot! 🚀
