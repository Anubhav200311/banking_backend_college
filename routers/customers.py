from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from db.database import get_db_connection, execute_read_query, execute_read_single_query, execute_write_query
from models.customer import Customer, CustomerCreate

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[Customer])
def get_all_customers():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM customer"
        customers = execute_read_query(conn, query)
        return customers
    finally:
        conn.close()

@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int):
    conn = get_db_connection()
    try:
        query = "SELECT * FROM customer WHERE customer_id = %s"
        customer = execute_read_single_query(conn, query, (customer_id,))
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer
    finally:
        conn.close()

@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate):
    conn = get_db_connection()
    try:
        # Get next available customer_id
        query = "SELECT MAX(customer_id) as max_id FROM customer"
        result = execute_read_single_query(conn, query)
        next_id = 1 if not result or result["max_id"] is None else result["max_id"] + 1
        
        # Insert new customer
        query = """
        INSERT INTO customer (customer_id, customer_name, customer_street, customer_city) 
        VALUES (%s, %s, %s, %s)
        """
        execute_write_query(conn, query, (
            next_id,
            customer.customer_name,
            customer.customer_street,
            customer.customer_city
        ))
        
        return {
            "customer_id": next_id,
            "customer_name": customer.customer_name,
            "customer_street": customer.customer_street,
            "customer_city": customer.customer_city
        }
    finally:
        conn.close()

@router.put("/{customer_id}", response_model=Customer)
def update_customer(customer_id: int, customer: CustomerCreate):
    conn = get_db_connection()
    try:
        # Check if customer exists
        check_query = "SELECT * FROM customer WHERE customer_id = %s"
        existing = execute_read_single_query(conn, check_query, (customer_id,))
        if not existing:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Update customer
        query = """
        UPDATE customer 
        SET customer_name = %s, customer_street = %s, customer_city = %s 
        WHERE customer_id = %s
        """
        execute_write_query(conn, query, (
            customer.customer_name,
            customer.customer_street,
            customer.customer_city,
            customer_id
        ))
        
        return {
            "customer_id": customer_id,
            "customer_name": customer.customer_name,
            "customer_street": customer.customer_street,
            "customer_city": customer.customer_city
        }
    finally:
        conn.close()

@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int):
    conn = get_db_connection()
    try:
        # Check if customer exists
        check_query = "SELECT * FROM customer WHERE customer_id = %s"
        existing = execute_read_single_query(conn, check_query, (customer_id,))
        if not existing:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Delete customer
        query = "DELETE FROM customer WHERE customer_id = %s"
        execute_write_query(conn, query, (customer_id,))
    finally:
        conn.close()