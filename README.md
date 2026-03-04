# gpu-job-management-api



Production-style backend system for submitting and managing asynchronous GPU compute jobs.



Built with FastAPI, Celery, PostgreSQL, Redis, and Docker.



\## Architecture



gpu-job-management-api/

│

├── app/                  # FastAPI service

│   ├── main.py

│   ├── core/

│   ├── models/

│   ├── schemas/

│   ├── routes/

│   └── services/

│

├── worker/               # Celery worker service

│   ├── celery\_app.py

│   └── tasks.py

│

├── docker/

│   ├── api.Dockerfile

│   └── worker.Dockerfile

│

├── docker-compose.yml

├── alembic/

├── requirements.txt

├── .env

├── .env.example

└── README.md



Client → FastAPI → Redis Queue → Celery Worker → PostgreSQL



            ┌────────────┐

            │   Client  	 │

            └─────┬──────┘

                  │

            ┌─────▼──────┐

            │  FastAPI  	 │

            └─────┬──────┘

                  │

            ┌─────▼──────┐

            │   Redis   	 │

            └─────┬──────┘

                  │

            ┌─────▼──────┐

            │  Celery   	 │

            │  Worker   	 │

            └─────┬──────┘

                  │

            ┌─────▼──────┐

            │ PostgreSQL	 │

            └────────────┘



\## Design Decisions



Why Celery instead of FastAPI BackgroundTasks?



BackgroundTasks run inside the API container.

Celery allows:



-Horizontal scaling



-Worker isolation



-Retries



-Failure handling



-Production-grade async processing





Why Redis as broker?



Redis is lightweight, fast, and commonly used with Celery for task queuing.





Why PostgreSQL over SQLite?



-Concurrency support



-Production reliability



-Transaction safety



-Real-world deployment parity





Why Separate Worker Container?



Separating the worker:



-Mirrors real distributed systems



-Enables independent scaling



-Improves fault isolation





Future Improvements



-Job priority queues



-Rate limiting



-Admin dashboard



-Monitoring with Flower



-Cloud deployment (AWS / Azure / Render)



-CI/CD pipeline





Purpose of This Project



This project is intentionally structured to reflect a real-world backend system used in cloud compute platforms.



It demonstrates understanding of:



-API architecture



-Distributed systems



-Infrastructure design



-Production-ready patterns





Status



Actively in development

