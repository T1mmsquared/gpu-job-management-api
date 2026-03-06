# gpu-job-management-api

Production-style backend for authenticated asynchronous job execution.

This project is a backend system for submitting, tracking, and managing background jobs through a clean API. It uses FastAPI for the application layer, Redis and Celery for asynchronous task execution, PostgreSQL for durable persistence, and Alembic for migration-based schema management. The full local stack runs with Docker Compose.

## Overview

The API is designed around a simple distributed workflow:

Client -> FastAPI API -> Redis Broker -> Celery Worker -> PostgreSQL


A user authenticates, submits a job, and receives an immediate API response while the actual work is processed asynchronously by a worker. Job state is stored in PostgreSQL so the system can track execution progress, results, and failures over time.

## Why this project

This project was built to demonstrate practical backend engineering patterns:

- Authentication with JWT-based protected routes
- Persistent job state and ownership rules
- Queue/worker separation for asynchronous execution
- Migration-driven database management with Alembic
- Containerized local development with Docker Compose
- Clear failure handling and safer delete behavior

## Features

- User registration and login
- JWT access tokens for protected endpoints
- Submit background jobs
- List only the current user's jobs
- View a specific job by ID
- Delete jobs only when safe to remove
- Persist job results and error messages
- Interactive API documentation through FastAPI

## Job lifecycle

Jobs move through these states:

- `queued`
- `running`
- `succeeded`
- `failed`

The current implementation includes two example job types:

- `test_sleep` — simulates asynchronous work by sleeping for a number of seconds
- `validate_payload` — validates required input and demonstrates a controlled failure path

## Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- Celery
- Docker Compose

## Project structure

gpu-job-management-api/
├── app/
│   ├── core/
│   ├── models/
│   ├── routes/
│   ├── schemas/
│   └── services/
├── worker/
├── docker/
├── alembic/
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md

## Local setup

### Prerequisites

- Docker
- Docker Compose
- Git

### 1. Clone the repository

```bash
git clone https://github.com/T1mmsquared/gpu-job-management-api.git
cd gpu-job-management-api
```

### 2. Rename the `.env.example` file

Rename a `.env.example` file in the project root to `.env.` and add your application, database, and broker settings.

Example:

```env
POSTGRES_USER=gpu_jobs
POSTGRES_PASSWORD=change_me
POSTGRES_DB=gpu_jobs
DATABASE_URL=postgresql+psycopg2://gpu_jobs:change_me@db:5432/gpu_jobs
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

### 3. Start the services

```bash
docker compose up -d --build
```

### 4. Apply migrations

```bash
docker compose run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/app" \
  -w /app \
  api alembic upgrade head
```

### 5. Confirm migration state

```bash
docker compose run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/app" \
  -w /app \
  api alembic current

docker compose run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/app" \
  -w /app \
  api alembic heads
```

### 6. Check running services

```bash
docker compose ps
```

### 7. Open the API docs

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

## Run commands

### Start the stack

```bash
docker compose up -d --build
```

### Stop the stack

```bash
docker compose down
```

### Stop and remove volumes

```bash
docker compose down -v
```

### Rebuild from scratch

```bash
docker compose down -v
docker compose up -d --build

docker compose run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/app" \
  -w /app \
  api alembic upgrade head
```

### View API logs

```bash
docker compose logs -f api
```

### View worker logs

```bash
docker compose logs -f worker
```

## Alembic workflow

### Upgrade to head

```bash
docker compose run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/app" \
  -w /app \
  api alembic upgrade head
```

### Check current revision

```bash
docker compose run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/app" \
  -w /app \
  api alembic current
```

### Check heads

```bash
docker compose run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/app" \
  -w /app \
  api alembic heads
```

### Create a new migration

Always upgrade first, then generate the next revision.

```bash
docker compose run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/app" \
  -w /app \
  api alembic upgrade head

docker compose run --rm \
  --user "$(id -u):$(id -g)" \
  -v "$(pwd):/app" \
  -w /app \
  api alembic revision --autogenerate -m "describe change"
```

## API examples

### Register

```bash
curl -s -X POST http://localhost:8000/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"Strong#Pass123"}'
echo
```

### Login and save token

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"Strong#Pass123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "$TOKEN"
```

### Submit a job

```bash
curl -s -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"job_type":"test_sleep","payload":{"seconds":2}}'
echo
```

### List jobs

```bash
curl -s "http://localhost:8000/jobs?limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"
echo
```

### Filter jobs by status

```bash
curl -s "http://localhost:8000/jobs?status=succeeded&limit=10&offset=0" \
  -H "Authorization: Bearer $TOKEN"
echo
```

### Get one job

```bash
curl -s http://localhost:8000/jobs/<JOB_ID> \
  -H "Authorization: Bearer $TOKEN"
echo
```

### Delete a job

```bash
curl -i -X DELETE http://localhost:8000/jobs/<JOB_ID> \
  -H "Authorization: Bearer $TOKEN"
```

## Example validation flow

### Successful job

```bash
curl -s -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"job_type":"test_sleep","payload":{"seconds":2}}'
```

### Failure path

```bash
curl -s -X POST http://localhost:8000/jobs \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"job_type":"validate_payload","payload":{}}'
```

### Protected route check

```bash
curl -i http://localhost:8000/jobs
```

### Expected behavior

- Unauthenticated access to `/jobs` returns `401 Unauthorized`
- Jobs created with `test_sleep` move to `succeeded`
- Jobs created with invalid `validate_payload` input move to `failed`
- A user cannot access another user's job
- Running jobs return `409 Conflict` on delete attempts
- Completed jobs can be deleted successfully

## Development notes

- After `docker compose down -v`, the database is empty and migrations must be applied again.
- Alembic is the schema source of truth for this project.
- The current implementation is focused on a clean backend slice rather than full production infrastructure.

## Future improvements

- True cancellation support for running jobs
- Retry policies and worker recovery handling
- Job priority queues
- Monitoring and observability
- Admin tooling
- CI/CD
- Deployment hardening
- GPU-specific scheduling improvements

## Status

Actively in development. The core backend flow is implemented and validated locally, including authentication, ownership enforcement, asynchronous job execution, migration-based schema management, failure handling, and safe deletion behavior.
