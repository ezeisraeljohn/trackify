# Trackify

Trackify is a modern financial tracking and insights platform that helps users link their bank accounts, sync transactions, and gain actionable insights using AI-powered analytics and large language models (LLMs). Built with FastAPI, SQLModel, Celery, and integrated with Mono and Google Gemini APIs, Trackify provides a robust backend for personal finance management.

---

## Features

- **User Authentication & Email Verification**  
  Secure registration, login, and email verification with OTP.

- **Bank Account Linking**  
  Seamless integration with Mono to link and fetch bank account details.

- **Transaction Syncing**  
  Fetch and store user transactions from linked accounts.

- **Automated Categorization**  
  Normalize and categorize transactions for better insights.

- **AI-Powered Insights**  
  Generate financial insights and summaries using LLMs (Google Gemini).

- **Email Notifications**  
  Send verification and notification emails via SMTP.

- **Celery Task Queue**  
  Background job processing for emails and insights.

- **RESTful API**  
  Well-structured, documented API endpoints with OpenAPI/Swagger support.

---

## Tech Stack

- **Python 3.10+**
- **FastAPI** (API framework)
- **SQLModel** (ORM)
- **PostgreSQL** (Production DB) / **SQLite** (Testing)
- **Celery** (Task queue)
- **Redis** (Broker/Backend for Celery)
- **Mono API** (Bank data aggregation)
- **Google Gemini** (LLM for AI insights)
- **Docker** (Containerization)
- **Alembic** (Database migrations)

---

## Getting Started

### Prerequisites

- Docker & Docker Compose (recommended for local development)
- (Optional) Python 3.10+ if you want to run without Docker

---

## Environment Variables

Trackify uses environment variables for configuration. Example variables are provided in `.env.example`.

1. **Copy the example file to the environment you want:**

   ```bash
   cp .env.example .env.development
   cp .env.example .env.testing
   cp .env.example .env.production
   ```

2. **Edit the copied file** (`.env.development`, `.env.testing`, or `.env.production`) and fill in the correct values for your environment (database, API keys, email, etc).

---

## Running Locally with Docker and Docker Compose

Trackify is designed to run easily with Docker Compose, which will set up the API, PostgreSQL database, and Redis for Celery automatically.

### 1. Choose the Environment

- By default, `compose.yml` uses `.env.development` as the `env_file` for all services.
- **To use a different environment file** (e.g., for production or testing), edit the `env_file:` section in `compose.yml` to point to `.env.production` or `.env.testing` as needed.

### 2. Build and Start All Services

```bash
docker compose up --build
```

This will start the following containers:

- `trackify_app`: FastAPI backend (with hot-reload)
- `trackify_db`: PostgreSQL database
- `trackify_redis`: Redis for Celery
- `trackify_alembic`: Runs Alembic migrations on startup
- `trackify_celery_worker`: Celery worker for background jobs
- `trackify_celery_beat`: Celery beat for scheduled jobs

### 3. Apply Database Migrations

If migrations do not run automatically, you can run them manually:

```bash
docker compose run --rm alembic
```

Or, to run a command inside the app container:

```bash
docker compose exec app alembic upgrade head
```

### 4. Access the API

- FastAPI docs: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- Redoc: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

### 5. Running Celery Worker/Beat (if not already running)

Celery worker and beat are started as services in the compose file. If you want to run them manually:

```bash
docker compose exec app celery -A app.celery_app.celery_app worker --loglevel=info
docker compose exec app celery -A app.celery_app.celery_app beat --loglevel=info
```

---

## Running Without Docker

You can still run the application directly with Python and manage dependencies and services yourself.

**Important:**  
When running any command manually (e.g., `uvicorn`, `alembic`, `celery`), specify the environment by setting the `ENV` variable, for example:

```bash
ENV=production uvicorn app.main:app --host 0.0.0.0 --port 8000
ENV=development alembic upgrade head
ENV=testing celery -A app.celery_app.celery_app worker --loglevel=info
```

This ensures the correct environment configuration is loaded.

1. **Install Python dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set up the database:**

   - For PostgreSQL, create a database and user, and update the `.env` file with the credentials.
   - For SQLite, ensure the file path in the `.env` file is correct.

3. **Run database migrations:**

   ```bash
   alembic upgrade head
   ```

4. **Start the FastAPI application:**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Run the Celery worker:**

   In a new terminal, activate the virtual environment and run:

   ```bash
   celery -A app.celery_app.celery_app worker --loglevel=info
   ```

---

## API Documentation

- Swagger UI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- Redoc: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

---

## Running Tests

```bash
pytest tests/
```

---

## Project Structure

```
trackify/
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 3abca017133a_initial_migration.py
│       ├── 9f9360a328ae_initial_migration.py
│       └── e11c008822ba_first_initialization.py
├── alembic.ini
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── accounts.py
│   │       │   ├── assistant.py
│   │       │   ├── auth.py
│   │       │   ├── insights.py
│   │       │   ├── transactions.py
│   │       │   ├── users.py
│   │       │   └── webhooks.py
│   │       └── __init__.py
│   ├── celery_app.py
│   ├── celeryconfig.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── crud/
│   │   ├── crud_account.py
│   │   ├── crud_insight.py
│   │   ├── crud_otp.py
│   │   ├── crud_transaction.py
│   │   ├── crud_user.py
│   │   └── __init__.py
│   ├── db/
│   │   ├── base.py
│   │   ├── init_db.py
│   │   ├── __init__.py
│   │   └── session.py
│   ├── email_templates/
│   │   ├── email_verification_reminder.html
│   │   └── verify_email.html
│   ├── jobs/
│   │   ├── email_jobs/
│   │   │   ├── email_jobs.py
│   │   │   └── __init__.py
│   │   ├── schedules/
│   │   │   ├── schedules.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── account.py
│   │   ├── base.py
│   │   ├── insight.py
│   │   ├── otp.py
│   │   ├── transaction.py
│   │   ├── user.py
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── assistant.py
│   │   ├── insight.py
│   │   ├── transaction.py
│   │   ├── user.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── ai_engine.py
│   │   ├── email_setup.py
│   │   ├── insights.py
│   │   ├── llm_assistant.py
│   │   ├── mono_client.py
│   │   └── normalizer.py
│   ├── utils/
│   │   ├── email_utils.py
│   │   └── helpers.py
│   └── __init__.py
├── compose.yml
├── create_scaffold.sh
├── Dockerfile
├── manifest.yml
├── README.md
├── requirements.txt
├── tests/
│   ├── test_ai_insights.py
│   ├── test_auth.py
│   └── test_transactions.py
```

> **Note:**  
> The following files and folders are excluded from version control as per `.gitignore` and should not be uploaded to GitHub:
>
> - `__pycache__/`
> - `.env*`
> - `.vscode/`
> - `transaction_sample.py`
> - `.trackify` (if present)
> - `celerybeat-schedule` (runtime file)

---

## Contribution

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [Mono](https://mono.co/)
- [Google Gemini](https://ai.google.dev/)
- [Celery](https://docs.celeryq.dev/)
