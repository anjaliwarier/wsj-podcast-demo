import logging
from google.adk.tools import ToolContext
from ..synthetic_data_generator import generate_synthetic_wsj_emails

logger = logging.getLogger(__name__)

def ingest_recent_wsj_emails(tool_context: ToolContext) -> dict:
    """Simulates fetching or synthesizing the 5 most recent Wall Street Journal front-page story emails
    and archives them into the Agent Runtime Memory Bank.

    Args:
        tool_context (ToolContext): ADK tool context providing access to session state / Memory Bank.

    Returns:
        dict: Ingestion status and summary list of email headlines.
    """
    logger.info("ADK Tool Call: Ingesting recent WSJ emails...")
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
