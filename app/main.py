from fastapi import FastAPI
from app.db.session import get_session
from app.api.v1.endpoints import accounts, transactions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(accounts.router)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
