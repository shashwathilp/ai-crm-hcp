# routers/interactions.py
# API routes for interactions (meeting logs)
# This handles creating, reading, and the AI chat endpoint

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
from database import get_db
from models.interaction import Interaction, HCP
from agent.graph import run_agent

router = APIRouter(prefix="/interactions", tags=["Interactions"])


# Shape of data when creating an interaction via the FORM
class InteractionCreate(BaseModel):
    hcp_id: int
    rep_name: str
    interaction_date: date      # Python's date type validates format automatically
    interaction_type: str
    products_discussed: Optional[str] = None
    notes: Optional[str] = None
    next_steps: Optional[str] = None
    follow_up_date: Optional[date] = None


# Shape of data returned to the frontend
class InteractionResponse(BaseModel):
    id: int
    hcp_id: int
    rep_name: str
    interaction_date: date
    interaction_type: Optional[str] = None
    products_discussed: Optional[str] = None
    notes: Optional[str] = None
    summary: Optional[str] = None
    next_steps: Optional[str] = None
    follow_up_date: Optional[date] = None

    class Config:
        from_attributes = True


# Shape of a chat message from the frontend
class ChatMessage(BaseModel):
    role: str       # "user" or "assistant"
    content: str    # the actual text

class ChatRequest(BaseModel):
    messages: List[ChatMessage]   # full conversation history


# GET /interactions — get all interactions
@router.get("/", response_model=List[InteractionResponse])
def get_all_interactions(db: Session = Depends(get_db)):
    """Get all logged interactions"""
    interactions = db.query(Interaction)\
        .order_by(Interaction.created_at.desc())\
        .all()
    return interactions


# GET /interactions/{id} — get one interaction
@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Get a specific interaction by ID"""
    interaction = db.query(Interaction)\
        .filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


# POST /interactions — log a new interaction via the FORM
@router.post("/", response_model=InteractionResponse)
def create_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    """Log a new interaction using the structured form"""
    # Verify the HCP exists
    hcp = db.query(HCP).filter(HCP.id == data.hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    new_interaction = Interaction(**data.model_dump())
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)
    return new_interaction


# PUT /interactions/{id} — update an existing interaction
@router.put("/{interaction_id}", response_model=InteractionResponse)
def update_interaction(
    interaction_id: int,
    data: InteractionCreate,
    db: Session = Depends(get_db)
):
    """Update an existing interaction"""
    interaction = db.query(Interaction)\
        .filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    # Update each field
    for key, value in data.model_dump().items():
        setattr(interaction, key, value)
        # setattr(obj, "name", value) is same as obj.name = value
        # but lets us do it dynamically in a loop

    db.commit()
    db.refresh(interaction)
    return interaction


# POST /interactions/chat — the AI chat endpoint
# This is where the LangGraph agent gets called
@router.post("/chat/message")
async def chat_with_agent(request: ChatRequest):
    """
    Send a message to the LangGraph AI agent.
    The agent will understand the message and use the appropriate tool.
    """
    # Convert Pydantic models to the format LangGraph expects
    # LangGraph wants: [{"role": "user", "content": "..."}]
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]
    # This is a list comprehension — a compact way to build a list with a loop

    # Run the agent and get its response
    response = await run_agent(messages)
    return {"response": response}