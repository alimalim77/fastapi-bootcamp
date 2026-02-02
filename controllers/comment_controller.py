from sqlalchemy.orm import Session
from services.comment_service import CommentService
from schemas.comment_schema import (
    CommentCreate, CommentUpdate, CommentResponse, CommentListResponse, AuthorResponse
)


class CommentController:
    def __init__(self):
        self.service = CommentService()

    def create_comment(self, card_id: int, author_id: int, comment_data: CommentCreate, db: Session) -> CommentResponse:
        comment = self.service.create_comment(card_id, author_id, comment_data, db)
        return self._to_response(comment)

    def get_comments(self, card_id: int, user_id: int, db: Session) -> CommentListResponse:
        comments = self.service.get_comments_by_card(card_id, user_id, db)
        return CommentListResponse(
            comments=[self._to_response(c) for c in comments],
            total=len(comments)
        )

    def get_comment(self, comment_id: int, user_id: int, db: Session) -> CommentResponse:
        comment = self.service.get_comment_by_id(comment_id, user_id, db)
        return self._to_response(comment)

    def update_comment(self, comment_id: int, user_id: int, comment_data: CommentUpdate, db: Session) -> CommentResponse:
        comment = self.service.update_comment(comment_id, user_id, comment_data, db)
        return self._to_response(comment)

    def delete_comment(self, comment_id: int, user_id: int, db: Session) -> None:
        self.service.delete_comment(comment_id, user_id, db)

    def _to_response(self, comment) -> CommentResponse:
        author_response = None
        if comment.author:
            author_response = AuthorResponse(
                id=comment.author.id,
                email=comment.author.email
            )
        
        return CommentResponse(
            id=comment.id,
            content=comment.content,
            card_id=comment.card_id,
            author_id=comment.author_id,
            author=author_response,
            created_at=comment.created_at,
            updated_at=comment.updated_at
        )
