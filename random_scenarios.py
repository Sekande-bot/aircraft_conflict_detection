"""
Generate random aircraft scenarios and detect conflicts at scale.
Tests the detector's performance on many pairs.
"""

import random
from aircraft import Aircraft, detect_conflict

def generate_random_aircraft(count=50, seed=42):
    """
    Generate random aircraft with realistic parameters.
    
    Args:
        count: number of aircraft to generate
        seed: random seed for reproducibility
    
    Returns:
        list of Aircraft objects
    """
    random.seed(seed)
    aircraft = []
    
    for i in range(count):
        # Random position (within 200km x 200km airspace)
        x = random.uniform(-100000, 100000)
        y = random.uniform(-100000, 100000)
        z = random.uniform(5000, 12000)  # Realistic cruise altitudes
        
        # Random velocity (100-300 m/s, realistic cruise speed)
        speed = random.uniform(100, 300)
        # Random direction (angle in radians)
        angle = random.uniform(0, 2 * 3.14159)
        vx = speed * (angle ** 0.5) * random.choice([-1, 1])
        vy = speed * (1 - angle ** 0.5) * random.choice([-1, 1])
        vz = random.uniform(-1, 1)  # Slight climb/descent
        
        aircraft.append(Aircraft(
            name=f"Flight_{i:03d}",
            x=x, y=y, z=z,
            vx=vx, vy=vy, vz=vz
        ))
    
    return aircraft


def detect_conflicts_bulk(aircraft_list, lookahead_time=600):
    """
    Run conflict detection on all pairs of aircraft.
    
    Args:
        aircraft_list: list of Aircraft objects
        lookahead_time: seconds to look ahead
    
    Returns:
        dict with conflict statistics
    """
    conflicts = []
    total_pairs = 0
    
    # Check all pairs (avoiding duplicates)
    for i in range(len(aircraft_list)):
        for j in range(i + 1, len(aircraft_list)):
            total_pairs += 1
            result = detect_conflict(
                aircraft_list[i], 
                aircraft_list[j], 
                lookahead_time=lookahead_time
            )
            
            if result['conflict']:
                conflicts.append({
                    'a': aircraft_list[i].name,
                    'b': aircraft_list[j].name,
                    't_closest': result['t_closest'],
                    'horiz_dist': result['min_horiz_dist'],
                    'vert_dist': result['min_vert_dist'],
                })
    
    return {
        'total_pairs': total_pairs,
        'conflicts': conflicts,
        'conflict_count': len(conflicts),
        'conflict_rate': len(conflicts) / total_pairs if total_pairs > 0 else 0,
    }


# Generate scenarios at different scales
print("=" * 100)
print("RANDOM SCENARIO GENERATION & BULK CONFLICT DETECTION")
print("=" * 100)
print()

for aircraft_count in [10, 20, 50]:
    print(f"Scenario: {aircraft_count} random aircraft")
    print("-" * 100)
    
    # Generate aircraft
    aircraft_list = generate_random_aircraft(count=aircraft_count)
    
    # Detect conflicts
    stats = detect_conflicts_bulk(aircraft_list)
    
    # Print results
    print(f"  Total pairs checked: {stats['total_pairs']}")
    print(f"  Conflicts found: {stats['conflict_count']}")
    print(f"  Conflict rate: {stats['conflict_rate']*100:.2f}%")
    print()
    
    # Show top 5 conflicts (closest approach time)
    if stats['conflicts']:
        sorted_conflicts = sorted(stats['conflicts'], key=lambda x: x['t_closest'])
        print(f"  Top {min(5, len(stats['conflicts']))} conflicts (by time to collision):")
        for idx, conflict in enumerate(sorted_conflicts[:5], 1):
            print(f"    {idx}. {conflict['a']} <-> {conflict['b']}")
            print(f"       Time to collision: {conflict['t_closest']:.1f}s")
            print(f"       Horiz sep: {conflict['horiz_dist']:.0f}m, Vert sep: {conflict['vert_dist']:.0f}m")
    else:
        print(f"  No conflicts detected (lucky!)")
    
    print()

print("=" * 100)