from fastapi import HTTPException
from fastapi.params import Depends
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from app import schemas,models,database,config
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = config.settings.secret_key
ALGORITHM = config.settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = config.settings.access_token_expire_minutes

def create_jwt_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt_token

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("user_id")
        is_admin: bool = payload.get("is_admin")

        if id is None:
            raise credentials_exception

        token_data = schemas.AccessTokenData(user_id=id, is_admin=is_admin)
    except JWTError:
        raise credentials_exception

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme),  db: Session =  Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials.",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    current_user = db.query(models.User).filter(models.User.user_id == token.user_id).first()
    return current_user


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials.",
                                          headers={"WWW-Authenticate": "Bearer"})

    token_data = verify_access_token(token, credentials_exception)

    try:
        if not token_data.is_admin:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    admin_user = db.query(models.AdminUser).filter(models.AdminUser.user_id == token_data.user_id).first()


    return admin_user