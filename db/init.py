import mysql.connector
from mysql.connector import Error
import pandas as pd

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")

def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL DB connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as err:
        print(f"Error: '{err}'")

# Connect and create database
# connection = create_server_connection("localhost", "root", "your_password")
# create_database_query = "CREATE DATABASE IF NOT EXISTS banking_system"
# create_database(connection, create_database_query)

# # Connect to the new DB
# db_connection = create_db_connection("localhost", "root", "your_password", "banking_system")

# Table creation
create_tables = [

    """
    CREATE TABLE branch (
        branch_name VARCHAR(50) PRIMARY KEY,
        branch_city VARCHAR(50),
        assets DECIMAL(15,2)
    );
    """,

    """
    CREATE TABLE customer (
        customer_id INT PRIMARY KEY,
        customer_name VARCHAR(50),
        customer_street VARCHAR(100),
        customer_city VARCHAR(50)
    );
    """,

    """
    CREATE TABLE employee (
        employee_id INT PRIMARY KEY,
        employee_name VARCHAR(50),
        telephone_number VARCHAR(20),
        dependent_name VARCHAR(50),
        start_date DATE,
        employment_length INT
    );
    """,

    """
    CREATE TABLE cust_banker (
        customer_id INT,
        employee_id INT,
        type VARCHAR(20),
        PRIMARY KEY (customer_id, employee_id),
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
        FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
    );
    """,

    """
    CREATE TABLE works_for (
        manager_id INT,
        worker_id INT,
        FOREIGN KEY (manager_id) REFERENCES employee(employee_id),
        FOREIGN KEY (worker_id) REFERENCES employee(employee_id)
    );
    """,

    """
    CREATE TABLE account (
        account_number INT PRIMARY KEY,
        balance DECIMAL(15,2)
    );
    """,

    """
    CREATE TABLE depositor (
        customer_id INT,
        account_number INT,
        access_date DATE,
        PRIMARY KEY (customer_id, account_number),
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
        FOREIGN KEY (account_number) REFERENCES account(account_number)
    );
    """,

    """
    CREATE TABLE savings_account (
        account_number INT PRIMARY KEY,
        interest_rate DECIMAL(5,2),
        FOREIGN KEY (account_number) REFERENCES account(account_number)
    );
    """,

    """
    CREATE TABLE checking_account (
        account_number INT PRIMARY KEY,
        overdraft_amount DECIMAL(10,2),
        FOREIGN KEY (account_number) REFERENCES account(account_number)
    );
    """,

    """
    CREATE TABLE loan (
        loan_number INT PRIMARY KEY,
        amount DECIMAL(15,2)
    );
    """,

    """
    CREATE TABLE loan_branch (
        branch_name VARCHAR(50),
        loan_number INT,
        PRIMARY KEY (branch_name, loan_number),
        FOREIGN KEY (branch_name) REFERENCES branch(branch_name),
        FOREIGN KEY (loan_number) REFERENCES loan(loan_number)
    );
    """,

    """
    CREATE TABLE borrower (
        customer_id INT,
        loan_number INT,
        PRIMARY KEY (customer_id, loan_number),
        FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
        FOREIGN KEY (loan_number) REFERENCES loan(loan_number)
    );
    """,

    """
    CREATE TABLE payment (
        payment_number INT PRIMARY KEY,
        payment_date DATE,
        payment_amount DECIMAL(10,2)
    );
    """,

    """
    CREATE TABLE loan_payment (
        loan_number INT,
        account_number INT,
        payment_number INT,
        PRIMARY KEY (loan_number, account_number, payment_number),
        FOREIGN KEY (loan_number) REFERENCES loan(loan_number),
        FOREIGN KEY (account_number) REFERENCES account(account_number),
        FOREIGN KEY (payment_number) REFERENCES payment(payment_number)
    );
    """
]

# # Execute all table creation queries
# for table_query in create_tables:
#     execute_query(db_connection, table_query)

#     # Replace the last part of init.py with:


def initialize_database(host="localhost", user="root", password="your_password"):
    # Connect and create database
    connection = create_server_connection(host, user, password)
    if connection is None:
        print("Failed to connect to MySQL server. Make sure it's running.")
        return None
        
    create_database_query = "CREATE DATABASE IF NOT EXISTS banking_system"
    create_database(connection, create_database_query)
    
    # Connect to the new DB
    db_connection = create_db_connection(host, user, password, "banking_system")
    if db_connection is None:
        print("Failed to connect to the banking_system database.")
        return None
    
    # Execute all table creation queries
    for table_query in create_tables:
        execute_query(db_connection, table_query)
    
    return db_connection

if __name__ == "__main__":
    initialize_database()
