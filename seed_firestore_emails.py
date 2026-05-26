import os
import logging
import datetime
from google.cloud import firestore
from wsj_podcast_agent.synthetic_data_generator import generate_synthetic_wsj_emails
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    logger.info("Initializing Firestore Database seeding...")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "warier-agents")
    
    try:
        db = firestore.Client(project=project_id)
    except Exception as e:
        logger.error(f"Failed to initialize Firestore Client: {e}")
        logger.error("Ensure you are authenticated via 'gcloud auth application-default login'")
        return

    logger.info("Generating synthetic WSJ emails...")
    emails = generate_synthetic_wsj_emails()
    
    collection_name = "inbound_wsj_emails"
    logger.info(f"Writing {len(emails)} emails to Firestore collection: {collection_name}...")
    
    for email in emails:
        # We append a server timestamp so the agent can pull the 'latest'
        email_id = email.get("email_id")
        doc_ref = db.collection(collection_name).document(email_id)
        email["ingested_at"] = firestore.SERVER_TIMESTAMP
        doc_ref.set(email)
        logger.info(f"Seeded document: {email_id} ({email['subject']})")
        
    logger.info("Firestore seeding complete! The pipeline is ready to consume data.")

if __name__ == "__main__":
    main()
