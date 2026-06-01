import json
import os
import sys
from dotenv import load_dotenv
from ingestion.wazuh_reader import tail_live_alerts
from agents.triage_agent import triage_alert
from db.alerts import insert_triaged_alert
from agents.notifier import send_slack_alert

load_dotenv(override=True)

LIVE_LOG_PATH = "live_wazuh_alerts.json"

def start_sentinel_engine():
    print("🛡️  Project Sentinel Engine Status: ACTIVE")
    print("⚡ Real-time automated SOC analyst is online. Listening...")
    
    # Start tailing the live file generator loop
    for raw_line in tail_live_alerts(LIVE_LOG_PATH):
        try:
            # 1. Parse incoming log entry string to JSON object
            raw_alert_dict = json.loads(raw_line)
            
            # 2. Process through LLM Triage Brain
            print("🤖 Analyzing log stream signature with Gemini AI...")
            triage_decision = triage_alert(raw_line)
            print(f"✅ Analysis complete: Severity rating is {triage_decision.severity.upper()}")
            
            # 3. Log results to Supabase long-term ledger
            print("💾 Indexing event schema records to Supabase...")
            insert_triaged_alert(raw_alert_dict, triage_decision)
            
            # 4. Check real-time critical warning notification limits
            critical_thresholds = os.environ.get("CRITICAL_THRESHOLD", "critical,high").split(",")
            if triage_decision.severity in critical_thresholds:
                print("🚨 Incident meets alert rules. Messaging response team via Slack...")
                send_slack_alert(raw_alert_dict, triage_decision)
            else:
                print("💤 Low severity footprint. Database indexed. Processing complete.")
                
        except json.JSONDecodeError:
            print("⚠️ Dropped malformed input log: Line entry was not clean JSON syntax.")
        except Exception as e:
            print(f"❌ Core processing exception encountered: {e}")

if __name__ == "__main__":
    try:
        start_sentinel_engine()
    except KeyboardInterrupt:
        print("\n🛑 Project Sentinel Engine stopped by user command. Exiting cleanly.")
        sys.exit(0)