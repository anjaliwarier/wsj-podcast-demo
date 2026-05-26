import os
import json
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WSJ_Podcast_Runner")

from wsj_podcast_agent.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

async def main():
    print("\n" + "="*80)
    print(" 🚀 INITIALIZING WSJ PODCAST ENTERPRISE AGENT PIPELINE")
    print("="*80)
    
    runner = InMemoryRunner(agent=root_agent, app_name="wsj_podcast_demo")
    
    print(f"\n[+] Active Agent Loaded: '{root_agent.name}'")
    print(f"[+] Target Runtime Foundation Model: '{root_agent.model}'")
    print("[+] Operation Mode: USE_SYNTHETIC_LOCAL_MOCK = True\n")
    
    prompt = "Please retrieve recent WSJ front page emails, parse their core journalistic text, synthesize a podcast via the Google Podcast API, stage it in GCS, and send an email with the signed URL."
    print(f"\n💬 USER REQUEST: \"{prompt}\"\n")
    print("-" * 80)
    print("🤖 AGENT EXECUTION TRAJECTORY (Memory Bank Orchestration):")
    print("-" * 80)

    # We try invoking the full LLM agent runner asynchronously.
    # If the environment lacks live Vertex/Gemini API keys, we seamlessly trigger
    # the exact underlying ADK tools to showcase full end-to-end execution.
    try:
        session = await runner.session_service.create_session(
            app_name=runner.app_name, user_id="gcp_architect_lead"
        )
        content = types.Content(parts=[types.Part(text=prompt)])
        
        got_response = False
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content,
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text, end="", flush=True)
                        got_response = True
                        
        if got_response:
            print("\n\n" + "="*80)
            print(" 🎉 FULL PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
            print("="*80)
            return
    except Exception as e:
        logger.warning(f"InMemoryRunner LLM invocation skipped due to runtime API authentication/model mapping: {e}. Executing explicit deterministic ADK Tool sequence.")
        return False
    return True

def run_sync_fallback():
    # -------------------------------------------------------------------------
    # Step-by-step ADK Tool Chain simulation for 100% reliable local demonstration
    # -------------------------------------------------------------------------
    class DummyToolContext:
        def __init__(self):
            self.state = {}
            
    tool_context = DummyToolContext()
    
    from wsj_podcast_agent.agent import (
        ingest_firestore_emails,
        parse_clean_journalistic_text,
        produce_and_distribute_podcast
    )
    
    print("\n⚡ [Tool Call 1] ingest_firestore_emails(tool_context)...")
    res1 = ingest_firestore_emails(tool_context)
    print(json.dumps(res1, indent=2))
    
    print("\n⚡ [Tool Call 2] parse_clean_journalistic_text(tool_context)...")
    res2 = parse_clean_journalistic_text(tool_context)
    print(json.dumps(res2, indent=2))
    
    print("\n⚡ [Tool Call 3] produce_and_distribute_podcast(tool_context)...")
    res3 = produce_and_distribute_podcast(tool_context)
    print(json.dumps(res3, indent=2))
    
    print("\n" + "="*80)
    print(" 🎉 ENTERPRISE ADK AGENT PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"🔒 Secure Signed URL (7-Day Expiry): {res3['secure_signed_url']}")
    print(f"📁 Staged Binary GCS Target: {res3['podcast_storage_uri']}")
    print(f"📧 Transmission Mode: {res3['email_dispatched_metadata']['mode']}")
    print("="*80 + "\n")

if __name__ == "__main__":
    success = asyncio.run(main())
    if not success:
        run_sync_fallback()
