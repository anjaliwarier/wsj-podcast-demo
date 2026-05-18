# 🎙️ Wall Street Journal Front Page Automated Podcast Agent

An enterprise-grade, serverless autonomous agent built natively on the **Gemini Enterprise Agent Platform** using the **Agent Development Kit (ADK)** (`google.adk`) and deployed to the **Gemini Enterprise Agent Platform Runtime**. 

This agent acts as an Editorial Assistant and Financial AI Producer to autonomously ingest synthetic Wall Street Journal front-page emails, strip promotional boilerplate, generate studio-quality conversational podcast briefings using the **Google Podcast API**, and distribute time-limited secure signed streaming links.

---

## 🏛️ System Architecture & Flow

This diagram outlines the end-to-end flow from ingestion to secure delivery, illustrating the orchestration layer, enterprise storage, and external API integrations.

```mermaid
flowchart TB
    %% Classes & Styles
    classDef agent fill:#e3f2fd,stroke:#0d47a1,stroke-width:1.5px;
    classDef service fill:#f1f8e9,stroke:#33691e,stroke-width:1.5px;
    classDef storage fill:#fff3e0,stroke:#e65100,stroke-width:1.5px;

    %% Node Definitions
    User([User / CLI Client])
    
    subgraph Runtime [Gemini Enterprise Agent Platform Runtime]
        Agent[WSJ Podcast Agent <br> Latest Gemini GA Model]
        Memory[(Memory Bank <br> Session State)]
    end

    subgraph Ingestion [1. Ingestion & Filtering]
        EmailService[Synthetic WSJ Email Generator <br> Latest Gemini GA Model]
        Extractor[Content Filter & Script Creator <br> Latest Gemini GA Model]
    end

    subgraph AudioGen [2. Podcast Production]
        PodcastAPI[Google Podcast API <br> Discovery Engine REST]
    end

    subgraph Distribution [3. Storage & Delivery]
        GCS[(GCS Staging Bucket <br> warier-agents)]
        SignedURL[Secure Signed URL <br> 7-Day Token]
        SMTP[SMTP Email Notification]
    end

    %% Relationships & Flow
    User -->|1. Trigger Session| Agent
    Agent <-->|Manage State| Memory
    
    Agent -->|2. Ingest| EmailService
    EmailService -->|Raw Bulletins| Extractor
    Extractor -->|Clean Editorial Transcript| Agent
    
    Agent -->|3. Synthesize Audio| PodcastAPI
    PodcastAPI -->|MP3 Binary Stream| Agent
    
    Agent -->|4. Stage Binary| GCS
    GCS -->|5. Secure Sign| SignedURL
    Agent -->|6. Send Delivery Email| SMTP
    SignedURL -->|Encrypted Audio Link| SMTP
    SMTP -->|7. Stream Briefing| User

    %% Apply Styling Classes
    class Agent,Memory agent;
    class EmailService,Extractor,PodcastAPI service;
    class GCS,SignedURL,SMTP storage;
```

### End-to-End Operational Flow
1. **Ingestion**: The agent triggers the `ingest_recent_wsj_emails` tool to retrieve the 5 most recent front-page news items. By default, this leverages our high-fidelity simulated news generator powered by the latest Gemini GA model.
2. **Extraction & Cleaning**: The `parse_clean_journalistic_text` tool invokes the latest Gemini GA model to strip all advertising, email signatures, and headers, leaving strictly core journalistic prose structured as a conversational podcast script.
3. **Audio Generation**: The agent calls the Google Podcast API (`discoveryengine.googleapis.com`) to synthesize a professional, studio-quality conversational MP3 briefing.
4. **Staging & Signing**: The MP3 binary is uploaded to the **`warier-agents`** GCS bucket. The GCS client generates an HMAC-SHA256 time-bounded Signed URL (valid for 7 days) that securely bypasses GCS ACL restrictions.
5. **Dispatch**: A rich HTML email is sent to the subscriber containing the secure signed URL for immediate streaming.

---

## 🛠️ Key Technologies & GCP Services

- **Gemini Enterprise Agent Platform Runtime**: Serverless execution runtime hosting our ADK agent with managed session-based persistence.
- **Agent Development Kit (`google.adk`)**: The native Google Cloud agent SDK used to bind memory-aware tools to stateful LLM flows.
- **Latest Gemini GA Model**: Enterprise-tier foundation model orchestrating deep reasoning, text parsing, and pipeline steps.
- **Cloud Storage (`google-cloud-storage`)**: Stages audio files and generates secure, time-bound signed URLs.
- **Cloud Trace & Platform Observability**: Built-in tracing that automatically profiles step latencies and model tokens.

---

## 📂 Directory Structure

```bash
wsj_podcast_demo/
├── README.md                   # System Architecture & Playbook (this file)
├── requirements.txt            # Pinned Python Dependencies
├── .env.example                # Configuration environment template
├── run_pipeline.py             # Demonstration script for local verification
├── deployment/
│   ├── deploy.py               # Deploys ADK Agent as a serverless Runtime Engine
│   └── test_deployment.py      # CLI client for real-time streaming testing
└── wsj_podcast_agent/
    ├── __init__.py             # Module initialization
    ├── agent.py                # Core ADK Agent & stateful Memory Bank Tools
    ├── services.py             # Content extraction, Podcast REST API, GCS, & SMTP clients
    ├── synthetic_data_generator.py # Gemini news engine
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

Deploy your agent directly to the **Gemini Enterprise Agent Platform Runtime** for managed execution.

### Deploy to Runtime Engines
```bash
python deployment/deploy.py --create
```

### Query the Remote Serverless Session
Once deployed, initiate an interactive, trace-monitored query stream using the returned resource ID:
```bash
python deployment/test_deployment.py --resource_id=<RESOURCE_ID>
```
All execution steps, latency, and tool invocations will automatically stream directly into **Google Cloud Trace** and **Platform Observability**!
