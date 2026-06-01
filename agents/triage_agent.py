import os
from typing import Literal, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()

# Define the strict schema required by your spec
class TriageDecision(BaseModel):
    severity: Literal["critical", "high", "medium", "low", "noise"]
    attack_type: Literal[
        "brute_force", "privilege_escalation", "lateral_movement", 
        "data_exfiltration", "malware", "recon", "policy_violation", 
        "false_positive", "unknown"
    ]
    mitre_tactic: Optional[str] = Field(description="The most relevant MITRE ATT&CK tactic ID (e.g., TA0006) or null")
    summary: str = Field(description="A clear 2-3 sentence plain-English explanation of what happened.")
    recommended_action: str = Field(description="Exactly 1 sentence detailing what the security analyst should execute next.")

def triage_alert(raw_alert_json: str) -> TriageDecision:
    """Sends raw alert data to Gemini 2.5 Flash Lite and returns a structured object."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY in environment variables.")

    # Initialize the official Google GenAI Client
    client = genai.Client(api_key=api_key)

    system_instruction = (
        "You are a Senior SOC analyst AI assistant working in a federal contractor environment. "
        "Your role is to triage Wazuh SIEM alerts with extreme accuracy. Be conservative — when in doubt, "
        "escalate the severity rather than suppressing it. Federal infrastructure has zero-tolerance "
        "for undetected critical infrastructure threats."
    )

    # Use gemini-2.5-flash-lite as specified for low cost and high speed
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"Please analyze this raw SIEM alert payload:\n\n{raw_alert_json}",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=TriageDecision,
            temperature=0.1,  # Low temperature for deterministic evaluation
        ),
    )

    # The SDK automatically handles the parsing constraint via response_schema
    return TriageDecision.model_validate_json(response.text)

# Local test runner
if __name__ == "__main__":
    import json
    
    print("Reading local mock alert payload...")
    try:
        with open("local_test_alerts.json", "r") as f:
            sample_data = f.read()
            
        print("Sending to Gemini 2.5 Flash Lite for evaluation...")
        result = triage_alert(sample_data)
        
        print("\n=== TRIAGE RESULT ===")
        print(json.dumps(result.model_dump(), indent=2))
        
    except FileNotFoundError:
        print("❌ Error: local_test_alerts.json file not found.")
    except Exception as e:
        print(f"❌ Execution failed: {e}")