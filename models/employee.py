from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class EmployeeBase(BaseModel):
    employee_name: str = Field(..., example="Jane Smith")
    telephone_number: Optional[str] = Field(None, example="555-123-4567")
    dependent_name: Optional[str] = Field(None, example="Tom Smith")
    start_date: Optional[date] = Field(None, example="2020-01-15")
    employment_length: Optional[int] = Field(None, example=3)

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    employee_id: int = Field(..., example=101)

    class Config:
        orm_mode = True