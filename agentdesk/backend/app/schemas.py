from pydantic import BaseModel
from typing import List, Optional
import datetime

class DataSourceBase(BaseModel):
    name: str
    type: str
    uri: str

class DataSourceCreate(DataSourceBase):
    pass

class DataSource(DataSourceBase):
    id: int
    knowledge_base_id: int

    class Config:
        orm_mode = True

class KnowledgeBaseBase(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass

class KnowledgeBase(KnowledgeBaseBase):
    id: int
    datasources: List[DataSource] = []

    class Config:
        orm_mode = True

class AgentVersionBase(BaseModel):
    version_number: str
    release_notes: Optional[str] = None

class AgentVersionCreate(AgentVersionBase):
    pass

class AgentVersion(AgentVersionBase):
    id: int
    agent_id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: int
    versions: List[AgentVersion] = []

    class Config:
        orm_mode = True
