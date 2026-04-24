# agent/tools.py
# These are the 5 tools our LangGraph AI agent can use
# Think of each tool as a specialist worker the agent can call on
# The agent reads the user's message and decides WHICH tool to use

from langchain_core.tools import tool
from sqlalchemy.orm import Session
from datetime import datetime, date
import json

# We import our database models so tools can read/write to PostgreSQL
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.interaction import HCP, Interaction
from database import SessionLocal

# Helper function to get a database session inside tools
# Tools don't use FastAPI's dependency injection, so we create sessions manually
def get_session():
    return SessionLocal()

# ============================================================
# TOOL 1: log_interaction
# Purpose: Save a new HCP interaction to the database
# The AI uses this when the user says something like:
# "I just met Dr. Sharma and discussed Metformin"
# ============================================================
@tool
def log_interaction(
    hcp_name: str,
    rep_name: str,
    interaction_date: str,
    interaction_type: str,
    products_discussed: str,
    notes: str,
    next_steps: str = "",
    follow_up_date: str = ""
) -> str:
    """
    Log a new interaction with an HCP (Healthcare Professional).
    Use this tool when the user wants to record a new meeting or conversation with a doctor.
    
    Args:
        hcp_name: Full name of the doctor (e.g. 'Dr. Arjun Sharma')
        rep_name: Name of the field representative logging this
        interaction_date: Date of interaction in YYYY-MM-DD format
        interaction_type: Type of meeting (e.g. 'In-person visit', 'Phone call')
        products_discussed: Medicines or products talked about
        notes: Detailed notes from the interaction
        next_steps: What needs to happen next (optional)
        follow_up_date: When to follow up in YYYY-MM-DD format (optional)
    """
    # Open a database session
    db = get_session()
    try:
        # Step 1: Find the HCP in our database by name
        # .filter() is like a WHERE clause in SQL
        # .first() gets the first matching result
        hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name}%")).first()
        # ilike() = case-insensitive search, so "dr sharma" finds "Dr. Sharma"

        # Step 2: If doctor doesn't exist yet, create them
        if not hcp:
            hcp = HCP(name=hcp_name)
            db.add(hcp)       # stage the new record
            db.commit()       # save it to the database
            db.refresh(hcp)   # reload it so we get the auto-generated id

        # Step 3: Parse the dates from string to Python date objects
        parsed_date = datetime.strptime(interaction_date, "%Y-%m-%d").date()
        parsed_follow_up = None
        if follow_up_date:
            parsed_follow_up = datetime.strptime(follow_up_date, "%Y-%m-%d").date()

        # Step 4: Create the new Interaction record
        new_interaction = Interaction(
            hcp_id=hcp.id,
            rep_name=rep_name,
            interaction_date=parsed_date,
            interaction_type=interaction_type,
            products_discussed=products_discussed,
            notes=notes,
            next_steps=next_steps,
            follow_up_date=parsed_follow_up
        )

        # Step 5: Save to database
        db.add(new_interaction)
        db.commit()
        db.refresh(new_interaction)

        return f"✅ Interaction logged successfully! ID: {new_interaction.id}, HCP: {hcp_name}, Date: {interaction_date}"

    except Exception as e:
        db.rollback()  # undo any partial changes if something went wrong
        return f"❌ Error logging interaction: {str(e)}"
    finally:
        db.close()  # always close the session


# ============================================================
# TOOL 2: edit_interaction
# Purpose: Update an existing interaction record
# The AI uses this when the user says:
# "Actually, change the notes on interaction #3"
# ============================================================
@tool
def edit_interaction(
    interaction_id: int,
    notes: str = "",
    next_steps: str = "",
    follow_up_date: str = "",
    products_discussed: str = "",
    summary: str = ""
) -> str:
    """
    Edit an existing interaction record by its ID.
    Use this tool when the user wants to update or correct a previously logged interaction.
    
    Args:
        interaction_id: The ID number of the interaction to edit
        notes: Updated notes (optional)
        next_steps: Updated next steps (optional)
        follow_up_date: Updated follow-up date in YYYY-MM-DD format (optional)
        products_discussed: Updated products list (optional)
        summary: Updated summary (optional)
    """
    db = get_session()
    try:
        # Find the interaction by its ID
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()

        # If it doesn't exist, tell the user
        if not interaction:
            return f"❌ No interaction found with ID {interaction_id}"

        # Only update fields that were actually provided (not empty strings)
        # This way we don't accidentally wipe out existing data
        if notes:
            interaction.notes = notes
        if next_steps:
            interaction.next_steps = next_steps
        if products_discussed:
            interaction.products_discussed = products_discussed
        if summary:
            interaction.summary = summary
        if follow_up_date:
            interaction.follow_up_date = datetime.strptime(follow_up_date, "%Y-%m-%d").date()

        db.commit()
        return f"✅ Interaction {interaction_id} updated successfully!"

    except Exception as e:
        db.rollback()
        return f"❌ Error editing interaction: {str(e)}"
    finally:
        db.close()


# ============================================================
# TOOL 3: get_hcp_profile
# Purpose: Fetch a doctor's profile and their interaction history
# The AI uses this when the user asks:
# "What's the history with Dr. Priya Nair?"
# ============================================================
@tool
def get_hcp_profile(hcp_name: str) -> str:
    """
    Get a Healthcare Professional's profile and their full interaction history.
    Use this tool when the user wants to look up information about a specific doctor.
    
    Args:
        hcp_name: The name of the doctor to look up
    """
    db = get_session()
    try:
        # Find the doctor by name (case-insensitive partial match)
        hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name}%")).first()

        if not hcp:
            return f"❌ No HCP found with name matching '{hcp_name}'"

        # Build a response string with all their details
        profile = f"""
👤 HCP Profile:
Name: {hcp.name}
Specialty: {hcp.specialty or 'Not specified'}
Hospital: {hcp.hospital or 'Not specified'}
City: {hcp.city or 'Not specified'}
Email: {hcp.email or 'Not specified'}
Phone: {hcp.phone or 'Not specified'}

📋 Interaction History ({len(hcp.interactions)} total):
"""
        # Loop through all interactions and add them to the response
        for i, interaction in enumerate(hcp.interactions, 1):
            profile += f"""
Interaction #{i} (ID: {interaction.id}):
  Date: {interaction.interaction_date}
  Type: {interaction.interaction_type}
  Products: {interaction.products_discussed}
  Notes: {interaction.notes}
  Next Steps: {interaction.next_steps}
  Follow-up: {interaction.follow_up_date}
"""
        return profile

    except Exception as e:
        return f"❌ Error fetching HCP profile: {str(e)}"
    finally:
        db.close()


# ============================================================
# TOOL 4: summarize_interaction
# Purpose: Use AI to generate a short summary of long notes
# The AI uses this when the user says:
# "Summarize my notes from the meeting with Dr. Sharma"
# ============================================================
@tool
def summarize_interaction(interaction_id: int) -> str:
    """
    Generate an AI summary for a specific interaction's notes.
    Use this when the user wants a concise summary of a logged interaction.
    
    Args:
        interaction_id: The ID of the interaction to summarize
    """
    db = get_session()
    try:
        interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()

        if not interaction:
            return f"❌ No interaction found with ID {interaction_id}"

        if not interaction.notes:
            return f"❌ Interaction {interaction_id} has no notes to summarize"

        # Return the notes so the LangGraph agent (which has LLM access)
        # can summarize them in its response
        # The actual summarization happens in the LLM layer, not here
        summary_prompt = f"""
Please summarize these interaction notes in 2-3 sentences:

Notes: {interaction.notes}
Products Discussed: {interaction.products_discussed}
Next Steps: {interaction.next_steps}
"""
        # Update the interaction with a placeholder so we know it was requested
        interaction.summary = f"Summary requested for: {interaction.notes[:100]}..."
        db.commit()

        return f"📝 Notes to summarize (Interaction #{interaction_id}):\n{summary_prompt}"

    except Exception as e:
        db.rollback()
        return f"❌ Error summarizing interaction: {str(e)}"
    finally:
        db.close()


# ============================================================
# TOOL 5: schedule_followup
# Purpose: Set or update the follow-up date for an interaction
# The AI uses this when the user says:
# "Schedule a follow-up with Dr. Nair for next week"
# ============================================================
@tool
def schedule_followup(
    hcp_name: str,
    follow_up_date: str,
    notes: str = ""
) -> str:
    """
    Schedule or update a follow-up date for an HCP interaction.
    Use this when the user wants to set a reminder or next meeting date with a doctor.
    
    Args:
        hcp_name: Name of the doctor
        follow_up_date: Date for the follow-up in YYYY-MM-DD format
        notes: Optional notes about what the follow-up is for
    """
    db = get_session()
    try:
        # Find the most recent interaction with this HCP
        hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name}%")).first()

        if not hcp:
            return f"❌ No HCP found matching '{hcp_name}'"

        # Get the latest interaction
        latest = db.query(Interaction)\
            .filter(Interaction.hcp_id == hcp.id)\
            .order_by(Interaction.created_at.desc())\
            .first()
        # .order_by(desc) sorts by newest first, .first() gets the top one

        if not latest:
            return f"❌ No interactions found for {hcp_name}. Log an interaction first."

        # Update the follow-up date
        latest.follow_up_date = datetime.strptime(follow_up_date, "%Y-%m-%d").date()
        if notes:
            latest.next_steps = notes

        db.commit()
        return f"✅ Follow-up scheduled with {hcp.name} on {follow_up_date}"

    except Exception as e:
        db.rollback()
        return f"❌ Error scheduling follow-up: {str(e)}"
    finally:
        db.close()


# This list is what we export to the LangGraph agent
# The agent needs to know all available tools upfront
all_tools = [
    log_interaction,
    edit_interaction,
    get_hcp_profile,
    summarize_interaction,
    schedule_followup
]