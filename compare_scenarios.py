"""
Compare brute-force vs exact closest-approach methods.
Validate that they give the same answer (within rounding error).
Measure speed difference.
"""

import time
from aircraft import (
    Aircraft, 
    closest_approach_exact, 
    closest_approach_brute_force
)

# Test scenarios
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

print("=" * 100)
print("BRUTE-FORCE vs EXACT METHOD COMPARISON")
print("=" * 100)
print()

for test_name, aircraft_a, aircraft_b in test_pairs:
    print(f"Test: {test_name}")
    print("-" * 100)
    
    # Exact method
    start = time.time()
    t_exact, dist_exact = closest_approach_exact(aircraft_a, aircraft_b)
    time_exact = time.time() - start
    
    # Brute-force method (dt=1 second)
    start = time.time()
    t_brute, dist_brute = closest_approach_brute_force(aircraft_a, aircraft_b, max_time=600, dt=1)
    time_brute = time.time() - start
    
    # Brute-force with finer resolution (dt=0.1 second)
    start = time.time()
    t_brute_fine, dist_brute_fine = closest_approach_brute_force(aircraft_a, aircraft_b, max_time=600, dt=0.1)
    time_brute_fine = time.time() - start
    
    # Display results
    print(f"  Exact Method:")
    print(f"    t_closest: {t_exact:.2f}s, distance: {dist_exact:.2f}m")
    print(f"    Time: {time_exact*1000:.4f}ms")
    print()
    
    print(f"  Brute-Force (dt=1s):")
    print(f"    t_closest: {t_brute:.2f}s, distance: {dist_brute:.2f}m")
    print(f"    Time: {time_brute*1000:.4f}ms")
    print(f"    Error (time): {abs(t_exact - t_brute):.2f}s")
    print(f"    Error (distance): {abs(dist_exact - dist_brute):.2f}m")
    print()
    
    print(f"  Brute-Force (dt=0.1s):")
    print(f"    t_closest: {t_brute_fine:.2f}s, distance: {dist_brute_fine:.2f}m")
    print(f"    Time: {time_brute_fine*1000:.4f}ms")
    print(f"    Error (time): {abs(t_exact - t_brute_fine):.2f}s")
    print(f"    Error (distance): {abs(dist_exact - dist_brute_fine):.2f}m")
    print()
    
    # Speedup
    speedup_1s = time_brute / time_exact if time_exact > 0 else float('inf')
    speedup_01s = time_brute_fine / time_exact if time_exact > 0 else float('inf')
    print(f"  Speedup (exact vs dt=1s): {speedup_1s:.0f}x")
    print(f"  Speedup (exact vs dt=0.1s): {speedup_01s:.0f}x")
    print()