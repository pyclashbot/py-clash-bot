# Contributing to py-clash-bot

Welcome to the py-clash-bot project! We appreciate your interest in contributing. Here are some guidelines to help you get started:

## Setting up a Development Environment

To set up a development environment for py-clash-bot, you will need to have the following tools installed:

- [Node.js](https://nodejs.org/)
- [Python 3.11](https://www.python.org/)
- [Poetry](https://python-poetry.org/)

Once you have these tools installed, follow these steps to set up the project:

1. Clone the py-clash-bot repository
   `git clone https://github.com/matthewmiglio/py-clash-bot.git; cd py-clash-bot`
2. Navigate to the `backend` directory
   `cd backend`
3. Use Poetry to create a virtual environment and install dependencies
   `poetry install --with build,dev`
4. Navigate to the `frontend` directory
   `cd ../frontend`
5. Install Node.js dependencies
   `npm install`

To start the development environment, run the `dev` script in the `frontend` directory: `npm run dev`. This will start the Python backend server, the React development server, and the Electron app.

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

To build the project for production, run the `package` script in the `frontend` directory: `npm run package`. This will build the frontend and backend for production and package them into an installer.

To release a new version of the project, you will need to bump the version number and push a new tag to GitHub. You can do this by running one of the bump scripts in the `frontend` directory:

- `npm run bump` for a prerelease bump (e.g. `1.2.3` -> `1.2.4-0`)
- `npm run bump-patch` for a patch bump (e.g. `1.2.4-2` -> `1.2.4`)
- `npm run bump-minor` for a minor bump (e.g. `1.2.4` -> `1.3.0`)
- `npm run bump-major` for a major bump (e.g. `1.3.0` -> `2.0.0`)

This will update the version number in the `package.json` file, commit the change, and push a new tag to GitHub. The release workflow will then be triggered to build and release the new version. The pre-releases will be published with a pre-release tag on GitHub and not be linked on [the website](https://matthewmiglio.github.io/py-clash-bot). You can view the status of the workflow on the [Actions tab](https://github.com/matthewmiglio/py-clash-bot/actions).

## Additional Guidelines

- Make sure to write thorough and accurate documentation for your changes
- Be respectful and considerate of others when communicating
