from pydantic import BaseModel, Field
from typing import Optional

class CustomerBase(BaseModel):
    customer_name: str = Field(..., example="John Doe")
    customer_street: Optional[str] = Field(None, example="123 Main St")
    customer_city: Optional[str] = Field(None, example="New York")

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    customer_id: int = Field(..., example=1)

    class Config:
        orm_mode = True