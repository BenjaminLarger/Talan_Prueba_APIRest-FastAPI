from typing import Annotated
from app.config import settings

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from starlette import status

from app.database import get_db
from app.models.user import Users

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

db_dependency = Annotated[Session, Depends(get_db)]


def get_current_user_with_db(
    token: Annotated[str, Depends(oauth2_bearer)], db: Session = Depends(get_db)
) -> Users:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


user_dependency = Annotated[Users, Depends(get_current_user_with_db)]
