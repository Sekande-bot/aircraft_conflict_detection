"""
Decision logic: convert probability of conflict into actionable alerts.
"""

from aircraft import Aircraft, detect_conflict
from uncertainty import probability_of_conflict

def should_alert(prob_conflict, t_closest, alert_strategy="adaptive"):
    """
    Decide whether to alert based on conflict probability and warning time.
    
    Args:
        prob_conflict: probability of conflict (0.0 to 1.0)
        t_closest: time to closest approach in seconds
        alert_strategy: "conservative", "balanced", or "adaptive"
    
    Returns:
        dict with alert decision and reasoning
    """
    if alert_strategy == "conservative":
        # High bar: only alert if very likely
        threshold = 0.20  # 20%
    elif alert_strategy == "balanced":
        # Middle ground
        threshold = 0.10  # 10%
    elif alert_strategy == "adaptive":
        # Adjust threshold based on warning time
        if t_closest > 300:
            threshold = 0.05  # 5% (lots of time to react)
        elif t_closest > 60:
            threshold = 0.10  # 10% (moderate time)
        else:
            threshold = 0.20  # 20% (late alert, need high certainty)
    
    should_alert = prob_conflict > threshold
    
    return {
        'alert': should_alert,
        'prob': prob_conflict,
        't_closest': t_closest,
        'threshold': threshold,
        'reasoning': (
            f"P={prob_conflict*100:.1f}% vs threshold={threshold*100:.0f}% "
            f"(t={t_closest:.0f}s)"
        )
    }


# Test it
test_pairs = [
    ("Head-On", Aircraft("HeadOn_A", 0, 0, 5000, 100, 0, 0),
                Aircraft("HeadOn_B", 50000, 0, 5000, -100, 0, 0)),
    
    ("Crossing", Aircraft("Crossing_A", -5000, 0, 5000, 100, 0, 0),
                 Aircraft("Crossing_B", 0, -5000, 5000, 0, 100, 0)),
    
    ("Close Call", Aircraft("CloseCall_A", 0, 0, 5000, 100, 0, 0),
                   Aircraft("CloseCall_B", 10000, 500, 5100, -80, 0, 0)),
]

print("=" * 100)
print("ALERT DECISION LOGIC")
print("=" * 100)
print()

for test_name, aircraft_a, aircraft_b in test_pairs:
    # Get deterministic result
    det_result = detect_conflict(aircraft_a, aircraft_b)
    t_closest = det_result['t_closest']
    
    # Get probabilistic result
    prob_result = probability_of_conflict(aircraft_a, aircraft_b, samples=1000)
    prob = prob_result['prob_conflict']
    
    print(f"Scenario: {test_name}")
    print(f"  Deterministic: {'CONFLICT' if det_result['conflict'] else 'SAFE'}")
    print(f"  Probabilistic: P = {prob*100:.1f}%")
    print()
    
    # Test each strategy
    for strategy in ["conservative", "balanced", "adaptive"]:
        decision = should_alert(prob, t_closest, alert_strategy=strategy)
        alert_text = "🚨 ALERT" if decision['alert'] else "✓ OK"
        print(f"  {strategy.upper():12s}: {alert_text} ({decision['reasoning']})")
    
    print()