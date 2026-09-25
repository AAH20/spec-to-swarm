"""
Comprehensive Unit Test Suite for Spec-To-Swarm.
"""

import unittest
from spec_to_swarm.models import AgentRoleType, EndpointMethod
from spec_to_swarm.parser import OpenAPIParser
from spec_to_swarm.decomposer import SwarmDecomposer
from spec_to_swarm.synthesizer import SwarmSynthesizer


MOCK_SPEC = {
    "openapi": "3.1.0",
    "info": {"title": "Test Cloud API", "version": "1.0.0"},
    "paths": {
        "/v1/users": {
            "get": {"summary": "List users", "tags": ["users"], "security": [{"bearerAuth": []}]},
            "post": {"summary": "Create user", "tags": ["users"], "security": [{"bearerAuth": []}]}
        },
        "/v1/billing/invoices": {
            "get": {"summary": "Get invoices", "tags": ["billing"], "security": [{"bearerAuth": []}]}
        }
    }
}


class TestSpecToSwarm(unittest.TestCase):

    def setUp(self):
        self.parser = OpenAPIParser(MOCK_SPEC)
        self.decomposer = SwarmDecomposer(self.parser)
        self.dag = self.decomposer.build_swarm_dag()

    def test_parser_extraction(self):
        """Test extraction of endpoints and grouping by domain."""
        eps = self.parser.extract_endpoints()
        self.assertEqual(len(eps), 3)

        grouped = self.parser.group_by_domain()
        self.assertIn("users", grouped)
        self.assertIn("billing", grouped)
        self.assertEqual(len(grouped["users"]), 2)

    def test_swarm_dag_topology(self):
        """Test that the generated DAG contains all roles and valid execution order."""
        self.assertIn("agent_schema_engineer", self.dag.agents)
        self.assertIn("agent_auth_gateway", self.dag.agents)
        self.assertIn("agent_domain_users", self.dag.agents)
        self.assertIn("agent_domain_billing", self.dag.agents)
        self.assertIn("agent_test_synthesizer", self.dag.agents)

        # Verify topological execution layers
        self.assertGreaterEqual(len(self.dag.execution_order), 4)
        # Schema engineer must be in stage 0
        self.assertIn("agent_schema_engineer", self.dag.execution_order[0])

    def test_prompt_and_code_synthesis(self):
        """Test prompt synthesis and artifact generation."""
        synthesizer = SwarmSynthesizer(self.dag)
        prompts = synthesizer.synthesize_system_prompts()
        self.assertEqual(len(prompts), len(self.dag.agents))

        # Check prompt contents
        schema_prompt = prompts["agent_schema_engineer"]
        self.assertIn("Lead Schema Architect", schema_prompt)

        artifacts = synthesizer.generate_code_artifacts()
        self.assertIn("agent_schema_engineer", artifacts)
        self.assertIn("models/schemas.py", artifacts["agent_schema_engineer"].generated_files)


if __name__ == "__main__":
    unittest.main()
