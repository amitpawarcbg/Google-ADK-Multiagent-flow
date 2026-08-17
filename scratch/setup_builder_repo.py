import os
import shutil

src = r"d:\Amit\Google ADK Multiagent flow"
dst = os.path.join(src, "scratch", "repos", "image-builder-sub-agent")

shutil.copytree(os.path.join(src, "agents"), os.path.join(dst, "agents"), dirs_exist_ok=True)
shutil.copyfile(os.path.join(src, "requirements.txt"), os.path.join(dst, "requirements.txt"))

dockerfile_content = """FROM python:3.11-slim
RUN apt-get update && apt-get install -y git curl gnupg && \
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
from agents.image_builder import image_builder_agent

app = FastAPI(title="Image Builder Sub-Agent API")

class BuildPayload(BaseModel):
    repo: str
    branch: str = "main"
    tag: str

@app.get("/health")
def health():
    return {"status": "healthy", "agent": "image-builder-sub-agent"}

@app.post("/build")
def build_image(payload: BuildPayload):
    try:
        res = image_builder_agent.build_and_push_image(
            repo=payload.repo,
            branch=payload.branch,
            tag=payload.tag
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

with open(os.path.join(dst, "main.py"), "w") as f:
    f.write(main_content)

print("Populated image-builder-sub-agent successfully")
