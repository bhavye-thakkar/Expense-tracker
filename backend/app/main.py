from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import crud, models, schemas
from .database import engine, get_db
import os
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")


# Add this new root route
@app.get("/")
async def root():
    return {
        "message": "Welcome to Expense Tracker API",
        "documentation": "/docs",
        "endpoints": {
            "users": "/users/",
            "expenses": "/expenses/",
            "statistics": "/statistics/"
        },
        "status": "running"
    }


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not crud.pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/expenses/", response_model=List[schemas.Expense])
def read_expenses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expenses = crud.get_expenses(db, user_id=current_user.id, skip=skip, limit=limit)
    return expenses


@app.post("/expenses/", response_model=schemas.Expense)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.create_expense(db=db, expense=expense, user_id=current_user.id)


@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expense = crud.delete_expense(db=db, expense_id=expense_id, user_id=current_user.id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}


@app.post("/groups/", response_model=schemas.Group)
def create_group(
    group: schemas.GroupCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_group(db, group.name, current_user.id)


@app.post("/groups/{group_id}/join")
def join_group(
    group_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.join_group(db, group_id, current_user.id)


@app.get("/groups/", response_model=list[schemas.Group])
def list_user_groups(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all groups that the current user is a member of"""
    return crud.get_user_groups(db, current_user.id, skip=skip, limit=limit)


@app.post("/groups/{group_id}/expenses", response_model=schemas.GroupExpense)
def create_group_expense(
    group_id: int,
    expense: schemas.GroupExpenseCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_group_expense(db, group_id, expense, current_user.id)


@app.get("/groups/{group_id}/expenses/", response_model=list[schemas.GroupExpense])
def list_group_expenses(
    group_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_group_expenses(
        db,
        group_id=group_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@app.delete("/groups/{group_id}/expenses/{expense_id}")
def delete_group_expense(
    group_id: int,
    expense_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.delete_group_expense(
        db,
        group_id=group_id,
        expense_id=expense_id,
        user_id=current_user.id
    )


# Added a new endpoint to search groups by name
@app.get("/groups/search/", response_model=list[schemas.Group])
def search_groups(
    name: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Search for groups by name (case-insensitive partial match)"""
    return db.query(models.Group).filter(
        models.Group.name.ilike(f"%{name}%")
    ).offset(skip).limit(limit).all()


@app.get("/groups/{group_id}/members/", response_model=List[schemas.GroupMemberBase])
def get_group_members(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get all members of a specific group"""
    return crud.get_group_members(db, group_id=group_id, current_user=current_user)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
