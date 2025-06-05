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

- Python 3.10+
- Docker & Docker Compose (optional, for containerized setup)
- PostgreSQL or SQLite
- Redis (for Celery)

### Clone the Repository

```bash
git clone https://github.com/yourusername/trackify.git
cd trackify
```

### Environment Variables

Copy and configure the appropriate `.env` file:

```bash
cp .env.development .env
# or for production
cp .env.production .env
```

Edit the `.env` file to set your database, Mono, Google, and email credentials.

### Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database Migration

```bash
alembic upgrade head
```

### Running the Application

#### Development

```bash
uvicorn app.main:app --reload
```

#### Production (with Docker)

```bash
docker build -t trackify .
docker run -p 8000:8000 --env-file .env trackify
```

### Running Celery Worker

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
├── app/
│   ├── api/
│   ├── core/
│   ├── crud/
│   ├── db/
│   ├── jobs/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
├── tests/
├── alembic/
├── requirements.txt
├── Dockerfile
├── compose.yml
├── .env
└── README.md
```

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
