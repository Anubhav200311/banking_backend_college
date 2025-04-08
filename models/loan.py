from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class LoanBase(BaseModel):
    amount: Decimal = Field(..., example="10000.00")

class LoanCreate(LoanBase):
    branch_name: str = Field(..., example="Main Branch")

class Loan(LoanBase):
    loan_number: int = Field(..., example=5001)

    class Config:
        orm_mode = True

class BorrowerCreate(BaseModel):
    customer_id: int = Field(..., example=1)
    loan_number: int = Field(..., example=5001)

class Borrower(BorrowerCreate):
    pass

    class Config:
        orm_mode = True