import os
from google.adk.agents import Agent

root_agent = Agent(
    name="student-registration-app",
    model="gemini-2.5-flash",
    description="Student Registration App Agent",
    instructions="Assist with Student Registration application operations and PR deployments."
)
