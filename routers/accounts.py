from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from db.database import get_db_connection, execute_read_query, execute_read_single_query, execute_write_query
from models.account import Account, AccountCreate, SavingsAccount, SavingsAccountCreate, CheckingAccount, CheckingAccountCreate
from decimal import Decimal

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=List[Account])
def get_all_accounts():
    conn = get_db_connection()
    try:
        query = "SELECT * FROM account"
        accounts = execute_read_query(conn, query)
        return accounts
    finally:
        conn.close()

@router.get("/savings", response_model=List[SavingsAccount])
def get_savings_accounts():
    conn = get_db_connection()
    try:
        query = """
        SELECT a.account_number, a.balance, s.interest_rate
        FROM account a
        JOIN savings_account s ON a.account_number = s.account_number
        """
        accounts = execute_read_query(conn, query)
        return accounts
    finally:
        conn.close()

@router.get("/checking", response_model=List[CheckingAccount])
def get_checking_accounts():
    conn = get_db_connection()
    try:
        query = """
        SELECT a.account_number, a.balance, c.overdraft_amount
        FROM account a
        JOIN checking_account c ON a.account_number = c.account_number
        """
        accounts = execute_read_query(conn, query)
        return accounts
    finally:
        conn.close()

@router.post("/savings", response_model=SavingsAccount, status_code=status.HTTP_201_CREATED)
def create_savings_account(account: SavingsAccountCreate, customer_id: int):
    conn = get_db_connection()
    try:
        # Verify customer exists
        customer_query = "SELECT * FROM customer WHERE customer_id = %s"
        customer = execute_read_single_query(conn, customer_query, (customer_id,))
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get next available account_number
        query = "SELECT MAX(account_number) as max_id FROM account"
        result = execute_read_single_query(conn, query)
        next_id = 1001 if not result or result["max_id"] is None else result["max_id"] + 1
        
        # Create base account
        account_query = "INSERT INTO account (account_number, balance) VALUES (%s, %s)"
        execute_write_query(conn, account_query, (next_id, account.balance))
        
        # Create savings account
        savings_query = "INSERT INTO savings_account (account_number, interest_rate) VALUES (%s, %s)"
        execute_write_query(conn, savings_query, (next_id, account.interest_rate))
        
        # Link account to customer (depositor)
        depositor_query = "INSERT INTO depositor (customer_id, account_number, access_date) VALUES (%s, %s, CURDATE())"
        execute_write_query(conn, depositor_query, (customer_id, next_id))
        
        return {
            "account_number": next_id,
            "balance": account.balance,
            "interest_rate": account.interest_rate
        }
    finally:
        conn.close()

@router.post("/checking", response_model=CheckingAccount, status_code=status.HTTP_201_CREATED)
def create_checking_account(account: CheckingAccountCreate, customer_id: int):
    conn = get_db_connection()
    try:
        # Verify customer exists
        customer_query = "SELECT * FROM customer WHERE customer_id = %s"
        customer = execute_read_single_query(conn, customer_query, (customer_id,))
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get next available account_number
        query = "SELECT MAX(account_number) as max_id FROM account"
        result = execute_read_single_query(conn, query)
        next_id = 1001 if not result or result["max_id"] is None else result["max_id"] + 1
        
        # Create base account
        account_query = "INSERT INTO account (account_number, balance) VALUES (%s, %s)"
        execute_write_query(conn, account_query, (next_id, account.balance))
        
        # Create checking account
        checking_query = "INSERT INTO checking_account (account_number, overdraft_amount) VALUES (%s, %s)"
        execute_write_query(conn, checking_query, (next_id, account.overdraft_amount))
        
        # Link account to customer (depositor)
        depositor_query = "INSERT INTO depositor (customer_id, account_number, access_date) VALUES (%s, %s, CURDATE())"
        execute_write_query(conn, depositor_query, (customer_id, next_id))
        
        return {
            "account_number": next_id,
            "balance": account.balance,
            "overdraft_amount": account.overdraft_amount
        }
    finally:
        conn.close()

@router.post("/{account_number}/deposit")
def deposit(account_number: int, amount: float):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")
    
    conn = get_db_connection()
    try:
        # Check if account exists
        account_query = "SELECT * FROM account WHERE account_number = %s"
        account = execute_read_single_query(conn, account_query, (account_number,))
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Update balance
        new_balance = account["balance"] + Decimal(str(amount))
        update_query = "UPDATE account SET balance = %s WHERE account_number = %s"
        execute_write_query(conn, update_query, (new_balance, account_number))
        
        return {"message": f"Deposited {amount}. New balance: {new_balance}"}
    finally:
        conn.close()

@router.post("/{account_number}/withdraw")
def withdraw(account_number: int, amount: float):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")
    
    conn = get_db_connection()
    try:
        # Check if account exists and get current balance
        account_query = """
        SELECT a.account_number, a.balance, c.overdraft_amount 
        FROM account a
        LEFT JOIN checking_account c ON a.account_number = c.account_number
        WHERE a.account_number = %s
        """
        account = execute_read_single_query(conn, account_query, (account_number,))
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        
        # Check if sufficient funds (including overdraft for checking accounts)
        current_balance = account["balance"]
        overdraft_limit = account.get("overdraft_amount") or Decimal('0')
        
        if current_balance - Decimal(str(amount)) < -overdraft_limit:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Update balance
        new_balance = current_balance - Decimal(str(amount))
        update_query = "UPDATE account SET balance = %s WHERE account_number = %s"
        execute_write_query(conn, update_query, (new_balance, account_number))
        
        return {"message": f"Withdrew {amount}. New balance: {new_balance}"}
    finally:
        conn.close()