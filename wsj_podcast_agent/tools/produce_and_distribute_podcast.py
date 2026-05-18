import logging
from google.adk.tools import ToolContext
from ..services import (
    generate_podcast,
    store_podcast_and_sign_url,
    send_summary_email
)

logger = logging.getLogger(__name__)

def produce_and_distribute_podcast(tool_context: ToolContext) -> dict:
    """Synthesizes studio-quality audio via Gemini Enterprise Podcast API using the structured script from Memory Bank,
    stages the binary audio to Google Cloud Storage, generates a 7-day signed URL, and sends a notification email.

    Args:
        tool_context (ToolContext): ADK tool context providing access to session state / Memory Bank.

    Returns:
        dict: Complete delivery execution metadata containing storage bucket URI and secure signed URL.
    """
    logger.info("ADK Tool Call: Producing and distributing podcast briefings...")
    state = tool_context.state
    structured_brief = state.get("structured_brief")
    if not structured_brief or "podcast_script" not in structured_brief:
        return {
            "status": "error",
            "error_message": "No structured brief/script located in Memory Bank. Execute 'parse_clean_journalistic_text' first."
        }
        
    podcast_script = structured_brief["podcast_script"]
    
    # 1. Produce Podcast Audio from structured text script property
    pod_res = generate_podcast(podcast_script)
    if pod_res.get("status") != "success":
        return pod_res
        
    audio_bytes = pod_res["audio_content_bytes"]
    
    # 2. Stage to GCS & Sign URL
    store_res = store_podcast_and_sign_url(audio_bytes)
    signed_url = store_res["signed_url"]
    storage_uri = store_res["storage_uri"]
    
    # 3. Transmit notification email
    email_res = send_summary_email(signed_url, podcast_script)
    
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
