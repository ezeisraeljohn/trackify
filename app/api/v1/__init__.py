from app.api.v1.endpoints.accounts import router as accounts_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.transactions import router as transactions_router
from app.api.v1.endpoints.insights import router as insights_router
from app.api.v1.endpoints.assistant import router as assistant_router

__all__ = [
    "accounts_router",
    "users_router",
    "auth_router",
    "transactions_router",
    "insights_router",
    "assistant_router",
]
