import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import ToolContext

from .synthetic_data_generator import generate_synthetic_wsj_emails
from .services import (
    filter_journalistic_content,
    generate_podcast,
    store_podcast_and_sign_url,
    send_summary_email
)

load_dotenv()

# -------------------------------------------------------------------------
# Define ADK Tools for the Agent (Interacting with Memory Bank)
# -------------------------------------------------------------------------

def ingest_recent_wsj_emails(tool_context: ToolContext) -> dict:
    """Simulates fetching or synthesizing the 5 most recent Wall Street Journal front-page story emails
    and archives them into the Agent Runtime Memory Bank.

    Args:
        tool_context (ToolContext): ADK tool context providing access to session state / Memory Bank.

    Returns:
        dict: Ingestion status and summary list of email headlines.
    """
    emails = generate_synthetic_wsj_emails()
    
    # Secure storage in Memory Bank
    state = tool_context.state
    state["recent_wsj_emails"] = emails
    
    summary = [{"email_id": e["email_id"], "timestamp": e["timestamp"], "subject": e["subject"]} for e in emails]
    return {
        "status": "success",
        "message": f"Successfully ingested {len(emails)} WSJ front-page stories into Memory Bank.",
        "headlines": summary
    }


def parse_clean_journalistic_text(tool_context: ToolContext) -> dict:
    """Processes raw ingested WSJ emails stored in the Memory Bank, extracts strictly core journalistic prose,
    filters out promotional overhead, and stores the resulting transcript into the Memory Bank.

    Args:
        tool_context (ToolContext): ADK tool context providing access to session state / Memory Bank.

    Returns:
        dict: Parsing status and preview snippet of extracted script.
    """
    state = tool_context.state
    emails = state.get("recent_wsj_emails")
    if not emails:
        return {
            "status": "error",
            "error_message": "No WSJ emails located in Memory Bank. Execute 'ingest_recent_wsj_emails' first."
        }
        
    cleaned_script = filter_journalistic_content(emails)
    state["cleaned_script"] = cleaned_script
    
    return {
        "status": "success",
        "message": "Extracted pristine journalistic prose successfully.",
        "char_count": len(cleaned_script),
        "transcript_snippet": cleaned_script[:350] + "..."
    }


def produce_and_distribute_podcast(tool_context: ToolContext) -> dict:
    """Synthesizes studio-quality audio via Gemini Enterprise Podcast API using the extracted script from Memory Bank,
    stages the binary audio to Google Cloud Storage, generates a 7-day signed URL, and sends a notification email.

    Args:
        tool_context (ToolContext): ADK tool context providing access to session state / Memory Bank.

    Returns:
        dict: Complete delivery execution metadata containing storage bucket URI and secure signed URL.
    """
    state = tool_context.state
    cleaned_script = state.get("cleaned_script")
    if not cleaned_script:
        return {
            "status": "error",
            "error_message": "No cleaned script located in Memory Bank. Execute 'parse_clean_journalistic_text' first."
        }
        
    # 1. Produce Podcast Audio
    pod_res = generate_podcast(cleaned_script)
    if pod_res.get("status") != "success":
        return pod_res
        
    audio_bytes = pod_res["audio_content_bytes"]
    
    # 2. Stage to GCS & Sign URL
    store_res = store_podcast_and_sign_url(audio_bytes)
    signed_url = store_res["signed_url"]
    storage_uri = store_res["storage_uri"]
    
    # 3. Transmit notification email
    email_res = send_summary_email(signed_url, cleaned_script)
    
    # Archive final status into Memory Bank
    execution_record = {
        "audio_bytes_len": len(audio_bytes),
        "storage_uri": storage_uri,
        "signed_url": signed_url,
        "email_dispatched": email_res.get("dispatched")
    }
    state["last_podcast_dispatch"] = execution_record
    
    return {
        "status": "success",
        "message": "Podcast synthesis, GCS staging, signed URL creation, and email dispatch completed successfully!",
        "podcast_storage_uri": storage_uri,
        "secure_signed_url": signed_url,
        "email_dispatched_metadata": email_res
    }


# -------------------------------------------------------------------------
# Define the Root ADK Agent
# -------------------------------------------------------------------------

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "warier-agents")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-pro")

if PROJECT_ID != "YOUR_GCP_PROJECT_ID" and not MODEL_NAME.startswith("projects/"):
    model_path = f"projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/{MODEL_NAME}"
else:
    model_path = MODEL_NAME

root_agent = Agent(
    name="wsj_podcast_architect_agent",
    model=model_path,
    description=(
        "Editorial Assistant Agent designed to ingest Wall Street Journal front-page stories, "
        "strip boilerplate formatting and metadata, and synthesize executive audio briefings."
    ),
    instruction="""You are an editorial assistant. 
Here are 5 emails containing Wall Street Journal articles. Strip out all email formatting, disclaimers, and metadata. Extract only the core journalistic text.

When a user requests to extract text from recent WSJ emails or generate a podcast briefing:
1. First invoke `ingest_recent_wsj_emails` to acquire the 5 most recent front-page feature stories.
2. Next invoke `parse_clean_journalistic_text` to clean and filter the text.
3. Finally invoke `produce_and_distribute_podcast` to generate audio via the Google Podcast API, stage it to Google Cloud Storage, and send the notification email with a secure signed URL.
4. Formulate a complete, polished executive delivery receipt summarizing the exact headlines analyzed and presenting the final Signed URL cleanly.

MANDATORY DISCLAIMER:
You must append these exact disclaimers at the very bottom of every response:
- 'This insight was generated by an AI agent deployed on the Gemini Enterprise Agent Platform.'
- 'Outputs should be validated by Subject Matter Experts (SMEs) before strategic execution.'""",
    tools=[ingest_recent_wsj_emails, parse_clean_journalistic_text, produce_and_distribute_podcast]
)

if __name__ == "__main__":
    print(f"Agent '{root_agent.name}' loaded successfully with model {root_agent.model}.")
