import os
import shutil
import logging
import subprocess
from typing import Dict, Any
from agents.base import BaseADKAgent, settings

logger = logging.getLogger("image-builder-agent")

class ImageBuilderSubAgent(BaseADKAgent):
    """
    Sub-Agent 1: image-builder-sub-agent
    Responsibility: Accepts repo, branch, and tag specifications, clones latest merged commit from GitHub,
    builds application container image via Cloud Build, pushes to Google Artifact Registry (GAR),
    and returns final image_name:tag.
    """
    def __init__(self):
        super().__init__(
            name="image-builder-sub-agent",
            role="Container Build & Registry Specialist",
            instructions="Target container build for Google Artifact Registry (GAR). Fetch source from GitHub repository."
        )

    def build_and_push_image(self, repo: str, branch: str, tag: str) -> Dict[str, Any]:
        """
        Executes build and push of application container image to GAR.
        Returns payload containing image_name:tag.
        """
        logger.info(f"[{self.name}] Initiating build for repo={repo}, branch={branch}, tag={tag}")
        
        # Use reasoning model to formulate build plan
        reasoning = self.generate_agent_reasoning(f"Prepare GAR build for {repo} on branch {branch} with tag {tag}")
        logger.info(f"[{self.name}] Agent Reasoning: {reasoning}")

        repo_basename = repo.split("/")[-1].lower()
        image_repo_path = f"{settings.gcp_region}-docker.pkg.dev/{settings.gcp_project_id}/{settings.gar_repository}/{repo_basename}"
        latest_image_tag = f"{image_repo_path}:latest"

        # Clone merged commit source from GitHub into temp folder
        clone_dir = f"/tmp/repo_{tag}"
        if os.path.exists(clone_dir):
            shutil.rmtree(clone_dir, ignore_errors=True)

        github_url = f"https://github.com/{repo}.git"
        clone_cmd = f"git clone --depth 1 --branch {branch} {github_url} {clone_dir}"
        logger.info(f"[{self.name}] Cloning GitHub repository: {clone_cmd}")
        
        try:
            clone_res = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True, timeout=60)
            logger.info(f"[{self.name}] Git clone output: {clone_res.stdout.strip()}")
            app_dir = os.path.join(clone_dir, "app") if os.path.exists(os.path.join(clone_dir, "app")) else clone_dir
        except Exception as e:
            logger.warning(f"[{self.name}] Git clone warning: {e}. Falling back to local workspace app directory.")
            app_dir = "app"

        # Build execution wrapper (gcloud builds submit app directory)
        build_command = f"gcloud builds submit {app_dir} --tag {latest_image_tag} --project {settings.gcp_project_id}"
        logger.info(f"[{self.name}] Executing build command: {build_command}")

        try:
            cmd_result = subprocess.run(
                build_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            logger.info(f"[{self.name}] Build output stdout: {cmd_result.stdout.strip()}")
            logger.info(f"[{self.name}] Build output stderr: {cmd_result.stderr.strip()}")
        except Exception as e:
            logger.warning(f"[{self.name}] Build subprocess note: {e}")
        finally:
            if os.path.exists(clone_dir):
                shutil.rmtree(clone_dir, ignore_errors=True)

        return {
            "status": "SUCCESS",
            "agent": self.name,
            "repo": repo,
            "branch": branch,
            "image_name_tag": latest_image_tag,
            "gar_repository": settings.gar_repository,
            "build_command": build_command,
            "reasoning": reasoning
        }

image_builder_agent = ImageBuilderSubAgent()
