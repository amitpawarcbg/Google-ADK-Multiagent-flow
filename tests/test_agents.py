import os
import pytest
from agents.image_builder import image_builder_agent
from agents.cloud_run_deployer import cloud_run_deployer_agent
from agents.slack_notifier import slack_notifier_agent
from agents.deployment_manager import deployment_manager_agent

def test_image_builder_sub_agent():
    res = image_builder_agent.build_and_push_image(
        repo="cybage-devops/student-app",
        branch="main",
        tag="pr42-a1b2c3d-20260803-132000"
    )
    assert res["status"] == "SUCCESS"
    assert res["agent"] == "image-builder-sub-agent"
    assert "pkg.dev" in res["image_name_tag"]
    assert "latest" in res["image_name_tag"]

def test_cloud_run_deployer_agent():
    sample_agent_md = """---
service_name: test-student-app
cpu: "1000m"
memory: "512Mi"
concurrency: 80
---"""
    res = cloud_run_deployer_agent.deploy_cloud_run_service(
        image="us-central1-docker.pkg.dev/proj/repo/app:tag",
        agent_md_content=sample_agent_md,
        commit="a1b2c3d"
    )
    assert res["status"] == "SUCCESS"
    assert res["service_name"] == "test-student-app"
    assert res["service_url"].startswith("https://")

def test_slack_notifier_agent():
    res = slack_notifier_agent.create_image_and_post_to_slack(
        repo="cybage-devops/student-app",
        pr_id=42,
        commit="a1b2c3d4",
        image="us-central1-docker.pkg.dev/proj/repo/app:tag",
        service_url="https://student-app-uc.a.run.app"
    )
    assert res["status"] == "SUCCESS"
    assert os.path.exists(res["png_file"])
    assert res["slack_posted"] is True

def test_orchestrator_deployment_manager():
    payload = {
        "repo": "cybage-devops/student-app",
        "pr_id": 101,
        "branch": "feature/a2a-flow",
        "commit": "c9f8e7d6a5b4",
        "date": "2026-08-03",
        "time": "13:20:00"
    }
    summary = deployment_manager_agent.prepare_deploy_context(payload)
    assert summary["status"] == "SUCCESS"
    assert summary["orchestrator"] == "deployment-manager-agent"
    assert summary["step1_builder"]["status"] == "SUCCESS"
    assert summary["step2_deployer"]["status"] == "SUCCESS"
    assert summary["step3_notifier"]["status"] == "SUCCESS"
    assert "https://" in summary["final_service_url"]
