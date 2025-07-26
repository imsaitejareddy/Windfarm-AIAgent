import numpy as np

def _get_agent_decision(prompt: str) -> str:
    if "Attack detected: True" in prompt:
        return "INCREASE RISK"
    
    return "MAINTAIN BASELINE RISK"


def get_risk_parameter(
    detection: bool,
    power: float,
    stress: float,
    omega_base: float,
    omega_attack: float
) -> float:
    prompt = (
        f"Analyze the following wind farm state and determine the appropriate risk level.\n"
        f"System State:\n"
        f"- Attack detected: {detection}\n"
        f"- Current Power: {power:,.0f} W\n"
        f"- Current Stress Proxy: {stress:.2f}\n"
    )

    decision = _get_agent_decision(prompt)

    if decision == "INCREASE RISK":
        return omega_attack
    else:
        return omega_base