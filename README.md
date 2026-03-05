gpu-job-management-api



Production-style backend for asynchronous GPU compute job management.



This project uses FastAPI for the API layer, Redis and Celery for asynchronous job processing, PostgreSQL for durable storage, and Alembic for database migrations. The application is containerized with Docker Compose for local development and service orchestration.





Overview



The platform is designed around a simple distributed workflow:



Client -> FastAPI -> Redis -> Celery Worker -> PostgreSQL



This architecture separates user-facing request handling from background processing and persistent storage, making the system easier to scale and maintain.





Project structure



gpu-job-management-api/

|

|-- app/ FastAPI application code

|-- worker/ Celery worker code

|-- docker/ Docker build files

|-- alembic/ Database migration scripts

|-- docker-compose.yml Multi-service local environment

|-- requirements.txt Python dependencies

|-- .env Local environment configuration

`-- README.md





Technology stack



-FastAPI



-Celery



-Redis



-PostgreSQL



-SQLAlchemy



-Alembic



-Docker Compose





Setup



Create a .env file in the project root with the required database, broker, and application settings



Start the services:



docker compose up -d --build



Apply database migrations:



docker compose run --rm

--user "$(id -u):$(id -g)"

-v "$(pwd):/app"

-w /app

api alembic upgrade head





Stop the services:



docker compose down





Development notes



For database migration commands, run Alembic from the containerized environment so the application dependencies, configuration, and project files are resolved consistently.





Future improvements



-job priority queues



-monitoring and observability



-admin tooling



-CI/CD



-cloud deployment



-GPU scheduling enhancements





Status



Actively in development.

