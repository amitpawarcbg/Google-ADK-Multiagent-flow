from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class DirectTriggerPayload(BaseModel):
    repo: str = Field(default="cybage-devops/student-app", description="GitHub Repository name")
    pr_id: int = Field(default=42, description="Pull Request ID")
    branch: str = Field(default="main", description="Target Git Branch")
    commit: str = Field(default="a1b2c3d4e5f6", description="Git Commit SHA")
    date: str = Field(default="2026-08-03", description="Event Date")
    time: str = Field(default="13:20:00", description="Event Time")

class GitHubHeadRef(BaseModel):
    ref: str = "main"
    sha: str = "a1b2c3d4e5f6"

class GitHubRepository(BaseModel):
    full_name: str = "cybage-devops/student-app"

class GitHubPullRequest(BaseModel):
    number: int = 42
    head: GitHubHeadRef

class GitHubWebhookPayload(BaseModel):
    action: Optional[str] = "closed"
    pull_request: Optional[GitHubPullRequest] = None
    repository: Optional[GitHubRepository] = None

class PipelineResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]
