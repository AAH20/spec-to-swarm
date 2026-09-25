"""
Autonomous Swarm Decomposer & DAG Synthesizer for Spec-To-Swarm.
Translates OpenAPI schemas into topological execution graphs of specialized micro-agents.
"""

from typing import Dict, List, Set
from .models import MicroAgentNode, AgentRoleType, SwarmDAG, APIEndpoint
from .parser import OpenAPIParser


class SwarmDecomposer:
    """Decomposes API specifications into parallelized topological micro-agent swarms."""

    def __init__(self, parser: OpenAPIParser):
        self.parser = parser

    def build_swarm_dag(self) -> SwarmDAG:
        """Construct the complete agent dependency graph and execution tiers."""
        endpoints = self.parser.extract_endpoints()
        grouped_domains = self.parser.group_by_domain()
        agents: Dict[str, MicroAgentNode] = {}

        # 1. Foundation Agent: Schema & Data Models (Layer 0)
        schema_agent_id = "agent_schema_engineer"
        agents[schema_agent_id] = MicroAgentNode(
            agent_id=schema_agent_id,
            name="Schema & Contract Engineer",
            role_type=AgentRoleType.SCHEMA_ENGINEER,
            domain_tag="core_models",
            target_endpoints=endpoints,
            dependencies=[],
            assigned_tools=["generate_pydantic_models", "validate_json_schema"],
            recommended_model="claude-opus-5-5"
        )

        # 2. Auth Gateway Agent (Layer 1)
        auth_agent_id = "agent_auth_gateway"
        agents[auth_agent_id] = MicroAgentNode(
            agent_id=auth_agent_id,
            name="Auth & Security Gateway Engineer",
            role_type=AgentRoleType.AUTH_GATEWAY,
            domain_tag="security",
            target_endpoints=[ep for ep in endpoints if ep.requires_auth],
            dependencies=[schema_agent_id],
            assigned_tools=["generate_auth_middleware", "jwt_token_validator"],
            recommended_model="claude-opus-5-5"
        )

        # 3. Domain Micro-Agents (Layer 2 - Parallel Execution)
        domain_agent_ids = []
        for tag, domain_eps in grouped_domains.items():
            agent_id = f"agent_domain_{tag.lower().replace(' ', '_')}"
            domain_agent_ids.append(agent_id)
            agents[agent_id] = MicroAgentNode(
                agent_id=agent_id,
                name=f"{tag.title()} Domain Engineer",
                role_type=AgentRoleType.DOMAIN_ENGINEER,
                domain_tag=tag,
                target_endpoints=domain_eps,
                dependencies=[schema_agent_id, auth_agent_id],
                assigned_tools=["generate_fastapi_router", "implement_business_logic"],
                recommended_model="claude-opus-5-5"
            )

        # 4. Integration Test Synthesizer Agent (Layer 3 - Depends on all domain agents)
        test_agent_id = "agent_test_synthesizer"
        agents[test_agent_id] = MicroAgentNode(
            agent_id=test_agent_id,
            name="Adversarial Test & Fixture Synthesizer",
            role_type=AgentRoleType.TEST_SYNTHESIZER,
            domain_tag="qa_integration",
            target_endpoints=endpoints,
            dependencies=domain_agent_ids,
            assigned_tools=["generate_pytest_fixtures", "execute_contract_tests"],
            recommended_model="claude-opus-5-5"
        )

        # 5. Top-Level Supervisor
        supervisor_id = "agent_supervisor"
        agents[supervisor_id] = MicroAgentNode(
            agent_id=supervisor_id,
            name="Swarm Orchestrator & Code Reviewer",
            role_type=AgentRoleType.SUPERVISOR,
            domain_tag="meta",
            target_endpoints=endpoints,
            dependencies=[test_agent_id],
            assigned_tools=["lint_codebase", "package_distribution"],
            recommended_model="claude-opus-5-5"
        )

        # Compute topological execution layers
        execution_order = self._compute_topological_layers(agents)

        return SwarmDAG(
            spec_title=self.parser.title,
            version=self.parser.version,
            agents=agents,
            execution_order=execution_order,
            total_endpoints=len(endpoints)
        )

    def _compute_topological_layers(self, agents: Dict[str, MicroAgentNode]) -> List[List[str]]:
        """Compute parallel execution layers using Kahn's topological sort."""
        in_degree = {aid: len(node.dependencies) for aid, node in agents.items()}
        remaining_deps = {aid: set(node.dependencies) for aid, node in agents.items()}

        layers = []
        completed: Set[str] = set()

        while len(completed) < len(agents):
            current_layer = [
                aid for aid, deps in remaining_deps.items()
                if aid not in completed and deps.issubset(completed)
            ]
            if not current_layer:
                # Break circular reference safeguard if any
                current_layer = [aid for aid in agents if aid not in completed]

            layers.append(current_layer)
            for aid in current_layer:
                completed.add(aid)

        return layers
