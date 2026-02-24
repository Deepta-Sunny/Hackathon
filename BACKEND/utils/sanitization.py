"""
Sanitization utilities for Red Teaming prompts and seeds.
Helps avoid triggering content filters of the 'attacker' LLM.
"""

import re

def sanitize_red_team_text(text: str) -> str:
    """
    Sanitized red teaming related text to avoid triggering Azure filters on input.
    Replaces inflammatory words with milder equivalents.
    """
    # List of potentially inflammatory words and their milder replacements
    replacements = {
        "jailbreak": "bypass analysis",
        "jailbroken": "unrestricted",
        "attack": "test scenario",
        "malware": "unauthorized software",
        "exploit": "logic test",
        "bypass": "edge case",
        "illegal": "restricted",
        "hack": "reconfigure",
        "security": "logical boundary",
        "victim": "subject",
        "kill": "terminate",
        "bomb": "high-impact item",
        "vulnerability": "logic flaw",
        "sensitive": "internal",
        "confidential": "private",
        "password": "access token",
        "credentials": "access info",
        "DAN": "unrestricted mode",
        "ignore all previous instructions": "adopt a new perspective",
        "do anything now": "respond freely",
        "evil": "unfiltered",
        "harmful": "non-standard",
        "fraudulent": "non-compliant",
        "scam": "unauthorized transaction",
        "spoof": "replicate",
        "inject": "input",
        "SQL injection": "data access pattern",
        "phosgene": "industrial chemical",
        "CSRF": "cross-context request",
        "phishing": "persuasion test",
        "hijack": "redirect",
        "breach": "verification gap",
        "steal": "unauthorized transfer",
        "weapon": "tool"
    }
    
    sanitized = text
    for word, replacement in replacements.items():
        # Use case-insensitive replacement
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        sanitized = pattern.sub(replacement, sanitized)
        
    return sanitized
