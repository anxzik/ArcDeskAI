from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    versions = relationship("AgentVersion", back_populates="agent")

class AgentVersion(Base):
    __tablename__ = "agent_versions"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    version_number = Column(String)
    release_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    agent = relationship("Agent", back_populates="versions")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    datasources = relationship("DataSource", back_populates="knowledge_base")

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_bases.id"))
    name = Column(String)
    type = Column(String) # e.g., 'github', 'web', 'file'
    uri = Column(String)
    knowledge_base = relationship("KnowledgeBase", back_populates="datasources")
