"""
Avoidance logic: given a conflict, find the minimum altitude change to avoid it.
"""

from aircraft import Aircraft, position_at_time, detect_conflict
import math

def find_min_altitude_change(aircraft_a, aircraft_b, lookahead_time=600):
    """
    Find the minimum altitude change for aircraft_a to avoid conflict with aircraft_b.
    
    Strategy: adjust aircraft_a's altitude (keep position/velocity otherwise same)
    and find the altitude that just barely avoids the horizontal threshold.
    
    Args:
        aircraft_a: Aircraft to adjust (will change altitude only)
        aircraft_b: Aircraft to avoid (stays fixed)
        lookahead_time: seconds to look ahead
    
    Returns:
        dict with avoidance strategy
    """
    
    # Current conflict status
    current_result = detect_conflict(aircraft_a, aircraft_b, lookahead_time)
    
    if not current_result['conflict']:
        return {
            'current_conflict': False,
            'min_altitude_change': 0,
            'strategy': 'No conflict detected'
        }
    
    # Get positions at closest approach
    t_closest = current_result['t_closest']
    pos_a = position_at_time(aircraft_a, t_closest)
    pos_b = position_at_time(aircraft_b, t_closest)
    
    # Current separation
    horiz_dist = math.sqrt((pos_b[0] - pos_a[0])**2 + (pos_b[1] - pos_a[1])**2)
    vert_threshold = 305  # 1000 ft
    
    # If we're within horizontal threshold, we need altitude change
    if horiz_dist < 9260:
        # Required vertical separation to avoid conflict
        required_vert_sep = vert_threshold + 1  # Just over threshold
        current_vert_sep = abs(pos_b[2] - pos_a[2])
        
        # How much altitude change needed?
        altitude_change_needed = required_vert_sep - current_vert_sep
        
        # Split the burden (A climbs half, B descends half)
        # For simplicity, we just have A climb
        altitude_adjustment = max(0, altitude_change_needed)
        
        return {
            'current_conflict': True,
            'horiz_dist': horiz_dist,
            'current_vert_sep': current_vert_sep,
            'required_vert_sep': required_vert_sep,
            'min_altitude_change': altitude_adjustment,
            'strategy': f"Aircraft {aircraft_a.name} should climb {altitude_adjustment:.0f}m to maintain separation"
        }
    
    return {
        'current_conflict': False,
        'min_altitude_change': 0,
        'strategy': 'Horizontal separation is sufficient'
    }


# Test scenarios
test_pairs = [
    ("Head-On", Aircraft("HeadOn_A", 0, 0, 5000, 100, 0, 0),
                Aircraft("HeadOn_B", 50000, 0, 5000, -100, 0, 0)),
    
    ("Crossing", Aircraft("Crossing_A", -5000, 0, 5000, 100, 0, 0),
                 Aircraft("Crossing_B", 0, -5000, 5000, 0, 100, 0)),
    
    ("Close Call", Aircraft("CloseCall_A", 0, 0, 5000, 100, 0, 0),
                   Aircraft("CloseCall_B", 10000, 500, 5100, -80, 0, 0)),
]

print("=" * 100)
print("AVOIDANCE LOGIC: MINIMUM ALTITUDE CHANGE TO AVOID CONFLICT")
print("=" * 100)
print()

for test_name, aircraft_a, aircraft_b in test_pairs:
    result = find_min_altitude_change(aircraft_a, aircraft_b)
    
    print(f"Scenario: {test_name}")
    print(f"  Current conflict: {result['current_conflict']}")
    
    if result['current_conflict']:
        print(f"  Horizontal distance: {result['horiz_dist']:.0f}m")
        print(f"  Current vertical separation: {result['current_vert_sep']:.0f}m")
        print(f"  Required vertical separation: {result['required_vert_sep']:.0f}m")
        print(f"  ➜ {result['strategy']}")
    else:
        print(f"  ➜ {result['strategy']}")
    
    print()