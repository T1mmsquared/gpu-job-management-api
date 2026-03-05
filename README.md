gpu-job-management-api

Production-style backend system for submitting and managing asynchronous GPU compute jobs.



Built with FastAPI, Celery, PostgreSQL, Redis, Docker, SQLAlchemy, and Alembic.



Overview

This project is structured like a real-world backend system used for asynchronous compute workloads.



It exposes an API for job submission, pushes work to a Redis-backed queue, processes jobs in a separate Celery worker, and stores application data in PostgreSQL.



Project Structure

gpu-job-management-api/

|

|-- app/ FastAPI service

| |-- main.py

| |-- core/

| |-- models/

| |-- schemas/

| |-- routes/

| -- services/ | |-- worker/ Celery worker service | |-- celery\_app.py | -- tasks.py

|

|-- docker/

| |-- api.Dockerfile

| -- worker.Dockerfile | |-- alembic/ Database migration scripts |-- docker-compose.yml |-- requirements.txt |-- .env |-- .env.example -- README.md



Request flow:



Client -> FastAPI -> Redis Queue -> Celery Worker -> PostgreSQL



Tech Stack

FastAPI



Celery



Redis



PostgreSQL



SQLAlchemy



Alembic



Docker / Docker Compose



Pydantic Settings



Why This Design

Celery instead of FastAPI BackgroundTasks



FastAPI BackgroundTasks run inside the API process.



Celery is better for production-style asynchronous processing because it supports:



Worker isolation



Retries



Failure handling



Horizontal scaling



Separation between API and job execution



Redis as broker



Redis is lightweight, fast, and commonly used with Celery for task queuing.



PostgreSQL instead of SQLite



PostgreSQL is a better fit for concurrent workloads and production-style deployment.



Benefits include:



Better concurrency support



Transaction safety



Reliability under load



Real deployment parity



Separate worker container



Keeping the worker separate from the API:



Mirrors real distributed systems



Allows independent scaling



Improves fault isolation



Keeps web and job execution responsibilities separate



Environment Variables

Create a .env file in the project root.



Example values:



POSTGRES\_USER=gpu\_jobs

POSTGRES\_PASSWORD=changeme

POSTGRES\_DB=gpu\_jobs

DATABASE\_URL=postgresql://gpu\_jobs:changeme@db:5432/gpu\_jobs

CELERY\_BROKER\_URL=redis://redis:6379/0

CELERY\_RESULT\_BACKEND=redis://redis:6379/0

JWT\_SECRET=changeme

JWT\_ALGORITHM=HS256

JWT\_EXPIRES\_MINUTES=60



Docker Services

The project uses these services:



db PostgreSQL 16



redis Redis 7 Alpine



api FastAPI application



worker Celery worker



Dockerfiles

The API Dockerfile uses /app as the working directory and installs Python dependencies from requirements.txt, then copies in the application code.



That means files created at runtime inside the container only persist to your host machine if the project directory is bind-mounted.



Initial Setup

From the project root:



docker compose up -d --build



To stop the stack:



docker compose down



To stop and remove volumes:



docker compose down -v



Alembic Setup

Alembic is used for database migrations.



Important note:



If you run Alembic inside Docker without mounting the repo, generated files may be created only inside the container and not appear on the host filesystem.



Recommended command pattern for Alembic operations:



docker compose run --rm

--user "$(id -u):$(id -g)"

-v "$(pwd):/app"

-w /app

api alembic <command>



Using --user "$(id -u):$(id -g)" helps avoid root-owned files on the host.



Using -v "$(pwd):/app" ensures alembic.ini and migration files are read from and written to the host project directory.



Using -w /app ensures Alembic runs from the directory containing alembic.ini.



Alembic Workflow

Check current revision:



docker compose run --rm

--user "$(id -u):$(id -g)"

-v "$(pwd):/app"

-w /app

api alembic current



Show migration heads:



docker compose run --rm

--user "$(id -u):$(id -g)"

-v "$(pwd):/app"

-w /app

api alembic heads



Upgrade database:



docker compose run --rm

--user "$(id -u):$(id -g)"

-v "$(pwd):/app"

-w /app

api alembic upgrade head



Create a new migration:



Only do this after making actual SQLAlchemy model changes and after ensuring the database is already at head.



docker compose run --rm

--user "$(id -u):$(id -g)"

-v "$(pwd):/app"

-w /app

api alembic revision --autogenerate -m "describe change"



Important Alembic Notes

Do not run host alembic



Do not run plain host commands like:



alembic current

alembic heads



Those may use your host Python installation instead of the container environment and fail with missing dependency errors.



Use the Docker-based Alembic commands instead.



Avoid placeholder migrations



Do not create placeholder migrations with messages like:



add what changed



describe change



Only create a migration when there is a real schema change.



If you create and apply a migration, then delete the file later, Alembic history becomes inconsistent and you may need to reset the database volume in development.



If Alembic says "Target database is not up to date"



That means your database revision is behind the migration head.



Fix it by running:



docker compose run --rm

--user "$(id -u):$(id -g)"

-v "$(pwd):/app"

-w /app

api alembic upgrade head



Then rerun your revision --autogenerate command if needed.



Common Issues

Files created by Docker are owned by root



If MobaXterm or your editor says "Permission denied" when saving a file, fix ownership with:



sudo chown -R $(id -u):$(id -g) alembic alembic.ini



Alembic cannot find alembic.ini



Use:



-v "$(pwd):/app"



-w /app



or explicitly specify the config:



api alembic -c /app/alembic.ini current



Compose says service depends on undefined service



If docker compose config fails with errors like:



depends on undefined service "db"



depends on undefined service "redis"



the compose file may be malformed or saved incorrectly.



Validate with:



docker compose -f ./docker-compose.yml config



Development Reset

If Alembic history becomes inconsistent during development and you do not need to preserve local DB data:



docker compose down -v

rm -rf alembic/versions/pycache

docker compose up -d db redis

docker compose run --rm

--user "$(id -u):$(id -g)"

-v "$(pwd):/app"

-w /app

api alembic upgrade head



Future Improvements

Job priority queues



Rate limiting



Monitoring with Flower



Admin dashboard



Cloud deployment



CI/CD pipeline



Authentication and authorization hardening



Better job lifecycle tracking



GPU resource scheduling



Purpose of the Project

This project is intentionally structured to reflect a real-world backend system used in cloud compute platforms.



It demonstrates understanding of:



API architecture



Distributed systems



Infrastructure design



Production-ready patterns



Status

Actively in development.

