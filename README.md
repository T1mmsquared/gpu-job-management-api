gpu-job-management-api



Production-style backend for asynchronous GPU compute job management.



This project uses FastAPI for the API layer, Redis and Celery for asynchronous job processing, PostgreSQL for durable storage, and Alembic for database migrations. The application is containerized with Docker Compose for local development and service orchestration.





Overview



The platform is designed around a simple distributed workflow:



Client -> FastAPI -> Redis -> Celery Worker -> PostgreSQL



This architecture separates user-facing request handling from background processing and persistent storage, making the system easier to scale and maintain.





Project structure



├── alembic

│   ├── env.py

│   ├── \_\_pycache\_\_

│   │   └── env.cpython-312.pyc

│   ├── README

│   ├── script.py.mako

│   └── versions

│       └── 90f9e28103f8\_initial\_schema.py

├── alembic.ini

├── app

│   ├── core

│   │   ├── config.py

│   │   ├── db.py

│   │   ├── deps.py

│   │   ├── \_\_pycache\_\_

│   │   └── security.py

│   ├── main.py

│   ├── models

│   │   ├── \_\_init\_\_.py

│   │   ├── job.py

│   │   └── user.py

│   ├── routes

│   │   └── auth.py

│   ├── schemas

│   │   ├── auth.py

│   │   └── job.py

│   └── services

│       ├── jobs.py

│       └── password\_policy.py

├── docker

│   ├── api.Dockerfile

│   └── worker.Dockerfile

├── docker-compose.yml

├── README.md

├── requirements.txt

└── worker

&nbsp;   ├── celery\_app.py

&nbsp;   └── tasks.py



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

