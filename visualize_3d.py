"""
3D interactive visualization of aircraft trajectories and conflicts.
Uses plotly for interactive 3D plots.
"""

import plotly.graph_objects as go
import plotly.express as px
from aircraft import Aircraft, position_at_time, detect_conflict
import math

def plot_3d_scenario(test_name, aircraft_a, aircraft_b, max_time=600, dt=20):
    """
    Create an interactive 3D plot of aircraft trajectories.
    
    Args:
        test_name: name of scenario
        aircraft_a, aircraft_b: Aircraft objects
        max_time: time horizon
        dt: sampling interval
    """
    
    # Generate trajectories
    times = list(range(0, max_time, dt))
    
    # Aircraft A trajectory
    traj_a = [position_at_time(aircraft_a, t) for t in times]
    traj_a_x = [p[0] for p in traj_a]
    traj_a_y = [p[1] for p in traj_a]
    traj_a_z = [p[2] for p in traj_a]
    
    # Aircraft B trajectory
    traj_b = [position_at_time(aircraft_b, t) for t in times]
    traj_b_x = [p[0] for p in traj_b]
    traj_b_y = [p[1] for p in traj_b]
    traj_b_z = [p[2] for p in traj_b]
    
    # Detect conflict
    result = detect_conflict(aircraft_a, aircraft_b)
    
    # Create figure
    fig = go.Figure()
    
    # Aircraft A trajectory
    fig.add_trace(go.Scatter3d(
        x=traj_a_x, y=traj_a_y, z=traj_a_z,
        mode='lines',
        name=f"{aircraft_a.name}",
        line=dict(color='blue', width=4),
        hoverinfo='text',
        text=[f"t={t}s" for t in times]
    ))
    
    # Aircraft B trajectory
    fig.add_trace(go.Scatter3d(
        x=traj_b_x, y=traj_b_y, z=traj_b_z,
        mode='lines',
        name=f"{aircraft_b.name}",
        line=dict(color='red', width=4),
        hoverinfo='text',
        text=[f"t={t}s" for t in times]
    ))
    
    # Starting positions (markers)
    fig.add_trace(go.Scatter3d(
        x=[aircraft_a.pos[0]], y=[aircraft_a.pos[1]], z=[aircraft_a.pos[2]],
        mode='markers',
        name=f"{aircraft_a.name} (start)",
        marker=dict(size=10, color='blue', symbol='circle')
    ))
    
    fig.add_trace(go.Scatter3d(
        x=[aircraft_b.pos[0]], y=[aircraft_b.pos[1]], z=[aircraft_b.pos[2]],
        mode='markers',
        name=f"{aircraft_b.name} (start)",
        marker=dict(size=10, color='red', symbol='circle')
    ))
    
    # Closest approach position
    t_closest = result['t_closest']
    pos_a_closest = position_at_time(aircraft_a, t_closest)
    pos_b_closest = position_at_time(aircraft_b, t_closest)
    
    fig.add_trace(go.Scatter3d(
        x=[pos_a_closest[0]], y=[pos_a_closest[1]], z=[pos_a_closest[2]],
        mode='markers',
        name=f"{aircraft_a.name} (closest t={t_closest:.0f}s)",
        marker=dict(size=15, color='blue', symbol='diamond')
    ))
    
    fig.add_trace(go.Scatter3d(
        x=[pos_b_closest[0]], y=[pos_b_closest[1]], z=[pos_b_closest[2]],
        mode='markers',
        name=f"{aircraft_b.name} (closest t={t_closest:.0f}s)",
        marker=dict(size=15, color='red', symbol='diamond')
    ))
    
    # Add a line between closest approach points
    fig.add_trace(go.Scatter3d(
        x=[pos_a_closest[0], pos_b_closest[0]],
        y=[pos_a_closest[1], pos_b_closest[1]],
        z=[pos_a_closest[2], pos_b_closest[2]],
        mode='lines',
        name='Minimum separation',
        line=dict(color='orange', width=3, dash='dash')
    ))
    
    # Update layout
    status = "⚠️ CONFLICT" if result['conflict'] else "✓ SAFE"
    
    fig.update_layout(
        title=f"<b>{test_name}</b><br>{status}",
        scene=dict(
            xaxis_title='X (metres)',
            yaxis_title='Y (metres)',
            zaxis_title='Altitude Z (metres)',
            aspectmode='auto',
        ),
        hovermode='closest',
        showlegend=True,
        width=1000,
        height=800,
    )
    
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

print("Generating 3D visualizations...")
print()

for test_name, aircraft_a, aircraft_b in test_pairs:
    fig = plot_3d_scenario(test_name, aircraft_a, aircraft_b)
    
    # Save as HTML
    filename = f"{test_name.replace(' ', '_')}_3d.html"
    fig.write_html(filename)
    print(f"  ✓ Saved {filename}")

print()
print("Open the .html files in your browser to see interactive 3D plots!")
print("(You can rotate, zoom, hover to see details)")