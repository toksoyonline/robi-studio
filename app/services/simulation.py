from datetime import datetime


def run_performance_simulation(input_score: int, scenario: str) -> dict:
    scenario_modifier = min(len(scenario) // 8, 10)
    confidence_boost = 6 if "practice" in scenario.lower() else 2
    predicted_score = min(input_score + scenario_modifier + confidence_boost, 100)

    if predicted_score >= 90:
        feedback = "Outstanding trajectory. Move into advanced challenge tracks."
    elif predicted_score >= 75:
        feedback = "Strong momentum. Reinforce weak topics and take timed simulations."
    elif predicted_score >= 60:
        feedback = "Moderate outcome. Increase guided practice and parent check-ins."
    else:
        feedback = "At-risk profile. Shift to foundation modules and mentoring support."

    return {
        "simulated_score": predicted_score,
        "feedback": feedback,
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }
