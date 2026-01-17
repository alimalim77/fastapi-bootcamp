from sqlalchemy.orm import Session
from models.todo import Todo
from schemas.todo_schema import TodoCreate, TodoUpdate
from fastapi import HTTPException


class TodoService:
    def create_todo(self, user_id: int, todo_data: TodoCreate, db: Session) -> Todo:
        todo = Todo(
            title=todo_data.title,
            description=todo_data.description,
            user_id=user_id
        )
        return todo.save(db)

    def get_todos_by_user(self, user_id: int, db: Session) -> list[Todo]:
        return Todo.get_by_user(db, user_id)

    def get_todo_by_id(self, todo_id: int, db: Session) -> Todo:
        todo = Todo.get_by_id(db, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo

    def update_todo(self, todo_id: int, todo_data: TodoUpdate, db: Session) -> Todo:
        todo = self.get_todo_by_id(todo_id, db)
        
        if todo_data.title is not None:
            todo.title = todo_data.title
        if todo_data.description is not None:
            todo.description = todo_data.description
        if todo_data.completed is not None:
            todo.completed = todo_data.completed
        
        return todo.save(db)

    def delete_todo(self, todo_id: int, db: Session) -> None:
        todo = self.get_todo_by_id(todo_id, db)
        todo.delete(db)
