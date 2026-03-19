# Hybrid Cloud App POC

A Python Flask REST API with MSSQL backend, designed for hybrid cloud deployment on Red Hat OpenShift (ROSA).

## 🚀 Getting Started

### Prerequisites

- Docker Desktop & `docker-compose`
- Python 3.9+ (for local development)
- `oc` CLI (for OpenShift deployment)

### 🛠 Configuration

Configuration is managed via `app/config.yaml` (default values) and Environment Variables.

| Variable | Description |
|----------|-------------|
| `DATABASE_URI` | MSSQL Connection string |
| `DATABASE_PASSWORD` | DB Password |
| `PROFILE` | `local`, `test`, or `production` |

### 💻 Running Locally

The easiest way to run the application is using Docker Compose, which sets up both the Flask app and the MSSQL Edge database.

```bash
podman-compose up --build
```

Access the application at: `http://localhost:8081`

### 📦 Project Structure

- `app/`: Flask Application (Controllers, Services, Models)
- `db/`: Database initialization scripts
- `oc/`: OpenShift Kubernetes Manifests
- `doc/`: API Documentation (Postman)

### ☁️ Deployment

Deployment is handled via OpenShift manifests in the `oc/` directory.
See `.agent/workflows/deploy-openshift.md` for details or use the agent to help you deploy.

### 📝 Development Rules

Coding standards and project guidelines are managed via Kiro steering files in `.kiro/steering/`.

- `project-context.md` — Project overview, architecture, and API reference (always loaded)
- `coding-standards.md` — PEP 8, type hints, project structure rules (always loaded)
- `add-module.md` — Template for adding new feature modules (use `#add-module` in chat)
- `deploy-openshift.md` — OpenShift deployment steps (use `#deploy-openshift` in chat)
- `run-local.md` — Local development setup (use `#run-local` in chat)
- `run-load-test.md` — Load testing on EC2 bastion (use `#run-load-test` in chat)
