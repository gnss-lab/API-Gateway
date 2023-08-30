from sqlalchemy.orm import Session

from core.database.models import TokenModel


def create_token_db(db: Session, user_id: int, token: str):
    db_token = TokenModel(user_id=user_id, token=token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)