import os
from google.adk.agents import Agent

root_agent = Agent(
    name="deployment-manager-agent",
    model="gemini-2.5-flash",
    description="Main CI/CD Pipeline Orchestrator Agent for Google ADK Multiagent flow",
    instructions=(
        "Orchestrate PR deployment pipeline step by step: "
        "1. Build container image via image-builder-sub-agent. "
        "2. Provision Cloud Run service via cloud-run-deployer-sub-agent. "
        "3. Notify team via image-creator-slack-notifier-sub-agent."
    )
)
