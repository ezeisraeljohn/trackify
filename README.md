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
- (Optional) Python 3.10+ if you want to run the API app manually

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

Trackify uses Docker Compose to run background services (Celery worker, Celery beat, Redis), but **the FastAPI app itself should be run manually using Uvicorn**.

### 1. Choose the Environment

- By default, `compose.yml` uses `.env.development` as the `env_file` for all services.
- To use a different environment file (e.g., for production or testing), edit the `env_file:` section in `compose.yml` to point to `.env.production` or `.env.testing` as needed.

### 2. Start Background Services

Start Redis, Celery worker, and Celery beat using Docker Compose:

```bash
docker compose up --build
```

This will start:

- `trackify_redis`: Redis for Celery
- `trackify_celery_worker`: Celery worker for background jobs
- `trackify_celery_beat`: Celery beat for scheduled jobs

### 3. Run the FastAPI App

In a new terminal (with your virtual environment activated and dependencies installed), run the FastAPI app manually:

```bash
ENV=development uvicorn app.main:app --reload
```

- Adjust `ENV=development` to match your environment (`production`, `testing`, etc).
- The app will be available at [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs).

### 4. Apply Database Migrations

If you need to run Alembic migrations, do so manually:

```bash
ENV=development alembic upgrade head
```

---

## Running Without Docker

You can run everything manually if you prefer:

1. **Install Python dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Set up the database and environment variables as above.**

3. **Run Redis** (locally or via Docker):

   ```bash
   docker run -p 6379:6379 redis
   ```

4. **Run Alembic migrations:**

   ```bash
   ENV=development alembic upgrade head
   ```

5. **Run the FastAPI app:**

   ```bash
   ENV=development uvicorn app.main:app --reload
   ```

6. **Run Celery worker and beat:**

   ```bash
   ENV=development celery -A app.celery_app.celery_app worker --loglevel=info
   ENV=development celery -A app.celery_app.celery_app beat --loglevel=info
   ```

---

## API Documentation

- Swagger UI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- Redoc: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

---

## Running Tests

To run tests, you must ensure that the `app` package is discoverable by Python.  
**If you see `ModuleNotFoundError: No module named 'app'`, it means your Python path does not include the project root.**

**Recommended:**  
Run tests from the project root directory using the following command:

```bash
pytest
```

Or, explicitly set the `PYTHONPATH`:

```bash
PYTHONPATH=. pytest
```

If you are using a virtual environment, make sure it is activated.

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
