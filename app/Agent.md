---
service_name: student-registration-app
region: us-central1
cpu: "1000m"
memory: "512Mi"
concurrency: 80
min_instances: 0
max_instances: 5
port: 8080
env_vars:
  ENV: "production"
  APP_NAME: "StudentRegistration"
  ORG: "cybage-devops"
---

# Agent Deployment Specification

This file defines the runtime specifications for deploying the **Student Registration App** onto Google Cloud Run via the `cloud-run-deployer-sub-agent`.

## Deployment Directives

- **Service Name**: `student-registration-app`
- **Region**: `us-central1`
- **CPU Allocation**: `1000m` (1 vCPU)
- **Memory Allocation**: `512Mi`
- **Max Concurrency**: `80` requests per instance
- **Scaling Limits**: `0` min instances (scale-to-zero enabled), `5` max instances.
- **Environment Variables**:
  - `ENV`: production
  - `APP_NAME`: StudentRegistration
  - `ORG`: cybage-devops
