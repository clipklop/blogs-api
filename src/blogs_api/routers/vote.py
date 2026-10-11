from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
from blogs_api.schemas import Vote, Token
from blogs_api.database import get_db
from blogs_api.oauth2 import get_current_user

router = APIRouter(
    tags=["Votes"],
    prefix="/vote",
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: Vote, 
    db: Session = Depends(get_db), 
    current_user: int = Depends(get_current_user)
):
    """Cast a vote for a post."""
    vote_query = db.query(Vote).filter(
        Vote.post_id == vote.post_id, vote.user_id == current_user.id
    )
    found_vote = vote_query.first()
    if (vote.dir == 1):
       if found_vote:
           raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.id} has already voted on post {vote.post_id}")
        new_vote = Vote(post_id=vote.post_id, user_id=current_user.id)
       db.add(new_vote)
       db.commit()
       return {"message": "successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote doesn't exist.")
        vote_query.delete(synchronize_session=False)
        db.commit
        return {"message": "successfully deleted vote"}
