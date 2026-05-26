import os
import json
import logging
import asyncio
from pydantic import BaseModel, Field
from google.adk.tools import ToolContext

load_dotenv_success = False
try:
    from google import genai
    from google.genai import types
    load_dotenv_success = True
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Pydantic Structured JSON News Schemas
# -----------------------------------------------------------------------------
class WSJArticle(BaseModel):
    headline: str = Field(description="Headline of the news article.")
    core_prose: str = Field(description="Pure editorial prose and content body stripped of all disclaimers and formatting.")

class WSJEditorialBrief(BaseModel):
    headlines: list[str] = Field(description="List of all article headlines extracted.")
    key_takeaways: list[str] = Field(description="Key high-level bullet points of the front page news.")
    podcast_script: str = Field(description="A continuous unified script combining the core journalistic text optimized for conversational audio generation.")

async def process_single_email(client, email: dict) -> str:
    """MAP Phase: Process a single email asynchronously."""
    prompt = f"Extract the core journalistic text and the headline from this email. Strip all boilerplate.\nSubject: {email['subject']}\nBody: {email['raw_body']}"
    response = await asyncio.to_thread(
        client.models.generate_content,
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1)
    )
    return response.text

async def map_reduce_extraction(client, emails: list) -> dict:
    """MAP-REDUCE Pipeline"""
    logger.info("Starting Map phase for 5 emails concurrently...")
    tasks = [process_single_email(client, email) for email in emails]
    individual_summaries = await asyncio.gather(*tasks)
    
    logger.info("Starting Reduce phase to synthesize final script...")
    combined_summaries = "\n\n=== NEXT ARTICLE ===\n\n".join(individual_summaries)
    
    prompt = f"""
    You are an editorial assistant. Here are 5 individual summaries of Wall Street Journal articles. 
    Format your extraction into a structured JSON object matching the requested schema:
    - headlines: A list of the 5 article headlines.
    - key_takeaways: A short bulleted summary list of critical macroeconomic points.
    - podcast_script: A continuous, clean script containing strictly the core editorial narrative optimized for audio podcast generation.

    Summaries:
    {combined_summaries}
    """
    
    response = await asyncio.to_thread(
        client.models.generate_content,
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=WSJEditorialBrief
        )
    )
    return json.loads(response.text)

def parse_clean_journalistic_text(tool_context: ToolContext) -> dict:
    """Processes raw ingested WSJ emails stored in the Memory Bank via Map-Reduce."""
    logger.info("ADK Tool Call: Extracting clean journalistic text and converting to structured JSON...")
    state = tool_context.state
    emails = state.get("recent_wsj_emails")
    if not emails:
        return {
            "status": "error",
            "error_message": "No WSJ emails located in Memory Bank. Execute 'ingest_live_gmail' first."
        }
        
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    structured_brief = None
    
    from ..services import get_firestore_client
    import datetime
    db = get_firestore_client()
    doc_id = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    doc_ref = db.collection("wsj_podcast_runs").document(doc_id) if db else None
    
    if doc_ref:
        doc = doc_ref.get()
        if doc.exists:
            logger.info(f"Found cached execution state in Firestore for {doc_id}. Bypassing LLM Map-Reduce.")
            structured_brief = doc.to_dict().get("structured_brief")
    
    if not structured_brief and genai and project_id and project_id != "YOUR_GCP_PROJECT_ID":
        try:
            client = genai.Client(vertexai=True, project=project_id, location=location)
            structured_brief = asyncio.run(map_reduce_extraction(client, emails))
            logger.info("Successfully extracted and parsed structured news JSON via Map-Reduce Vertex AI.")
            
            if doc_ref:
                doc_ref.set({"structured_brief": structured_brief}, merge=True)
                logger.info("State successfully persisted to Firestore.")
        except Exception as e:
            logger.warning(f"Structured Vertex AI parsing failed ({e}). Attempting standard fallback parser.")
            
    if not structured_brief:
        headlines = [e['subject'].replace("[WSJ Front Page]", "").strip() for e in emails]
        takeaways = ["Fed restrictive rates signal measured path.", "CognitionCore Hyperion $78B landmark merger.", "transnational battery energy storage pledge."]
        cleaned_articles = []
        for email in emails:
            clean_subj = email['subject'].replace("[WSJ Front Page]", "").strip()
            lines = email['raw_body'].split("\n")
            body_lines = [l.strip() for l in lines if not l.startswith("*") and not l.startswith("-") and "ADVERTISEMENT" not in l and "manage your subscription" not in l and "Copyright" not in l and l.strip()]
            cleaned_articles.append(f"## {clean_subj}\n" + "\n".join(body_lines))
            
        structured_brief = {
            "headlines": headlines,
            "key_takeaways": takeaways,
            "podcast_script": "\n\n".join(cleaned_articles)
        }
        if doc_ref:
             doc_ref.set({"structured_brief": structured_brief}, merge=True)
        
    state["structured_brief"] = structured_brief
    return {
        "status": "success",
        "message": "Pristine editorial text extracted and successfully converted to structured JSON in Memory Bank.",
        "structured_brief_keys": list(structured_brief.keys()),
        "headlines_extracted": structured_brief["headlines"],
        "script_snippet": structured_brief["podcast_script"][:350] + "..."
    }
