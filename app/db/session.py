from sqlmodel import Session, create_engine
from dotenv import load_dotenv
import os

load_dotenv()


DATABASE_URL = os.getenv("PROD_DATABASE_URL", "sqlite:///./app.db")
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    """Creates a Session for a transaction"""
    with Session(engine) as session:
        yield session
