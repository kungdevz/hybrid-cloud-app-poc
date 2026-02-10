---
description: Set up and run the application locally
---

# Local Development Workflow

## Option 1: Docker Compose (Recommended)

// turbo

```bash
podman-compose up --build
```

Access the app at <http://localhost:8081>

## Option 2: Python Virtual Environment

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 2. Install dependencies

// turbo

```bash
cd app && pip install -r requirements.txt
```

### 3. Configure database connection

Set environment variables:

```bash
export DATABASE_URI='mssql+pyodbc://user:%s@host:port/db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes'
export DATABASE_PASSWORD='your_password'
```

Or edit `app/config.yaml` with your database settings.

### 4. Initialize database (first time only)

```bash
cd app
flask db init
flask db migrate
flask db upgrade
```

Or run the DDL script directly on MSSQL:

- `db/init-scripts/init.sql`

### 5. Run the application

// turbo

```bash
cd app && python app.py
```

Access the app at <http://localhost:5000>

## Verify Installation

// turbo

```bash
curl http://localhost:5000/users
```

Expected response: `[]` or list of users JSON
