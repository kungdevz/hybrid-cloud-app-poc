---
inclusion: always
---

# Coding Standards and Project Rules

## Python (Backend)

- Follow PEP 8 guidelines
- Use type hints for function arguments and return values
- Add docstrings to all modules, classes, and functions using Google style guide
- Organize imports: standard library → third-party → local application
- Use specific exception handling. Never use bare `except:` clauses
- Use SQLAlchemy ORM exclusively for database interactions
- Use snake_case for table and column names

## HTML/JS (Frontend)

- Use semantic HTML5 elements
- Use vanilla JavaScript (ES6+). No frameworks unless explicitly requested
- Use CSS variables for colors and spacing. Keep styles modular

## Project Structure Rules

- All new feature modules must be implemented as Flask Blueprints in `app/controllers`
- Business logic must reside in `app/services`, not in controllers
- Database models must reside in `app/models`
- Never hardcode secrets. Use `os.getenv` for all credentials
- If adding new packages, update `app/requirements.txt` immediately

## Architecture Pattern

Always follow: Controller (Route) → Service (Business Logic) → Model (Data)

- Controllers handle HTTP request/response only
- Services contain CRUD operations and business logic
- Models define database schema and ORM mappings

## Critical Behaviors

- Ensure changes do not break the main dashboard UI at `/`
- Ensure changes do not break existing User CRUD endpoints
- Verify logic locally with `docker-compose up` when possible
- Always generate migration scripts for schema changes (`flask db migrate`)

## Commands

- Lint: `flake8 app/`
- Test: `pytest`
- Run locally: `docker-compose up --build`
- Access app: `http://localhost:8081`
