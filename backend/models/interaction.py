# models/interaction.py
# This file defines what our database tables look like in Python
# Think of each class here as a blueprint for a table

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# HCP = Healthcare Professional (a doctor)
# This class maps to the "hcps" table in PostgreSQL
class HCP(Base):
    __tablename__ = "hcps"  # this must match the table name we created in Phase 2

    # Column() defines each field in the table
    # Integer, String, Text etc. are the data types
    id = Column(Integer, primary_key=True, index=True)
    # primary_key=True means this is the unique identifier
    # index=True means PostgreSQL will create a fast-lookup index on this column

    name = Column(String(255), nullable=False)
    # nullable=False means this field is REQUIRED — you can't save an HCP without a name

    specialty = Column(String(255))
    hospital = Column(String(255))
    city = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    # func.now() automatically fills in the current timestamp

    # relationship() links this model to the Interaction model
    # "interactions" is the name we use in Python to access related records
    # back_populates="hcp" means Interaction also has a .hcp property pointing back here
    interactions = relationship("Interaction", back_populates="hcp")


# Interaction = one logged meeting between a field rep and a doctor
# This class maps to the "interactions" table in PostgreSQL
class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)

    # ForeignKey links this to the hcps table
    # This means every interaction MUST be linked to a real HCP
    hcp_id = Column(Integer, ForeignKey("hcps.id"))

    rep_name = Column(String(255), nullable=False)
    interaction_date = Column(Date, nullable=False)
    interaction_type = Column(String(100))
    products_discussed = Column(Text)
    notes = Column(Text)
    summary = Column(Text)       # AI will fill this automatically
    next_steps = Column(Text)
    follow_up_date = Column(Date)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    # onupdate=func.now() means this auto-updates whenever the record changes

    # This is the reverse side of the relationship defined in HCP
    hcp = relationship("HCP", back_populates="interactions")