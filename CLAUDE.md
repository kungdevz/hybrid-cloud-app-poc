# Hybrid Cloud App POC (Flask + MSSQL + OpenShift)

A Python Flask REST API with MSSQL backend for user management, designed for hybrid cloud deployment with Docker and Red Hat OpenShift.

## 🚨 MANDATORY AGENT INSTRUCTIONS

**BEFORE you start working, READ `RULES.md` for coding standards and project guidelines.**

### Agent Workflow

1. **Understand Context**: Read `CLAUDE.md` and `RULES.md` thoroughly.
2. **Check Environment**: Verify if you are running locally (`docker-compose`) or on OpenShift (`oc`).
3. **Choose Workflow**: Check `.agent/workflows/` for predefined tasks:
    - Need a new feature? ➔ Use `/add-module` workflow.
    - Need to deploy? ➔ Use `/deploy-openshift` workflow.
    - Need to run locally? ➔ Use `/run-local` workflow.
4. **Implement**: Follow the architecture: `Controller` → `Service` → `Model`.
5. **Verify**: Ensure changes don't break existing functionality (Dashboard, User CRUD).

## Tech Stack

- **Backend**: Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Session
- **Database**: MSSQL (Azure SQL Edge) with ODBC Driver 18
- **Frontend**: Single-page HTML + vanilla JavaScript dashboard
- **Deployment**: Docker, docker-compose, Red Hat OpenShift (ROSA)

## Project Structure

```
hybrid-cloud-app-poc/
├── app/                    # Flask application
│   ├── app.py              # Entry point, registers blueprints
│   ├── config.py           # Flask config, DB connection, session
│   ├── config.yaml         # Database connection defaults
│   ├── controllers/        # API route handlers (Blueprints)
│   ├── models/             # SQLAlchemy ORM models
│   ├── services/           # Business logic layer
│   └── templates/          # Jinja2 HTML templates
├── db/                     # Database container + init scripts
├── oc/                     # OpenShift deployment manifests
├── docs/                   # Postman collection for testing
├── docker-compose.yml      # Local container orchestration
├── RULES.md                # comprehensive coding standards
└── README.md               # User onboarding guide
```

## Architecture

```
Controllers (Blueprints) → Services (Business Logic) → Models (SQLAlchemy ORM) → MSSQL
```

| Layer | Location | Purpose |
|-------|----------|---------|
| Controller | `app/controllers/` | HTTP routes, request/response handling |
| Service | `app/services/` | CRUD operations, business logic |
| Model | `app/models/` | Database schema, ORM mappings |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URI` | MSSQL connection string with `%s` placeholder for password |
| `DATABASE_PASSWORD` | Database password (URL-encoded) |
| `SECRET_KEY` | Flask session secret key |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | Get all users |
| POST | `/users` | Create a user |
| PUT | `/users/<id>` | Update user by ID |
| DELETE | `/users/<id>` | Delete user by ID |
| GET | `/` | Dashboard UI |

## Workflows

Use these workflows for common tasks:

- `/add-module` - Add a new feature module (Model + Service + Controller)
- `/run-local` - Set up and run locally
- `/deploy-openshift` - Deploy to OpenShift

## Dependencies

PyYAML, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Session, pyodbc, cryptography, requests
