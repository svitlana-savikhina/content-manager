from datetime import date, datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import func, case, literal
from sqlalchemy.orm import Session

from posts import schemas, models
from posts.models import Comment
from posts.schemas import CommentAnalytics
from posts.text_moderation import check_profanity


def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    # Check for toxicity in title and content
    title_is_toxic, title_message = check_profanity(post.title)
    content_is_toxic, content_message = check_profanity(post.content)
    if title_is_toxic or content_is_toxic:
        raise HTTPException(
            status_code=400,
            detail="Content contains profanity or inappropriate language.",
        )

    try:
        db_post = models.Post(
            title=post.title,
            content=post.content,
            user_id=user_id,
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")


def get_post_by_id(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def get_all_posts(db: Session, skip: int = 0, limit: int = 10) -> List[models.Post]:
    return db.query(models.Post).offset(skip).limit(limit).all()


def update_post_by_id(
    db: Session, post_id: int, post_data: schemas.PostUpdate, user_id: int
):
    db_post = (
        db.query(models.Post)
        .filter(models.Post.id == post_id, models.Post.user_id == user_id)
        .first()
    )
    if db_post:
        try:
            title_is_toxic, title_message = check_profanity(post_data.title)
            content_is_toxic, content_message = check_profanity(post_data.content)

            if title_is_toxic or content_is_toxic:
                raise HTTPException(
                    status_code=400,
                    detail="Content contains profanity or inappropriate language.",
                )

            db_post.title = post_data.title
            db_post.content = post_data.content

            db.commit()
            db.refresh(db_post)
            return db_post

        except HTTPException as e:
            db.rollback()
            raise e

    else:
        raise HTTPException(status_code=404, detail="Post not found")


def delete_post_by_id(db: Session, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post:
        db.delete(post)
        db.commit()
        return True
    return False


def create_comment(
    db: Session, comment: schemas.CommentCreate, user_id: int, post_id: int
):
    content_is_toxic, content_message = check_profanity(comment.content)
    blocked = content_is_toxic

    try:
        db_comment = models.Comment(
            content=comment.content,
            user_id=user_id,
            post_id=post_id,
            created_at=comment.created_at,
            blocked=blocked,
        )

        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        if blocked:
            raise HTTPException(
                status_code=400,
                detail="Content contains profanity or inappropriate language.",
            )

        return db_comment

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to create comment: {str(e)}"
        )


def get_comments_for_post(db: Session, post_id: int, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Comment)
        .filter(models.Comment.post_id == post_id, models.Comment.blocked == False)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_comment(
    db: Session, comment_id: int, comment_data: schemas.CommentUpdate
) -> models.Comment:
    db_comment = (
        db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    )

    if db_comment:
        try:

            if db_comment.blocked:
                raise HTTPException(
                    status_code=400, detail="Cannot update blocked comment."
                )

            if comment_data.content:
                content_is_toxic, content_message = check_profanity(
                    comment_data.content
                )
                if content_is_toxic:
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot update comment with profanity or inappropriate language.",
                    )

            db_comment.content = comment_data.content
            db_comment.updated_at = comment_data.updated_at

            db.commit()
            db.refresh(db_comment)
            return db_comment

        except HTTPException as e:
            raise e
    else:
        raise HTTPException(status_code=404, detail="Comment not found")


def delete_comment_by_id_and_post_id(db: Session, comment_id: int, post_id: int):
    comment = (
        db.query(models.Comment)
        .filter(models.Comment.id == comment_id, models.Comment.post_id == post_id)
        .first()
    )

    if comment:
        if comment.blocked:
            raise HTTPException(
                status_code=400, detail="Cannot delete blocked comment."
            )
        db.delete(comment)
        db.commit()
        return True
    return False


def get_comments_data(
    date_from: date, date_to: date, db: Session
) -> List[CommentAnalytics]:
    created_comments_case = case((Comment.blocked == literal(False), 1), else_=0)
    blocked_comments_case = case((Comment.blocked == literal(True), 1), else_=0)

    result = (
        db.query(
            func.date(Comment.created_at).label("date"),
            func.sum(created_comments_case).label("created_comments"),
            func.sum(blocked_comments_case).label("blocked_comments"),
        )
        .filter(
            Comment.created_at >= datetime.combine(date_from, datetime.min.time()),
            Comment.created_at <= datetime.combine(date_to, datetime.max.time()),
        )
        .group_by(func.date(Comment.created_at))
        .order_by(func.date(Comment.created_at))
        .all()
    )

    return [
        CommentAnalytics(
            date=row.date,
            created_comments=row.created_comments,
            blocked_comments=row.blocked_comments,
        )
        for row in result
    ]
