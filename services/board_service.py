from sqlalchemy.orm import Session
from models.board import Board, BoardMember, BoardRole
from schemas.board_schema import BoardCreate, BoardUpdate, BoardMemberAdd
from fastapi import HTTPException


class BoardService:
    
    def create_board(self, user_id: int, board_data: BoardCreate, db: Session) -> Board:
        """Create a new board with the user as owner and admin member"""
        board = Board(
            name=board_data.name,
            description=board_data.description,
            color=board_data.color or "#3B82F6",
            owner_id=user_id
        )
        board.save(db)
        
        # Add owner as admin member
        member = BoardMember(
            board_id=board.id,
            user_id=user_id,
            role=BoardRole.ADMIN
        )
        member.save(db)
        
        return board

    def get_boards_by_user(self, user_id: int, db: Session) -> list[Board]:
        """Get all boards where user is owner or member"""
        return Board.get_by_user(db, user_id)

    def get_board_by_id(self, board_id: int, user_id: int, db: Session) -> Board:
        """Get board by ID with access check"""
        board = Board.get_by_id(db, board_id)
        if not board:
            raise HTTPException(status_code=404, detail="Board not found")
        
        # Check if user has access
        if not self._user_has_access(board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Access denied to this board")
        
        return board

    def update_board(self, board_id: int, user_id: int, board_data: BoardUpdate, db: Session) -> Board:
        """Update board (admin only)"""
        board = self.get_board_by_id(board_id, user_id, db)
        
        # Check if user is admin
        if not self._user_is_admin(board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Only board admins can update the board")
        
        if board_data.name is not None:
            board.name = board_data.name
        if board_data.description is not None:
            board.description = board_data.description
        if board_data.color is not None:
            board.color = board_data.color
        
        return board.save(db)

    def delete_board(self, board_id: int, user_id: int, db: Session) -> None:
        """Delete board (owner only)"""
        board = self.get_board_by_id(board_id, user_id, db)
        
        if board.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Only the board owner can delete the board")
        
        board.delete(db)

    def add_member(self, board_id: int, user_id: int, member_data: BoardMemberAdd, db: Session) -> BoardMember:
        """Add a member to the board (admin only)"""
        # Check if requesting user is admin
        if not self._user_is_admin(board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Only board admins can add members")
        
        # Check if target user is already a member
        existing = BoardMember.get_membership(db, board_id, member_data.user_id)
        if existing:
            raise HTTPException(status_code=400, detail="User is already a member of this board")
        
        # Verify target user exists
        from models.user_model import User
        target_user = User.get_by_id(db, member_data.user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        member = BoardMember(
            board_id=board_id,
            user_id=member_data.user_id,
            role=member_data.role
        )
        return member.save(db)

    def remove_member(self, board_id: int, user_id: int, target_user_id: int, db: Session) -> None:
        """Remove a member from the board (admin only, cannot remove owner)"""
        board = self.get_board_by_id(board_id, user_id, db)
        
        # Cannot remove the owner
        if target_user_id == board.owner_id:
            raise HTTPException(status_code=400, detail="Cannot remove the board owner")
        
        # Check if requesting user is admin
        if not self._user_is_admin(board_id, user_id, db):
            raise HTTPException(status_code=403, detail="Only board admins can remove members")
        
        membership = BoardMember.get_membership(db, board_id, target_user_id)
        if not membership:
            raise HTTPException(status_code=404, detail="Member not found")
        
        membership.delete(db)

    def get_members(self, board_id: int, user_id: int, db: Session) -> list[BoardMember]:
        """Get all members of a board"""
        self.get_board_by_id(board_id, user_id, db)  # Access check
        return db.query(BoardMember).filter(BoardMember.board_id == board_id).all()

    def _user_has_access(self, board_id: int, user_id: int, db: Session) -> bool:
        """Check if user has access to the board (owner or member)"""
        membership = BoardMember.get_membership(db, board_id, user_id)
        return membership is not None

    def _user_is_admin(self, board_id: int, user_id: int, db: Session) -> bool:
        """Check if user is an admin of the board"""
        membership = BoardMember.get_membership(db, board_id, user_id)
        return membership is not None and membership.role == BoardRole.ADMIN
