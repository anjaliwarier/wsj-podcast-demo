import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines

FLAGS = flags.FLAGS

flags.DEFINE_string("project_id", None, "GCP project ID.")
flags.DEFINE_string("location", None, "GCP location.")
flags.DEFINE_string("bucket", None, "GCP staging bucket.")
flags.DEFINE_string(
    "resource_id",
    None,
    "ReasoningEngine resource ID (returned upon successful deployment creation)",
)
flags.DEFINE_string("user_id", "financial_executive", "Enterprise User ID for isolated session state.")
flags.mark_flag_as_required("resource_id")


def main(argv: list[str]) -> None:
    del argv

    load_dotenv()

    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT", "warier-agents")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    )
    bucket = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", "warier-agents-podcast-bucket")
    )

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    agent = agent_engines.get(FLAGS.resource_id)
    print(f"Connected successfully to serverless agent engine: {FLAGS.resource_id}")
    session = agent.create_session(user_id=FLAGS.user_id)
    print(f"Instantiated persistent session state for user: {FLAGS.user_id}")
    print("Interactive interactive streaming ready. Enter 'quit' to terminate.")
    
    while True:
        user_input = input("User Request: ")
        if user_input.lower() in ["quit", "exit"]:
            break

        for event in agent.stream_query(
            user_id=FLAGS.user_id, session_id=session["id"], message=user_input
        ):
            if "content" in event and "parts" in event["content"]:
                parts = event["content"]["parts"]
                for part in parts:
                    if "text" in part:
                        print(f"Agent Engine: {part['text']}")

    agent.delete_session(user_id=FLAGS.user_id, session_id=session["id"])
    print(f"Decommissioned session state for user: {FLAGS.user_id}")


if __name__ == "__main__":
    app.run(main)
