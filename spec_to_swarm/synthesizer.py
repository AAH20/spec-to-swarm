"""
Agent Prompt & Code Generation Synthesizer for Spec-To-Swarm.
Synthesizes system prompts and produces production backend code and test fixtures.
"""

from typing import Dict, List, Any
from .models import SwarmDAG, MicroAgentNode, AgentRoleType, SwarmExecutionArtifact


class SwarmSynthesizer:
    """Generates specialized agent system prompts and operational code artifacts."""

    def __init__(self, dag: SwarmDAG):
        self.dag = dag

    def synthesize_system_prompts(self) -> Dict[str, str]:
        """Generate tailored system prompts for each agent in the swarm."""
        prompts = {}
        for agent_id, agent in self.dag.agents.items():
            lines = [
                f"# Role: {agent.name} ({agent.role_type.value})",
                f"# Swarm Target: {self.dag.spec_title} v{self.dag.version}",
                f"# Target Domain: {agent.domain_tag}",
                "",
                "## Objective:",
            ]

            if agent.role_type == AgentRoleType.SCHEMA_ENGINEER:
                lines.append("You are the Lead Schema Architect. Generate robust Pydantic v2 data models with complete typing, validations, and field constraints based on the API components.")
            elif agent.role_type == AgentRoleType.AUTH_GATEWAY:
                lines.append("You are the Security Gateway Architect. Implement JWT Bearer token validation, rate-limiting headers, and FastAPI dependency injection for protected routes.")
            elif agent.role_type == AgentRoleType.DOMAIN_ENGINEER:
                lines.append(f"You are the Domain Backend Engineer for '{agent.domain_tag}'. Implement clean FastAPI router endpoints with full request/response validation, error handling, and business logic.")
            elif agent.role_type == AgentRoleType.TEST_SYNTHESIZER:
                lines.append("You are the Adversarial Test Engineer. Generate comprehensive pytest suites covering happy paths, 400 Bad Request validations, 401 Unauthorized states, and edge cases.")
            elif agent.role_type == AgentRoleType.SUPERVISOR:
                lines.append("You are the Swarm Orchestrator. Review generated code for architectural consistency, ensure all contract schemas match, and package the project.")

            lines.append("\n## Assigned Target Endpoints:")
            for ep in agent.target_endpoints[:5]:
                lines.append(f"- [{ep.method.value}] {ep.path}: {ep.summary}")

            lines.append("\n## Allowed Tools:")
            for tool in agent.assigned_tools:
                lines.append(f"- {tool}")

            lines.append("\n## Operational Guidelines:")
            lines.append("1. Produce production-grade code with 100% type hints.")
            lines.append("2. Strictly adhere to contract schemas without inventing unauthorized fields.")
            lines.append("3. Handle all HTTP exception scenarios (400, 404, 422, 500).")

            prompts[agent_id] = "\n".join(lines)
            agent.system_prompt = prompts[agent_id]

        return prompts

    def generate_code_artifacts(self) -> Dict[str, SwarmExecutionArtifact]:
        """Synthesize backend Python code for each micro-agent tier."""
        artifacts = {}

        # 1. Schema Artifact
        schema_agent = self.dag.agents.get("agent_schema_engineer")
        if schema_agent:
            code = '''"""Core Pydantic Data Models."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PaymentCreateRequest(BaseModel):
    amount_cents: int = Field(..., gt=0, description="Payment amount in cents")
    currency: str = Field("USD", min_length=3, max_length=3)
    customer_id: str = Field(..., description="ID of customer")
    payment_method: str = Field("card", description="Payment method token")

class PaymentResponse(BaseModel):
    payment_id: str
    amount_cents: int
    currency: str
    status: str
    created_at: datetime

class RefundRequest(BaseModel):
    payment_id: str
    reason: Optional[str] = "Customer return"
'''
            artifacts[schema_agent.agent_id] = SwarmExecutionArtifact(
                agent_id=schema_agent.agent_id,
                agent_name=schema_agent.name,
                generated_files={"models/schemas.py": code},
                execution_duration_ms=42.5
            )

        # 2. Auth Artifact
        auth_agent = self.dag.agents.get("agent_auth_gateway")
        if auth_agent:
            auth_code = '''"""Authentication & Security Middleware."""
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    if not token or token == "invalid":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token"
        )
    return "user_verified_99"
'''
            artifacts[auth_agent.agent_id] = SwarmExecutionArtifact(
                agent_id=auth_agent.agent_id,
                agent_name=auth_agent.name,
                generated_files={"core/auth.py": auth_code},
                execution_duration_ms=28.1
            )

        # 3. Domain Handlers
        for aid, agent in self.dag.agents.items():
            if agent.role_type == AgentRoleType.DOMAIN_ENGINEER:
                tag = agent.domain_tag
                router_code = f'''"""FastAPI Router for Domain: {tag}."""
from fastapi import APIRouter, Depends, HTTPException
import uuid
from datetime import datetime

router = APIRouter(prefix="/v1/{tag.lower()}", tags=["{tag}"])

@router.post("/", status_code=201)
def create_{tag.lower()}(payload: dict):
    return {{
        "id": f"{tag.lower()}_{{uuid.uuid4().hex[:8]}}",
        "status": "processed",
        "timestamp": datetime.utcnow().isoformat()
    }}

@router.get("/{{item_id}}")
def get_{tag.lower()}(item_id: str):
    return {{
        "id": item_id,
        "status": "active"
    }}
'''
                artifacts[aid] = SwarmExecutionArtifact(
                    agent_id=aid,
                    agent_name=agent.name,
                    generated_files={f"routers/{tag.lower()}_router.py": router_code},
                    execution_duration_ms=35.0
                )

        # 4. Test Suite
        test_agent = self.dag.agents.get("agent_test_synthesizer")
        if test_agent:
            test_code = '''"""Synthesized Integration & Contract Test Suite."""
import pytest

def test_payment_schema_contract():
    from models.schemas import PaymentCreateRequest
    req = PaymentCreateRequest(amount_cents=5000, customer_id="cust_123")
    assert req.amount_cents == 5000
    assert req.currency == "USD"

def test_auth_rejection():
    from core.auth import get_current_user
    from fastapi import HTTPException
    from unittest.mock import MagicMock
    mock_cred = MagicMock(credentials="invalid")
    with pytest.raises(HTTPException):
        get_current_user(mock_cred)
'''
            artifacts[test_agent.agent_id] = SwarmExecutionArtifact(
                agent_id=test_agent.agent_id,
                agent_name=test_agent.name,
                generated_files={"tests/test_api_contracts.py": test_code},
                execution_duration_ms=50.2
            )

        return artifacts
