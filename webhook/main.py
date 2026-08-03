from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, status
from webhook.schemas import DirectTriggerPayload, GitHubWebhookPayload, PipelineResponse
from agents.deployment_manager import deployment_manager_agent

app = FastAPI(
    title="GitHub PR Webhook Service - Google ADK Pipeline",
    description="FastAPI Webhook capturing GitHub PR events to trigger the deployment-manager-agent orchestrator.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "github-webhook-handler"}

@app.post("/github/webhook", response_model=PipelineResponse, status_code=status.HTTP_200_OK)
async def github_webhook_handler(request: Request):
    """
    Captures GitHub Pull Request webhook events (or direct triggers),
    extracts metadata ({repo, pr_id, branch, commit, date, time}), and forwards to deployment-manager-agent.
    """
    raw_payload = await request.json()
    
    # Extract metadata flexibly (supporting GitHub webhook structure or direct payload)
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    if "pull_request" in raw_payload:
        pr = raw_payload.get("pull_request", {})
        repo = raw_payload.get("repository", {}).get("full_name", "cybage-devops/student-app")
        pr_id = pr.get("number", 1)
        branch = pr.get("head", {}).get("ref", "main")
        commit = pr.get("head", {}).get("sha", "a1b2c3d")
    else:
        repo = raw_payload.get("repo", "cybage-devops/student-app")
        pr_id = raw_payload.get("pr_id", 42)
        branch = raw_payload.get("branch", "main")
        commit = raw_payload.get("commit", "a1b2c3d")
        date_str = raw_payload.get("date", date_str)
        time_str = raw_payload.get("time", time_str)

    extracted_context = {
        "repo": repo,
        "pr_id": pr_id,
        "branch": branch,
        "commit": commit,
        "date": date_str,
        "time": time_str
    }

    # Pass payload to Orchestrator Agent (deployment-manager-agent)
    result = deployment_manager_agent.prepare_deploy_context(extracted_context)

    return PipelineResponse(
        status="SUCCESS",
        message=f"Deployment pipeline executed successfully for PR #{pr_id} on {repo}.",
        data=result
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
