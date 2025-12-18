from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from enum import Enum

app = FastAPI() 

class Item(BaseModel):
    name: str
    price: float 
    is_offer: Union[bool, None] = None 

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

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

# Usage of type for the parameter to get_model_info being enum shows the values
# present in the documentation as they are predefined ( from what the documentation says so far )
@app.get("/models/{model_name}")
async def get_model_info(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {
            model_name: "Deep Learning FTW!"
        }
    elif model_name == ModelName.resnet:
        return {
            model_name: "Residuals FTW!"
        }
    else:
        return {
            model_name: "LeCNN FTW!"
        }
    

# creating a route with pipe for multiple types and a defaul value 
@app.get("/items/price")
def read_item_price(price: int | None = None):
    if price is not None:
        return {"price": price}
    return {"price": "No price provided"}

# creating a route with handling boolean values and default conversion for truthy values 
# giving out unique function names avoids uncertain issues like distinguishing between two routes with same name
@app.get("/items/valid")
def read_item_valid(valid: bool = False):
    return {"valid": valid}
