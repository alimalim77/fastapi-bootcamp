from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.checklist_item import ChecklistItem
from models.todo import Todo
from models.list import List
from models.board import Board, BoardMember
from schemas.checklist_schema import ChecklistItemCreate, ChecklistItemUpdate


class ChecklistService:
    """Service for checklist-related business logic."""

    def create_item(self, card_id: int, user_id: int, item_data: ChecklistItemCreate, db: Session) -> ChecklistItem:
        """Create a new checklist item in a card."""
        card = self._get_card_with_access(card_id, user_id, db)
        
        # Auto-calculate position
        position = item_data.position
        if position is None:
            position = ChecklistItem.get_max_position(db, card_id) + 1
        
        item = ChecklistItem(
            content=item_data.content,
            position=position,
            card_id=card_id
        )
        return item.save(db)

    def get_items_by_card(self, card_id: int, user_id: int, db: Session) -> list[ChecklistItem]:
        """Get all checklist items for a card."""
        self._get_card_with_access(card_id, user_id, db)
        return ChecklistItem.get_by_card(db, card_id)

    def get_progress(self, card_id: int, user_id: int, db: Session) -> dict:
        """Get checklist completion progress for a card."""
        self._get_card_with_access(card_id, user_id, db)
        progress = ChecklistItem.get_progress(db, card_id)
        progress["items"] = ChecklistItem.get_by_card(db, card_id)
        return progress

    def get_item_by_id(self, item_id: int, user_id: int, db: Session) -> ChecklistItem:
        """Get a specific checklist item by ID."""
        item = ChecklistItem.get_by_id(db, item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Checklist item not found")
        
        # Verify access through card
        self._get_card_with_access(item.card_id, user_id, db)
        return item

    def update_item(self, item_id: int, user_id: int, item_data: ChecklistItemUpdate, db: Session) -> ChecklistItem:
        """Update a checklist item."""
        item = self.get_item_by_id(item_id, user_id, db)
        
        if item_data.content is not None:
            item.content = item_data.content
        if item_data.completed is not None:
            item.completed = item_data.completed
        
        return item.save(db)

    def toggle_item(self, item_id: int, user_id: int, db: Session) -> ChecklistItem:
        """Toggle a checklist item's completed status."""
        item = self.get_item_by_id(item_id, user_id, db)
        return item.toggle(db)

    def delete_item(self, item_id: int, user_id: int, db: Session) -> None:
        """Delete a checklist item."""
        item = self.get_item_by_id(item_id, user_id, db)
        item.delete(db)

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
