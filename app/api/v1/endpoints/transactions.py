from fastapi import APIRouter, Depends, HTTPException, requests
from sqlmodel import Session
from app.db.session import get_session
from app.services.mono_client import fetch_transactions
from ....models import Transaction
from datetime import datetime


router = APIRouter(prefix="/api/v1/transactions", tags=["Transactions"])


@router.post("/sync")
def sync_transactions(account_id: str, session: Session = Depends(get_session)):
    """Sync transactions for a linked account.
    This endpoint fetches transactions from the Mono API and stores them in the database.
    It is assumed that the account_id is already linked to a user in the database.
    The transactions are fetched using the Mono API and stored in the database.
    The transactions are associated with the linked account using the account_id.

    Args:
        account_id (str): The account ID to sync transactions for.
        session (Session, optional): _description_. Defaults to Depends(get_session).
    """
    try:
        # Fetch transactions from the Mono API
        transactions_response = fetch_transactions(account_id)
        transactions = transactions_response.get("data", [])

        if not transactions:
            return {"message": "No new transactions to sync."}

        # Store transactions in the database
        for transaction in transactions:
            # Create a new transaction object
            new_transaction = Transaction(
                account_id=account_id,
                user_id="bc9e0bfd-6082-4341-b792-a1097ada67a8",
                transaction_id=transaction.get("data").get("id"),
                transaction_type=transaction.get("data").get("type"),
                amount=transaction.get("data").get("amount"),
                currency=transaction.get("data").get("currency"),
                raw_description=transaction.get("data").get("narration"),
                normalized_description=transaction.get("data").get("narration"),
                transaction_date=datetime.strptime(
                    transaction.get("data").get("date"), "%Y-%m-%d"
                ).date(),
            )
            session.add(new_transaction)

        session.commit()
        return {"message": "Transactions synced successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
