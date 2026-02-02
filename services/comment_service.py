from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.comment import Comment
from models.todo import Todo
from models.list import List
from models.board import Board, BoardMember
from schemas.comment_schema import CommentCreate, CommentUpdate


class CommentService:
    """Service for comment-related business logic."""

    def create_comment(self, card_id: int, author_id: int, comment_data: CommentCreate, db: Session) -> Comment:
        """Create a new comment on a card."""
        # Verify card exists and user has access
        self._get_card_with_access(card_id, author_id, db)
        
        comment = Comment(
            content=comment_data.content,
            card_id=card_id,
            author_id=author_id
        )
        return comment.save(db)

    def get_comments_by_card(self, card_id: int, user_id: int, db: Session) -> list[Comment]:
        """Get all comments for a card."""
        self._get_card_with_access(card_id, user_id, db)
        return Comment.get_by_card(db, card_id)

    def get_comment_by_id(self, comment_id: int, user_id: int, db: Session) -> Comment:
        """Get a specific comment by ID."""
        comment = Comment.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Verify user has access to the card
        self._get_card_with_access(comment.card_id, user_id, db)
        return comment

    def update_comment(self, comment_id: int, user_id: int, comment_data: CommentUpdate, db: Session) -> Comment:
        """Update a comment (author-only)."""
        comment = self.get_comment_by_id(comment_id, user_id, db)
        
        # AUTHOR-ONLY: Only the comment author can edit
        if not comment.is_author(user_id):
            raise HTTPException(status_code=403, detail="Only the comment author can edit this comment")
        
        comment.content = comment_data.content
        return comment.save(db)

    def delete_comment(self, comment_id: int, user_id: int, db: Session) -> None:
        """Delete a comment (author-only)."""
        comment = self.get_comment_by_id(comment_id, user_id, db)
        
        # AUTHOR-ONLY: Only the comment author can delete
        if not comment.is_author(user_id):
            raise HTTPException(status_code=403, detail="Only the comment author can delete this comment")
        
        comment.delete(db)

    def _get_card_with_access(self, card_id: int, user_id: int, db: Session) -> Todo:
        """Get card and verify user has access."""
        card = Todo.get_by_id(db, card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Check access via card's list's board
        if card.list_id:
            list_item = List.get_by_id(db, card.list_id)
            if list_item and not self._user_has_board_access(list_item.board_id, user_id, db):
                raise HTTPException(status_code=403, detail="Access denied to this board")
        
        return card

    def _user_has_board_access(self, board_id: int, user_id: int, db: Session) -> bool:
        """Check if user has access to the board."""
        board = Board.get_by_id(db, board_id)
        if not board:
            return False
        
        if board.owner_id == user_id:
            return True
        
        membership = BoardMember.get_membership(db, board_id, user_id)
        return membership is not None
