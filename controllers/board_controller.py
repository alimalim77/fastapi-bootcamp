from sqlalchemy.orm import Session
from services.board_service import BoardService
from schemas.board_schema import (
    BoardCreate, BoardUpdate, BoardResponse, BoardDetailResponse,
    BoardMemberAdd, BoardMemberResponse
)


class BoardController:
    def __init__(self):
        self.service = BoardService()

    def create_board(self, user_id: int, board_data: BoardCreate, db: Session) -> BoardResponse:
        board = self.service.create_board(user_id, board_data, db)
        return self._to_response(board, db)

    def get_boards(self, user_id: int, db: Session) -> list[BoardResponse]:
        boards = self.service.get_boards_by_user(user_id, db)
        return [self._to_response(b, db) for b in boards]

    def get_board(self, board_id: int, user_id: int, db: Session) -> BoardDetailResponse:
        board = self.service.get_board_by_id(board_id, user_id, db)
        members = self.service.get_members(board_id, user_id, db)
        
        member_responses = [
            BoardMemberResponse(
                user_id=m.user_id,
                email=m.user.email,
                role=m.role.value,
                joined_at=m.joined_at
            )
            for m in members
        ]
        
        return BoardDetailResponse(
            id=board.id,
            name=board.name,
            description=board.description,
            color=board.color,
            owner_id=board.owner_id,
            created_at=board.created_at,
            member_count=len(members),
            members=member_responses
        )

    def update_board(self, board_id: int, user_id: int, board_data: BoardUpdate, db: Session) -> BoardResponse:
        board = self.service.update_board(board_id, user_id, board_data, db)
        return self._to_response(board, db)

    def delete_board(self, board_id: int, user_id: int, db: Session) -> None:
        self.service.delete_board(board_id, user_id, db)

    def add_member(self, board_id: int, user_id: int, member_data: BoardMemberAdd, db: Session) -> BoardMemberResponse:
        member = self.service.add_member(board_id, user_id, member_data, db)
        return BoardMemberResponse(
            user_id=member.user_id,
            email=member.user.email,
            role=member.role.value,
            joined_at=member.joined_at
        )

    def remove_member(self, board_id: int, user_id: int, target_user_id: int, db: Session) -> None:
        self.service.remove_member(board_id, user_id, target_user_id, db)

    def _to_response(self, board, db: Session) -> BoardResponse:
        member_count = len(board.members) if board.members else 0
        return BoardResponse(
            id=board.id,
            name=board.name,
            description=board.description,
            color=board.color,
            owner_id=board.owner_id,
            created_at=board.created_at,
            member_count=member_count
        )
