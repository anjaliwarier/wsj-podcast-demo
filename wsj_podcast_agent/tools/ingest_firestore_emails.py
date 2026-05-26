import os
import logging
from google.cloud import firestore
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

def ingest_firestore_emails(tool_context: ToolContext) -> dict:
    """Fetches the 5 most recent Wall Street Journal emails dynamically from the Firestore database.

    Args:
        tool_context (ToolContext): ADK tool context providing access to session state / Memory Bank.

    Returns:
        dict: Ingestion status and summary list of email headlines.
    """
    logger.info("ADK Tool Call: Ingesting recent WSJ emails from Firestore...")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "warier-agents")
    
    use_mock = os.getenv("USE_SYNTHETIC_LOCAL_MOCK", "True").lower() == "true"
    
    # Bypass logic if requested
    if use_mock:
        logger.info("USE_SYNTHETIC_LOCAL_MOCK is True. Yielding entirely to synthetic data generator.")
        from ..synthetic_data_generator import generate_synthetic_wsj_emails
        emails = generate_synthetic_wsj_emails()
    else:
        try:
            db = firestore.Client(project=project_id)
            collection_ref = db.collection("inbound_wsj_emails")
            # Query the 5 most recent emails
            docs = collection_ref.order_by("ingested_at", direction=firestore.Query.DESCENDING).limit(5).stream()
            
            emails = []
            for doc in docs:
                data = doc.to_dict()
                emails.append({
                    "email_id": doc.id,
                    "timestamp": data.get("timestamp"),
                    "subject": data.get("subject", "No Subject"),
                    "raw_body": data.get("raw_body", "")
                })
                
            if not emails:
                logger.warning("No emails found in Firestore. Falling back to synthetic mock generator.")
                from ..synthetic_data_generator import generate_synthetic_wsj_emails
                emails = generate_synthetic_wsj_emails()
                
        except Exception as e:
            logger.error(f"Firestore ingestion failed: {e}. Falling back to mock generator.")
            from ..synthetic_data_generator import generate_synthetic_wsj_emails
            emails = generate_synthetic_wsj_emails()
            
    # Secure storage in Memory Bank
    state = tool_context.state
    state["recent_wsj_emails"] = emails
    
    summary = [{"email_id": e["email_id"], "subject": e["subject"]} for e in emails]
    return {
        "status": "success",
        "message": f"Successfully ingested {len(emails)} WSJ front-page stories from Firestore into Memory Bank.",
        "headlines": summary
    }
