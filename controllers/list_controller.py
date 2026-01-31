from sqlalchemy.orm import Session
from services.list_service import ListService
from schemas.list_schema import (
    ListCreate, ListUpdate, ListMove, ListResponse
)


class ListController:
    def __init__(self):
        self.service = ListService()

    def create_list(self, board_id: int, user_id: int, list_data: ListCreate, db: Session) -> ListResponse:
        list_item = self.service.create_list(board_id, user_id, list_data, db)
        return self._to_response(list_item)

    def get_lists(self, board_id: int, user_id: int, db: Session) -> list[ListResponse]:
        lists = self.service.get_lists_by_board(board_id, user_id, db)
        return [self._to_response(lst) for lst in lists]

    def get_list(self, list_id: int, user_id: int, db: Session) -> ListResponse:
        list_item = self.service.get_list_by_id(list_id, user_id, db)
        return self._to_response(list_item)

    def update_list(self, list_id: int, user_id: int, list_data: ListUpdate, db: Session) -> ListResponse:
        list_item = self.service.update_list(list_id, user_id, list_data, db)
        return self._to_response(list_item)

    def move_list(self, list_id: int, user_id: int, move_data: ListMove, db: Session) -> ListResponse:
        list_item = self.service.move_list(list_id, user_id, move_data, db)
        return self._to_response(list_item)

    def delete_list(self, list_id: int, user_id: int, db: Session) -> None:
        self.service.delete_list(list_id, user_id, db)

    def _to_response(self, list_item) -> ListResponse:
        return ListResponse(
            id=list_item.id,
            name=list_item.name,
            position=list_item.position,
            board_id=list_item.board_id,
            created_at=list_item.created_at
        )
