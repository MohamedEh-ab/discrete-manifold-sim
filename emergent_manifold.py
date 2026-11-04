#import os
#os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'      # uncomment if you get an OMP Error 15
import torch
import matplotlib.pyplot as plt
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# hyperparameters 
GRID_SIZE = 50         # a 50x50 universe
NUM_PARTICLES = 5000   # the random paths moving through space
EPSILON = 0.05         # the bounded differential: how much one particle warps a mirror
MOMENTUM = 0.8         # keeps particles from stopping instantly when they hit a sharp angle
STEPS = 400            # how many frames the universe will run for

# 1. initialize the space (the mirrors .. let's use the random start to watch it shatter)
angles = torch.rand((GRID_SIZE, GRID_SIZE), device=device) * 2 * np.pi
mirrors = torch.stack([torch.cos(angles), torch.sin(angles)], dim=-1)

# 2. initialize the particles (the paths)
positions = torch.rand((NUM_PARTICLES, 2), device=device) * GRID_SIZE
vel_angles = torch.rand(NUM_PARTICLES, device=device) * 2 * np.pi
velocities = torch.stack([torch.cos(vel_angles), torch.sin(vel_angles)], dim=-1)

plt.ion()  # turn on interactive mode
fig, ax = plt.subplots(figsize=(8, 8), facecolor='black')
ax.set_facecolor('black')

# initial particle scatter plot
pos_np = positions.cpu().numpy()
scat = ax.scatter(pos_np[:, 0], pos_np[:, 1], c='orange', s=0.6, alpha=0.6)
ax.set_xlim(0, GRID_SIZE)
ax.set_ylim(0, GRID_SIZE)
ax.set_title("Live Manifold Simulation: Watching Emergence", color='white', pad=15)
ax.axis('off')

for step in range(STEPS):
    coords = positions.long() % GRID_SIZE
    x_idx, y_idx = coords[:, 0], coords[:, 1]
    
    local_mirrors = mirrors[x_idx, y_idx]
    
    # 3. the merge (geometric refraction)
    dot_products = (velocities * local_mirrors).sum(dim=1, keepdim=True)
    projected_vel = dot_products * local_mirrors
    
    velocities = (MOMENTUM * velocities) + ((1 - MOMENTUM) * projected_vel)
    velocities = torch.nn.functional.normalize(velocities, dim=1)
    
    # 4. the metric mutation (space rewrites itself)
    mirrors[x_idx, y_idx] += EPSILON * velocities
    mirrors = torch.nn.functional.normalize(mirrors, dim=-1)
    
    # move the particles forward (Toroidal wrap)
    positions = (positions + velocities * 0.5) % GRID_SIZE
    
    # update the frame every 2 steps for smooth visual performance
    if step % 2 == 0:
        pos_np = positions.cpu().numpy()
        scat.set_offsets(pos_np)
        fig.canvas.draw()
        fig.canvas.flush_events()

plt.ioff()
plt.show()