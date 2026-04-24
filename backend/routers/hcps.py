# routers/hcps.py
# This file defines all the API routes related to HCPs (doctors)
# Think of routes as the different "windows" at a bank
# Each window handles a specific type of request

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models.interaction import HCP

# APIRouter groups related routes together
# prefix="/hcps" means all routes here start with /hcps
# tags=["HCPs"] groups them in the API documentation
router = APIRouter(prefix="/hcps", tags=["HCPs"])


# Pydantic models define the shape of data coming IN and going OUT
# Think of these as forms — they validate that all required fields are present

# HCPCreate = data shape when CREATING a new HCP
class HCPCreate(BaseModel):
    name: str
    specialty: Optional[str] = None   # Optional means not required
    hospital: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

# HCPResponse = data shape when RETURNING an HCP to the frontend
class HCPResponse(BaseModel):
    id: int
    name: str
    specialty: Optional[str] = None
    hospital: Optional[str] = None
    city: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True
        # from_attributes=True lets Pydantic read from SQLAlchemy objects
        # Without this, it can only read from plain dictionaries


# GET /hcps — returns all doctors
# Depends(get_db) automatically gives us a database session
@router.get("/", response_model=List[HCPResponse])
def get_all_hcps(db: Session = Depends(get_db)):
    """Get all Healthcare Professionals"""
    hcps = db.query(HCP).all()
    return hcps


# GET /hcps/{hcp_id} — returns one specific doctor by ID
# {hcp_id} is a path parameter — it comes from the URL itself
@router.get("/{hcp_id}", response_model=HCPResponse)
def get_hcp(hcp_id: int, db: Session = Depends(get_db)):
    """Get a specific HCP by ID"""
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        # HTTPException sends a proper error response with a status code
        # 404 = "Not Found" — standard HTTP convention
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp


# POST /hcps — creates a new doctor
# The request body must match HCPCreate shape
@router.post("/", response_model=HCPResponse)
def create_hcp(hcp_data: HCPCreate, db: Session = Depends(get_db)):
    """Create a new Healthcare Professional"""
    new_hcp = HCP(**hcp_data.model_dump())
    # **hcp_data.model_dump() unpacks the Pydantic model into keyword arguments
    # It's the same as writing: HCP(name=hcp_data.name, specialty=hcp_data.specialty, ...)
    db.add(new_hcp)
    db.commit()
    db.refresh(new_hcp)
    return new_hcp