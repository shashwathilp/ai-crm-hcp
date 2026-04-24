# database.py
# This file sets up the connection between Python and PostgreSQL
# Think of it as plugging in a phone line to the database

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load the .env file so we can read DATABASE_URL and GROQ_API_KEY
load_dotenv()

# Read the database URL from .env
# Example: postgresql://postgres:mypassword@localhost:5432/crm_hcp
DATABASE_URL = os.getenv("DATABASE_URL")

# create_engine() opens the connection pool to PostgreSQL
# A "connection pool" is like having 5 phone lines open instead of 1
# so multiple requests can hit the DB at the same time
engine = create_engine(DATABASE_URL)

# SessionLocal is a "session factory"
# Every time we need to talk to the DB, we create a new session from this
# Think of a session like a single conversation with the database
# autocommit=False means we manually confirm (commit) every change
# autoflush=False means changes don't auto-send until we say so
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all our database models (tables)
# When we define a table in Python, it inherits from Base
Base = declarative_base()

# get_db() is a helper function used by FastAPI
# It creates a DB session, gives it to the route, then closes it when done
# "yield" means: give this session to whoever asked, then come back here to close it
# This is called a "dependency" in FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db  # hand the session to the route handler
    finally:
        db.close()  # always close, even if an error happened