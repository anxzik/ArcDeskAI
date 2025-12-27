from sqlalchemy.orm import Session
from .database import models
from . import schemas

def get_agent(db: Session, agent_id: int):
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()

def get_agents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Agent).offset(skip).limit(limit).all()

def create_agent(db: Session, agent: schemas.AgentCreate):
    db_agent = models.Agent(name=agent.name, description=agent.description)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def get_knowledge_base(db: Session, kb_id: int):
    return db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == kb_id).first()

def get_knowledge_bases(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.KnowledgeBase).offset(skip).limit(limit).all()

def create_knowledge_base(db: Session, kb: schemas.KnowledgeBaseCreate):
    db_kb = models.KnowledgeBase(name=kb.name, description=kb.description)
    db.add(db_kb)
    db.commit()
    db.refresh(db_kb)
    return db_kb

def get_data_source(db: Session, ds_id: int):
    return db.query(models.DataSource).filter(models.DataSource.id == ds_id).first()

def get_data_sources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DataSource).offset(skip).limit(limit).all()

def create_data_source(db: Session, ds: schemas.DataSourceCreate, kb_id: int):
    db_ds = models.DataSource(**ds.dict(), knowledge_base_id=kb_id)
    db.add(db_ds)
    db.commit()
    db.refresh(db_ds)
    return db_ds

