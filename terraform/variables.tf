variable "project_id" {
  type        = string
  description = "GCP Project ID"
  default     = "amittechnet-0626"
}

variable "region" {
  type        = string
  description = "GCP Region for Cloud Run & Artifact Registry"
  default     = "us-central1"
}

variable "gar_repository_name" {
  type        = string
  description = "Google Artifact Registry Repository Name"
  default     = "cybage-devops-repo"
}

variable "gcs_bucket_name" {
  type        = string
  description = "Google Cloud Storage Bucket for deployment artifacts"
  default     = "cybage-devops-deployment-artifacts"
}

variable "slack_webhook_url" {
  type        = string
  description = "Slack Webhook URL for notifications"
  default     = "https://hooks.slack.com/services/mock/devops/deployments"
}

variable "github_repository" {
  type        = string
  description = "GitHub Repository in owner/repo format for Workload Identity Federation"
  default     = "amitpawarcbg/Google-ADK-Multiagent-flow"
}
