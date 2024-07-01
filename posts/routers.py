from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import posts
from posts import models

from dependencies import get_db
from posts import schemas, crud
from posts.crud import get_all_posts, get_comments_data
from posts.schemas import CommentAnalytics
from users.crud import get_current_user

router = APIRouter()


@router.post("/posts/", response_model=schemas.PostCreate)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_post(db=db, post=post, user_id=current_user.id)


@router.get("/posts/{post_id}", response_model=schemas.Post)
def get_post_by_id(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_post = crud.get_post_by_id(db, post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@router.get("/all_posts/", response_model=List[schemas.Post])
def get_posts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    posts = get_all_posts(db, skip, limit)
    return posts


@router.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(
    post_id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing_post = crud.get_post_by_id(db=db, post_id=post_id)
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    if existing_post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this post",
        )
    updated_post = crud.update_post_by_id(
        db=db, post_id=post_id, post_data=post, user_id=current_user.id
    )
    return updated_post


@router.delete("/posts_del/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = crud.get_post_by_id(db, post_id)
    if not post:
        return {"message": "Post not found"}

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this post",
        )

    deleted = crud.delete_post_by_id(db, post_id)
    if deleted:
        return {"message": "Post deleted successfully"}
    else:
        return {"message": "Post not found"}


@router.post("/posts/{post_id}/comments/", response_model=schemas.Comment)
def create_comment_for_post(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.create_comment(
        db=db, comment=comment, user_id=current_user.id, post_id=post_id
    )


@router.get("/posts/{post_id}/all_comments/", response_model=list[schemas.Comment])
def read_comments_for_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_comments = crud.get_comments_for_post(db, post_id)
    return db_comments


@router.put("/posts/{post_id}/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(
    comment_id: int,
    comment_data: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    comment = crud.update_comment(db, comment_id, comment_data)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this comment",
        )

    updated_comment = crud.update_comment(db, comment_id, comment_data)
    return updated_comment


@router.delete("/posts/{post_id}/comments_del/{comment_id}")
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    comment = (
        db.query(models.Comment)
        .filter(models.Comment.id == comment_id, models.Comment.post_id == post_id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this comment",
        )

    deleted = crud.delete_comment_by_id_and_post_id(
        db=db, comment_id=comment_id, post_id=post_id
    )
    if deleted:
        return {"message": "Comment deleted successfully"}
    else:
        return {"message": "Comment not found"}


@router.get("/api/comments-daily-breakdown", response_model=List[CommentAnalytics])
def get_comments_daily_breakdown(
    date_from: date,
    date_to: date,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    comments_data = get_comments_data(date_from, date_to, db)
    return comments_data
