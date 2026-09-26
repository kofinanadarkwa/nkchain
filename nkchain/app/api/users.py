#this code creates the User API
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.database.connection import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


router = APIRouter(prefix = "/users", tags = ["Users"])


@router.post("/", response_model = UserResponse)#this adds functionality to create_user
#the route returns only id, username and created_at
def create_user(# This code is what allows users to be created
    user_data: UserCreate,
    db: Session = Depends(get_db)#this gives each request its own session

):
    user = User(username = user_data.username)

    db.add(user)
    db.commit()
    db.refresh(user)# this line reloads the row so id and created_at are populated before you return after the commit.

    return user