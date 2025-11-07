# Plagiarism Detection Project

This project detects plagiarism in uploaded documents.

## Project Structure

- [backend](backend/) - FastAPI backend service
- [frontend](frontend/) - Next.js frontend application
- [file_processor](file_processor/) - File processing service

## GitHub Actions Workflows

This project includes several GitHub Actions workflows for CI/CD:

1. **Comprehensive CI/CD Pipeline** - Runs code quality checks, builds, and deploys Docker images
2. **Code Quality** - Runs linting and formatting checks for all components
3. **Dependency Security Check** - Checks for security vulnerabilities in dependencies
4. **Deploy Application** - Manually triggered deployment workflow
5. **Run Tests** - Runs unit tests for all components (placeholders currently)

Workflows are triggered on push/PR to main/master branches, and can also be triggered manually.

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency.

### Setup

Run the setup script:

**Windows:**
```bash
scripts\setup-precommit.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/setup-precommit.sh
./scripts/setup-precommit.sh
```

Or manually install:

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

### Hooks Included

1. **Black** - Python code formatting
2. **Flake8** - Python linting
3. **ESLint** - JavaScript/TypeScript linting
4. **Prettier** - Code formatting for various file types
5. **Conventional Commits** - Commit message validation

### Commit Message Format

This project follows the Conventional Commits specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- feat: A new feature
- fix: A bug fix
- chore: Maintenance work
- docs: Documentation changes
- style: Code style changes
- refactor: Code refactoring
- perf: Performance improvements
- test: Adding or modifying tests

Examples:
```
feat(auth): add login functionality
fix(api): resolve user data validation issue
chore(deps): update dependencies
docs(readme): add installation instructions
```