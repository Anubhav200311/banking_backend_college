from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from db.database import get_db_connection, execute_read_query, execute_read_single_query, execute_write_query
from models.payment import Payment, PaymentCreate

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[Payment])
def get_all_payments():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM payment"
        payments = execute_read_query(conn, query)
        return payments
    finally:
        conn.close()

@router.get("/{payment_number}", response_model=Payment)
def get_payment(payment_number: int):
    conn = get_db_connection()
    try:
        query = "SELECT * FROM payment WHERE payment_number = %s"
        payment = execute_read_single_query(conn, query, (payment_number,))
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        return payment
    finally:
        conn.close()

@router.post("/", response_model=Payment, status_code=status.HTTP_201_CREATED)
def create_payment(payment: PaymentCreate):
    conn = get_db_connection()
    try:
        # Verify loan exists
        loan_query = "SELECT * FROM loan WHERE loan_number = %s"
        loan = execute_read_single_query(conn, loan_query, (payment.loan_number,))
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        # Verify account exists
        account_query = "SELECT * FROM account WHERE account_number = %s"
        account = execute_read_single_query(conn, account_query, (payment.account_number,))
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Get next available payment_number
        query = "SELECT MAX(payment_number) as max_id FROM payment"
        result = execute_read_single_query(conn, query)
        next_id = 7001 if not result or result["max_id"] is None else result["max_id"] + 1
        
        # Create payment
        payment_query = "INSERT INTO payment (payment_number, payment_date, payment_amount) VALUES (%s, %s, %s)"
        execute_write_query(conn, payment_query, (next_id, payment.payment_date, payment.payment_amount))
        
        # Link payment to loan and account
        loan_payment_query = """
        INSERT INTO loan_payment (loan_number, account_number, payment_number) 
        VALUES (%s, %s, %s)
        """
        execute_write_query(
            conn, 
            loan_payment_query, 
            (payment.loan_number, payment.account_number, next_id)
        )
        
        return {
            "payment_number": next_id,
            "payment_date": payment.payment_date,
            "payment_amount": payment.payment_amount
        }
    finally:
        conn.close()