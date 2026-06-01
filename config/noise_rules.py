# Pre-LLM rules filter configuration matrix

NOISE_RULES = [
    {"rule_id": 5706, "reason": "SSH disconnect (normal)"},
    {"rule_id": 5715, "reason": "SSH login success (expected)"},
    {"rule_id": 31530, "reason": "Google crawler (expected web traffic)"},
    {"rule_id": 31531, "reason": "Google crawler (expected web traffic)"},
]

NOISE_AGENTS = []        # Hostnames to completely drop (e.g., local sandbox boxes)
NOISE_LEVEL_MAX = 3      # Wazuh raw alert levels 3 and below are automatically skipped