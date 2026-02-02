from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.label import Label, CardLabel
from models.board import Board, BoardMember
from schemas.label_schema import LabelCreate, LabelUpdate


class LabelService:
    """Service for label-related business logic."""

    def create_label(self, board_id: int, user_id: int, label_data: LabelCreate, db: Session) -> Label:
        """Create a new label in a board."""
        if not self._user_has_board_access(board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this board")
        
        label = Label(
            name=label_data.name,
            color=label_data.color,
            board_id=board_id
        )
        return label.save(db)

    def get_labels_by_board(self, board_id: int, user_id: int, db: Session) -> list[Label]:
        """Get all labels for a board."""
        if not self._user_has_board_access(board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this board")
        
        return Label.get_by_board(db, board_id)

    def get_label_by_id(self, label_id: int, user_id: int, db: Session) -> Label:
        """Get a specific label by ID."""
        label = Label.get_by_id(db, label_id)
        if not label:
            raise HTTPException(status_code=404, detail="Label not found")
        
        if not self._user_has_board_access(label.board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this board")
        
        return label

    def update_label(self, label_id: int, user_id: int, label_data: LabelUpdate, db: Session) -> Label:
        """Update a label's name or color."""
        label = self.get_label_by_id(label_id, user_id, db)
        
        if label_data.name is not None:
            label.name = label_data.name
        if label_data.color is not None:
            label.color = label_data.color
        
        return label.save(db)

    def delete_label(self, label_id: int, user_id: int, db: Session) -> None:
        """Delete a label."""
        label = self.get_label_by_id(label_id, user_id, db)
        label.delete(db)

    def attach_to_card(self, card_id: int, label_id: int, user_id: int, db: Session) -> bool:
        """Attach a label to a card."""
        label = self.get_label_by_id(label_id, user_id, db)
        
        # Check if already attached
        existing = db.query(CardLabel).filter(
            CardLabel.card_id == card_id,
            CardLabel.label_id == label_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Label already attached to card")
        
        CardLabel.attach(db, card_id, label_id)
        return True

    def detach_from_card(self, card_id: int, label_id: int, user_id: int, db: Session) -> bool:
        """Detach a label from a card."""
        label = self.get_label_by_id(label_id, user_id, db)
        
        if not CardLabel.detach(db, card_id, label_id):
            raise HTTPException(status_code=404, detail="Label not attached to card")
        
        return True

    def _user_has_board_access(self, board_id: int, user_id: int, db: Session) -> bool:
        """Check if user has access to the board."""
        board = Board.get_by_id(db, board_id)
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        if board.owner_id == user_id:
            return True
        
        membership = BoardMember.get_membership(db, board_id, user_id)
        return membership is not None
