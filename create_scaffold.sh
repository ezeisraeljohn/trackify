#!/bin/bash

# Set the root directory name
ROOT_DIR="trackify"

# Define the full directory structure
mkdir -p $ROOT_DIR/app/api/v1/endpoints
mkdir -p $ROOT_DIR/app/core
mkdir -p $ROOT_DIR/app/services
mkdir -p $ROOT_DIR/app/models
mkdir -p $ROOT_DIR/app/schemas
mkdir -p $ROOT_DIR/app/crud
mkdir -p $ROOT_DIR/app/db
mkdir -p $ROOT_DIR/tests
mkdir -p $ROOT_DIR/alembic

# Create Python files
touch $ROOT_DIR/app/api/v1/endpoints/{auth.py,transactions.py,insights.py,assistant.py,users.py}
touch $ROOT_DIR/app/api/v1/__init__.py
touch $ROOT_DIR/app/api/deps.py

touch $ROOT_DIR/app/core/{config.py,security.py,settings.py}
touch $ROOT_DIR/app/services/{ai_engine.py,llm_assistant.py,insights.py,categorizer.py,mono_client.py}
touch $ROOT_DIR/app/models/{user.py,transaction.py,account.py,base.py}
touch $ROOT_DIR/app/schemas/{user.py,transaction.py,insight.py,assistant.py}
touch $ROOT_DIR/app/crud/{crud_user.py,crud_transaction.py,crud_insight.py}
touch $ROOT_DIR/app/db/{session.py,init_db.py,base.py}

touch $ROOT_DIR/app/main.py
touch $ROOT_DIR/app/__init__.py

# Create test files
touch $ROOT_DIR/tests/{test_transactions.py,test_ai_insights.py,test_auth.py}

# Create top-level files
touch $ROOT_DIR/.env
touch $ROOT_DIR/requirements.txt
touch $ROOT_DIR/Dockerfile
touch $ROOT_DIR/README.md

echo "Project structure for '$ROOT_DIR' created successfully."
echo "Remember to fill in the files with the appropriate code and configurations."
echo "You can now navigate to the '$ROOT_DIR' directory and start developing your application."
echo "To activate the virtual environment, run: source venv/bin/activate"
echo "To install the required packages, run: pip install -r requirements.txt"
echo "To run the application, use: uvicorn app.main:app --reload"
echo "To run the tests, use: pytest tests/"
echo "To build the Docker image, use: docker build -t trackify ."
echo "To run the Docker container, use: docker run -p 8000:8000 trackify"
echo "To run Alembic migrations, use: alembic upgrade head"
echo "To create a new Alembic migration, use: alembic revision --autogenerate -m 'migration_message'"
echo "To run Alembic in Docker, use: docker run -v $(pwd):/app trackify alembic upgrade head"