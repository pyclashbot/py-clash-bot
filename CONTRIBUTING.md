# Contributing to py-clash-bot

Welcome to the py-clash-bot project! We appreciate your interest in contributing. Here are some guidelines to help you get started:

## Setting up a Development Environment

To set up a development environment for py-clash-bot, you will need to have the following tools installed:

- [Python 3.11](https://www.python.org/)
- [Poetry](https://python-poetry.org/)

Once you have these tools installed, follow these steps to set up the project:

1. Clone the py-clash-bot repository
   `git clone https://github.com/matthewmiglio/py-clash-bot.git; cd py-clash-bot`
2. Navigate to the `backend` directory
   `cd backend`
3. Use Poetry to create a virtual environment and install dependencies
   `poetry install --with build,dev`
4. Start the project locally
   `poetry run python pyclashbot/__main__.py`

## Testing Changes

Before submitting a pull request, make sure to test your changes thoroughly. This could include writing unit tests or manually testing the project to ensure it is functioning as expected.

## Submitting Pull Requests

To submit a pull request, follow these steps:

1. Create a new branch for your changes: `git checkout -b my-branch`
2. Make your changes and commit them to the branch: `git commit -am "My changes"`
3. Push the branch to GitHub: `git push origin my-branch`
4. Navigate to the py-clash-bot repository on GitHub and create a new pull request.

Please make sure to install and run the [pre-commit](https://pre-commit.com/) hooks when submitting a pull request.

## Building and Releasing the Project

To build the project for testing or production, follow these steps:

1. Navigate to the `backend` directory
   `cd backend`
2. Use Poetry to build the project
   `poetry run python setup_msi.py bdist_msi`
   This will create a `dist` directory containing the built project.

## Additional Guidelines

- Make sure to write thorough and accurate documentation for your changes
- Be respectful and considerate of others when communicating
