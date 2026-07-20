"""
Fetch real flight data from OpenSky Network and run conflict detection.
Uses requests library to query the API directly.
"""

import requests
import math
from aircraft import Aircraft, detect_conflict

def fetch_aircraft_in_region(lat_min, lat_max, lon_min, lon_max):
    """
    Fetch all aircraft in a geographic region using OpenSky API via HTTP.
    
    Args:
        lat_min, lat_max, lon_min, lon_max: bounding box (degrees)
    
    Returns:
        list of Aircraft objects with current position/velocity
    """
    try:
        url = "https://opensky-network.org/api/states/all"
        params = {
            'lamin': lat_min,
            'lamax': lat_max,
            'lomin': lon_min,
            'lomax': lon_max
        }
        
        print(f"  Querying OpenSky API for region: [{lat_min}, {lon_min}] to [{lat_max}, {lon_max}]")
        print(f"  (This may take 10-30 seconds...)")
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if not data or 'states' not in data or not data['states']:
            print("  No aircraft found in this region.")
            return []
        
        aircraft_list = []
        for state in data['states']:
            try:
                # state format: [icao24, callsign, origin_country, time_position, last_contact,
                #                longitude, latitude, baro_altitude, on_ground, velocity,
                #                true_track, vertical_rate, sensors, geo_altitude, ...]
                
                callsign = state[1].strip() if state[1] else f"ICAO_{state[0]}"
                lon = state[5]
                lat = state[6]
                alt = state[7]  # baro_altitude
                velocity = state[9]
                track = state[10]
                vert_rate = state[11]
                
                # Skip if missing critical data
                if lat is None or lon is None or alt is None:
                    continue
                if velocity is None or velocity == 0:
                    velocity = 0.1
                if track is None:
                    track = 0
                if vert_rate is None:
                    vert_rate = 0
                
                # Convert lat/lon to approximate metres
                x = lon * 111000
                y = lat * 111000
                z = alt
                
                # Velocity components from heading and speed
                track_rad = math.radians(track)
                vx = velocity * math.sin(track_rad)
                vy = velocity * math.cos(track_rad)
                vz = vert_rate
                
                aircraft_list.append(Aircraft(
                    name=callsign,
                    x=x, y=y, z=z,
                    vx=vx, vy=vy, vz=vz
                ))
            
            except (IndexError, TypeError):
                continue
        
        print(f"  ✓ Found {len(aircraft_list)} aircraft")
        return aircraft_list
    
    except Exception as e:
        print(f"  ✗ Error fetching data: {e}")
        return []


def detect_conflicts_bulk(aircraft_list, lookahead_time=600):
    """Run conflict detection on all pairs."""
    conflicts = []
    total_pairs = 0
    
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
    
    return {'total_pairs': total_pairs, 'conflicts': conflicts}


# Try West African airspace (Accra, Dakar, Lagos corridor)
LAG_LAT_MIN, LAG_LAT_MAX = 4.0, 10.0
LAG_LON_MIN, LAG_LON_MAX = -6.0, 5.0

print("=" * 100)
print("REAL FLIGHT DATA: CONFLICT DETECTION OVER LAGOS")
print("=" * 100)
print()

print("Step 1: Fetch live aircraft data from OpenSky Network")
print("-" * 100)
aircraft_list = fetch_aircraft_in_region(LAG_LAT_MIN, LAG_LAT_MAX, LAG_LON_MIN, LAG_LON_MAX)

if not aircraft_list:
    print("\n⚠️  No aircraft found. Trying a wider region...")
    LAG_LAT_MIN, LAG_LAT_MAX = 6.0, 7.0
    LAG_LON_MIN, LAG_LON_MAX = 2.5, 4.5
    aircraft_list = fetch_aircraft_in_region(LAG_LAT_MIN, LAG_LAT_MAX, LAG_LON_MIN, LAG_LON_MAX)

print()

if aircraft_list:
    print("Step 2: Run conflict detection")
    print("-" * 100)
    
    stats = detect_conflicts_bulk(aircraft_list)
    
    print(f"  Total pairs checked: {stats['total_pairs']}")
    print(f"  Conflicts found: {len(stats['conflicts'])}")
    print()
    
    if stats['conflicts']:
        print("  Top conflicts:")
        for idx, conflict in enumerate(sorted(stats['conflicts'], key=lambda x: x['t_closest'])[:5], 1):
            print(f"    {idx}. {conflict['a']} <-> {conflict['b']}")
            print(f"       Time: {conflict['t_closest']:.0f}s, Horiz: {conflict['horiz_dist']:.0f}m, Vert: {conflict['vert_dist']:.0f}m")
    else:
        print("  ✓ No conflicts detected!")

else:
    print("✗ Could not fetch aircraft data.")
    print("(OpenSky API might be rate-limited. Falling back to synthetic data.)")
    print()

print()
print("=" * 100)