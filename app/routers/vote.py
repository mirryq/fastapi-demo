from fastapi import status, HTTPException, Response, APIRouter, Depends
from app import schemas, models, database, oauth2, database
from typing import Annotated
from sqlmodel import select, and_


router = APIRouter(prefix="/votes", tags=["votes"])


@router.post("", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, session: database.SessionDep, current_user: Annotated[models.User, Depends(oauth2.get_current_user)]):
    # 1. check if post exists
    post = session.get(models.Post, vote.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {vote.post_id} not found")

    # 2. check if user has already voted on this post
    vote_query = select(models.Vote).where(and_(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id))

    # 3. dir == 1 表示点赞，dir == 0 表示取消点赞
    found_vote = session.exec(vote_query).first()
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user {current_user.id} has already voted on post {vote.post_id}")
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        session.add(new_vote)
        session.commit()
        return {"message": "successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")
        session.delete(found_vote)
        session.commit()
        return {"message": "successfully deleted vote"}
