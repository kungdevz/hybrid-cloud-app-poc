---
inclusion: always
---

# Hybrid Cloud App POC (Flask + MSSQL + OpenShift)

A Python Flask REST API with MSSQL backend for user management, designed for hybrid cloud deployment with Docker and Red Hat OpenShift.

## Tech Stack

- Backend: Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Session
- Database: MSSQL (Azure SQL Edge) with ODBC Driver 18
- Frontend: Single-page HTML + vanilla JavaScript dashboard
- Deployment: Docker, docker-compose, Red Hat OpenShift (ROSA)
- Load Testing: k6 + InfluxDB + Grafana on EC2 bastion

## Architecture

```
Controllers (Blueprints) → Services (Business Logic) → Models (SQLAlchemy ORM) → MSSQL
```

| Layer | Location | Purpose |
|-------|----------|---------|
| Controller | `app/controllers/` | HTTP routes, request/response handling |
| Service | `app/services/` | CRUD operations, business logic |
| Model | `app/models/` | Database schema, ORM mappings |

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
├── load-test/              # k6 load testing infrastructure
├── docker-compose.yml      # Local container orchestration
└── README.md               # User onboarding guide
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | Get users (paginated) |
| GET | `/users/<id>` | Get user by ID |
| POST | `/users` | Create a user |
| PUT | `/users/<id>` | Update user by ID |
| DELETE | `/users/<id>` | Delete user by ID |
| GET | `/` | Dashboard UI |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URI` | MSSQL connection string with `%s` placeholder for password |
| `DATABASE_PASSWORD` | Database password (URL-encoded) |
| `SECRET_KEY` | Flask session secret key |
| `PROFILE` | `local`, `test`, or `production` |

## Dependencies

PyYAML, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Session, pyodbc, cryptography, requests
