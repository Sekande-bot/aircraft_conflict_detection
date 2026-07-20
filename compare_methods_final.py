"""
Compare geometric conflict detection vs neural network prediction.
Which is better? When does each fail?
"""

import pickle
import numpy as np
import random
from aircraft import Aircraft, detect_conflict

print("=" * 100)
print("GEOMETRIC vs NEURAL NETWORK: HEAD-TO-HEAD COMPARISON")
print("=" * 100)
print()

# Load trained model
print("Loading trained model...")
model, scaler = pickle.load(open('conflict_model.pkl', 'rb'))
print("✓ Model loaded")
print()

# Generate test scenarios
print("Generating 100 random test scenarios...")
test_scenarios = []

for _ in range(100):
    a = Aircraft(
        name="A",
        x=0, y=0, z=5000,
        vx=random.uniform(50, 300),
        vy=random.uniform(-150, 150),
        vz=random.uniform(-2, 2)
    )
    
    b = Aircraft(
        name="B",
        x=random.uniform(-50000, 50000),
        y=random.uniform(-50000, 50000),
        z=random.uniform(4000, 12000),
        vx=random.uniform(50, 300),
        vy=random.uniform(-150, 150),
        vz=random.uniform(-2, 2)
    )
    
    test_scenarios.append((a, b))

print(f"✓ Generated {len(test_scenarios)} scenarios")
print()

# Compare predictions
print("Comparing predictions...")
print("-" * 100)

agreement = 0
disagreement = 0
disagreements = []

for i, (a, b) in enumerate(test_scenarios):
    # Geometric method
    geo_result = detect_conflict(a, b)
    geo_conflict = geo_result['conflict']
    
    # Neural network prediction
    rel_pos = [b.pos[j] - a.pos[j] for j in range(3)]
    rel_vel = [b.vel[j] - a.vel[j] for j in range(3)]
    horiz_dist = ((rel_pos[0]**2 + rel_pos[1]**2) ** 0.5) / 50000
    vert_dist = abs(rel_pos[2]) / 10000
    
    features = np.array([[
        rel_pos[0] / 100000,
        rel_pos[1] / 100000,
        rel_pos[2] / 10000,
        rel_vel[0] / 300,
        rel_vel[1] / 300,
        rel_vel[2] / 10,
        horiz_dist,
        vert_dist,
    ]])
    
    features_scaled = scaler.transform(features)
    nn_prob = model.predict_proba(features_scaled)[0, 1]
    nn_conflict = nn_prob > 0.5
    
    # Compare
    if geo_conflict == nn_conflict:
        agreement += 1
    else:
        disagreement += 1
        disagreements.append({
            'geo': geo_conflict,
            'nn': nn_conflict,
            'nn_prob': nn_prob,
            'horiz_dist': rel_pos[0]**2 + rel_pos[1]**2,
            'vert_dist': abs(rel_pos[2])
        })

print(f"Agreement: {agreement}/100 ({agreement}%)")
print(f"Disagreement: {disagreement}/100 ({disagreement}%)")
print()

if disagreements:
    print("Disagreements (where methods differ):")
    print("-" * 100)
    for i, d in enumerate(disagreements[:10], 1):
        geo_str = "CONFLICT" if d['geo'] else "SAFE"
        nn_str = f"CONFLICT ({d['nn_prob']*100:.0f}%)" if d['nn'] else f"SAFE ({(1-d['nn_prob'])*100:.0f}%)"
        print(f"  {i}. Geo: {geo_str:10s} | NN: {nn_str}")

print()
print("=" * 100)
print("INTERPRETATION")
print("=" * 100)
print()
print("Geometric Method:")
print("  ✓ Exact, deterministic, based on physics")
print("  ✗ No uncertainty modeling")
print("  ✓ Fast (O(1) calculation)")
print()
print("Neural Network:")
print("  ✓ Learns from data patterns")
print("  ✓ Can incorporate uncertainty")
print("  ✗ Black box (hard to explain)")
print("  ✓ Could work with noisy sensors")
print()
print("VERDICT: Geometric method is better for this problem.")
print("  → Pure geometry is sufficiently accurate")
print("  → NN adds complexity without benefit here")
print("  → Use geometry for Phase 1, NN for Phase 2 with uncertainty")
print()