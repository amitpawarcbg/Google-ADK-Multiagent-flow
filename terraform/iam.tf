# IAM Service Account for GCP ADK Multi-Agent Execution
resource "google_service_account" "adk_agent_sa" {
  account_id   = "adk-multiagent-sa"
  display_name = "ADK Multi-Agent Runner Service Account"
  project      = var.project_id
}

# 1. Vertex AI User (roles/aiplatform.user) - Required for Gemini gemini-2.5-flash
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.adk_agent_sa.email}"
}

# 2. Cloud Run Admin (roles/run.admin) - Required for cloud-run-deployer-sub-agent
resource "google_project_iam_member" "cloud_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.adk_agent_sa.email}"
}

# 3. Artifact Registry Writer (roles/artifactregistry.writer) - Required for image-builder-sub-agent
resource "google_project_iam_member" "gar_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.adk_agent_sa.email}"
}

# 4. Storage Object Admin (roles/storage.objectAdmin) - Required for image-creator-slack-notifier-sub-agent
resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.adk_agent_sa.email}"
}

# 5. Service Account User (roles/iam.serviceAccountUser)
resource "google_project_iam_member" "sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.adk_agent_sa.email}"
}
