from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.security import get_password_hash, verify_password
from app.api.deps import get_current_active_user, get_current_active_admin

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Un usuario con este email ya existe.",
        )
    
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.patch("/me", response_model=UserResponse)
def update_users_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if user_in.email and user_in.email != current_user.email:
        existing = db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Un usuario con este email ya existe.",
            )
        current_user.email = user_in.email

    if user_in.new_password:
        if not user_in.current_password or not verify_password(
            user_in.current_password, current_user.hashed_password
        ):
            raise HTTPException(
                status_code=400,
                detail="La contraseña actual es incorrecta.",
            )
        current_user.hashed_password = get_password_hash(user_in.new_password)

    db.commit()
    db.refresh(current_user)
    return current_user

# Ejemplo de ruta protegida solo para ADMIN
@router.get("/all", response_model=list[UserResponse])
def read_all_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_admin)):
    users = db.query(User).all()
    return users
