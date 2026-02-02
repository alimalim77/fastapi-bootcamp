from sqlalchemy.orm import Session
from models.todo import Todo, Priority, CardMember
from models.list import List
from models.board import Board, BoardMember
from schemas.todo_schema import CardCreate, CardUpdate, CardMove
from fastapi import HTTPException


class CardService:
    """Service for card-related business logic."""

    def create_card(self, list_id: int, user_id: int, card_data: CardCreate, db: Session) -> Todo:
        """Create a new card in a list."""
        # Verify list exists and user has access
        list_item = List.get_by_id(db, list_id)
        if not list_item:
            raise HTTPException(status_code=404, detail="List not found")
        
        if not self._user_has_board_access(list_item.board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this board")
        
        # Auto-calculate position
        position = card_data.position
        if position is None:
            position = Todo.get_max_position(db, list_id) + 1
        
        priority = Priority(card_data.priority.value)
        card = Todo(
            title=card_data.title,
            description=card_data.description,
            priority=priority,
            position=position,
            due_date=card_data.due_date,
            list_id=list_id,
            user_id=user_id
        )
        return card.save(db)

    def get_cards_by_list(self, list_id: int, user_id: int, db: Session) -> list[Todo]:
        """Get all cards in a list."""
        list_item = List.get_by_id(db, list_id)
        if not list_item:
            raise HTTPException(status_code=404, detail="List not found")
        
        if not self._user_has_board_access(list_item.board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this board")
        
        return Todo.get_by_list(db, list_id)

    def get_card_by_id(self, card_id: int, user_id: int, db: Session) -> Todo:
        """Get a specific card by ID."""
        card = Todo.get_by_id(db, card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Check access via list's board
        if card.list_id:
            list_item = List.get_by_id(db, card.list_id)
            if list_item and not self._user_has_board_access(list_item.board_id, user_id, db):
                raise HTTPException(status_code=403, detail="Access denied to this board")
        
        return card

    def update_card(self, card_id: int, user_id: int, card_data: CardUpdate, db: Session) -> Todo:
        """Update a card's fields."""
        card = self.get_card_by_id(card_id, user_id, db)
        
        if card_data.title is not None:
            card.title = card_data.title
        if card_data.description is not None:
            card.description = card_data.description
        if card_data.completed is not None:
            card.completed = card_data.completed
        if card_data.priority is not None:
            card.priority = Priority(card_data.priority.value)
        if card_data.due_date is not None:
            card.due_date = card_data.due_date
        
        return card.save(db)

    def move_card(self, card_id: int, user_id: int, move_data: CardMove, db: Session) -> Todo:
        """Move a card to a new position or different list."""
        card = self.get_card_by_id(card_id, user_id, db)
        old_list_id = card.list_id
        old_position = card.position
        new_list_id = move_data.list_id or old_list_id
        new_position = move_data.position
        
        # Verify new list exists and user has access
        if new_list_id != old_list_id:
            new_list = List.get_by_id(db, new_list_id)
            if not new_list:
                raise HTTPException(status_code=404, detail="Target list not found")
            if not self._user_has_board_access(new_list.board_id, user_id, db):
                raise HTTPException(status_code=403, detail="Access denied to target board")
        
        # If moving within same list
        if new_list_id == old_list_id:
            if old_position != new_position:
                cards = Todo.get_by_list(db, old_list_id)
                if new_position < old_position:
                    for c in cards:
                        if new_position <= c.position < old_position:
                            c.position += 1
                else:
                    for c in cards:
                        if old_position < c.position <= new_position:
                            c.position -= 1
        else:
            # Moving to different list - shift positions in new list
            new_list_cards = Todo.get_by_list(db, new_list_id)
            for c in new_list_cards:
                if c.position >= new_position:
                    c.position += 1
        
        card.list_id = new_list_id
        card.position = new_position
        db.commit()
        db.refresh(card)
        return card

    def delete_card(self, card_id: int, user_id: int, db: Session) -> None:
        """Delete a card."""
        card = self.get_card_by_id(card_id, user_id, db)
        card.delete(db)

    def assign_member(self, card_id: int, target_user_id: int, user_id: int, db: Session) -> bool:
        """Assign a user to a card."""
        card = self.get_card_by_id(card_id, user_id, db)
        
        # Check if already assigned
        existing = db.query(CardMember).filter(
            CardMember.card_id == card_id,
            CardMember.user_id == target_user_id
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="User already assigned to card")
        
        CardMember.assign(db, card_id, target_user_id)
        return True

    def unassign_member(self, card_id: int, target_user_id: int, user_id: int, db: Session) -> bool:
        """Unassign a user from a card."""
        card = self.get_card_by_id(card_id, user_id, db)
        
        if not CardMember.unassign(db, card_id, target_user_id):
            raise HTTPException(status_code=404, detail="User not assigned to card")
        
        return True

    def _user_has_board_access(self, board_id: int, user_id: int, db: Session) -> bool:
        """Check if user has access to the board."""
        board = Board.get_by_id(db, board_id)
        if not board:
            return False
        
        if board.owner_id == user_id:
            return True
        
        membership = BoardMember.get_membership(db, board_id, user_id)
        return membership is not None


# Backwards compatibility alias
TodoService = CardService
