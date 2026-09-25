"""
Spec-To-Swarm: Self-Assembling Autonomous Micro-Agent Swarm from an OpenAPI/RFC Spec.
Engineered for Claude 3.7 Sonnet, OpenAI o3, and Gemini 2.5 Pro.
"""

from .models import (
    APIEndpoint,
    MicroAgentNode,
    AgentRoleType,
    SwarmDAG,
    SwarmExecutionArtifact,
)
from .parser import OpenAPIParser
from .decomposer import SwarmDecomposer
from .synthesizer import SwarmSynthesizer

__version__ = "1.0.0"
__all__ = [
    "APIEndpoint",
    "MicroAgentNode",
    "AgentRoleType",
    "SwarmDAG",
    "SwarmExecutionArtifact",
    "OpenAPIParser",
    "SwarmDecomposer",
    "SwarmSynthesizer",
]
