from mysql.connector import Error
from db.init import create_db_connection
from fastapi import HTTPException
import os

# Get database credentials (you may also import these from config.py if available)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "your_new_password")
DB_NAME = os.environ.get("DB_NAME", "banking_system")

def get_db_connection():
    """Establish a database connection using configuration parameters"""
    return create_db_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

def execute_read_query(connection, query, params=None):
    """Execute a SELECT query returning multiple rows"""
    cursor = connection.cursor(dictionary=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()

def execute_read_single_query(connection, query, params=None):
    """Execute a SELECT query returning a single row"""
    cursor = connection.cursor(dictionary=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()

def execute_write_query(connection, query, params=None):
    """Execute an INSERT, UPDATE, or DELETE query"""
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        return cursor.lastrowid
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()