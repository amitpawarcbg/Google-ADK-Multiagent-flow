import os
import shutil

src = r"d:\Amit\Google ADK Multiagent flow"
dst = os.path.join(src, "scratch", "repos", "image-creator-slack-notifier-sub-agent")

shutil.copytree(os.path.join(src, "agents"), os.path.join(dst, "agents"), dirs_exist_ok=True)
shutil.copyfile(os.path.join(src, "requirements.txt"), os.path.join(dst, "requirements.txt"))

dockerfile_content = """FROM python:3.11-slim
RUN apt-get update && apt-get install -y git curl gnupg fonts-dejavu && \
    curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    apt-get update && apt-get install -y google-cloud-cli && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
ENV PYTHONPATH=/app
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
"""

with open(os.path.join(dst, "Dockerfile"), "w") as f:
    f.write(dockerfile_content)

main_content = """from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.slack_notifier import slack_notifier_agent

app = FastAPI(title="Image Creator Slack Notifier Sub-Agent API")

class NotifyPayload(BaseModel):
    repo: str
    pr_id: int
    commit: str
    image: str
    service_url: str

@app.get("/health")
def health():
    return {"status": "healthy", "agent": "image-creator-slack-notifier-sub-agent"}

@app.post("/notify")
def notify_slack(payload: NotifyPayload):
    try:
        res = slack_notifier_agent.create_image_and_post_to_slack(
            repo=payload.repo,
            pr_id=payload.pr_id,
            commit=payload.commit,
            image=payload.image,
            service_url=payload.service_url
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

with open(os.path.join(dst, "main.py"), "w") as f:
    f.write(main_content)

print("Populated image-creator-slack-notifier-sub-agent successfully")
