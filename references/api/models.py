from pydantic import BaseModel, Field
from typing import Optional

# A Pydantic model for an Item
class Item(BaseModel):
    name: str = Field(..., example="Apple")
    description: Optional[str] = Field(None, example="A delicious and healthy fruit.")
    price: float = Field(..., example=1.25)
    tax: Optional[float] = Field(None, example=0.10)

    # You can configure examples for the OpenAPI documentation
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Apple",
                "description": "A delicious and healthy fruit.",
                "price": 1.25,
                "tax": 0.10
            }
        }