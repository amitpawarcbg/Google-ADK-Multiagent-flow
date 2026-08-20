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

# 6. Workload Identity Pool for GitHub Actions
resource "google_iam_workload_identity_pool" "github_pool" {
  provider                  = google
  workload_identity_pool_id = "github-actions-pool"
  display_name              = "GitHub Actions Pool"
  description               = "Workload Identity Pool for GitHub Actions CI/CD"
  project                   = var.project_id
}

# 7. Workload Identity Provider for GitHub OIDC
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  provider                           = google
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-provider"
  display_name                       = "GitHub Provider"
  project                            = var.project_id

  attribute_condition = "assertion.repository == \"${var.github_repository}\""

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
    "attribute.owner"      = "assertion.repository_owner"
  }

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# 8. Allow GitHub Actions from repository to impersonate Service Account
resource "google_service_account_iam_member" "wif_sa_impersonation" {
  service_account_id = google_service_account.adk_agent_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_repository}"
}
#
