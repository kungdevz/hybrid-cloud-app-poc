# Project Rules and Guidelines

This file serves as the single source of truth for project standards.
It is integrated with the IDE via `.cursorrules`, `.editorconfig`, and `.vscode/settings.json`.

## 1. Code Standards

### Python (Backend)

- **Style**: Follow PEP 8 guidelines.
- **Type Hinting**: Use type hints for function arguments and return values where possible.
- **Docstrings**: Add docstrings to all modules, classes, and functions using the Google style guide.
- **Imports**: Organize imports: standard library, third-party, local application.
- **Error Handling**: Use specific exception handling. Do not use bare `except:` clauses.

### HTML/JS (Frontend)

- **HTML**: Use semantic HTML5 elements.
- **JS**: Use vanilla JavaScript (ES6+). Avoid jQuery unless necessary.
- **CSS**: Use CSS variables for colors and spacing. Keep styles modular.

### Database

- **ORM**: Use SQLAlchemy for all database interactions.
- **Migrations**: Always generate migration scripts for schema changes (`flask db migrate`).
- **Naming**: Use snake_case for table and column names.

## 2. Project Structure

- **Blueprints**: All new feature modules must be implemented as Flask Blueprints in `app/controllers`.
- **Services**: Business logic must reside in `app/services`, not in controllers.
- **Models**: Database models must reside in `app/models`.
- **Config**: Do not hardcode secrets. Use environment variables (see `CLAUDE.md`).

## 3. Development Workflow

1. **Create Feature Branch**: `git checkout -b feature/your-feature-name`
2. **Implement**: Follow the architecture (Controller -> Service -> Model).
3. **Test**: Verified locally using `docker-compose up`.
4. **Lint**: Ensure code is clean before committing.

## 4. Agent Interaction Rules (for AI Assistants)

This section is automatically applied via `.cursorrules`.

- **Context**: Always read `CLAUDE.md` for project context.
- **Workflows**: Use the provided workflows in `.agent/workflows` for standard tasks (adding modules, deploying).
- **Modification**: When modifying code, ensure existing functionality (especially the dashboard) remains intact.
- **Dependencies**: If adding new packages, update `app/requirements.txt` immediately.

## 5. IDE Configuration Reference

This project uses the following configuration files for IDE integration:

### .cursorrules (AI Context)

Validates that the AI Assistant follows `RULES.md` and `CLAUDE.md`.
See root `.cursorrules` file.

### .editorconfig (Formatting)

Enforces indentation and whitespace rules.
See root `.editorconfig` file.

### .vscode/settings.json (VS Code Settings)

Configures Python analysis, linting, and formatting.
See `.vscode/settings.json`.
