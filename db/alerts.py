from db.supabase_client import get_supabase_client
from agents.triage_agent import TriageDecision

def insert_triaged_alert(raw_alert: dict, triage: TriageDecision, suppressed: bool = False) -> dict:
    """
    Inserts a completely triaged alert record directly into the Supabase alerts table.
    """
    supabase = get_supabase_client()
    
    # Extract native data fields safely from the raw Wazuh structure
    rule_data = raw_alert.get("rule", {})
    agent_data = raw_alert.get("agent", {})
    
    payload = {
        "wazuh_rule_id": int(rule_data.get("id", 0)) if rule_data.get("id") else None,
        "agent_name": agent_data.get("name", "unknown"),
        "alert_level": int(rule_data.get("level", 0)) if rule_data.get("level") else None,
        "description": rule_data.get("description", ""),
        "full_log": raw_alert,  # Saves the whole raw json object to JSONB column
        "triage_severity": triage.severity,
        "attack_type": triage.attack_type,
        "mitre_tactic": triage.mitre_tactic,
        "summary": triage.summary,
        "recommended_action": triage.recommended_action,
        "suppressed": suppressed,
        "notified": False  # Will be flipped to True by the notification worker
    }
    
    # Execute the insert request
    response = supabase.table("alerts").insert(payload).execute()
    return response.data