from sqlalchemy.orm import Session
from services.label_service import LabelService
from schemas.label_schema import LabelCreate, LabelUpdate, LabelResponse


class LabelController:
    def __init__(self):
        self.service = LabelService()

    def create_label(self, board_id: int, user_id: int, label_data: LabelCreate, db: Session) -> LabelResponse:
        label = self.service.create_label(board_id, user_id, label_data, db)
        return self._to_response(label)

    def get_labels(self, board_id: int, user_id: int, db: Session) -> list[LabelResponse]:
        labels = self.service.get_labels_by_board(board_id, user_id, db)
        return [self._to_response(lbl) for lbl in labels]

    def get_label(self, label_id: int, user_id: int, db: Session) -> LabelResponse:
        label = self.service.get_label_by_id(label_id, user_id, db)
        return self._to_response(label)

    def update_label(self, label_id: int, user_id: int, label_data: LabelUpdate, db: Session) -> LabelResponse:
        label = self.service.update_label(label_id, user_id, label_data, db)
        return self._to_response(label)

    def delete_label(self, label_id: int, user_id: int, db: Session) -> None:
        self.service.delete_label(label_id, user_id, db)

    def attach_to_card(self, card_id: int, label_id: int, user_id: int, db: Session) -> None:
        self.service.attach_to_card(card_id, label_id, user_id, db)

    def detach_from_card(self, card_id: int, label_id: int, user_id: int, db: Session) -> None:
        self.service.detach_from_card(card_id, label_id, user_id, db)

    def _to_response(self, label) -> LabelResponse:
        return LabelResponse(
            id=label.id,
            name=label.name,
            color=label.color,
            board_id=label.board_id,
            created_at=label.created_at
        )
