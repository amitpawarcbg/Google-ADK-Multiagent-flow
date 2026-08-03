# PR-Triggered Cloud Run Deployment — Google ADK Multi-Agent Flow

An enterprise-grade, multi-agent CI/CD automated build and deployment pipeline designed for Google Cloud Platform (GCP). Built using **Google Agent Development Kit (ADK)** concepts, **Vertex AI (`gemini-2.5-flash`)**, **FastAPI**, **Google Cloud Run**, **Google Artifact Registry (GAR)**, **Google Cloud Storage (GCS)**, and **Terraform**.

---

## 🏛️ System Architecture

```
[ GitHub PR Merged/Synced ]
           │
           ▼
   [ GitHub Webhook ]  ───>  /github/webhook (FastAPI Service)
                                       │
                                       │ Payload: {repo, pr_id, branch, commit, date, time}
                                       ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│ deployment-manager-agent                                                                  │
│ Main Orchestrator Agent • Google ADK SDK (Vertex AI gemini-2.5-flash)                     │
│ Function: prepare_deploy_context                                                          │
└─────┬───────────────────────────────────────┬───────────────────────────────────────┬─────┘
      │                                       │                                       │
      │ 1. A2A Request: {repo, branch, tag}   │ 2. A2A Request: {image, Agent.md}     │ 3. A2A Request: {repo, pr_id, commit, image, url}
      ▼                                       ▼                                       ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐   ┌─────────────────────────────┐
│ image-builder-sub-agent     │   │ cloud-run-deployer-sub-agent│   │ image-creator-slack-        │
│ Tool: build_and_push_image  │   │ Tool: deploy_cloud_run_svc  │   │ notifier-sub-agent          │
│ (Vertex AI gemini-2.5-flash)│   │ (Vertex AI gemini-2.5-flash)│   │ Tool: create_img_slack_post │
└──────────────┬──────────────┘   └──────────────┬──────────────┘   │ (Vertex AI gemini-2.5-flash)│
               │                                 │                  └──────────────┬──────────────┘
               ▼                                 ▼                                 ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐   ┌─────────────────────────────┐
│   Google Artifact Registry  │   │     Google Cloud Run        │   │   PNG Status Badge + GCS    │
│ (us-central1-docker.pkg.dev)│   │    (Live HTTPS Service)     │   │      + Slack Notification   │
└─────────────────────────────┘   └─────────────────────────────┘   └─────────────────────────────┘
```

---

## 🔑 Model & Authentication Specification

- **LLM Backend**: Google Vertex AI (`google-genai` SDK in `vertexai=True` mode).
- **Model Target**: `gemini-2.5-flash`.
- **Authentication**: Explicit initialization using Application Default Credentials (ADC), GCP Project ID (`GCP_PROJECT_ID`), and Region (`GCP_REGION`), ensuring **no hardcoded raw API keys**.
- **IAM Permission**: Cloud Run Service Accounts use `roles/aiplatform.user` for Vertex AI model calls.

---

## 📁 Repository Directory Structure

```
.
├── app/                                # Student Registration Web Application
│   ├── main.py                         # FastAPI web app (in-memory student DB)
│   ├── Dockerfile                      # Application container definition
│   └── Agent.md                        # Runtime deployment specifications (CPU, Memory, Concurrency, Env)
├── agents/                             # GCP ADK Multi-Agent Definitions
│   ├── base.py                         # Base Vertex AI gemini-2.5-flash client configuration
│   ├── deployment_manager.py           # Orchestrator Agent (prepare_deploy_context)
│   ├── image_builder.py                # Sub-Agent 1: Container build & GAR push
│   ├── cloud_run_deployer.py           # Sub-Agent 2: Agent.md parser & Cloud Run deployment
│   └── slack_notifier.py               # Sub-Agent 3: Status badge PNG generator, GCS uploader & Slack alert
├── webhook/                            # GitHub Webhook Service
│   ├── main.py                         # FastAPI webhook server (/github/webhook)
│   └── schemas.py                      # Pydantic schemas for PR events & A2A payloads
├── terraform/                          # Infrastructure as Code
│   ├── main.tf                         # GCP APIs, GAR, GCS, & Cloud Run services
│   ├── variables.tf                    # Project, Region, GAR, and GCS variables
│   ├── iam.tf                          # Service Accounts & IAM role bindings (roles/aiplatform.user)
│   └── outputs.tf                      # Terraform deployment outputs
├── tests/                              # Unit & Integration Test Suite
│   ├── test_app.py                     # Student Registration app unit tests
│   ├── test_agents.py                  # Agent reasoning & tool wrappers tests
│   └── test_webhook.py                 # FastAPI webhook endpoint integration tests
├── requirements.txt                    # Python dependencies
└── README.md                           # Documentation
```

---

## ⚡ Quickstart & Testing Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Automated Tests
Execute pytest across all app endpoints, agent reasoning tools, and webhook handlers:
```bash
pytest -v
```

### 3. Run Webhook Server Locally
```bash
uvicorn webhook.main:app --host 0.0.0.0 --port 8000
```

### 4. Trigger Webhook via curl
```bash
curl -X POST "http://localhost:8000/github/webhook" \
     -H "Content-Type: application/json" \
     -d '{
       "repo": "cybage-devops/student-app",
       "pr_id": 42,
       "branch": "main",
       "commit": "a1b2c3d4e5f6",
       "date": "2026-08-03",
       "time": "13:20:00"
     }'
```

---

## 🛠️ Terraform Infrastructure Provisioning

To provision the complete GCP infrastructure (Artifact Registry, Cloud Storage, Service Accounts, Vertex AI IAM, Cloud Run):

```bash
cd terraform
terraform init
terraform plan -var="project_id=YOUR_GCP_PROJECT_ID"
terraform apply -var="project_id=YOUR_GCP_PROJECT_ID" -auto-approve
```
