"""
Visualize aircraft trajectories and conflict zones.
Creates 2D plots showing aircraft paths, closest approach, and conflict radii.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from aircraft import Aircraft, position_at_time, detect_conflict

def plot_scenario(test_name, aircraft_a, aircraft_b, max_time=600):
    """
    Plot a single scenario: trajectories, positions, conflict radius.
    
    Args:
        test_name: name of the scenario
        aircraft_a, aircraft_b: Aircraft objects
        max_time: time horizon in seconds
    """
    # Generate trajectories
    times = list(range(0, max_time, 10))  # Sample every 10 seconds
    
    # Aircraft A trajectory
    traj_a_x = [position_at_time(aircraft_a, t)[0] for t in times]
    traj_a_y = [position_at_time(aircraft_a, t)[1] for t in times]
    
    # Aircraft B trajectory
    traj_b_x = [position_at_time(aircraft_b, t)[0] for t in times]
    traj_b_y = [position_at_time(aircraft_b, t)[1] for t in times]
    
    # Detect conflict
    result = detect_conflict(aircraft_a, aircraft_b)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot trajectories
    ax.plot(traj_a_x, traj_a_y, 'b-', linewidth=2, label=f"{aircraft_a.name}")
    ax.plot(traj_b_x, traj_b_y, 'r-', linewidth=2, label=f"{aircraft_b.name}")
    
    # Plot starting positions
    ax.plot(aircraft_a.pos[0], aircraft_a.pos[1], 'bo', markersize=10, label="A start")
    ax.plot(aircraft_b.pos[0], aircraft_b.pos[1], 'ro', markersize=10, label="B start")
    
    # Plot closest approach position
    t_closest = result['t_closest']
    pos_a_closest = position_at_time(aircraft_a, t_closest)
    pos_b_closest = position_at_time(aircraft_b, t_closest)
    
    ax.plot(pos_a_closest[0], pos_a_closest[1], 'b*', markersize=20, 
            label=f"A at t={t_closest:.0f}s")
    ax.plot(pos_b_closest[0], pos_b_closest[1], 'r*', markersize=20, 
            label=f"B at t={t_closest:.0f}s")
    
    # Plot conflict radius (5 nautical miles = 9260 m)
    conflict_radius = 9260
    circle = patches.Circle(
        ((pos_a_closest[0] + pos_b_closest[0]) / 2, 
         (pos_a_closest[1] + pos_b_closest[1]) / 2),
        conflict_radius,
        fill=False,
        edgecolor='orange',
        linestyle='--',
        linewidth=2,
        label=f"Conflict radius ({conflict_radius}m)"
    )
    ax.add_patch(circle)
    
    # Labels and formatting
    ax.set_xlabel("X Position (metres)", fontsize=12)
    ax.set_ylabel("Y Position (metres)", fontsize=12)
    ax.set_title(f"Scenario: {test_name}", fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axis('equal')
    
    # Add conflict status
    status = "⚠️ CONFLICT" if result['conflict'] else "✓ SAFE"
    horiz_dist = result['min_horiz_dist']
    vert_dist = result['min_vert_dist']
    
    info_text = (
        f"{status}\n"
        f"t_closest: {t_closest:.1f}s\n"
        f"Horiz sep: {horiz_dist:.0f}m\n"
        f"Vert sep: {vert_dist:.0f}m"
    )
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
            fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    return fig


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

# Plot all scenarios
print("Generating plots...")
for test_name, aircraft_a, aircraft_b in test_pairs:
    fig = plot_scenario(test_name, aircraft_a, aircraft_b)
    plt.savefig(f"{test_name.replace(' ', '_')}_scenario.png", dpi=150, bbox_inches='tight')
    print(f"  ✓ Saved {test_name.replace(' ', '_')}_scenario.png")

print("\nDone! Check your folder for PNG files.")
plt.show()