import os
import io
import logging
from google.cloud import storage, firestore
from pypdf import PdfReader
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        logger.info(f"Deleting doc {doc.id} => {doc.to_dict().get('subject', 'Unknown Subject')}")
        doc.reference.delete()
        deleted += 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

def main():
    logger.info("Initializing Firestore & GCS for PDF ingestion...")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "warier-agents")
    bucket_name = "warier-agents"
    prefix = "wsj_podcasts/News_pdf/"
    
    try:
        db = firestore.Client(project=project_id)
        storage_client = storage.Client(project=project_id)
    except Exception as e:
        logger.error(f"Failed to initialize clients: {e}")
        return

    collection_name = "inbound_wsj_emails"
    coll_ref = db.collection(collection_name)
    
    logger.info(f"Clearing existing synthetic emails in {collection_name} to ensure clean PDF testing...")
    delete_collection(coll_ref, 50)

    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=prefix)
    
    pdf_count = 0
    for blob in blobs:
        if not blob.name.lower().endswith('.pdf'):
            continue
            
        logger.info(f"Downloading PDF: {blob.name}")
        pdf_bytes = blob.download_as_bytes()
        
        logger.info("Extracting text...")
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        
        if not text.strip():
            logger.warning(f"No text extracted from {blob.name}")
            continue
            
        # Treat the PDF filename as the subject/title
        title = os.path.basename(blob.name).replace(".pdf", "").replace("_", " ")
        doc_id = title.replace(" ", "_").lower()
        
        email_doc = {
            "email_id": doc_id,
            "subject": f"WSJ PDF News: {title}",
            "raw_body": text,
            "ingested_at": firestore.SERVER_TIMESTAMP,
            "timestamp": "Today"
        }
        
        coll_ref.document(doc_id).set(email_doc)
        logger.info(f"Seeded document from PDF: {title}")
        pdf_count += 1
        
    logger.info(f"Successfully seeded {pdf_count} PDFs into Firestore. The pipeline is ready to consume them.")

if __name__ == "__main__":
    main()
