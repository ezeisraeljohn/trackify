from fastapi import APIRouter, Request, Header, HTTPException
from app.core import settings
import logging

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])

MONO_WEBHOOK_SECRET = settings.MONO_WEBHOOK_SECRET


@router.post("/mono")
async def mono_webhook(
    request: Request,
    mono_webhook_secret: str = Header(None, alias="mono-webhook-secret"),
):
    """
    Handle Mono webhook events.

    Args:
        request (Request): The incoming request containing the webhook data.
        mono_webhook_secret (str): The secret key for verifying the webhook.

    Returns:
        dict: A response indicating the success or failure of the webhook handling.
    """
    if mono_webhook_secret != MONO_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=403,
            detail="Unauthorized request",
        )
    payload = await request.json()
    event_type = payload.get("event")

    logging.info(f"Webhook Event: {event_type}")
    logging.info(f"Webhook Payload: {payload}")

    if event_type == "mono.events.account_updated":
        account_info = payload["data"]["account"]
        # process account update here
        logging.info(f"Updated account info: {account_info}")

    return {"status": "ok"}
