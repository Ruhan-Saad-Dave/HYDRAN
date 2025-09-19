from fastapi import APIRouter
from typing import List
from .models import Item

# Create an APIRouter instance
router = APIRouter(
    prefix="/items", # The path prefix for all endpoints in this router
    tags=["items"]   # Tags for grouping in the API documentation
)

# Endpoint to create a new item
@router.post("/", response_model=Item)
def create_item(item: Item):
    return item

# Endpoint to get a single item by ID
@router.get("/{item_id}", response_model=Item)
def read_item(item_id: int):
    # In a real app, you would fetch the item from a database
    return {"name": f"Item {item_id}", "price": 10.0}

# Endpoint to get a list of all items
@router.get("/", response_model=List[Item])
def read_items():
    # In a real app, you would fetch items from a database
    return [
        {"name": "Laptop", "price": 1200.0},
        {"name": "Mouse", "price": 25.0}
    ]