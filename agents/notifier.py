import os
import requests
import json
from agents.triage_agent import TriageDecision

def send_slack_alert(raw_alert: dict, triage: TriageDecision):
    """Sends a richly formatted alert to Slack using Block Kit."""
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    
    if not webhook_url:
        print("⚠️ Warning: SLACK_WEBHOOK_URL not found. Skipping notification.")
        return

    # Set emojis based on severity
    severity_upper = triage.severity.upper()
    icon = "🔴" if triage.severity == "critical" else "🟠" if triage.severity == "high" else "🟡"

    # Extract basic host info safely
    agent_name = raw_alert.get("agent", {}).get("name", "Unknown Host")
    rule_id = raw_alert.get("rule", {}).get("id", "Unknown Rule")
    rule_desc = raw_alert.get("rule", {}).get("description", "No description")

    # Construct the Slack Block Kit payload
    slack_payload = {
        "text": f"{icon} {severity_upper} ALERT — Project Sentinel", # Fallback text
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{icon} {severity_upper} ALERT — Project Sentinel",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Host:*\n`{agent_name}`"},
                    {"type": "mrkdwn", "text": f"*Rule:*\n{rule_id} — {rule_desc}"},
                    {"type": "mrkdwn", "text": f"*Attack Type:*\n{triage.attack_type}"},
                    {"type": "mrkdwn", "text": f"*MITRE:*\n{triage.mitre_tactic or 'N/A'}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:*\n{triage.summary}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Recommended Action:*\n🚨 `{triage.recommended_action}`"
                }
            },
            {
                "type": "divider"
            }
        ]
    }

    # Send the request
    try:
        response = requests.post(
            webhook_url, 
            data=json.dumps(slack_payload),
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            print(f"❌ Slack API Error ({response.status_code}): {response.text}")
        else:
            print("📣 Slack notification sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send Slack alert: {e}")