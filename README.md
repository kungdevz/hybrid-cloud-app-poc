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
docker-compose up --build
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

Please refer to [RULES.md](./RULES.md) for coding standards and contribution guidelines.
