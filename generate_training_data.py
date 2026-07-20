"""
Generate 10,000 training samples for the neural network.
Each sample: relative position + relative velocity → conflict (yes/no)
"""

import random
import math
from aircraft import Aircraft, detect_conflict

def generate_training_sample():
    """
    Generate a single training sample: random aircraft pair + label.
    
    Returns:
        tuple: (features, label)
        features: [rel_x, rel_y, rel_z, rel_vx, rel_vy, rel_vz, horiz_dist, vert_dist]
        label: 1 if conflict, 0 if safe
    """
    
    # Aircraft A at origin
    a = Aircraft(
        name="A",
        x=0, y=0, z=5000,
        vx=random.uniform(50, 300),
        vy=random.uniform(-150, 150),
        vz=random.uniform(-2, 2)
    )
    
    # Aircraft B at random relative position
    b = Aircraft(
        name="B",
        x=random.uniform(-50000, 50000),
        y=random.uniform(-50000, 50000),
        z=random.uniform(4000, 12000),
        vx=random.uniform(50, 300),
        vy=random.uniform(-150, 150),
        vz=random.uniform(-2, 2)
    )
    
    # Relative position and velocity
    rel_pos = [b.pos[i] - a.pos[i] for i in range(3)]
    rel_vel = [b.vel[i] - a.vel[i] for i in range(3)]
    
    # Horizontal and vertical distances
    horiz_dist = math.sqrt(rel_pos[0]**2 + rel_pos[1]**2)
    vert_dist = abs(rel_pos[2])
    
    # Features (normalized to reasonable scales for NN)
    features = [
        rel_pos[0] / 100000,    # Normalize to [-0.5, 0.5]
        rel_pos[1] / 100000,
        rel_pos[2] / 10000,
        rel_vel[0] / 300,       # Normalize to [-1, 1]
        rel_vel[1] / 300,
        rel_vel[2] / 10,
        horiz_dist / 50000,     # Normalize distance
        vert_dist / 10000,
    ]
    
    # Label: detect conflict
    result = detect_conflict(a, b)
    label = 1 if result['conflict'] else 0
    
    return features, label


def generate_training_dataset(n_samples=10000):
    """Generate n_samples training examples."""
    print(f"Generating {n_samples} training samples...")
    
    features = []
    labels = []
    
    conflict_count = 0
    
    for i in range(n_samples):
        if (i + 1) % 1000 == 0:
            print(f"  {i + 1}/{n_samples} samples generated ({conflict_count} conflicts so far)")
        
        feat, label = generate_training_sample()
        features.append(feat)
        labels.append(label)
        
        if label == 1:
            conflict_count += 1
    
    print(f"\n✓ Generated {n_samples} samples")
    print(f"  Conflicts: {conflict_count} ({conflict_count/n_samples*100:.1f}%)")
    print(f"  Safe: {n_samples - conflict_count} ({(n_samples-conflict_count)/n_samples*100:.1f}%)")
    
    return features, labels


if __name__ == "__main__":
    features, labels = generate_training_dataset(n_samples=10000)
    
    # Save to file
    import pickle
    with open('training_data.pkl', 'wb') as f:
        pickle.dump((features, labels), f)
    
    print(f"\n✓ Saved to training_data.pkl")