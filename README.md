# Hybrid Cloud App POC

A Python Flask REST API with an MSSQL backend for user management, designed to
demonstrate **hybrid cloud** deployment: the same application runs on a managed
cloud OpenShift cluster (Red Hat OpenShift on AWS / ROSA) and on an on-prem
OpenShift cluster, both talking to a shared on-prem SQL Server.

## Overview

The app exposes a small User CRUD REST API plus a single-page dashboard. It is
deployed two ways from one codebase:

| Environment | OpenShift | Namespace | Image source | Database |
|-------------|-----------|-----------|--------------|----------|
| **Cloud** | ROSA (AWS) | `ks-hybrid-cloud-poc` | In-cluster BuildConfig (builds from GitHub) → internal registry | On-prem MSSQL `192.168.66.147:9677` (over hybrid network) |
| **On-prem** | On-prem OpenShift | `rosa-poc` | Harbor registry (`harbor.krungsri.net`) | On-prem MSSQL `192.168.66.147:9677` |

Both environments run the `production` profile, so the app reaches the external
on-prem SQL Server. The in-cluster MSSQL manifests are retained for the `test`
profile / local use but are not used by the production profile.

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Session
- **Database:** MSSQL (Azure SQL Edge locally) via ODBC Driver 18, `pyodbc`
- **Frontend:** Single-page HTML + vanilla JavaScript dashboard
- **Deployment:** Docker / podman-compose (local), Red Hat OpenShift (cloud + on-prem)
- **Load testing:** k6 + InfluxDB + Grafana on an EC2 bastion (see `load-test/`)

## Architecture

```
Controllers (Blueprints) → Services (Business Logic) → Models (SQLAlchemy ORM) → MSSQL
```

| Layer | Location | Purpose |
|-------|----------|---------|
| Controller | `app/controllers/` | HTTP routes, request/response handling |
| Service | `app/services/` | CRUD operations, business logic |
| Model | `app/models/` | Database schema, ORM mappings |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Dashboard UI |
| GET | `/users` | List users (paginated) |
| GET | `/users/<id>` | Get user by ID |
| POST | `/users` | Create a user |
| PUT | `/users/<id>` | Update user by ID |
| DELETE | `/users/<id>` | Delete user by ID |

## Project Structure

```
hybrid-cloud-app-poc/
├── app/                 # Flask application
│   ├── app.py           # Entry point, registers blueprints
│   ├── config.py        # Flask config, profile-based DB connection
│   ├── config.yaml      # Production DB defaults (gitignored — see Configuration)
│   ├── controllers/     # API route handlers (Blueprints)
│   ├── models/          # SQLAlchemy ORM models
│   ├── services/        # Business logic layer
│   ├── db/              # init.sql + init_db.py (schema bootstrap)
│   └── templates/       # Dashboard HTML
├── oc/
│   ├── cloud/           # ROSA/AWS manifests (namespace ks-hybrid-cloud-poc)
│   ├── onprem/          # On-prem manifests (namespace rosa-poc)
│   └── buildconfig.yml  # Cloud BuildConfig + ImageStream
├── load-test/           # k6 load-testing infrastructure
├── docker-compose.yml   # Local container orchestration
└── README.md
```

## Configuration

Configuration is profile-based, resolved in `app/config.py`. The `PROFILE`
environment variable selects the behavior:

| Profile | Database target |
|---------|-----------------|
| `local` / `test` | In-cluster / local MSSQL (`database:1433`) |
| `production` | External DB from `DATABASE_URI` (on-prem SQL Server) |

| Variable | Description |
|----------|-------------|
| `PROFILE` | `local`, `test`, or `production` (defaults to `production`) |
| `DATABASE_URI` | SQLAlchemy MSSQL URI with a `%s` placeholder for the password |
| `DATABASE_PASSWORD` | DB password; substituted into the `%s` in `DATABASE_URI` |
| `SECRET_KEY` | Flask session secret |

**Important for production:** `app/config.yaml` is **gitignored**, so it is NOT
present in images built from GitHub. In the `production` profile the app reads
`DATABASE_URI` and `DATABASE_PASSWORD` from the environment. In OpenShift these
come from the `app-config` ConfigMap (`DATABASE_URI`) and the `app-db-secret`
Secret (`DATABASE_PASSWORD`). If `DATABASE_URI` is unset in production the app
fails at startup.

## Running Locally

The quickest path is compose, which starts both the Flask app and a local
Azure SQL Edge database:

```bash
podman-compose up --build      # or: docker-compose up --build
```

Access the app at: http://localhost:8081

## Deploying to OpenShift

Both environments use the manifests under `oc/`. The cloud set builds its image
in-cluster from GitHub; the on-prem set pulls a pre-built image from Harbor.

> The manifests keep the DB password in a plaintext `app-db-secret.yml` for this
> POC. For anything beyond a POC, source it from an external secret store
> (External Secrets Operator / Vault) instead of committing it.

### Cloud (ROSA / AWS) — `oc/cloud/`

Namespace `ks-hybrid-cloud-poc`. The image is built in-cluster by the
BuildConfig, which pulls source from the GitHub repo and pushes to the internal
registry.

```bash
# 1. Log in to the ROSA cluster
oc login https://api.n0w7a5w8g3j0z4e.en6d.p3.openshiftapps.com:443 \
  --username cluster-admin --password <password>

# 2. Create / select the project
oc new-project ks-hybrid-cloud-poc

# 3. Build the image from GitHub (BuildConfig + ImageStream)
oc apply -f oc/buildconfig.yml -n ks-hybrid-cloud-poc
oc start-build app-build -n ks-hybrid-cloud-poc --follow

# 4. Apply config + secret + app
oc apply -f oc/cloud/app-configmap.yml -n ks-hybrid-cloud-poc
oc apply -f oc/cloud/app-db-secret.yml -n ks-hybrid-cloud-poc
oc apply -f oc/cloud/app-service.yml   -n ks-hybrid-cloud-poc
oc apply -f oc/cloud/app-deployment.yml -n ks-hybrid-cloud-poc

# 5. Expose it
#    Simple edge route on the default cluster domain:
oc create route edge app-route --service=app-service --port=5000 -n ks-hybrid-cloud-poc
#    OR the custom hostname + dedicated AWS NLB:
#    oc apply -f oc/cloud/ingresscontroller.yml
#    oc apply -f oc/cloud/app-route.yml -n ks-hybrid-cloud-poc

# 6. Verify
oc rollout status deployment/python-app -n ks-hybrid-cloud-poc
HOST=$(oc get route app-route -n ks-hybrid-cloud-poc -o jsonpath='{.spec.host}')
curl -sk -o /dev/null -w "HTTP %{http_code}\n" "https://$HOST/"   # expect 200
```

> The `oc/cloud/ingresscontroller.yml` `domain` field references a specific
> cluster; update it to the current cluster's apps domain before applying.

### On-prem OpenShift — `oc/onprem/`

Namespace `rosa-poc`. The image is pulled from Harbor, so the
`harbor-pull-secret` imagePullSecret must exist in the namespace first.

```bash
# 1. Log in to the on-prem cluster, then create / select the project
oc new-project rosa-poc

# 2. Ensure the Harbor pull secret exists (prerequisite for image pulls)
#    oc create secret docker-registry harbor-pull-secret \
#      --docker-server=harbor.krungsri.net --docker-username=<u> --docker-password=<p> -n rosa-poc

# 3. Apply config + secret
oc apply -f oc/onprem/app-configmap.yml -n rosa-poc
oc apply -f oc/onprem/app-db-secret.yml -n rosa-poc

# 4. (Optional) in-cluster MSSQL — only needed for the test profile
#    oc apply -f oc/onprem/mssql-deployment.yml -n rosa-poc
#    oc apply -f oc/onprem/mssql-service.yml    -n rosa-poc

# 5. Deploy the app + service + route + autoscaler
oc apply -f oc/onprem/app-service.yml    -n rosa-poc
oc apply -f oc/onprem/app-deployment.yml -n rosa-poc
oc apply -f oc/onprem/app-route.yml      -n rosa-poc
oc apply -f oc/onprem/hpa.yml            -n rosa-poc

# 6. Verify
oc rollout status deployment/python-app -n rosa-poc
oc get route app-route -n rosa-poc -o jsonpath='{.spec.host}'
```

### Updating a deployment

```bash
# Cloud: rebuild from GitHub, then roll out
oc start-build app-build -n ks-hybrid-cloud-poc --follow
oc rollout restart deployment/python-app -n ks-hybrid-cloud-poc

# On-prem: push a new image to Harbor, then roll out
oc rollout restart deployment/python-app -n rosa-poc
```

For a detailed cloud walkthrough and troubleshooting (including the
production-profile `DATABASE_URI` requirement), see
`.kiro/steering/deploy-openshift.md`.

## Development Rules

Coding standards and project guidelines live in Kiro steering files under
`.kiro/steering/`:

- `project-context.md` — Project overview, architecture, API reference
- `coding-standards.md` — PEP 8, type hints, project structure rules
- `deploy-openshift.md` — OpenShift deployment steps (use `#deploy-openshift` in chat)
