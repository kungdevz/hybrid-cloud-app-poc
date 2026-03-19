# Requirements Document

## Introduction

This document specifies the requirements for the Hybrid Cloud App POC — a Flask-based user management REST API with an MSSQL backend, a single-page dashboard frontend, and hybrid cloud deployment targeting both local Docker Compose and Red Hat OpenShift (ROSA) on AWS. The system demonstrates a Controller → Service → Model architecture using Flask Blueprints, profile-based database configuration, containerized orchestration, and load testing infrastructure.

## Glossary

- **API_Server**: The Flask application that serves REST endpoints and the dashboard UI
- **User_Controller**: The Flask Blueprint handling HTTP routing for user CRUD operations at `/users`
- **Frontend_Controller**: The Flask Blueprint serving the dashboard UI and session management endpoints
- **User_Service**: The service layer containing business logic and database operations for User entities
- **User_Model**: The SQLAlchemy ORM model mapping to the `dbo.users` table in MSSQL
- **Dashboard**: The single-page HTML + vanilla JavaScript UI served at `/` for managing users
- **Config_Module**: The Python module (`config.py`) that initializes Flask, SQLAlchemy, Flask-Migrate, and profile-based database configuration
- **Database_Initializer**: The startup routine in `app.py` that creates database tables with retry logic
- **Docker_Compose_Stack**: The local development environment orchestrating the Flask app and Azure SQL Edge containers
- **OpenShift_Manifests**: The Kubernetes/OpenShift YAML files defining BuildConfig, Deployment, Service, Route, ConfigMap, HPA, and IngressController resources
- **Load_Test_Suite**: The k6-based load testing infrastructure with InfluxDB and Grafana for performance monitoring
- **Session_Manager**: The filesystem-based Flask-Session component managing server-side session state
- **HPA**: Horizontal Pod Autoscaler — the OpenShift resource that scales application pods based on CPU utilization
- **DB_Init_Script**: The SQL script (`init.sql`) that creates the `dbo.users` table and seeds initial data

## Requirements

### Requirement 1: User Creation via REST API

**User Story:** As an API consumer, I want to create a new user by sending a POST request with a handle, so that the user is persisted in the database.

#### Acceptance Criteria

1. WHEN a POST request with a valid JSON body containing a `handle` field is sent to `/users`, THE User_Controller SHALL return a JSON response with the created user's `id` and `handle` and HTTP status 200
2. WHEN a POST request is sent to `/users`, THE User_Service SHALL persist a new row in the `dbo.users` table with an auto-incremented `id` and the provided `handle`
3. THE User_Model SHALL define the `id` column as BigInteger with auto-increment and the `handle` column as String(200) not-null

### Requirement 2: List Users with Pagination

**User Story:** As an API consumer, I want to retrieve a paginated list of users, so that I can browse large datasets efficiently.

#### Acceptance Criteria

1. WHEN a GET request is sent to `/users` with optional `page` and `limit` query parameters, THE User_Controller SHALL return a JSON response containing a `users` array and a `meta` object with `page`, `limit`, `total`, and `pages` fields
2. WHEN `page` or `limit` query parameters are not valid integers, THE User_Controller SHALL default `page` to 1 and `limit` to 100
3. THE User_Service SHALL return users ordered by `id` ascending, offset by `(page - 1) * limit`, and limited to `limit` results

### Requirement 3: Get User by ID

**User Story:** As an API consumer, I want to retrieve a single user by ID, so that I can view specific user details.

#### Acceptance Criteria

1. WHEN a GET request is sent to `/users/<id>` with a valid user ID, THE User_Controller SHALL return a JSON response with the matching user's `id` and `handle`
2. WHEN a GET request is sent to `/users/<id>` with an ID that does not exist, THE User_Service SHALL raise a NotFound error with the message "no such entity found with id=<id>"

### Requirement 4: User Update via REST API

**User Story:** As an API consumer, I want to update an existing user's handle, so that I can correct or change user information.

#### Acceptance Criteria

1. WHEN a PUT request with a valid JSON body is sent to `/users/<id>`, THE User_Controller SHALL remove any `id` field from the request body before passing the data to the User_Service
2. WHEN a PUT request is sent to `/users/<id>` with a valid ID, THE User_Service SHALL update the matching row in `dbo.users` using a native SQL UPDATE statement and return the updated user
3. WHEN a PUT request is sent to `/users/<id>` with an ID that does not exist, THE User_Service SHALL raise a NotFound error
4. WHEN a PUT request is sent with an empty update body (after filtering out `id`), THE User_Service SHALL return the existing user without executing an UPDATE statement
5. IF the provided user ID is not a valid integer, THEN THE User_Service SHALL raise a NotFound error with the message "Invalid user ID format"

### Requirement 5: User Deletion via REST API

**User Story:** As an API consumer, I want to delete a user by ID, so that I can remove users from the system.

#### Acceptance Criteria

1. WHEN a DELETE request is sent to `/users/<id>` with a valid existing user ID, THE User_Service SHALL remove the user from the database and return `{"success": true}`
2. WHEN a DELETE request is sent to `/users/<id>` with an ID that does not exist, THE User_Service SHALL raise a NotFound error with the message "no such entity found with id=<id>"

### Requirement 6: HTTP Error Handling

**User Story:** As an API consumer, I want to receive consistent JSON error responses, so that I can programmatically handle errors.

#### Acceptance Criteria

1. WHEN an HTTPException occurs within the User_Controller Blueprint, THE User_Controller SHALL return a JSON response with `success: false` and a `message` field containing the error description
2. THE User_Controller SHALL set the response content type to `application/json` for all error responses

### Requirement 7: Dashboard User Interface with Session Management

**User Story:** As a user, I want a web-based dashboard to create, view, edit, and delete users with server-side session support, so that I can manage users without using API tools.

#### Acceptance Criteria

1. WHEN a GET request is sent to `/`, THE Frontend_Controller SHALL render the `index.html` template containing the User Management Dashboard
2. THE Dashboard SHALL display a form with fields for User ID (read-only) and Handle (required) and buttons for Create/Update and Reset
3. THE Dashboard SHALL display a paginated list of user cards, each showing the user's handle, ID, and action buttons for Edit and Delete
4. WHEN the user submits the form with a handle value and no editing ID is set, THE Dashboard SHALL send a POST request to `/users` to create a new user
5. WHEN the user clicks Edit on a user card, THE Dashboard SHALL fetch the user by ID via GET `/users/<id>` and populate the form fields for editing
6. WHEN the user submits the form while an editing ID is set, THE Dashboard SHALL send a PUT request to `/users/<id>` to update the user
7. WHEN the user clicks Delete on a user card and confirms the action, THE Dashboard SHALL send a DELETE request to `/users/<id>` and reload the user list
8. THE Dashboard SHALL display success and error alert messages that auto-dismiss after 5 seconds
9. THE Dashboard SHALL support pagination with Previous and Next buttons, displaying the current page and total pages
10. WHEN a POST request with a JSON body containing a `users` array is sent to `/api/session/users`, THE Frontend_Controller SHALL store the array in the server-side session and return `{"success": true, "message": "Session updated"}`
11. WHEN a GET request is sent to `/api/session/users`, THE Frontend_Controller SHALL return a JSON response with the `users` array from the session, defaulting to an empty array
12. WHEN a POST request is sent to `/api/session/clear`, THE Frontend_Controller SHALL clear all session data and return `{"success": true, "message": "Session cleared"}`
13. THE Config_Module SHALL configure Flask-Session with filesystem-based storage in a temporary directory, a file threshold of 200, and a session lifetime of 1800 seconds

### Requirement 8: Profile Selection

**User Story:** As a developer, I want to select a configuration profile via environment variables, so that the application loads the correct settings for each environment.

#### Acceptance Criteria

1. THE Config_Module SHALL support three profiles: `local`, `test`, and `production`, selected via the `PROFILE` or `APP_PROFILE` environment variable, defaulting to `production`
2. WHEN the `SQLALCHEMY_DATABASE_URI` environment variable is set, THE Config_Module SHALL use the value directly as the database connection string, bypassing profile-based configuration

### Requirement 9: Database Connection Configuration

**User Story:** As a developer, I want profile-specific database connection settings, so that the application connects to the correct database in each environment.

#### Acceptance Criteria

1. WHILE the `local` or `test` profile is active, THE Config_Module SHALL use the hardcoded MSSQL connection string targeting `database:1433/master` with ODBC Driver 18
2. WHILE the `production` profile is active, THE Config_Module SHALL read the database URI and password from `config.yaml`, with environment variable overrides for `DATABASE_URI` and `DATABASE_PASSWORD`
3. THE Config_Module SHALL URL-encode the database password using `urllib.parse.quote_plus` before substituting the password into the connection string

### Requirement 10: Database Initialization with Retry Logic

**User Story:** As a DevOps engineer, I want the application to retry database initialization on startup, so that it handles container startup ordering gracefully.

#### Acceptance Criteria

1. WHEN the API_Server starts, THE Database_Initializer SHALL attempt to create all database tables using `db.create_all()`
2. IF a database initialization attempt fails, THEN THE Database_Initializer SHALL retry up to 10 times with a 5-second delay between attempts
3. IF all 10 initialization attempts fail, THEN THE Database_Initializer SHALL log a warning and allow the application to continue starting

### Requirement 11: Containerized Development Environment

**User Story:** As a developer, I want a containerized local development setup with database schema initialization, so that I can run the full application stack locally with a single command.

#### Acceptance Criteria

1. THE Docker_Compose_Stack SHALL define two services: `app` (Flask application) and `database` (Azure SQL Edge)
2. THE Docker_Compose_Stack SHALL configure the `app` service to depend on the `database` service, map port 8081 to container port 5000, set `PROFILE=local`, and mount the `./app` directory as a volume
3. THE Docker_Compose_Stack SHALL configure the `database` service with Azure SQL Edge, expose port 1433, and set the `MSSQL_SA_PASSWORD` and `ACCEPT_EULA` environment variables
4. THE Docker_Compose_Stack SHALL connect both services via a shared `app-network` bridge network
5. THE DB_Init_Script SHALL create the `dbo.users` table with a `BIGINT IDENTITY(1,1)` primary key column `id` and an `NVARCHAR(200) NOT NULL` column `handle`, only if the table does not already exist
6. THE DB_Init_Script SHALL seed the `dbo.users` table with initial handles `jdoe_99` and `tech_wiz`, only if those handles do not already exist in the table
7. THE API_Server Containerfile SHALL use `python:3.12-slim-bookworm` as the base image
8. THE API_Server Containerfile SHALL install system dependencies including `curl`, `gnupg`, `gcc`, `g++`, `unixodbc-dev`, and Microsoft ODBC Driver 18 for SQL Server
9. THE API_Server Containerfile SHALL install Python dependencies from `requirements.txt` and expose port 5000
10. THE API_Server Containerfile SHALL set `python app.py` as the default command

### Requirement 12: Hybrid Cloud Deployment (OpenShift)

**User Story:** As a DevOps engineer, I want OpenShift manifests for deploying the application to both ROSA on AWS and on-premises OpenShift clusters, so that the application runs in production-grade Kubernetes environments with dedicated ingress and autoscaling.

#### Acceptance Criteria

1. THE OpenShift_Manifests SHALL define a BuildConfig that builds the Flask application image from the Git repository using the Containerfile in the `app/` directory
2. THE OpenShift_Manifests SHALL define a Deployment for `python-app` with resource requests (100m CPU, 128Mi memory) and limits (200m CPU, 256Mi memory), readiness probe on `/` port 5000, and liveness probe on `/` port 5000
3. THE OpenShift_Manifests SHALL define a ClusterIP Service (`app-service`) routing traffic to port 5000 on pods labeled `app: python-app`
4. THE OpenShift_Manifests SHALL define a Route (`app-route`) with edge TLS termination forwarding traffic to `app-service`
5. THE OpenShift_Manifests SHALL define a ConfigMap (`app-config`) containing `PROFILE` and `FLASK_APP` environment variables, referenced by the Deployment via `envFrom`
6. THE OpenShift_Manifests SHALL define a Deployment for the `database` service running Azure SQL Edge with port 1433 exposed and a corresponding ClusterIP Service
7. THE OpenShift_Manifests SHALL define an HPA targeting the `python-app` Deployment with min 1 replica, max 5 replicas, and a CPU utilization target of 70%
8. THE OpenShift_Manifests SHALL define an IngressController (`hybrid-cloud-ingress`) with an internal AWS NLB endpoint publishing strategy
9. THE OpenShift_Manifests SHALL configure the IngressController with a namespace selector matching `kubernetes.io/metadata.name: ks-hybrid-cloud-poc`
10. THE OpenShift_Manifests SHALL set the IngressController to use TLS 1.2 as the minimum TLS version and run 2 replicas
11. THE OpenShift_Manifests SHALL provide an on-premises variant in the `oc/onprem/` directory with Deployments pulling images from a private Harbor registry
12. THE OpenShift_Manifests SHALL configure the on-premises database Deployment with `runAsNonRoot: true` and dropped capabilities for security compliance
13. THE OpenShift_Manifests SHALL configure the on-premises Deployments to use `imagePullSecrets` referencing `harbor-pull-secret`

### Requirement 13: Load Testing Infrastructure

**User Story:** As a QA engineer, I want a k6 load testing setup with InfluxDB and Grafana, so that I can measure API performance and visualize results.

#### Acceptance Criteria

1. THE Load_Test_Suite SHALL define a k6 test script that executes a functional API happy path scenario (POST create, GET read, PUT update, DELETE) and a constant-arrival-rate load test scenario
2. THE Load_Test_Suite SHALL track custom metrics for error rate and API latency, with thresholds of less than 1% errors and p95 latency under 2000ms
3. THE Load_Test_Suite SHALL define a Docker Compose stack with k6, InfluxDB 1.8, and Grafana services connected via a shared network
4. THE Load_Test_Suite SHALL configure Grafana with provisioned datasources pointing to InfluxDB and a pre-built k6 dashboard
