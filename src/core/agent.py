"""
AgentDesk Core - Basic Implementation
A starting point for the hierarchical AI agent organization system
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class AgentRole(Enum):
    """Standard business roles for agents"""
    EXECUTIVE = "executive"
    MANAGER = "manager"
    SENIOR_ENGINEER = "senior_engineer"
    ENGINEER = "engineer"
    JUNIOR_ENGINEER = "junior_engineer"
    QA_ENGINEER = "qa_engineer"
    SECURITY_ANALYST = "security_analyst"
    RESEARCHER = "researcher"


class DeskStatus(Enum):
    """Current status of an agent desk"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


class TaskStatus(Enum):
    """Status of tasks in the system"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class Priority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class LLMConfig:
    """Configuration for LLM provider"""
    provider: str  # "anthropic", "openai", "local", etc.
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000
    api_key: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }


@dataclass
class AgentMemory:
    """Agent's memory and context"""
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    learnings: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def add_conversation(self, role: str, content: str):
        """Add a conversation turn to history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_learning(self, learning: str):
        """Record a learning or insight"""
        self.learnings.append({
            "content": learning,
            "timestamp": datetime.now().isoformat()
        })


@dataclass
class Artifact:
    """Output artifact from a task"""
    artifact_id: str
    artifact_type: str  # "code", "document", "analysis", etc.
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Task:
    """Represents a task in the system"""
    task_id: str
    title: str
    description: str
    created_by: str
    assigned_to: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    parent_task_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    artifacts: List[Artifact] = field(default_factory=list)
    qa_required: bool = True
    qa_assigned_to: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "created_by": self.created_by,
            "assigned_to": self.assigned_to,
            "status": self.status.value,
            "priority": self.priority.value,
            "qa_required": self.qa_required,
            "created_at": self.created_at.isoformat(),
        }


class AgentDesk:
    """Represents an agent's workspace and configuration"""
    
    def __init__(
        self,
        desk_id: str,
        title: str,
        role: AgentRole,
        llm_config: LLMConfig,
        capabilities: List[str] = None,
        hierarchy_level: int = 0,
        reports_to: Optional[str] = None,
        team_id: Optional[str] = None
    ):
        self.desk_id = desk_id
        self.title = title
        self.role = role
        self.llm_config = llm_config
        self.capabilities = capabilities or []
        self.hierarchy_level = hierarchy_level
        self.reports_to = reports_to
        self.team_id = team_id
        self.status = DeskStatus.IDLE
        self.memory = AgentMemory()
        self.current_task: Optional[Task] = None
        
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task using the configured LLM"""
        self.status = DeskStatus.BUSY
        self.current_task = task
        task.status = TaskStatus.IN_PROGRESS
        
        try:
            # This is where you'd integrate with actual LLM APIs
            result = await self._execute_with_llm(task)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            return result
        except Exception as e:
            task.status = TaskStatus.FAILED
            return {"error": str(e)}
        finally:
            self.status = DeskStatus.IDLE
            self.current_task = None
    
    async def _execute_with_llm(self, task: Task) -> Dict[str, Any]:
        """Execute task with configured LLM (placeholder for actual implementation)"""
        # Construct prompt based on role and task
        system_prompt = f"""You are a {self.title} in an AI organization.
Your role is {self.role.value}.
Your capabilities: {', '.join(self.capabilities)}

Task assigned to you:
Title: {task.title}
Description: {task.description}
Priority: {task.priority.name}
"""
        
        # Here you would call the actual LLM API based on provider
        if self.llm_config.provider == "anthropic":
            return await self._call_anthropic(system_prompt, task)
        elif self.llm_config.provider == "openai":
            return await self._call_openai(system_prompt, task)
        else:
            return {"result": "LLM integration pending"}
    
    async def _call_anthropic(self, system_prompt: str, task: Task) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        # Placeholder - integrate with actual Anthropic SDK
        # from anthropic import Anthropic
        # client = Anthropic(api_key=self.llm_config.api_key)
        # message = client.messages.create(...)
        return {
            "provider": "anthropic",
            "model": self.llm_config.model,
            "result": "Task completed (implementation pending)"
        }
    
    async def _call_openai(self, system_prompt: str, task: Task) -> Dict[str, Any]:
        """Call OpenAI API"""
        # Placeholder - integrate with actual OpenAI SDK
        return {
            "provider": "openai",
            "model": self.llm_config.model,
            "result": "Task completed (implementation pending)"
        }
    
    def can_delegate_to(self, other_desk: 'AgentDesk') -> bool:
        """Check if this desk can delegate to another desk"""
        # Can delegate to direct reports or same level in team
        if other_desk.reports_to == self.desk_id:
            return True
        if other_desk.team_id == self.team_id and other_desk.hierarchy_level >= self.hierarchy_level:
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "desk_id": self.desk_id,
            "title": self.title,
            "role": self.role.value,
            "hierarchy_level": self.hierarchy_level,
            "reports_to": self.reports_to,
            "team_id": self.team_id,
            "status": self.status.value,
            "llm_config": self.llm_config.to_dict(),
            "capabilities": self.capabilities
        }


class OrganizationStructure:
    """Manages the organizational hierarchy"""
    
    def __init__(self, org_name: str):
        self.org_name = org_name
        self.desks: Dict[str, AgentDesk] = {}
        self.tasks: Dict[str, Task] = {}
        
    def add_desk(self, desk: AgentDesk):
        """Add an agent desk to the organization"""
        self.desks[desk.desk_id] = desk
        
    def get_desk(self, desk_id: str) -> Optional[AgentDesk]:
        """Get a desk by ID"""
        return self.desks.get(desk_id)
    
    def get_subordinates(self, desk_id: str) -> List[AgentDesk]:
        """Get all desks that report to this desk"""
        return [
            desk for desk in self.desks.values()
            if desk.reports_to == desk_id
        ]
    
    def get_hierarchy_chain(self, desk_id: str) -> List[AgentDesk]:
        """Get the reporting chain from desk to top"""
        chain = []
        current_desk = self.get_desk(desk_id)
        
        while current_desk:
            chain.append(current_desk)
            if current_desk.reports_to:
                current_desk = self.get_desk(current_desk.reports_to)
            else:
                break
        
        return chain
    
    async def delegate_task(self, task: Task, from_desk_id: str, to_desk_id: str) -> bool:
        """Delegate a task from one desk to another"""
        from_desk = self.get_desk(from_desk_id)
        to_desk = self.get_desk(to_desk_id)
        
        if not from_desk or not to_desk:
            return False
        
        if not from_desk.can_delegate_to(to_desk):
            return False
        
        task.assigned_to = to_desk_id
        self.tasks[task.task_id] = task
        
        # Process the task asynchronously
        asyncio.create_task(to_desk.process_task(task))
        return True
    
    def create_task(
        self,
        title: str,
        description: str,
        created_by: str,
        priority: Priority = Priority.MEDIUM,
        qa_required: bool = True
    ) -> Task:
        """Create a new task"""
        task_id = f"task_{len(self.tasks) + 1:04d}"
        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            created_by=created_by,
            priority=priority,
            qa_required=qa_required
        )
        self.tasks[task_id] = task
        return task
    
    def get_org_chart(self) -> Dict[str, Any]:
        """Generate organization chart data structure"""
        chart = {
            "name": self.org_name,
            "desks": {}
        }
        
        # Find root desks (no reports_to)
        roots = [desk for desk in self.desks.values() if not desk.reports_to]
        
        def build_tree(desk: AgentDesk) -> Dict[str, Any]:
            subordinates = self.get_subordinates(desk.desk_id)
            return {
                "desk": desk.to_dict(),
                "subordinates": [build_tree(sub) for sub in subordinates]
            }
        
        chart["hierarchy"] = [build_tree(root) for root in roots]
        return chart


# Example usage
async def example_usage():
    """Demonstrate basic usage"""
    
    # Create organization
    org = OrganizationStructure("AI Development Team")
    
    # Create CTO desk
    cto_desk = AgentDesk(
        desk_id="cto-001",
        title="Chief Technology Officer",
        role=AgentRole.EXECUTIVE,
        llm_config=LLMConfig(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            temperature=0.7
        ),
        capabilities=["strategic_planning", "architecture_design", "team_coordination"],
        hierarchy_level=1
    )
    org.add_desk(cto_desk)
    
    # Create Senior Engineer desk
    senior_dev_desk = AgentDesk(
        desk_id="dev-senior-001",
        title="Senior Software Engineer",
        role=AgentRole.SENIOR_ENGINEER,
        llm_config=LLMConfig(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            temperature=0.3
        ),
        capabilities=["code_generation", "code_review", "debugging", "documentation"],
        hierarchy_level=2,
        reports_to="cto-001",
        team_id="backend-team"
    )
    org.add_desk(senior_dev_desk)
    
    # Create QA Engineer desk
    qa_desk = AgentDesk(
        desk_id="qa-001",
        title="QA Engineer",
        role=AgentRole.QA_ENGINEER,
        llm_config=LLMConfig(
            provider="openai",
            model="gpt-4",
            temperature=0.2
        ),
        capabilities=["testing", "quality_assurance", "test_automation"],
        hierarchy_level=2,
        reports_to="cto-001",
        team_id="qa-team"
    )
    org.add_desk(qa_desk)
    
    # Create a task
    task = org.create_task(
        title="Implement user authentication",
        description="Create a secure authentication system with JWT tokens",
        created_by="user-001",
        priority=Priority.HIGH,
        qa_required=True
    )
    
    # CTO delegates to senior developer
    await org.delegate_task(task, "cto-001", "dev-senior-001")
    
    # Print org chart
    print(json.dumps(org.get_org_chart(), indent=2))
    
    # Wait for task processing
    await asyncio.sleep(2)
    
    print(f"\nTask Status: {task.status.value}")


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage())
