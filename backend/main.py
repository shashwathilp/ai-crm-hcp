# main.py
# This is the entry point of the entire backend
# Think of it as the reception desk of the restaurant
# It receives all incoming requests and routes them to the right department

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import hcps, interactions

# Create the FastAPI application
app = FastAPI(
    title="AI CRM HCP Module",
    description="An AI-first CRM for pharmaceutical field representatives",
    version="1.0.0"
)

# CORS = Cross-Origin Resource Sharing
# This is a security rule in browsers that blocks requests from different domains
# Our React app runs on localhost:3000, our API on localhost:8000
# Without CORS config, the browser would BLOCK React from talking to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # only allow our React app
    allow_credentials=True,
    allow_methods=["*"],    # allow GET, POST, PUT, DELETE etc.
    allow_headers=["*"],    # allow all headers
)

# Create all database tables if they don't exist
# Base.metadata.create_all reads all our models and creates their tables
# If tables already exist (from Phase 2), it skips them — safe to run multiple times
Base.metadata.create_all(bind=engine)

# Register the routers
# include_router() plugs in all the routes from each router file
app.include_router(hcps.router)
app.include_router(interactions.router)

# Root endpoint — just a health check
@app.get("/")
def root():
    return {
        "message": "AI CRM HCP Module is running",
        "docs": "Visit /docs for API documentation"
    }