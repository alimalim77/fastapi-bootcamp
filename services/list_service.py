from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.list import List
from models.board import Board, BoardMember
from schemas.list_schema import ListCreate, ListUpdate, ListMove


class ListService:
    """Service for list-related business logic."""

    def create_list(self, board_id: int, user_id: int, list_data: ListCreate, db: Session) -> List:
        """Create a new list in a board."""
        # Check board exists and user has access
        if not self._user_has_board_access(board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this board")
        
        # Auto-calculate position if not provided
        position = list_data.position
        if position is None:
            position = List.get_max_position(db, board_id) + 1
        
        new_list = List(
            name=list_data.name,
            position=position,
            board_id=board_id
        )
        return new_list.save(db)

    def get_lists_by_board(self, board_id: int, user_id: int, db: Session) -> list[List]:
        """Get all lists for a board."""
        if not self._user_has_board_access(board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this board")
        
        return List.get_by_board(db, board_id)

    def get_list_by_id(self, list_id: int, user_id: int, db: Session) -> List:
        """Get a specific list by ID."""
        list_item = List.get_by_id(db, list_id)
        if not list_item:
            raise HTTPException(status_code=404, detail="List not found")
        
        if not self._user_has_board_access(list_item.board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this board")
        
        return list_item

    def update_list(self, list_id: int, user_id: int, list_data: ListUpdate, db: Session) -> List:
        """Update a list's name."""
        list_item = self.get_list_by_id(list_id, user_id, db)
        
        if list_data.name is not None:
            list_item.name = list_data.name
        
        return list_item.save(db)

    def move_list(self, list_id: int, user_id: int, move_data: ListMove, db: Session) -> List:
        """Move a list to a new position within the board."""
        list_item = self.get_list_by_id(list_id, user_id, db)
        old_position = list_item.position
        new_position = move_data.position
        
        if old_position == new_position:
            return list_item
        
        # Get all lists in the board
        board_lists = List.get_by_board(db, list_item.board_id)
        
        # Shift positions of affected lists
        if new_position < old_position:
            # Moving up: shift others down
            for lst in board_lists:
                if new_position <= lst.position < old_position:
                    lst.position += 1
        else:
            # Moving down: shift others up
            for lst in board_lists:
                if old_position < lst.position <= new_position:
                    lst.position -= 1
        
        list_item.position = new_position
        db.commit()
        db.refresh(list_item)
        return list_item

    def delete_list(self, list_id: int, user_id: int, db: Session) -> None:
        """Delete a list and all its cards."""
        list_item = self.get_list_by_id(list_id, user_id, db)
        list_item.delete(db)

    def _user_has_board_access(self, board_id: int, user_id: int, db: Session) -> bool:
        """Check if user has access to the board."""
        board = Board.get_by_id(db, board_id)
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Owner always has access
        if board.owner_id == user_id:
            return True
        
        # Check if user is a member
        membership = BoardMember.get_membership(db, board_id, user_id)
        return membership is not None
