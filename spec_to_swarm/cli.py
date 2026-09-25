"""
Command Line Interface for Spec-To-Swarm.
Autonomous multi-agent backend decomposition and synthesis.
"""

import argparse
import sys
import time
from .parser import OpenAPIParser
from .decomposer import SwarmDecomposer
from .synthesizer import SwarmSynthesizer


SAMPLE_OPENAPI_SPEC = {
    "openapi": "3.1.0",
    "info": {
        "title": "HyperPay Sovereign Payments Engine",
        "version": "2.4.0",
        "description": "High-throughput global payments and refund processing gateway"
    },
    "paths": {
        "/v1/payments": {
            "post": {
                "summary": "Authorize and capture customer payment",
                "tags": ["payments"],
                "security": [{"bearerAuth": []}]
            },
            "get": {
                "summary": "List historical payment transactions",
                "tags": ["payments"],
                "security": [{"bearerAuth": []}]
            }
        },
        "/v1/refunds": {
            "post": {
                "summary": "Initiate partial or full payment refund",
                "tags": ["refunds"],
                "security": [{"bearerAuth": []}]
            }
        },
        "/v1/webhooks": {
            "post": {
                "summary": "Ingest payment provider webhook callbacks",
                "tags": ["webhooks"],
                "security": []
            }
        }
    }
}


def run_demo() -> None:
    print("=" * 76)
    print("  🐝 SPEC-TO-SWARM: AUTONOMOUS MICRO-AGENT DECOMPOSITION FROM OPENAPI")
    print("  Frontier Multi-Agent Engine: Claude 3.7 Sonnet | OpenAI o3 | Gemini 2.5 Pro")
    print("=" * 76)

    t0 = time.time()
    parser = OpenAPIParser(SAMPLE_OPENAPI_SPEC)
    endpoints = parser.extract_endpoints()
    print(f"✓ Parsed OpenAPI Specification: '{parser.title}' v{parser.version}")
    print(f"✓ Extracted {len(endpoints)} API operations across {len(parser.group_by_domain())} functional domains.\n")

    # Step 1: Decompose into Swarm DAG
    print("-" * 76)
    print("[1/3] Decomposing API Contract into Micro-Agent Directed Acyclic Graph (DAG)")
    print("-" * 76)
    decomposer = SwarmDecomposer(parser)
    dag = decomposer.build_swarm_dag()

    print(f"• Total Autonomous Micro-Agents: {len(dag.agents)}")
    print(f"• Topological Execution Tiers  : {len(dag.execution_order)} Stages\n")

    for tier_idx, layer in enumerate(dag.execution_order):
        layer_names = [dag.agents[aid].name for aid in layer]
        print(f"  Stage {tier_idx} (Parallel): {', '.join(layer_names)}")

    # Step 2: Synthesize System Prompts & Tools
    print("\n" + "-" * 76)
    print("[2/3] Synthesizing Specialized System Prompts & Tool Contracts")
    print("-" * 76)
    synthesizer = SwarmSynthesizer(dag)
    prompts = synthesizer.synthesize_system_prompts()

    for aid, prompt in list(prompts.items())[:2]:
        agent = dag.agents[aid]
        print(f"• Synthesized Prompt for: [{agent.role_type.value.upper()}] {agent.name}")
        first_few_lines = "\n    ".join(prompt.splitlines()[:5])
        print(f"    {first_few_lines}\n")

    # Step 3: Execute Swarm & Generate Codebase
    print("-" * 76)
    print("[3/3] Executing Micro-Agent Swarm Code Synthesis Pipeline")
    print("-" * 76)
    artifacts = synthesizer.generate_code_artifacts()

    for aid, artifact in artifacts.items():
        files_str = ", ".join(artifact.generated_files.keys())
        print(f"✓ [{artifact.agent_name}] -> Generated: {files_str} ({artifact.execution_duration_ms:.1f}ms)")

    total_dur_ms = (time.time() - t0) * 1000.0
    print("\n" + "=" * 76)
    print(f"  SWARM ASSEMBLED & COMPLETE BACKEND CODEBASE GENERATED IN {total_dur_ms:.1f}ms")
    print("=" * 76)


def main() -> None:
    parser = argparse.ArgumentParser(description="Spec-To-Swarm Micro-Agent Synthesizer")
    subparsers = parser.add_subparsers(dest="command")

    demo_parser = subparsers.add_parser("demo", help="Run interactive OpenAPI to Swarm demo")

    args = parser.parse_args()

    if args.command == "demo" or len(sys.argv) == 1:
        run_demo()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
