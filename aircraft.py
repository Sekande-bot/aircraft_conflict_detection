"""
Aircraft Conflict Detection System - Phase 1 (Pure Geometry)

No machine learning, just vector math.
Units: metres, metres/second
"""

class Aircraft:
    """Represents an aircraft in 3D space with constant velocity."""
    def __init__(self, name, x, y, z, vx, vy, vz):
        self.name = name
        self.pos = [x, y, z]
        self.vel = [vx, vy, vz]
    
    def __repr__(self):
        return f"Aircraft({self.name}, pos={self.pos}, vel={self.vel})"


def position_at_time(aircraft, t):
    """Project aircraft position at time t seconds ahead."""
    return [
        aircraft.pos[i] + aircraft.vel[i] * t
        for i in range(3)
    ]


def closest_approach_exact(aircraft_a, aircraft_b):
    """
    Find closest approach using vector calculus.
    
    Returns: (t_closest in seconds, min_distance in metres)
    """
    rel_pos = [aircraft_b.pos[i] - aircraft_a.pos[i] for i in range(3)]
    rel_vel = [aircraft_b.vel[i] - aircraft_a.vel[i] for i in range(3)]
    
    rel_pos_dot_rel_vel = sum(rel_pos[i] * rel_vel[i] for i in range(3))
    rel_vel_magnitude_sq = sum(rel_vel[i] ** 2 for i in range(3))
    
    if rel_vel_magnitude_sq < 1e-9:
        rel_pos_magnitude = (sum(x**2 for x in rel_pos) ** 0.5)
        return 0, rel_pos_magnitude
    
    t_closest = -rel_pos_dot_rel_vel / rel_vel_magnitude_sq
    
    if t_closest < 0:
        t_closest = 0
    
    pos_a = position_at_time(aircraft_a, t_closest)
    pos_b = position_at_time(aircraft_b, t_closest)
    sep = [pos_b[i] - pos_a[i] for i in range(3)]
    min_distance = (sum(x**2 for x in sep) ** 0.5)
    
    return t_closest, min_distance


def detect_conflict(aircraft_a, aircraft_b, lookahead_time=600):
    """
    Detect if two aircraft will conflict in the next lookahead_time seconds.
    
    Conflict = both horizontal AND vertical separation below thresholds.
    
    Returns: dict with conflict status and separation details
    """
    HORIZ_THRESHOLD = 9260  # 5 nautical miles
    VERT_THRESHOLD = 305    # 1000 ft
    
    t_closest, _ = closest_approach_exact(aircraft_a, aircraft_b)
    
    if t_closest > lookahead_time:
        return {
            'conflict': False,
            't_closest': t_closest,
            'min_horiz_dist': float('inf'),
            'min_vert_dist': float('inf'),
            'reason': 'Closest approach beyond lookahead window'
        }
    
    pos_a = position_at_time(aircraft_a, t_closest)
    pos_b = position_at_time(aircraft_b, t_closest)
    
    horiz_sep_x = pos_b[0] - pos_a[0]
    horiz_sep_y = pos_b[1] - pos_a[1]
    min_horiz_dist = (horiz_sep_x**2 + horiz_sep_y**2) ** 0.5
    min_vert_dist = abs(pos_b[2] - pos_a[2])
    
    conflict = (min_horiz_dist < HORIZ_THRESHOLD and 
                min_vert_dist < VERT_THRESHOLD)
    
    return {
        'conflict': conflict,
        't_closest': t_closest,
        'min_horiz_dist': min_horiz_dist,
        'min_vert_dist': min_vert_dist,
    }


def closest_approach_brute_force(aircraft_a, aircraft_b, max_time=600, dt=1):
    """
    Find closest approach by brute-force: loop over time steps.
    
    Args:
        aircraft_a, aircraft_b: Aircraft objects
        max_time: seconds to search ahead (default 600)
        dt: time step size in seconds (default 1)
    
    Returns:
        tuple: (t_closest, min_distance)
    """
    min_distance = float('inf')
    t_closest = 0
    
    # Loop through time steps
    t = 0
    while t < max_time:
        # Get positions at this time
        pos_a = position_at_time(aircraft_a, t)
        pos_b = position_at_time(aircraft_b, t)
        
        # Calculate separation vector
        sep = [pos_b[i] - pos_a[i] for i in range(3)]
        
        # Calculate distance (Euclidean norm)
        distance = (sep[0]**2 + sep[1]**2 + sep[2]**2) ** 0.5
        
        # Track minimum
        if distance < min_distance:
            min_distance = distance
            t_closest = t
        
        t += dt
    
    return t_closest, min_distance

    def detect_conflict_window(aircraft_a, aircraft_b, lookahead_time=600, dt=1.0):
    """
    Conflict = horizontal AND vertical separation both below thresholds
    at the SAME moment, checked across the whole lookahead window.

    Uses the closest-approach time as a candidate, then checks a short
    window around it, because horizontal and vertical minima can occur
    at different times.
    """
    HORIZ_THRESHOLD = 9260  # 5 NM
    VERT_THRESHOLD = 305    # 1000 ft

    min_horiz_dist = float('inf')
    min_vert_dist = float('inf')
    conflict_time = None

    t = 0.0
    while t <= lookahead_time:
        pos_a = position_at_time(aircraft_a, t)
        pos_b = position_at_time(aircraft_b, t)

        horiz = ((pos_b[0] - pos_a[0]) ** 2 + (pos_b[1] - pos_a[1]) ** 2) ** 0.5
        vert = abs(pos_b[2] - pos_a[2])

        min_horiz_dist = min(min_horiz_dist, horiz)
        min_vert_dist = min(min_vert_dist, vert)

        if horiz < HORIZ_THRESHOLD and vert < VERT_THRESHOLD and conflict_time is None:
            conflict_time = t

        t += dt

    return {
        'conflict': conflict_time is not None,
        't_closest': conflict_time,
        'min_horiz_dist': min_horiz_dist,
        'min_vert_dist': min_vert_dist,
    }