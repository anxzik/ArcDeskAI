from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import asyncio
from src.core.agent import (
    OrganizationStructure, AgentDesk, AgentRole, LLMConfig, Task, Priority
)

app = FastAPI(title="AgentDesk API", version="0.1.0")

# In-memory store for now
org = OrganizationStructure("AgentDesk Org")

def init_org():
    """Initialize the organization with default agents"""
    if not org.desks:
        print("Initializing Organization...")
        # CTO Agent
        cto_desk = AgentDesk(
            desk_id="cto-001",
            title="Chief Technology Officer",
            role=AgentRole.EXECUTIVE,
            llm_config=LLMConfig(
                provider=os.getenv("DEFAULT_LLM_PROVIDER", "gemini"),
                model=os.getenv("DEFAULT_LLM_MODEL", "gemini-pro"),
                api_key=os.getenv("GEMINI_API_KEY")
            ),
            capabilities=["strategic_planning", "architecture_design"],
            hierarchy_level=1
        )
        org.add_desk(cto_desk)
        
        # Senior Dev Agent
        dev_desk = AgentDesk(
            desk_id="dev-001",
            title="Senior Developer",
            role=AgentRole.SENIOR_ENGINEER,
            llm_config=LLMConfig(
                provider=os.getenv("DEFAULT_LLM_PROVIDER", "gemini"),
                model=os.getenv("DEFAULT_LLM_MODEL", "gemini-pro"),
                api_key=os.getenv("GEMINI_API_KEY")
            ),
            capabilities=["coding", "debugging", "review"],
            hierarchy_level=2,
            reports_to="cto-001"
        )
        org.add_desk(dev_desk)
        print(f"Organization initialized with {len(org.desks)} agents.")

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str = "MEDIUM"

@app.on_event("startup")
async def startup_event():
    init_org()

@app.get("/")
async def root():
    return {"message": "AgentDesk API is running", "provider": os.getenv("DEFAULT_LLM_PROVIDER")}

@app.get("/agents")
async def list_agents():
    return [desk.to_dict() for desk in org.desks.values()]

@app.post("/tasks")
async def create_task(task: TaskCreate, background_tasks: BackgroundTasks):
    try:
        priority_enum = Priority[task.priority.upper()]
    except KeyError:
        priority_enum = Priority.MEDIUM
        
    new_task = org.create_task(
        title=task.title,
        description=task.description,
        created_by="api_user",
        priority=priority_enum
    )
    
    # Simple routing logic: Assign to CTO or Dev based on title? 
    # For now, assign to Dev, but if critical, assign to CTO.
    assignee = "dev-001"
    if priority_enum == Priority.CRITICAL:
        assignee = "cto-001"
        
    # We trigger the delegation/processing
    # Since process_task is async and might take time, we should ideally run it in background
    # But OrganizationStructure.delegate_task uses asyncio.create_task internally?
    # Let's check agent.py logic.
    # delegate_task calls asyncio.create_task(to_desk.process_task(task))
    
    await org.delegate_task(new_task, "cto-001", assignee) # CTO delegates to assignee
    
    return new_task.to_dict()

@app.get("/tasks")
async def list_tasks():
    return [t.to_dict() for t in org.tasks.values()]

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = org.tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()
