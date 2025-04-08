from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from db.database import get_db_connection, execute_read_query, execute_read_single_query, execute_write_query
from models.employee import Employee, EmployeeCreate

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[Employee])
def get_all_employees():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM employee"
        employees = execute_read_query(conn, query)
        return employees
    finally:
        conn.close()

@router.get("/{employee_id}", response_model=Employee)
def get_employee(employee_id: int):
    conn = get_db_connection()
    try:
        query = "SELECT * FROM employee WHERE employee_id = %s"
        employee = execute_read_single_query(conn, query, (employee_id,))
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        return employee
    finally:
        conn.close()

@router.post("/", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate):
    conn = get_db_connection()
    try:
        # Get next available employee_id
        query = "SELECT MAX(employee_id) as max_id FROM employee"
        result = execute_read_single_query(conn, query)
        next_id = 101 if not result or result["max_id"] is None else result["max_id"] + 1
        
        # Insert new employee
        query = """
        INSERT INTO employee (employee_id, employee_name, telephone_number, dependent_name, start_date, employment_length)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        execute_write_query(conn, query, (
            next_id,
            employee.employee_name,
            employee.telephone_number,
            employee.dependent_name,
            employee.start_date,
            employee.employment_length
        ))
        
        return {
            "employee_id": next_id,
            "employee_name": employee.employee_name,
            "telephone_number": employee.telephone_number,
            "dependent_name": employee.dependent_name,
            "start_date": employee.start_date,
            "employment_length": employee.employment_length
        }
    finally:
        conn.close()

@router.put("/{employee_id}", response_model=Employee)
def update_employee(employee_id: int, employee: EmployeeCreate):
    conn = get_db_connection()
    try:
        # Check if employee exists
        check_query = "SELECT * FROM employee WHERE employee_id = %s"
        existing = execute_read_single_query(conn, check_query, (employee_id,))
        if not existing:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Update employee
        query = """
        UPDATE employee 
        SET employee_name = %s, telephone_number = %s, dependent_name = %s, start_date = %s, employment_length = %s
        WHERE employee_id = %s
        """
        execute_write_query(conn, query, (
            employee.employee_name,
            employee.telephone_number,
            employee.dependent_name,
            employee.start_date,
            employee.employment_length,
            employee_id
        ))
        
        return {
            "employee_id": employee_id,
            "employee_name": employee.employee_name,
            "telephone_number": employee.telephone_number,
            "dependent_name": employee.dependent_name,
            "start_date": employee.start_date,
            "employment_length": employee.employment_length
        }
    finally:
        conn.close()

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int):
    conn = get_db_connection()
    try:
        # Check if employee exists
        check_query = "SELECT * FROM employee WHERE employee_id = %s"
        existing = execute_read_single_query(conn, check_query, (employee_id,))
        if not existing:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        # Delete employee
        query = "DELETE FROM employee WHERE employee_id = %s"
        execute_write_query(conn, query, (employee_id,))
    finally:
        conn.close()