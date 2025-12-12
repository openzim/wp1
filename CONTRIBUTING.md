# Contributing to WP1

Thank you for your interest in contributing to WP1. You will be contributing not only to the bot with the most all time edits of English Wikipedia, but also a powerful tool for helping people explore Wikipedia content offline. Welcome!

## Code of Conduct

This project adheres to the [Wikimedia Foundation Universal Code of Conduct](https://foundation.wikimedia.org/wiki/Policy:Universal_Code_of_Conduct).

## Getting Started

See the [README.md](README.md) for installation and development setup instructions.

## Reporting Issues

Use the [GitHub issue tracker](https://github.com/openzim/wp1/issues) to report bugs or suggest features. When reporting bugs, include:

- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, etc.) if applicable

## Pull Requests

1. Fork the repository and create your branch from `main`.
2. Make your changes, following the existing code style.
3. Add tests for any new functionality.
4. Ensure all tests pass (`pipenv run pytest` for backend, `yarn test` for frontend).
5. Run pre-commit hooks (`pre-commit install` if you haven't already).
6. Submit your pull request.

Pull requests should be focused and address a single concern. Include a clear description of the changes and reference any related issues.

## Code Standards

- Python code is formatted with [Black](https://github.com/psf/black). There is a GitHub workflow check that will reject PRs that are not properly formatted.
- Frontend Javascript and HTML code is formatted with Prettier. 
- Pre-commit hooks enforce code quality checks.
- All new code MUST include appropriate tests. This project proudly maintains over 90% test coverage.
    - Python tests for wp1/logic/foo.py should live in wp1/logic/foo_test.py.
    - Use the provided base test classes (in `base_db_test.py` and `wiki_db_test.py`). When you call `super().setUp()`, the base test class will handle giving you a fresh, empty database.
    - Feel free ot make liberal use of `@patch` and mocks in Python tests.
    - Cypress frontend tests should almost ALWAYS mock the backend API (see the `fixtures` directory).
    - Similarly, Python tests should NEVER make actual outbound network requests, even if a service is free, idempotent or reliably available. Always mock the necessary methods on the `requests` library.
- Follow existing patterns and conventions in the codebase. In particular:
    - The Python code is not generally object oriented, but instead uses dependency injection to provide necessary objects like the `wp10db` database connection.
    - The main exception to this is that data models that have tables in the database should have an [attrs](https://www.attrs.org/en/stable/) based data model class. So there is a a `selections` table and a `selection.py` data model class.
    - Flask API handlers (in `wp1/web/`) should strive to be as "lean" as possible. Don't put lots of complex logic there, instead delegate to methods in `wp1/logic`.
    - Long running or periodic tasks should be delegated to `rq`.
    - It is better to raise an exception and "crash" a request than to give an incorrect or incomplete answer. However, forseeable error conditions should be handled, including providing detailed error messages.
    - User data should be validated on the frontend as a convenience, when possible. However ultimately all validation and policy enforcement is done in the backend.

## Usage of LLMs/AI coding assistants

In general, we are okay with contributors using AI tools to help them write code. We do it ourselves. However, the maintainers of this project are not interested in wasting time reviewing low effort or low quality PRs _in general_. Unfortunately, AI tools can sometimes make it easy to create such PRs. When using these tools, make sure they are in service of your own contribution efforts. That is, the tool should _assist you_ not _replace you_.

To be completely explicit, please do not point an LLM at one of our issues, have it write a PR that you didn't look at, ask us to review it, and then simply feed our feedback back into the tool. We could do that ourselves, thank you anyways.

Basically, you should be able to understand, explain, and justify any code that an AI tool contributes to your PR.

And if you use an AI tool, please be honest about it when asked. Attempting to mask the use of AI and "pass it off as one's own" is distasteful to say the least, and will make us not want to work with you.

## Questions?

For questions about the project, open a discussion on GitHub, ask in an issue, or discuss on [English Wikipedia](https://en.wikipedia.org/wiki/Wikipedia_talk:Version_1.0_Editorial_Team/Index).
