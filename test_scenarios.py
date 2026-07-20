"""Test scenarios for conflict detection."""

from aircraft import Aircraft, detect_conflict

# Define test pairs
test_pairs = [
    ("Head-On", Aircraft("HeadOn_A", 0, 0, 5000, 100, 0, 0),
                Aircraft("HeadOn_B", 50000, 0, 5000, -100, 0, 0)),
    
    ("Crossing", Aircraft("Crossing_A", -5000, 0, 5000, 100, 0, 0),
                 Aircraft("Crossing_B", 0, -5000, 5000, 0, 100, 0)),
    
    ("Same Direction", Aircraft("SameDir_A", 0, 0, 5000, 100, 0, 0),
                       Aircraft("SameDir_B", 50000, 1000, 5500, 100, 0, 0)),
    
    ("Clear", Aircraft("Clear_A", 0, 0, 5000, 100, 0, 0),
              Aircraft("Clear_B", 100000, 100000, 10000, 100, 0, 0)),
]

def run_tests():
    """Run all test scenarios and print results."""
    print("=" * 80)
    print("AIRCRAFT CONFLICT DETECTION - TEST RESULTS")
    print("=" * 80)
    print()
    
    for test_name, aircraft_a, aircraft_b in test_pairs:
        result = detect_conflict(aircraft_a, aircraft_b)
        
        print(f"Test: {test_name}")
        print(f"  Aircraft 1: {aircraft_a.name}")
        print(f"  Aircraft 2: {aircraft_b.name}")
        print(f"  Closest approach time: {result['t_closest']:.1f} seconds")
        print(f"  Horizontal separation: {result['min_horiz_dist']:.1f} m")
        print(f"  Vertical separation: {result['min_vert_dist']:.1f} m")
        
        if result['conflict']:
            print(f"  ⚠️  CONFLICT DETECTED!")
        else:
            if 'reason' in result:
                print(f"  ✓ No conflict: {result['reason']}")
            else:
                reasons = []
                if result['min_horiz_dist'] >= 9260:
                    reasons.append(f"horiz {result['min_horiz_dist']:.0f}m >= 9260m")
                if result['min_vert_dist'] >= 305:
                    reasons.append(f"vert {result['min_vert_dist']:.0f}m >= 305m")
                print(f"  ✓ No conflict: {', '.join(reasons)}")
        
        print()

if __name__ == "__main__":
    run_tests()