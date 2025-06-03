from app.models import OTP
from ..utils.helpers import hash_otp, generate_otp, verify_otp as v_otp
from uuid import UUID
from sqlmodel import select, Session


def create_otp(db: Session, user_id: UUID) -> str:
    """
    Create a new OTP for the user and store it in the database.
    """
    otp = generate_otp()
    hashed_otp = hash_otp(otp)

    new_otp = OTP(user_id=user_id, otp_code=hashed_otp)
    print(new_otp)
    db.add(new_otp)
    db.commit()
    db.refresh(new_otp)
    return otp


def get_otp_by_user_id_and_is_used(
    db: Session,
    user_id: UUID,
    is_used: bool = False,
) -> OTP:
    """
    Retrieve the OTP for a user by user_id and is_used status.
    """
    statement = select(OTP).where(OTP.user_id == user_id, OTP.is_used == is_used)
    otp = db.exec(statement).first()
    if not otp:
        raise ValueError("Invalid OTP")
    if not otp.is_used:
        return otp


def verify_otp(db: Session, user_id: UUID, otp_code: str) -> bool:
    """
    Verify the OTP for the user.
    """
    otp = get_otp_by_user_id_and_is_used(db, user_id)

    if not otp:
        return False  # No valid OTP found for the user

    if v_otp(otp_code, otp.otp_code):
        otp.is_used = True  # Mark the OTP as used
        db.commit()
        return True

    return False  # OTP verification failed
