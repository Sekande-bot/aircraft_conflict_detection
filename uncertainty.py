"""
Uncertainty modeling: add Gaussian noise to position/velocity.
Compute probability of conflict by Monte Carlo sampling.
"""

import random
import math
from aircraft import Aircraft, detect_conflict, position_at_time

def add_uncertainty(aircraft, pos_std=50, vel_std=1):
    """
    Create a perturbed copy of an aircraft with Gaussian noise.
    
    Args:
        aircraft: Aircraft object
        pos_std: position standard deviation in metres (default 50m = ~±100m bounds)
        vel_std: velocity standard deviation in m/s (default 1 m/s)
    
    Returns:
        Aircraft with noisy position and velocity
    """
    # Add Gaussian noise to position and velocity
    noisy_pos = [
        aircraft.pos[i] + random.gauss(0, pos_std)
        for i in range(3)
    ]
    noisy_vel = [
        aircraft.vel[i] + random.gauss(0, vel_std)
        for i in range(3)
    ]
    
    return Aircraft(
        name=aircraft.name,
        x=noisy_pos[0], y=noisy_pos[1], z=noisy_pos[2],
        vx=noisy_vel[0], vy=noisy_vel[1], vz=noisy_vel[2]
    )


def probability_of_conflict(aircraft_a, aircraft_b, samples=1000, 
                           pos_std=50, vel_std=1, lookahead_time=600):
    """
    Estimate probability of conflict using Monte Carlo sampling.
    
    Logic:
        1. Sample N perturbed versions of each aircraft
        2. For each sample, check if conflict detected
        3. P(conflict) = (conflicts found) / (total samples)
    
    Args:
        aircraft_a, aircraft_b: Aircraft objects (ground truth)
        samples: number of Monte Carlo samples (default 1000)
        pos_std, vel_std: uncertainty parameters
        lookahead_time: seconds to look ahead
    
    Returns:
        dict with conflict probability and details
    """
    conflict_count = 0
    min_horiz_dists = []
    min_vert_dists = []
    
    for _ in range(samples):
        # Create noisy versions
        a_noisy = add_uncertainty(aircraft_a, pos_std=pos_std, vel_std=vel_std)
        b_noisy = add_uncertainty(aircraft_b, pos_std=pos_std, vel_std=vel_std)
        
        # Check for conflict
        result = detect_conflict(a_noisy, b_noisy, lookahead_time=lookahead_time)
        
        if result['conflict']:
            conflict_count += 1
        
        if result['min_horiz_dist'] != float('inf'):
           min_horiz_dists.append(result['min_horiz_dist'])
        if result['min_vert_dist'] != float('inf'):
            min_vert_dists.append(result['min_vert_dist'])
    
    # Compute statistics
    prob_conflict = conflict_count / samples
    avg_horiz_dist = sum(min_horiz_dists) / len(min_horiz_dists)
    avg_vert_dist = sum(min_vert_dists) / len(min_vert_dists)
    
    return {
        'prob_conflict': prob_conflict,
        'conflict_count': conflict_count,
        'avg_horiz_dist': avg_horiz_dist,
        'avg_vert_dist': avg_vert_dist,
        'min_horiz_dist_observed': min(min_horiz_dists),
        'max_horiz_dist_observed': max(min_horiz_dists),
    }


# Test scenarios
test_pairs = [
    ("Head-On", Aircraft("HeadOn_A", 0, 0, 5000, 100, 0, 0),
                Aircraft("HeadOn_B", 50000, 0, 5000, -100, 0, 0)),
    
    ("Crossing", Aircraft("Crossing_A", -5000, 0, 5000, 100, 0, 0),
                 Aircraft("Crossing_B", 0, -5000, 5000, 0, 100, 0)),
    
    ("Same Direction", Aircraft("SameDir_A", 0, 0, 5000, 100, 0, 0),
                       Aircraft("SameDir_B", 50000, 1000, 5500, 100, 0, 0)),
    
    ("Close Call", Aircraft("CloseCall_A", 0, 0, 5000, 100, 0, 0),
                   Aircraft("CloseCall_B", 10000, 500, 5100, -80, 0, 0)),
]

print("=" * 100)
print("UNCERTAINTY MODELING: PROBABILITY OF CONFLICT")
print("=" * 100)
print()

for test_name, aircraft_a, aircraft_b in test_pairs:
    print(f"Scenario: {test_name}")
    print("-" * 100)
    
    # Deterministic result (no uncertainty)
    det_result = detect_conflict(aircraft_a, aircraft_b)
    print(f"  Deterministic (no uncertainty):")
    print(f"    Conflict: {det_result['conflict']}")
    print(f"    Horiz sep: {det_result['min_horiz_dist']:.0f}m, Vert sep: {det_result['min_vert_dist']:.0f}m")
    print()
    
    # Probabilistic result (with uncertainty)
    prob_result = probability_of_conflict(aircraft_a, aircraft_b, samples=1000, 
                                          pos_std=50, vel_std=1)
    print(f"  With uncertainty (pos_std=50m, vel_std=1 m/s, 1000 samples):")
    print(f"    P(conflict): {prob_result['prob_conflict']*100:.2f}%")
    print(f"    Conflicts observed: {prob_result['conflict_count']}/1000")
    print(f"    Avg horiz sep: {prob_result['avg_horiz_dist']:.0f}m")
    print(f"    Avg vert sep: {prob_result['avg_vert_dist']:.0f}m")
    print(f"    Range (horiz): {prob_result['min_horiz_dist_observed']:.0f}m - {prob_result['max_horiz_dist_observed']:.0f}m")
    print()