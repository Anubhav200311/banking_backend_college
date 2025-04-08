from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class AccountBase(BaseModel):
    balance: Decimal = Field(..., example="1000.00")

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    account_number: int = Field(..., example=1001)

    class Config:
        orm_mode = True

class SavingsAccountBase(AccountBase):
    interest_rate: Decimal = Field(..., example="2.50")

class SavingsAccountCreate(SavingsAccountBase):
    pass

class SavingsAccount(SavingsAccountBase):
    account_number: int = Field(..., example=1001)

    class Config:
        orm_mode = True

class CheckingAccountBase(AccountBase):
    overdraft_amount: Decimal = Field(..., example="500.00")

class CheckingAccountCreate(CheckingAccountBase):
    pass

class CheckingAccount(CheckingAccountBase):
    account_number: int = Field(..., example=1002)

    class Config:
        orm_mode = True