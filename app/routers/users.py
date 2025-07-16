from app import schemas, models, functions, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends,APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.oauth2 import get_current_admin

router = APIRouter(
    prefix="/users",
    tags=["users"]
)




@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.UserCreateResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    hashed_password = functions.hash_password(user.user_password)
    user.user_password = hashed_password

    if hashed_password is None:
        raise HTTPException(status_code=500, detail=" password hashing failed")

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/", response_model=list[schemas.UserCreateResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()

    if users is None:
        raise HTTPException(status_code=404, detail="User not found")

    return users


@router.get("/{id}", response_model=schemas.UserCreateResponse)
def get_user(id:int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{id}")
def update_user_pass(id: int,
                     user_pass:schemas.UserUpdatePassword,
                     db: Session = Depends(get_db)):

    return functions.update_pass_by_user_id(db, id, user_pass.model_dump())

@router.post("/admin", status_code= status.HTTP_201_CREATED, response_model=schemas.UserCreateResponse)
def create_admin_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    hashed_password = functions.hash_password(user.user_password)
    user.user_password = hashed_password

    if hashed_password is None:
        raise HTTPException(status_code=500, detail=" password hashing failed")

    new_user = models.AdminUser(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user