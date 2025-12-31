# models.py - Database Models for SmartFormsGPT

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base
from schemas.base_claim import ClaimStatus, ClaimType

class User(Base):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(String(20), default="user")  # user, admin, processor
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    claims = relationship("Claim", back_populates="user")


class Claim(Base):
    """Claim model for persistent storage."""
    
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(50), unique=True, nullable=False, index=True)
    claim_type = Column(SQLEnum(ClaimType), nullable=False)
    status = Column(SQLEnum(ClaimStatus), default=ClaimStatus.DRAFT)
    
    # Patient Information
    patient_name = Column(String(200), nullable=False)
    patient_id = Column(String(50), nullable=False, index=True)
    date_of_birth = Column(DateTime, nullable=False)
    
    # Provider Information
    provider_name = Column(String(200), nullable=False)
    provider_id = Column(String(20))
    service_date = Column(DateTime, nullable=False, index=True)
    
    # Financial
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Documentation
    description = Column(Text)
    diagnosis_codes = Column(Text)  # JSON string
    procedure_codes = Column(Text)  # JSON string
    
    # Decision Information
    decision_confidence = Column(Float)
    decision_reasons = Column(Text)  # JSON string
    
    # Metadata
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime)
    processed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="claims")
    documents = relationship("Document", back_populates="claim", cascade="all, delete-orphan")
    history = relationship("ClaimHistory", back_populates="claim", cascade="all, delete-orphan")


class Document(Base):
    """Document model for file attachments."""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    
    # Extraction metadata
    extracted_text = Column(Text)
    extraction_confidence = Column(Float)
    page_count = Column(Integer)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    claim = relationship("Claim", back_populates="documents")


class ClaimHistory(Base):
    """Claim history model for audit trail."""
    
    __tablename__ = "claim_history"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id"), nullable=False)
    
    action = Column(String(50), nullable=False)  # created, updated, submitted, approved, rejected
    old_status = Column(SQLEnum(ClaimStatus))
    new_status = Column(SQLEnum(ClaimStatus))
    
    changed_by = Column(Integer, ForeignKey("users.id"))
    change_reason = Column(Text)
    change_details = Column(Text)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    claim = relationship("Claim", back_populates="history")


# Export all models
__all__ = ["User", "Claim", "Document", "ClaimHistory"]
