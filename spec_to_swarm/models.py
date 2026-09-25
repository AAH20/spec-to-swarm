"""
Data models and DAG schemas for Spec-To-Swarm.
Autonomous multi-agent synthesis from OpenAPI 3.1 & RFC specifications.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
import time


class AgentRoleType(str, Enum):
    SUPERVISOR = "supervisor"
    SCHEMA_ENGINEER = "schema_engineer"
    DOMAIN_ENGINEER = "domain_engineer"
    AUTH_GATEWAY = "auth_gateway"
    TEST_SYNTHESIZER = "test_synthesizer"


class EndpointMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class APIEndpoint:
    path: str
    method: EndpointMethod
    summary: str
    tag: str
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    requires_auth: bool = True


@dataclass
class MicroAgentNode:
    agent_id: str
    name: str
    role_type: AgentRoleType
    domain_tag: str
    target_endpoints: List[APIEndpoint] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list) # Agent IDs that must complete first
    system_prompt: str = ""
    assigned_tools: List[str] = field(default_factory=list)
    recommended_model: str = "claude-3-7-sonnet-20250219" # Frontier default


@dataclass
class SwarmDAG:
    spec_title: str
    version: str
    agents: Dict[str, MicroAgentNode] = field(default_factory=dict)
    execution_order: List[List[str]] = field(default_factory=list) # Topological layers (parallel batches)
    total_endpoints: int = 0
    created_at: float = field(default_factory=time.time)


@dataclass
class SwarmExecutionArtifact:
    agent_id: str
    agent_name: str
    generated_files: Dict[str, str] # filename -> code string
    execution_duration_ms: float = 0.0
    status: str = "SUCCESS"
    diagnostics: List[str] = field(default_factory=list)
