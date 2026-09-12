from fastapi import status, HTTPException, Response, APIRouter, Depends
from app.database import SessionDep
from app import models, schemas
from sqlmodel import select, or_
from app.oauth2 import get_current_user
from typing import Annotated
from sqlalchemy import func

router = APIRouter(prefix="/posts", tags=["posts"])


# get all posts
# response_model=list[schemas.Post]
@router.get("", response_model=list[schemas.PostWithVotes])
def get_posts(session: SessionDep, current_user: Annotated[models.User, Depends(get_current_user)], limit: int = 10, skip: int = 0, search: str = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    votes_query = select(models.Post, func.count(models.Vote.post_id).label("votes")).outerjoin(
        models.Vote, models.Vote.post_id == models.Post.id).group_by(models.Post.id).where(or_(models.Post.title.ilike(
            f"%{search}%"), models.Post.content.ilike(f"%{search}%"))).limit(limit).offset(skip)
    posts_with_votes = session.exec(votes_query).all()
    return posts_with_votes


# create a post
@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, session: SessionDep, current_user: Annotated[models.User, Depends(get_current_user)]):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(
        **post.model_dump(), owner_id=current_user.id)
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post


# get a post
@router.get("/{id}", response_model=schemas.PostWithVotes)
def get_post(id: int, session: SessionDep, current_user: Annotated[models.User, Depends(get_current_user)]):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    votes_query = select(models.Post, func.count(models.Vote.post_id).label("votes")).outerjoin(
        models.Vote, models.Vote.post_id == models.Post.id).group_by(models.Post.id).where(models.Post.id == id)
    post_with_votes = session.exec(votes_query).first()
    if not post_with_votes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return post_with_votes


# delete a post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, session: SessionDep, current_user: Annotated[models.User, Depends(get_current_user)]):
    # cursor.execute(
    #     """DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    deleted_post = session.get(models.Post, id)
    if deleted_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="you are not allowed to delete this post")
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    session.delete(deleted_post)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update a post
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostUpdate, session: SessionDep, current_user: Annotated[models.User, Depends(get_current_user)]):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    updated_post = session.get(models.Post, id)
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="you are not allowed to update this post")
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    # conn.commit()
    updated_post.sqlmodel_update(post.model_dump())
    session.commit()
    session.refresh(updated_post)
    return updated_post
