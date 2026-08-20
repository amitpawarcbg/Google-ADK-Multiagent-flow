output "artifact_registry_url" {
  description = "Google Artifact Registry Docker repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.gar_repository_name}"
}

output "gcs_bucket_name" {
  description = "GCS bucket name for status PNG badges"
  value       = google_storage_bucket.artifacts_bucket.name
}

output "webhook_service_url" {
  description = "Live Cloud Run URL for GitHub Webhook Endpoint"
  value       = google_cloud_run_v2_service.webhook_service.uri
}

output "deployment_manager_agent_url" {
  description = "Live Cloud Run URL for deployment-manager-agent"
  value       = google_cloud_run_v2_service.deployment_manager_agent.uri
}

output "image_builder_sub_agent_url" {
  description = "Live Cloud Run URL for image-builder-sub-agent"
  value       = google_cloud_run_v2_service.image_builder_sub_agent.uri
}

output "cloud_run_deployer_sub_agent_url" {
  description = "Live Cloud Run URL for cloud-run-deployer-sub-agent"
  value       = google_cloud_run_v2_service.cloud_run_deployer_sub_agent.uri
}

output "slack_notifier_sub_agent_url" {
  description = "Live Cloud Run URL for image-creator-slack-notifier-sub-agent"
  value       = google_cloud_run_v2_service.slack_notifier_sub_agent.uri
}

output "service_account_email" {
  description = "ADK Multi-Agent Service Account Email"
  value       = google_service_account.adk_agent_sa.email
}

output "workload_identity_provider" {
  description = "Full identifier of the Workload Identity Provider for GitHub Actions"
  value       = google_iam_workload_identity_pool_provider.github_provider.name
}
