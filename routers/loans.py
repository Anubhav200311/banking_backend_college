from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from db.database import get_db_connection, execute_read_query, execute_read_single_query, execute_write_query
from models.loan import Loan, LoanCreate, Borrower, BorrowerCreate

router = APIRouter(
    prefix="/loans",
    tags=["loans"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[Loan])
def get_all_loans():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM loan"
        loans = execute_read_query(conn, query)
        return loans
    finally:
        conn.close()

@router.get("/{loan_number}", response_model=Loan)
def get_loan(loan_number: int):
    conn = get_db_connection()
    try:
        query = "SELECT * FROM loan WHERE loan_number = %s"
        loan = execute_read_single_query(conn, query, (loan_number,))
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        return loan
    finally:
        conn.close()

@router.post("/", response_model=Loan, status_code=status.HTTP_201_CREATED)
def create_loan(loan: LoanCreate):
    conn = get_db_connection()
    try:
        # Verify branch exists
        branch_query = "SELECT * FROM branch WHERE branch_name = %s"
        branch = execute_read_single_query(conn, branch_query, (loan.branch_name,))
        if not branch:
            raise HTTPException(status_code=404, detail="Branch not found")
        
        # Get next available loan_number
        query = "SELECT MAX(loan_number) as max_id FROM loan"
        result = execute_read_single_query(conn, query)
        next_id = 5001 if not result or result["max_id"] is None else result["max_id"] + 1
        
        # Create loan
        loan_query = "INSERT INTO loan (loan_number, amount) VALUES (%s, %s)"
        execute_write_query(conn, loan_query, (next_id, loan.amount))
        
        # Link loan to branch
        loan_branch_query = "INSERT INTO loan_branch (branch_name, loan_number) VALUES (%s, %s)"
        execute_write_query(conn, loan_branch_query, (loan.branch_name, next_id))
        
        return {
            "loan_number": next_id,
            "amount": loan.amount
        }
    finally:
        conn.close()

@router.post("/borrower", response_model=Borrower, status_code=status.HTTP_201_CREATED)
def add_borrower(borrower: BorrowerCreate):
    conn = get_db_connection()
    try:
        # Verify customer exists
        customer_query = "SELECT * FROM customer WHERE customer_id = %s"
        customer = execute_read_single_query(conn, customer_query, (borrower.customer_id,))
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Verify loan exists
        loan_query = "SELECT * FROM loan WHERE loan_number = %s"
        loan = execute_read_single_query(conn, loan_query, (borrower.loan_number,))
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        
        # Add borrower
        borrower_query = "INSERT INTO borrower (customer_id, loan_number) VALUES (%s, %s)"
        execute_write_query(conn, borrower_query, (borrower.customer_id, borrower.loan_number))
        
        return {
            "customer_id": borrower.customer_id,
            "loan_number": borrower.loan_number
        }
    except Exception as e:
        if "Duplicate entry" in str(e):
            raise HTTPException(status_code=400, detail="This customer is already a borrower for this loan")
        raise
    finally:
        conn.close()