import os
import json
import logging
import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

def generate_synthetic_wsj_emails() -> list[dict]:
    """
    Leverages Google GenAI (Gemini 2.0 Flash) to dynamically synthesize 5 realistic
    Wall Street Journal front-page email bulletins complete with headers, footers,
    and simulated journalistic prose.
    """
    logger.info("Generating synthetic WSJ front-page email bulletins...")
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    prompt = """
    You are an expert financial news editor for the Wall Street Journal. 
    Synthesize exactly 5 distinct front-page feature story emails as received by a subscriber.
    Cover the following strategic macro themes:
    1. US Federal Reserve Interest Rate strategy and inflation expectations.
    2. Large-scale enterprise technology merger / acquisition in the generative AI sector.
    3. Global energy markets shift towards renewable grid transformation.
    4. Major multinational corporate quarterly earnings beat and forward valuation adjustments.
    5. Geopolitical trade corridor adjustments impacting global supply chain logistics.

    Each item in the output JSON array must be an object containing:
    - "email_id": Unique identifier string (e.g., "wsj_summary_001").
    - "sender": "wsj_frontpage@dowjones.internal.wsj.com"
    - "timestamp": ISO-8601 formatted timestamp string representing current financial news hour.
    - "subject": Email subject starting with '[WSJ Front Page] ...'
    - "raw_body": Full email text containing simulated advertising headers, copyright footers, subscription management disclaimers, and the core journalistic article.

    Return ONLY a valid JSON array of objects with the exact keys listed above. Do not include markdown formatting or code block syntax.
    """
    
    if genai and project_id and project_id != "YOUR_GCP_PROJECT_ID":
        try:
            client = genai.Client(vertexai=True, project=project_id, location=location)
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            data = json.loads(response.text)
            logger.info("Successfully generated synthetic WSJ bulletins via Vertex AI Gemini.")
            return data
        except Exception as e:
            logger.warning(f"Vertex AI GenAI generation failed ({e}). Attempting fallback to standard GenAI Client...")
            try:
                client = genai.Client()
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        response_mime_type="application/json"
                    )
                )
                data = json.loads(response.text)
                logger.info("Successfully generated synthetic WSJ bulletins via Google GenAI.")
                return data
            except Exception as ex:
                logger.warning(f"Standard GenAI Client also failed ({ex}). Using deterministic local enterprise mock fallback.")
    else:
        logger.warning("Google GenAI SDK or GOOGLE_CLOUD_PROJECT not configured. Using deterministic local enterprise mock fallback.")
        
    return _fallback_wsj_synthetic_data()


def _fallback_wsj_synthetic_data() -> list[dict]:
    """Returns absolute top-quality deterministic synthetic data mimicking WSJ emails."""
    base_time = datetime.datetime.now(datetime.timezone.utc)
    
    return [
        {
            "email_id": "wsj_summary_001",
            "sender": "wsj_frontpage@dowjones.internal.wsj.com",
            "timestamp": (base_time - datetime.timedelta(hours=4)).isoformat(),
            "subject": "[WSJ Front Page] Federal Reserve Signals Measured Disinflation Path Amid Stubborn Labor Metrics",
            "raw_body": (
                "************************************************************\n"
                "ADVERTISEMENT: Open a Premier High-Yield Checking Trust Account today!\n"
                "************************************************************\n\n"
                "WASHINGTON — Federal Reserve officials indicated they are preparing to maintain benchmark interest rates near twenty-year highs for an extended duration, signaling that renewed economic resiliency and persistent services inflation could necessitate a prolonged restrictive monetary posture.\n\n"
                "In a highly anticipated post-symposium declaration, policymakers emphasized that while labor equilibrium has improved, corporate earnings stability and consumer purchasing power remain exceptionally robust. 'We are navigating an economy that continually outperforms restrictive models,' stated leading economists. Analysts across Wall Street immediately recalibrated forward bond yields, expecting terminal rate cuts to shift well into the next fiscal calendar.\n\n"
                "------------------------------------------------------------\n"
                "To manage your subscription or unsubscribe, visit wsj.com/account/prefs.\n"
                "Copyright ©2026 Dow Jones & Company, Inc. All Rights Reserved.\n"
            )
        },
        {
            "email_id": "wsj_summary_002",
            "sender": "wsj_frontpage@dowjones.internal.wsj.com",
            "timestamp": (base_time - datetime.timedelta(hours=3)).isoformat(),
            "subject": "[WSJ Front Page] Multibillion-Dollar AI Consolidation: CognitionCore Finalizes Landmark Hyperion Merger",
            "raw_body": (
                "************************************************************\n"
                "ADVERTISEMENT: Secure Enterprise Architecture Managed Services with CoreSECURE\n"
                "************************************************************\n\n"
                "SAN FRANCISCO — In an epochal shift for the enterprise software landscape, autonomous AI pioneer CognitionCore has formalized an acquisition agreement for infrastructure powerhouse Hyperion Systems, valuing the combined enterprise entity at an astronomical $78 billion.\n\n"
                "The definitive merger pact unites hyperscale GPU orchestration networks with advanced multi-modal agent frameworks. Corporate executives project that the unified platform will reduce model inference latencies across cloud environments by over fifty percent, establishing an unchallenged global operational monopoly across Fortune 500 digital transformations.\n\n"
                "------------------------------------------------------------\n"
                "To manage your subscription or unsubscribe, visit wsj.com/account/prefs.\n"
                "Copyright ©2026 Dow Jones & Company, Inc. All Rights Reserved.\n"
            )
        },
        {
            "email_id": "wsj_summary_003",
            "sender": "wsj_frontpage@dowjones.internal.wsj.com",
            "timestamp": (base_time - datetime.timedelta(hours=2)).isoformat(),
            "subject": "[WSJ Front Page] Global Grid Renaissance: European & North American Utilities Commit $400B to Next-Gen Storage",
            "raw_body": (
                "************************************************************\n"
                "ADVERTISEMENT: Global Asset Management Strategies - Discover the Alpha Edge\n"
                "************************************************************\n\n"
                "LONDON — A transnational consortium of utility operations and sovereign capital funds has formally pledged over $400 billion toward rapid buildouts of industrial utility-scale long-duration energy storage systems over the next half-decade.\n\n"
                "Faced with extreme intermittent supply surges from offshore wind arrays and expanded solar installations, regional transmission authorities are investing aggressively in heavy grid infrastructure to stabilize grid frequencies. Energy sector equity valuations surged on the announcement, positioning specialized battery engineering firms for unprecedented secular growth.\n\n"
                "------------------------------------------------------------\n"
                "To manage your subscription or unsubscribe, visit wsj.com/account/prefs.\n"
                "Copyright ©2026 Dow Jones & Company, Inc. All Rights Reserved.\n"
            )
        },
        {
            "email_id": "wsj_summary_004",
            "sender": "wsj_frontpage@dowjones.internal.wsj.com",
            "timestamp": (base_time - datetime.timedelta(hours=1)).isoformat(),
            "subject": "[WSJ Front Page] Mega-Cap Earnings Resurgence: Retail Corporate Balance Sheets Outperform Inflation Pressures",
            "raw_body": (
                "************************************************************\n"
                "ADVERTISEMENT: Elite Executive Corporate Charter Card Membership\n"
                "************************************************************\n\n"
                "NEW YORK — Defying sustained pricing inflation and compressed margins, global top-tier commercial retailers reported extraordinary gross volume expansion across their fiscal first-quarter reporting filings this morning.\n\n"
                "Optimized corporate inventory logistics and sophisticated artificial intelligence pricing algorithms allowed commercial leadership to offset input wage expansions. Gross operating efficiency jumped to record margins, igniting a broader intraday rally across global stock indices and reinforcing underlying consumer market resilience.\n\n"
                "------------------------------------------------------------\n"
                "To manage your subscription or unsubscribe, visit wsj.com/account/prefs.\n"
                "Copyright ©2026 Dow Jones & Company, Inc. All Rights Reserved.\n"
            )
        },
        {
            "email_id": "wsj_summary_005",
            "sender": "wsj_frontpage@dowjones.internal.wsj.com",
            "timestamp": base_time.isoformat(),
            "subject": "[WSJ Front Page] Geopolitical Logistics Restructuring: Marine Fleet Reroutes Shift Hub Capacity to Alternative Corridors",
            "raw_body": (
                "************************************************************\n"
                "ADVERTISEMENT: Institutional Equity Trading Terminals & Low-Latency Feeds\n"
                "************************************************************\n\n"
                "SINGAPORE — Leading international merchant fleets have initiated permanent route revisions across vital oceanic trade pathways, shifting primary docking and transshipment hub capacity toward stabilized maritime corridors across Southeast Asia and the southern capes.\n\n"
                "While transcontinental transit intervals have expanded by several market days, consolidated ocean freight alliances have successfully established secondary feeder ports, insulating corporate balance sheets from unheralded tariff disruptions and securing critical semiconductor delivery pipelines worldwide.\n\n"
                "------------------------------------------------------------\n"
                "To manage your subscription or unsubscribe, visit wsj.com/account/prefs.\n"
                "Copyright ©2026 Dow Jones & Company, Inc. All Rights Reserved.\n"
            )
        }
    ]

if __name__ == "__main__":
    bulletins = generate_synthetic_wsj_emails()
    print(json.dumps(bulletins, indent=2))
