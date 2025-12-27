"""
AgentDesk Core - Basic Implementation
A starting point for the hierarchical AI agent organization system
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import json
import google.generativeai as genai
import os
import mlflow
import chromadb
from src.utils.security import PIIMasker

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


class KnowledgeBase:
    """RAG Knowledge Base using ChromaDB"""
    def __init__(self, collection_name: str = "agent_knowledge", persist_path: str = "./agent_knowledge"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        
    def add_documents(self, documents: List[str], metadatas: List[Dict] = None, ids: List[str] = None):
        """Add documents to knowledge base"""
        if ids is None:
            ids = [f"doc_{datetime.now().timestamp()}_{i}" for i in range(len(documents))]
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
        
    def query(self, query_text: str, n_results: int = 3) -> List[str]:
        """Query knowledge base"""
        try:
            results = self.collection.query(query_texts=[query_text], n_results=n_results)
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            print(f"RAG Query failed: {e}")
            return []


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

    def export_to_jsonl(self, file_path: str):
        """Export conversation history to JSONL format for fine-tuning"""
        with open(file_path, 'w') as f:
            for i in range(0, len(self.conversation_history) - 1, 2):
                if i + 1 < len(self.conversation_history):
                    # Simple user/model pair assumption
                    entry = {
                        "messages": [
                            {"role": self.conversation_history[i]["role"], "content": self.conversation_history[i]["content"]},
                            {"role": self.conversation_history[i+1]["role"], "content": self.conversation_history[i+1]["content"]}
                        ]
                    }
                    f.write(json.dumps(entry) + '\n')


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
        team_id: Optional[str] = None,
        knowledge_base: Optional[KnowledgeBase] = None
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
        self.knowledge_base = knowledge_base
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
            
    def provide_feedback(self, task_id: str, rating: int, comment: str):
        """Process feedback for a task to improve future performance"""
        self.memory.add_learning(f"Feedback for task {task_id}: Rating {rating}/5. Comment: {comment}")
        # In enterprise version, this would fine-tune the model or update the vector DB
        if self.knowledge_base:
            # Store feedback in KB for retrieval
            self.knowledge_base.add_documents(
                documents=[f"Feedback on {task_id}: {comment} (Rating: {rating})"],
                metadatas=[{"type": "feedback", "rating": rating, "task_id": task_id}]
            )
    
    async def _execute_with_llm(self, task: Task) -> Dict[str, Any]:
        """Execute task with configured LLM (placeholder for actual implementation)"""
        
        # RAG: Retrieve context
        context_str = ""
        if self.knowledge_base:
            docs = self.knowledge_base.query(task.description + " " + task.title)
            if docs:
                context_str = "\n\nRelevant Organizational Knowledge:\n" + "\n---\n".join(docs)

        # Construct prompt based on role and task
        system_prompt = f"""You are a {self.title} in an AI organization.
Your role is {self.role.value}.
Your capabilities: {', '.join(self.capabilities)}

Task assigned to you:
Title: {task.title}
Description: {task.description}
Priority: {task.priority.name}
{context_str}
"""
        
        # MLflow Tracking
        try:
            mlflow.set_experiment("AgentDesk_Operations")
            
            with mlflow.start_run(run_name=f"task_{task.task_id}", nested=True):
                mlflow.log_param("agent_role", self.role.value)
                mlflow.log_param("agent_title", self.title)
                mlflow.log_param("task_id", task.task_id)
                mlflow.log_text(PIIMasker.mask(task.description), "task_description.txt")
                mlflow.log_param("provider", self.llm_config.provider)
                mlflow.log_param("model", self.llm_config.model)
                
                result = {}
                # Here you would call the actual LLM API based on provider
                if self.llm_config.provider == "anthropic":
                    result = await self._call_anthropic(system_prompt, task)
                elif self.llm_config.provider == "openai":
                    result = await self._call_openai(system_prompt, task)
                elif self.llm_config.provider == "gemini":
                    result = await self._call_gemini(system_prompt, task)
                else:
                    result = {"result": "LLM integration pending"}
                
                mlflow.log_param("status", "success" if "error" not in result else "failed")
                mlflow.log_text(json.dumps(result, default=str), "result.json")
                
                return result
        except Exception as e:
            # Fallback if MLflow fails (e.g. connection error)
            print(f"MLflow logging failed: {e}")
            # Still execute if we haven't yet
            if 'result' not in locals():
                 if self.llm_config.provider == "anthropic":
                    return await self._call_anthropic(system_prompt, task)
                 elif self.llm_config.provider == "openai":
                    return await self._call_openai(system_prompt, task)
                 elif self.llm_config.provider == "gemini":
                    return await self._call_gemini(system_prompt, task)
            return {"error": f"Execution failed: {str(e)}"}
    
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

    async def _call_gemini(self, system_prompt: str, task: Task) -> Dict[str, Any]:
        """Call Google Gemini API"""
        api_key = self.llm_config.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
             return {"error": "Gemini API key not found"}

        genai.configure(api_key=api_key)
        
        # Combine system prompt and task details
        full_prompt = f"{system_prompt}\n\nTask: {task.title}\n{task.description}"
        
        try:
            # Run blocking call in thread
            model = genai.GenerativeModel(self.llm_config.model or "gemini-pro")
            response = await asyncio.to_thread(model.generate_content, full_prompt)
            
            return {
                "provider": "gemini",
                "model": self.llm_config.model,
                "result": response.text
            }
        except Exception as e:
            return {"error": str(e)}
    
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


@dataclass
class Team:
    team_id: str
    name: str
    lead: str  # desk_id of the lead agent
    members: List[str]  # list of desk_ids
    focus: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

@dataclass
class Committee:
    committee_id: str
    name: str
    chair: str  # desk_id of the chair agent
    members: List[str]  # list of desk_ids
    purpose: Optional[str] = None
    meeting_frequency: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

@dataclass
class QAPipelineStage:
    type: str
    agent: Optional[str] = None
    assignee_level: Optional[str] = None
    required_reviewers: Optional[int] = None
    criteria: Optional[List[str]] = field(default_factory=list)
    timeout: Optional[int] = None
    block_on_critical: Optional[bool] = None
    required_for_types: Optional[List[str]] = field(default_factory=list)
    assessment_areas: Optional[List[str]] = field(default_factory=list)
    frameworks: Optional[List[str]] = field(default_factory=list)
    required_for_priority: Optional[List[str]] = field(default_factory=list)
    approval_criteria: Optional[List[str]] = field(default_factory=list)
    tools: Optional[List[str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

@dataclass
class QAPipeline:
    enabled: bool = True
    required_for: List[str] = field(default_factory=list)
    stages: List[QAPipelineStage] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "required_for": self.required_for,
            "stages": [stage.to_dict() for stage in self.stages]
        }

@dataclass
class WorkflowStep:
    name: str
    assigned_role: Optional[str] = None
    assigned_agent: Optional[str] = None
    committee: Optional[str] = None
    team: Optional[str] = None
    outputs: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    qa_required: bool = False
    max_duration: Optional[int] = None
    verification_required: bool = False
    tools: Optional[List[str]] = field(default_factory=list)
    focus_areas: Optional[List[str]] = field(default_factory=list)
    test_types: Optional[List[str]] = field(default_factory=list)
    required_for: Optional[List[str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

@dataclass
class Workflow:
    name: str
    trigger: str
    steps: List[WorkflowStep] = field(default_factory=list)
    priority: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "trigger": self.trigger,
            "steps": [step.to_dict() for step in self.steps],
            "priority": self.priority
        }

@dataclass
class TaskRoutingRule:
    keywords: List[str] = field(default_factory=list)
    route_to: Optional[str] = None
    escalate_if_critical: Optional[str] = None
    notify_committee: Optional[str] = None
    escalate_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

@dataclass
class NotificationChannel:
    type: str
    webhook_url: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    integration_key: Optional[str] = None
    notify_on: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

@dataclass
class MetricsDashboard:
    name: str
    metrics: List[str] = field(default_factory=list)
    refresh_interval: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

@dataclass
class MetricsConfig:
    track: List[str] = field(default_factory=list)
    dashboards: List[MetricsDashboard] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track": self.track,
            "dashboards": [dashboard.to_dict() for dashboard in self.dashboards]
        }

@dataclass
class AgentBehavior:
    communication_style: Optional[str] = None
    decision_making: Optional[str] = None
    escalation_threshold: Optional[str] = None
    automation_preference: Optional[str] = None
    negotiation_style: Optional[str] = None
    research_depth: Optional[str] = None
    ioc_extraction: Optional[str] = None
    report_format: Optional[str] = None
    documentation_level: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__

class OrganizationStructure:
    """Manages the organizational hierarchy"""
    
    def __init__(self, org_name: str):
        self.org_name = org_name
        self.desks: Dict[str, AgentDesk] = {}
        self.tasks: Dict[str, Task] = {}
        self.teams: Dict[str, Team] = {}
        self.committees: Dict[str, Committee] = {}
        self.qa_pipeline: Optional[QAPipeline] = None
        self.workflows: Dict[str, Workflow] = {}
        self.task_routing_rules: List[TaskRoutingRule] = []
        self.notifications: List[NotificationChannel] = []
        self.metrics: Optional[MetricsConfig] = None
        self.agent_behaviors: Dict[str, AgentBehavior] = {}

        
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
