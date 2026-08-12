import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, status, BackgroundTasks
from webhook.schemas import DirectTriggerPayload, GitHubWebhookPayload, PipelineResponse
from agents.deployment_manager import deployment_manager_agent

logger = logging.getLogger("github-webhook-service")

app = FastAPI(
    title="GitHub PR Webhook Service - Google ADK Pipeline",
    description="FastAPI Webhook capturing GitHub PR events to trigger the deployment-manager-agent orchestrator.",
    version="1.2.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "github-webhook-handler"}

def run_orchestrator_pipeline(extracted_context: dict):
    """
    Background worker executing the full multi-agent pipeline asynchronously.
    Safely catches exceptions to prevent background worker crashes.
    """
    logger.info(f"[webhook-service] Starting background pipeline for {extracted_context}")
    try:
        deployment_manager_agent.prepare_deploy_context(extracted_context)
        logger.info(f"[webhook-service] Background pipeline completed successfully for PR #{extracted_context.get('pr_id')}")
    except Exception as e:
        logger.error(f"[webhook-service] Error running background pipeline for PR #{extracted_context.get('pr_id')}: {e}", exc_info=True)

@app.post("/github/webhook", status_code=status.HTTP_200_OK)
async def github_webhook_handler(request: Request, background_tasks: BackgroundTasks):
    """
    Captures GitHub Pull Request webhook events (or direct triggers),
    extracts metadata ({repo, pr_id, branch, commit, date, time}),
    responds immediately to GitHub (preventing webhook timeout),
    and triggers deployment-manager-agent in background.
    """
    raw_payload = await request.json()
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # Default to user's active repository
    default_repo = "amitpawarcbg/Google-ADK-Multiagent-flow"

    if "pull_request" in raw_payload:
        pr = raw_payload.get("pull_request", {})
        repo = raw_payload.get("repository", {}).get("full_name", default_repo)
        # Extract PR number safely from top-level 'number' or 'pull_request.number'
        pr_id = raw_payload.get("number") or pr.get("number") or 1
        branch = pr.get("base", {}).get("ref", "main")
        commit = pr.get("head", {}).get("sha", "a1b2c3d")
        action = raw_payload.get("action")
        is_merged = pr.get("merged", False)

        # Ignore unmerged closed events or non-closed events
        if action != "closed" or not is_merged:
            logger.info(f"[webhook-service] Ignoring PR #{pr_id} action={action} (merged={is_merged})")
            return {"status": "IGNORED", "message": f"PR #{pr_id} action '{action}' (merged={is_merged}) ignored."}
    else:
        repo = raw_payload.get("repo", default_repo)
        pr_id = raw_payload.get("pr_id", 29)
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

    # Dispatch to background task to prevent GitHub Webhook 10s timeout
    background_tasks.add_task(run_orchestrator_pipeline, extracted_context)

    return {
        "status": "ACCEPTED",
        "message": f"Orchestrator pipeline triggered in background for PR #{pr_id} on {repo}.",
        "context": extracted_context
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
