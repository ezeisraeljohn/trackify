from .session import engine
from sqlmodel import SQLModel

from ..models import User, LinkedAccount, Transaction


def init_db():
    """Create the database tables."""
    SQLModel.metadata.create_all(engine)
