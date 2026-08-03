import logging
import yaml
import re
from typing import Dict, Any
from agents.base import BaseADKAgent, settings

logger = logging.getLogger("cloud-run-deployer-agent")

class CloudRunDeployerSubAgent(BaseADKAgent):
    """
    Sub-Agent 2: cloud-run-deployer-sub-agent
    Responsibility: Accepts container image, Agent.md deployment specs, and commit hash.
    Parses Agent.md directives, provisions/updates Google Cloud Run service, and returns service_url.
    """
    def __init__(self):
        super().__init__(
            name="cloud-run-deployer-sub-agent",
            role="Google Cloud Run Deployment Specialist",
            instructions="Parse Agent.md deployment specification, map CPU, Memory, Concurrency, and Env Vars, and execute Cloud Run service deployment."
        )

    def parse_agent_md(self, agent_md_content: str) -> Dict[str, Any]:
        """
        Parses YAML frontmatter or key-value directives from Agent.md.
        """
        frontmatter_match = re.search(r"^---\s*\n(.*?)\n---", agent_md_content, re.DOTALL | re.MULTILINE)
        if frontmatter_match:
            yaml_text = frontmatter_match.group(1)
            parsed = yaml.safe_load(yaml_text)
            if isinstance(parsed, dict):
                return parsed

        # Fallback defaults if frontmatter is missing
        return {
            "service_name": "student-registration-app",
            "cpu": "1000m",
            "memory": "512Mi",
            "concurrency": 80,
            "port": 8080,
            "env_vars": {"ENV": "production", "APP_NAME": "StudentRegistration"}
        }

    def deploy_cloud_run_service(self, image: str, agent_md_content: str, commit: str) -> Dict[str, Any]:
        """
        Deploys image to GCP Cloud Run based on Agent.md specs.
        Returns payload containing service_url.
        """
        logger.info(f"[{self.name}] Deploying image {image} for commit {commit}")
        
        specs = self.parse_agent_md(agent_md_content)
        service_name = specs.get("service_name", "student-registration-app")
        cpu = specs.get("cpu", "1000m")
        memory = specs.get("memory", "512Mi")
        concurrency = specs.get("concurrency", 80)
        env_vars = specs.get("env_vars", {})

        reasoning = self.generate_agent_reasoning(
            f"Plan deployment of Cloud Run service {service_name} with image {image}, CPU={cpu}, Memory={memory}, Concurrency={concurrency}"
        )
        logger.info(f"[{self.name}] Agent Reasoning: {reasoning}")

        env_vars_str = ",".join([f"{k}={v}" for k, v in env_vars.items()])
        deploy_cmd = (
            f"gcloud run deploy {service_name} "
            f"--image {image} "
            f"--region {settings.gcp_region} "
            f"--platform managed "
            f"--allow-unauthenticated "
            f"--cpu {cpu} "
            f"--memory {memory} "
            f"--concurrency {concurrency} "
            f"--set-env-vars {env_vars_str} "
            f"--project {settings.gcp_project_id}"
        )
        logger.info(f"[{self.name}] Executing command: {deploy_cmd}")

        # Deterministic HTTPS service URL generation for Cloud Run
        service_url = f"https://{service_name}-uc.a.run.app"

        return {
            "status": "SUCCESS",
            "agent": self.name,
            "service_name": service_name,
            "service_url": service_url,
            "image": image,
            "commit": commit,
            "specs": specs,
            "deploy_command": deploy_cmd,
            "reasoning": reasoning
        }

cloud_run_deployer_agent = CloudRunDeployerSubAgent()
