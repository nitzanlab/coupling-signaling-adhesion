import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pickle
from collections import deque
import pandas as pd

import pickle
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML


def run_simulation(IS_INDUCED, L=20, N=200, fraction_core=0.25, T=1e-10, p=0.025, steps=400,
                   J_AA=-10, J_BB=-100):
    L = int(2*(N/np.pi)**(0.5))+2

    # Assign parameters
    N_B = int(N * fraction_core)   # number of B-type
    N_A = N - N_B
    
    # Initialize grid
    grid = -1 * np.ones((L, L), dtype=int)
    
    # Place cells in a circular region
    center = (L//2, L//2)
    positions = [(x, y) for x in range(L) for y in range(L)]
    positions.sort(key=lambda pos: (pos[0]-center[0])**2+(pos[1]-center[1])**2)
    selected_positions = positions[:N]
    np.random.shuffle(selected_positions)
    for i, (x, y) in enumerate(selected_positions):
        if i < N_A:
            grid[x, y] = 0 # A
        else:
            if IS_INDUCED:
                grid[x, y] = 1 # B (low)
            else:
                grid[x, y] = 2 # B (high)
    
    # Helper functions
    
    # could be either 4 or 8 neighbors. now chose 8
    def get_neighbors(x, y):
        nbrs = []
        # for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        for dx, dy in [ (1,0),(-1,0),(0,1),(0,-1),
                        (-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < L and 0 <= ny < L:
                nbrs.append((nx, ny))
        return nbrs

    # here cores are only B_HIGH cells
    def count_cores(grid):
        visited = np.zeros_like(grid, dtype=bool)
        # directions = [(1,0),(-1,0),(0,1),(0,-1)]
        cores = 0
        L = grid.shape[0]

        for i in range(L):
            for j in range(L):
                if (grid[i,j] == 2) and not visited[i,j]:
                    # BFS/DFS to find connected component
                    cores += 1
                    queue = deque([(i,j)])
                    visited[i,j] = True
                    while queue:
                        x,y = queue.popleft()
                        for nx,ny in get_neighbors(x,y):
                        # for dx,dy in directions:
                        #     nx, ny = x+dx, y+dy
                            if 0<=nx<L and 0<=ny<L and not visited[nx,ny]:
                                if grid[nx,ny] == 2:
                                    visited[nx,ny] = True
                                    queue.append((nx,ny))
        return cores

    def local_energy(x, y):
        ctype = grid[x,y]
        if ctype == -1:
            return 0
        nbrs = get_neighbors(x,y)
        E = 0
        for nx, ny in nbrs:
            ntype = grid[nx, ny]
            if ntype == -1:
                continue
            # For simplicity, assume J_AB = J_AA as in the original code snippet
            if ctype==2 and ntype==2:
                E += J_BB
            else:
                E += J_AA
        return E
    
    def energy_difference_swap(x1, y1, x2, y2):
        E_before = local_energy(x1,y1) + local_energy(x2,y2)
        c1, c2 = grid[x1,y1], grid[x2,y2]
        grid[x1,y1], grid[x2,y2] = c2, c1
        E_after = local_energy(x1,y1) + local_energy(x2,y2)
        grid[x1,y1], grid[x2,y2] = c1, c2
        return E_after - E_before
    
    def attempt_state_transition(x, y):
        if np.random.rand() < p:
            if grid[x,y] == 1:
                nbrs = get_neighbors(x,y)
                A_count = sum(grid[nx,ny] == 0 for nx,ny in nbrs)
                if A_count >= 3:
                    grid[x,y] = 2 # B_low -> B_high
    
    def attempt_swap(x, y):
        nbrs = get_neighbors(x,y)
        ctype = grid[x,y]

        valid_nbrs = [nbr for nbr in nbrs if grid[nbr]!=ctype]  

        if len(valid_nbrs)==0: return        
        nx, ny = valid_nbrs[np.random.randint(len(valid_nbrs))]
        dE = energy_difference_swap(x,y,nx,ny)
        if dE <= 0:
            grid[x, y], grid[nx, ny] = grid[nx, ny], grid[x, y]
        else:
            if np.random.rand() < np.exp(-dE/T):
                grid[x, y], grid[nx, ny] = grid[nx, ny], grid[x, y]
    
    # Simulation loop
    grids_over_time = []
    cores_over_time = []
    for step_i in range(steps+1):
        # Record state
        grids_over_time.append(grid.copy())
        cores_over_time.append(count_cores(grid))
        
        if step_i == steps:
            break

        for _ in range(N):
            occ_positions = np.argwhere(grid != -1)
            x, y = occ_positions[np.random.randint(len(occ_positions))]
            attempt_state_transition(x, y)
            attempt_swap(x, y)
    
    return cores_over_time[-1]

