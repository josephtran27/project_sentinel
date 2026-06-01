# Project Sentinel: Autonomous AI SOC Analyst 🛡️

Project Sentinel is an automated, real-time security event triage pipeline. It bridges the gap between raw Security Information and Event Management (SIEM) telemetry and human response teams by using Generative AI to autonomously analyze, index, and notify on critical infrastructure attacks. 

The engine continuously tails a live log source (mimicking a production Wazuh SIEM deployment), extracts context using structured JSON schemas via **Gemini 2.5 Flash Lite**, archives data into a cloud-managed ledger via **Supabase**, and routes high-priority incidents directly to communication hubs via **Slack ChatOps**.

---

## Architecture & Data Flow

```text
[ Live Log Ingestion ] ---> [ AI Triage Agent ] ---> [ Long-Term Ledger ]
    (wazuh_reader)             (Gemini API)               (Supabase DB)
         |                                                      |
         v                                                      v
[ Evaluates Severity ] ---> (If CRITICAL/HIGH) ---> [ ChatOps Incident Response ]
                                                          (Slack Alert)
```

* **Ingestion Engine (`wazuh_reader.py`):** Efficiently tails JSON log streams without memory spikes, acting as a real-time event listener.
* **AI Triage Layer (`triage_agent.py`):** Enforces a strict schema validation layer on LLM outputs via Pydantic to ensure mathematically consistent data structures.
* **Storage Engine (`db/`):** Indexes alerts securely in a PostgreSQL backend leveraging Row Level Security (RLS) bypass via managed server-role tokens.
* **ChatOps Router (`notifier.py`):** Formats raw incident payloads into Slack Block Kit components for asynchronous human response.

---

## Tech Stack

* **Language:** Python 3.11+
* **AI Core:** Google Gemini 2.5 Flash Lite (`google-genai`)
* **Database:** Supabase / PostgreSQL
* **Incident Response:** Slack Webhooks (Block Kit)
* **Configuration:** Python Dotenv & Pydantic Validation

---

## Installation & Setup

### 1. Clone & Environment Setup
```bash
git clone [https://github.com/YOUR_GITHUB_USERNAME/project_sentinel.git](https://github.com/YOUR_GITHUB_USERNAME/project_sentinel.git)
cd project_sentinel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory and populate it with your specific provider credentials:

```env
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase Infrastructure
SUPABASE_URL=[https://your-project-id.supabase.co](https://your-project-id.supabase.co)
SUPABASE_KEY=your_service_role_secret_key_here

# ChatOps Routing
SLACK_WEBHOOK_URL=[https://hooks.slack.com/services/your/webhook/path](https://hooks.slack.com/services/your/webhook/path)
CRITICAL_THRESHOLD=critical,high
```

### 3. Database Schema Provisioning
Execute the following SQL query inside your Supabase SQL Editor to establish the underlying data ledger:

```sql
CREATE TABLE alerts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    wazuh_rule_id INTEGER,
    agent_name TEXT,
    alert_level INTEGER,
    description TEXT,
    full_log JSONB,
    triage_severity TEXT,
    attack_type TEXT,
    mitre_tactic TEXT,
    summary TEXT,
    recommended_action TEXT,
    notified BOOLEAN DEFAULT FALSE,
    suppressed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## Verification & Execution

### Start the Engine
Launch the real-time background listener:
```bash
python main.py
```

### Simulating a Privilege Escalation Attack
In a separate terminal window, execute the following command to append a simulated critical alert event into the monitored target log:

```bash
echo '{"timestamp": "2026-05-29T16:05:00.000+0000", "rule": {"level": 12, "id": "5402", "description": "Successful sudo to ROOT executed", "mitre": {"id": ["T1078"], "tactic": ["Privilege Escalation"]}}, "agent": {"id": "005", "name": "db-server-02", "ip": "10.0.0.50"}, "full_log": "May 29 16:05:00 db-server-02 sudo: jsmith : TTY=pts/0 ; PWD=/home/jsmith ; USER=root ; COMMAND=/bin/bash"}' >> live_wazuh_alerts.json
```

---

## Enterprise Value Add

* **Eliminates Alert Fatigue:** Suppresses lower-tier event noise by processing bulk data dynamically, routing only valid indicators to Slack channels.
* **Reduces MTTR (Mean Time to Respond):** Provides automated operational playbooks, risk assessments, and exact command traces for on-call engineers inside the threat notification card.
