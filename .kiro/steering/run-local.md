---
inclusion: manual
---

# Local Development Workflow

## Option 1: Docker Compose (Recommended)

```bash
docker-compose up --build
```

Access the app at <http://localhost:8081>

## Option 2: Python Virtual Environment

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
cd app && pip install -r requirements.txt
```

### 3. Configure database connection

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

Or run the DDL script directly: `db/init-scripts/init.sql`

### 5. Run the application

```bash
cd app && python app.py
```

Access the app at <http://localhost:5000>

## Verify Installation

```bash
curl http://localhost:5000/users
```

Expected response: `[]` or list of users JSON
