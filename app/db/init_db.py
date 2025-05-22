from .session import engine
from dotenv import load_dotenv
from sqlmodel import SQLModel

from ..models import User, LinkedAccount, Transaction


def init_db():
    """Create the database tables."""
    SQLModel.metadata.create_all(engine)


init_db()
