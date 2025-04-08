from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class BranchBase(BaseModel):
    branch_name: str = Field(..., example="Main Branch")
    branch_city: Optional[str] = Field(None, example="Chicago")
    assets: Optional[Decimal] = Field(None, example="1000000.00")

class BranchCreate(BranchBase):
    pass

class Branch(BranchBase):
    class Config:
        orm_mode = True