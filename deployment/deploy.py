import os
import sys

# Ensure parent directory is in path to import agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp
from wsj_podcast_agent.agent import root_agent

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP storage bucket for Agent Runtime artifacts.")
flags.DEFINE_string("resource_id", None, "ReasoningEngine resource ID.")

flags.DEFINE_bool("list", False, "List all active deployed agents.")
flags.DEFINE_bool("create", False, "Creates a new remote agent engine.")
flags.DEFINE_bool("delete", False, "Deletes an existing deployed remote agent.")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete", "list"])


def create() -> None:
    """Creates a serverless agent engine for WSJ Podcast Architect Agent."""
    adk_app = AdkApp(agent=root_agent, enable_tracing=True)

    remote_agent = agent_engines.create(
        adk_app,
        display_name=root_agent.name,
        requirements=[
            "google-adk>=1.5.0,<2.0.0",
            "google-cloud-aiplatform[agent_engines]>=1.91.0",
            "google-genai>=0.1.0",
            "google-cloud-storage",
            "google-cloud-texttospeech",
            "google-api-python-client",
            "google-auth",
            "requests",
            "pydantic>=2.0.0,<3.0.0",
            "python-dotenv>=1.0.0,<2.0.0",
            "absl-py>=2.2.1,<3.0.0",
        ],
    )
    print(f"Created remote agent on Vertex AI Reasoning Engines: {remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"Deleted remote agent engine resource: {resource_id}")


def list_agents() -> None:
    remote_agents = agent_engines.list()
    template = """
{agent.name} ("{agent.display_name}")
- Create time: {agent.create_time}
- Update time: {agent.update_time}
"""
    remote_agents_string = "\n".join(
        template.format(agent=agent) for agent in remote_agents
    )
    print(f"All active remote agent engines:\n{remote_agents_string}")


def main(argv: list[str]) -> None:
    del argv  # unused
    load_dotenv()

    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    )
    bucket = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    )

    print(f"PROJECT ID: {project_id}")
    print(f"LOCATION: {location}")
    print(f"STAGING BUCKET: {bucket}")

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    if FLAGS.list:
        list_agents()
    elif FLAGS.create:
        create()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("Error: --resource_id=... is mandatory when running --delete")
            return
        delete(FLAGS.resource_id)
    else:
        print("Please specify an operational command: --create, --list, or --delete --resource_id=...")


if __name__ == "__main__":
    app.run(main)
