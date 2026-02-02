from sqlalchemy.orm import Session
from services.checklist_service import ChecklistService
from schemas.checklist_schema import (
    ChecklistItemCreate, ChecklistItemUpdate, ChecklistItemResponse, ChecklistProgressResponse
)


class ChecklistController:
    def __init__(self):
        self.service = ChecklistService()

    def create_item(self, card_id: int, user_id: int, item_data: ChecklistItemCreate, db: Session) -> ChecklistItemResponse:
        item = self.service.create_item(card_id, user_id, item_data, db)
        return self._to_response(item)

    def get_items(self, card_id: int, user_id: int, db: Session) -> list[ChecklistItemResponse]:
        items = self.service.get_items_by_card(card_id, user_id, db)
        return [self._to_response(item) for item in items]

    def get_progress(self, card_id: int, user_id: int, db: Session) -> ChecklistProgressResponse:
        progress = self.service.get_progress(card_id, user_id, db)
        return ChecklistProgressResponse(
            total=progress["total"],
            completed=progress["completed"],
            percentage=progress["percentage"],
            items=[self._to_response(item) for item in progress["items"]]
        )

    def get_item(self, item_id: int, user_id: int, db: Session) -> ChecklistItemResponse:
        item = self.service.get_item_by_id(item_id, user_id, db)
        return self._to_response(item)

    def update_item(self, item_id: int, user_id: int, item_data: ChecklistItemUpdate, db: Session) -> ChecklistItemResponse:
        item = self.service.update_item(item_id, user_id, item_data, db)
        return self._to_response(item)

    def toggle_item(self, item_id: int, user_id: int, db: Session) -> ChecklistItemResponse:
        item = self.service.toggle_item(item_id, user_id, db)
        return self._to_response(item)

    def delete_item(self, item_id: int, user_id: int, db: Session) -> None:
        self.service.delete_item(item_id, user_id, db)

    def _to_response(self, item) -> ChecklistItemResponse:
        return ChecklistItemResponse(
            id=item.id,
            content=item.content,
            completed=item.completed,
            position=item.position,
            card_id=item.card_id,
            created_at=item.created_at
        )
