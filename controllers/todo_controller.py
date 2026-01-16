from sqlalchemy.orm import Session
from services.todo_service import TodoService
from schemas.todo_schema import TodoCreate, TodoUpdate, TodoResponse


class TodoController:
    def __init__(self):
        self.service = TodoService()

    def create_todo(self, user_id: int, todo_data: TodoCreate, db: Session) -> TodoResponse:
        todo = self.service.create_todo(user_id, todo_data, db)
        return todo

    def get_todos(self, user_id: int, db: Session) -> list[TodoResponse]:
        return self.service.get_todos_by_user(user_id, db)

    def get_todo(self, todo_id: int, db: Session) -> TodoResponse:
        return self.service.get_todo_by_id(todo_id, db)

    def update_todo(self, todo_id: int, todo_data: TodoUpdate, db: Session) -> TodoResponse:
        return self.service.update_todo(todo_id, todo_data, db)

    def delete_todo(self, todo_id: int, db: Session) -> None:
        self.service.delete_todo(todo_id, db)
