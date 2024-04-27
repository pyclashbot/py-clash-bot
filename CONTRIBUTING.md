# Contributing to py-clash-bot

Welcome to the py-clash-bot project! We appreciate your interest in contributing. Here are some guidelines to help you get started:

## Setting up a Development Environment

To set up a development environment for py-clash-bot, you will need to have the following tools installed:

- [Python 3.12](https://www.python.org/)
- [Poetry](https://python-poetry.org/)

Once you have these tools installed, follow these steps to set up the project:

1. Clone the py-clash-bot repository
   `git clone https://github.com/pyclashbot/py-clash-bot.git; cd py-clash-bot`
2. Navigate to the `src` directory
   `cd src`
3. Use Poetry to create a virtual environment and install dependencies
   `poetry install --with build,dev`
4. Run or build the project:
   - Run: `poetry run python pyclashbot/__main__.py`
   - Build a Windows installer: `poetry run python setup_msi.py bdist_msi`

## Testing Changes

Before submitting a pull request, make sure to test your changes thoroughly. This could include writing unit tests or manually testing the project to ensure it is functioning as expected.

## Submitting Pull Requests

To submit a pull request, follow these steps:

1. Create a new branch for your changes: `git checkout -b my-branch`
2. Install Pre-Commit hooks: `poetry run pre-commit install`
3. Make your changes and commit them to the branch: `git commit -am "My changes"`
4. Push the branch to GitHub: `git push origin my-branch`
5. Navigate to the py-clash-bot repository on GitHub and create a new pull request.

## Additional Guidelines

- Make sure to write thorough and accurate documentation for your changes
- Be respectful and considerate of others when communicating
