from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI() 

class Item(BaseModel):
    name: str
    price: float 
    is_offer: Union[bool, None] = None

@app.get("/")
async def read_root():
    return {"Hello": "World"}

# Create a GET endpoint that takes a path parameter 'name' and returns a greeting message
# If no path parameter is provided, query parameter of same function parameter name should be used
# Else an error is thrown to pass the name as ID Parameter
@app.get("/greet/{name}")
async def greet_name(name: Optional[str] = "User", 
                     age: int = 0 ) -> dict: 
    return {"name": f"Hello {name}", "age": age}
