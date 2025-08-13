from fastapi import Response, status, HTTPException, Depends,APIRouter
from app import schemas, models, functions, oauth2
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from starlette.concurrency import run_in_threadpool

from app.schemas import AccessToken

router = APIRouter(prefix= "/login",
                   tags=["auth"])

@router.get("/auth/me/")
async def check_token_validity(current_user: models.User = Depends(oauth2.get_current_user)):
    return "valid"


@router.post("/", response_model=schemas.AccessToken)
async def user_login(user_cred: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    def sync():
        user_cred_db = db.query(models.User).filter(models.User.user_email == user_cred.username).first()

        if not user_cred_db:
            raise HTTPException(status_code=403, detail="Invalid credentials")

        if not functions.compare_password(user_cred_db.user_password, user_cred.password):
            raise HTTPException(status_code=403, detail="Invalid credentials")

        access_token = oauth2.create_jwt_access_token(data={"user_id": user_cred_db.user_id, "is_admin": user_cred_db.is_admin})
        return {"access_token": access_token, "token_type": "bearer"}
    return await run_in_threadpool(sync)


@router.post("/admin", response_model=schemas.AccessToken)
async def admin_login(admin_cred: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    def sync():
        admin_cred_db = db.query(models.AdminUser).filter(models.AdminUser.user_email == admin_cred.username).first()

        if not admin_cred_db:
            raise HTTPException(status_code=403, detail="Invalid credentials")

        if not functions.compare_password( admin_cred_db.user_password,admin_cred.password ):
            raise HTTPException(status_code=403, detail="Invalid credentials")

        access_token = oauth2.create_jwt_access_token(data={"is_admin": admin_cred_db.is_admin, "user_id": admin_cred_db.user_id})
        return {"access_token": access_token, "token_type": "bearer"}
    return await run_in_threadpool(sync)



