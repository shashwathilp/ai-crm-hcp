# test_db.py
# This file just checks if Python can talk to PostgreSQL
# Think of it like making a test phone call before a big meeting

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# load_dotenv() reads the .env file and loads the variables into the environment
load_dotenv()

# os.getenv() fetches the DATABASE_URL we set in .env
DATABASE_URL = os.getenv("DATABASE_URL")

# create_engine() creates a "connection pool" to PostgreSQL
# Think of it as opening a phone line to the database
engine = create_engine(DATABASE_URL)

# Now let's test it by running a simple query
try:
    with engine.connect() as connection:
        # text() wraps raw SQL so SQLAlchemy can run it safely
        result = connection.execute(text("SELECT COUNT(*) FROM hcps"))
        count = result.fetchone()[0]
        print(f"✅ Database connected! Found {count} doctors in the HCPs table.")
except Exception as e:
    print(f"❌ Connection failed: {e}")