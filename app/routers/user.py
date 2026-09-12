from fastapi import status, HTTPException, APIRouter, Depends
from app.database import SessionDep
from app import models, schemas, utils, oauth2
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from typing import Annotated
from sqlalchemy import func

router = APIRouter(prefix="/users", tags=["users"])


# create a user
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, session: SessionDep):
    # hash the password - user.password
    new_user = models.User(
        email=user.email, password=utils.hash(user.password))
    session.add(new_user)
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already exists")
    session.refresh(new_user)
    return new_user


# get all posts from a user
@router.get("/posts", response_model=list[schemas.PostWithVotes])
def get_user_posts(current_user: Annotated[models.User, Depends(oauth2.get_current_user)], session: SessionDep):
    posts_with_votes = session.exec(select(models.Post, func.count(models.Vote.post_id).label("votes")).outerjoin(
        models.Vote, models.Vote.post_id == models.Post.id).group_by(models.Post.id).where(models.Post.owner_id == current_user.id)).all()
    return posts_with_votes


# get a user
@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, session: SessionDep):
    user = session.get(models.User, id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} was not found")
    return user
