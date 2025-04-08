from fastapi import FastAPI
import uvicorn
from config import API_TITLE, API_DESCRIPTION, API_VERSION

# Initialize FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Import and include routers
from routers import customers, accounts, employees, loans, payments

app.include_router(customers.router)
app.include_router(accounts.router)
app.include_router(employees.router)
app.include_router(loans.router)
app.include_router(payments.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Banking System API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)