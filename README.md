git clone https://github.com/Anubhav200311/banking_backend_college.git
cd banking

# Create a virtual environment
python -m venv venv

# Activate the environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

cd banking_backend
pip install -r requirements.txt

# In config.py
DB_PASSWORD = "your_actual_password"  # Replace with your MySQL password

# Make sure you're in the banking_backend directory
# Activate your virtual environment if not already activated
python -c "from db.init import initialize_database; initialize_database(password='your_actual_password')"


# Make sure you're in the banking_backend directory
uvicorn main:app --reload
