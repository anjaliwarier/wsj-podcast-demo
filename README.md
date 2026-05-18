# 🎙️ Wall Street Journal Front Page Automated Podcast Agent

An enterprise-grade, serverless autonomous agent built natively on the **Gemini Enterprise Agent Platform** using the **Agent Development Kit (ADK)** (`google.adk`) and deployed to the **Vertex AI Agent Runtime (Reasoning Engines)**. 

This agent acts as an expert Google Cloud Architect and Financial AI Producer to autonomously ingest synthetic Wall Street Journal front-page emails, strip promotional boilerplate, generate studio-quality conversational podcast briefings using the **Google Podcast API**, and distribute time-limited secure signed streaming links.

---

## 🏛️ System Architecture & Flow

This diagram outlines the end-to-end flow from ingestion to secure delivery, illustrating the orchestration layer, enterprise storage, and external API integrations.

```mermaid
graph TD
    %% Nodes
    subgraph Client_Interface [Client & Trigger Layer]
        A[User / CLI Client] -->|adk run / stream_query| B(Reasoning Engine Runtime)
    end

    subgraph Enterprise_Agent [Vertex AI Agent Runtime / Reasoning Engines]
        B -->|Tool Call 1| C[Ingest WSJ Bulletins]
        B -->|Tool Call 2| D[Clean Editorial Parser]
        B -->|Tool Call 3| E[Synthesize & Stage]
        
        C -->|Store state| F[(Managed Memory Bank)]
        D -->|Store state| F
        E -->|Store state| F
    end

    subgraph Synthesis_Engine [Generative AI & Media Synthesis Services]
        C -.->|Mock/Live Gmail Ingest| G(Gmail API / Mock Queue)
        D -->|Gemini 2.5 Pro Content Filter| H(Vertex AI GenAI)
        E -->|POST /podcasts:generate| I(NotebookLM Enterprise Podcast API)
    end

    subgraph Storage_Distribution [Storage & Secure Distribution]
        E -->|Stage MP3 Binary| J[(Google Cloud Storage - warier-agents)]
        E -->|HMAC-SHA256 URL Sign| K[GCS Signed URL Generation]
        E -->|SMTP Transport TLS| L[Outgoing Email Notification]
    end

    %% Styles & Classes
    style Enterprise_Agent fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px
    style Synthesis_Engine fill:#f1f8e9,stroke:#33691e,stroke-width:2px
    style Storage_Distribution fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style Client_Interface fill:#ede7f6,stroke:#4a148c,stroke-width:2px
```

### End-to-End Operational Flow
1. **Ingestion**: The agent triggers the `ingest_recent_wsj_emails` tool to retrieve the 5 most recent front-page news items. By default, this leverages our high-fidelity Gemini 2.0 Flash synthetic news generator.
2. **Extraction & Cleaning**: The `parse_clean_journalistic_text` tool invokes a tailored Gemini 2.5 Pro prompt that strips all advertising, email signatures, and headers, leaving strictly core journalistic prose structured as a conversational podcast script.
3. **Audio Generation**: The agent calls the Google Podcast API (`discoveryengine.googleapis.com`) to synthesize a professional, studio-quality conversational MP3 briefing.
4. **Staging & Signing**: The MP3 binary is uploaded to the **`warier-agents`** GCS bucket. The GCS client generates an HMAC-SHA256 time-bounded Signed URL (valid for 7 days) that securely bypasses GCS ACL restrictions.
5. **Dispatch**: A rich HTML email is sent to the subscriber containing the secure signed URL for immediate streaming.

---

## 🛠️ Key Technologies & GCP Services

- **Vertex AI Agent Runtime (Reasoning Engines)**: Serverless execution runtime hosting our ADK agent with managed session-based persistence.
- **Agent Development Kit (`google.adk`)**: The native Google Cloud agent SDK used to bind memory-aware tools to stateful LLM flows.
- **Gemini 2.5 Pro**: Enterprise-tier language model orchestrating deep reasoning, text parsing, and pipeline steps.
- **Gemini 2.0 Flash**: Dynamic high-speed synthesis engine used to generate high-fidelity simulated media.
- **Cloud Storage (`google-cloud-storage`)**: Stages audio files and generates secure, time-bound signed URLs.
- **Cloud Trace & Vertex AI Observability**: Built-in tracing that automatically profiles step latencies and model tokens.

---

## 📂 Directory Structure

```bash
wsj_podcast_demo/
├── README.md                   # System Architecture & Playbook (this file)
├── requirements.txt            # Pinned Python Dependencies
├── .env.example                # Configuration environment template
├── run_pipeline.py             # Demonstration script for local verification
├── deployment/
│   ├── deploy.py               # Deploys ADK Agent as a serverless Reasoning Engine
│   └── test_deployment.py      # CLI client for real-time streaming testing
└── wsj_podcast_agent/
    ├── __init__.py             # Module initialization
    ├── agent.py                # Core ADK Agent & stateful Memory Bank Tools
    ├── services.py             # Content extraction, Podcast REST API, GCS, & SMTP clients
    ├── synthetic_data_generator.py # Gemini 2.0 Flash synthetic news engine
    └── .env                    # Submodule runtime settings
```

---

## 🚀 Quick Start & Execution Playbook

### 1. Local Workspace Setup
```bash
# Copy the environment file
cp .env.example .env

# Install target dependencies
pip install -r requirements.txt
```

Configure the target GCS bucket in your `.env`:
```ini
GOOGLE_CLOUD_STORAGE_BUCKET=warier-agents
```

### 2. Run Local Demonstration Pipeline
Run the full end-to-end flow locally:
```bash
python run_pipeline.py
```

### 3. IAM Setup for Secure GCS URL Signing
Because corporate organizational policies (`constraints/iam.disableServiceAccountKeyCreation`) prevent downloading raw JSON key files, the agent uses secure **keyless Service Account Impersonation** to cryptographically sign GCS URLs.

To enable this in your environment, grant your active CLI user (`admin@anjaliwarier.altostrat.com`) the token creator role on the podcast agent's service account:
```bash
gcloud iam service-accounts add-iam-policy-binding \
    podcast-agent-sa@warier-agents.iam.gserviceaccount.com \
    --member="user:admin@anjaliwarier.altostrat.com" \
    --role="roles/iam.serviceAccountTokenCreator"
```

---

## 🌍 Managed Serverless Cloud Deployment

Deploy your agent directly to the **Vertex AI Agent Runtime** for managed execution.

### Deploy to Reasoning Engines
```bash
python deployment/deploy.py --create
```

### Query the Remote Serverless Session
Once deployed, initiate an interactive, trace-monitored query stream using the returned resource ID:
```bash
python deployment/test_deployment.py --resource_id=<REASONING_ENGINE_RESOURCE_ID>
```
All execution steps, latency, and tool invocations will automatically stream directly into **Google Cloud Trace** and **Vertex AI Observability**!
