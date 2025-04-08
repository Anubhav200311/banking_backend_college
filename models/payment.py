from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import date

class PaymentBase(BaseModel):
    payment_date: date = Field(..., example="2023-04-15")
    payment_amount: Decimal = Field(..., example="250.00")

class PaymentCreate(PaymentBase):
    loan_number: int = Field(..., example=5001)
    account_number: int = Field(..., example=1001)

class Payment(PaymentBase):
    payment_number: int = Field(..., example=7001)

    class Config:
        orm_mode = True