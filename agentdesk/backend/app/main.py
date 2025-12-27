from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import crud, schemas, mcp
from .database import models, SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/agents/", response_model=schemas.Agent)
def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    return crud.create_agent(db=db, agent=agent)

@app.get("/agents/", response_model=List[schemas.Agent])
def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    agents = crud.get_agents(db, skip=skip, limit=limit)
    return agents

@app.get("/agents/{agent_id}", response_model=schemas.Agent)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@app.post("/knowledge-bases/", response_model=schemas.KnowledgeBase)
def create_knowledge_base(kb: schemas.KnowledgeBaseCreate, db: Session = Depends(get_db)):
    return crud.create_knowledge_base(db=db, kb=kb)

@app.get("/knowledge-bases/", response_model=List[schemas.KnowledgeBase])
def read_knowledge_bases(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    kbs = crud.get_knowledge_bases(db, skip=skip, limit=limit)
    return kbs

@app.get("/knowledge-bases/{kb_id}", response_model=schemas.KnowledgeBase)
def read_knowledge_base(kb_id: int, db: Session = Depends(get_db)):
    db_kb = crud.get_knowledge_base(db, kb_id=kb_id)
    if db_kb is None:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    return db_kb

@app.post("/knowledge-bases/{kb_id}/datasources/", response_model=schemas.DataSource)
def create_data_source_for_kb(
    kb_id: int, ds: schemas.DataSourceCreate, db: Session = Depends(get_db)
):
    return crud.create_data_source(db=db, ds=ds, kb_id=kb_id)

@app.get("/datasources/", response_model=List[schemas.DataSource])
def read_data_sources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dss = crud.get_data_sources(db, skip=skip, limit=limit)
    return dss

@app.get("/mcp/search")
async def search_mcp_endpoint(q: str):
    return await mcp.search_mcp(q)

