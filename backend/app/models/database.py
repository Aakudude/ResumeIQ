from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./resumeiq.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    required_skills = Column(JSON, default=[])
    preferred_skills = Column(JSON, default=[])
    experience_years = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    candidates = relationship("Candidate", back_populates="job_description")


class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    raw_text = Column(Text, nullable=True)
    extracted_skills = Column(JSON, default=[])
    experience_years = Column(Float, nullable=True)
    education = Column(JSON, default=[])
    match_score = Column(Float, nullable=True)
    matched_skills = Column(JSON, default=[])
    missing_skills = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    rank = Column(Integer, nullable=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    job_description = relationship("JobDescription", back_populates="candidates")


def create_tables():
    Base.metadata.create_all(bind=engine)
