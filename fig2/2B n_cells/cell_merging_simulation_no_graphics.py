# import pygame
import numpy as np
import math
# import cv2
import csv
import os
import argparse
from datetime import datetime
from time import time
s_time = time()

# Argument parsing
parser = argparse.ArgumentParser(description="Cell Merging Simulation")
parser.add_argument("--n", type=int, default=300, help="Number of B cells")
parser.add_argument("--initial_radius", type=float, default=10, help="Initial radius of cells")
parser.add_argument("--speed", type=float, default=100, help="Speed of cells")
parser.add_argument("--k", type=int, default=15, help="Time points between adding new cells")
parser.add_argument("--B_cell_ratio", type=float, default=0.3, help="Cell to area ratio")
parser.add_argument("--speed_decay_factor", type=float, default=3, help="Speed decay factor")
parser.add_argument("--is_display", type=bool, default=True, help="Should pygame be used or only the simulation without visuals")

args = parser.parse_args()

# Simulation parameters
n = args.n
initial_radius = args.initial_radius
speed = args.speed
k = args.k
B_cell_ratio = args.B_cell_ratio
speed_decay_factor = args.speed_decay_factor

total_cell_area = n * (math.pi * initial_radius ** 2)
grid_area = total_cell_area / B_cell_ratio
l = int(math.sqrt(grid_area))  # Length of the square grid

#
TIMEOUT = 20000

# Directory and CSV setup
output_dir = "simulation_outputs"
os.makedirs(output_dir, exist_ok=True)
csv_file = os.path.join(output_dir, "simulation_log.csv")
csv_headers = ["timestamp", "l", "initial_radius", "speed", "k", "B_cell_ratio", "speed_decay_factor", "output_video", "final_time_step", "final_cell_count", "total_cells", "notes"]
timedata_file = os.path.join(output_dir,f'timedata.csv')


if not os.path.exists(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers)

if not os.path.exists(timedata_file):
    with open(timedata_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp','k','timestep','cell_count','cluster_count'])

# Colors
# BACKGROUND_COLOR = (0, 0, 0)
# CELL_COLOR = (0, 255, 0)
# TEXT_COLOR = (255, 255, 255)

# Initialize Pygame
# pygame.init()
# screen = pygame.display.set_mode((l, l))
# pygame.display.set_caption("Cell Merging Simulation")
# clock = pygame.time.Clock()

# Timestamp and video setup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
video_filename = f"cell_merging_simulation_{timestamp}.mp4"
# video_path = os.path.join(output_dir, video_filename)
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# out = cv2.VideoWriter(video_path, fourcc, 30.0, (l, l))
# image_filename = f"cell_merging_simulation_{timestamp}.png"
# image_path = os.path.join(output_dir, image_filename)


# Font setup
# font = pygame.font.Font(None, 20)

# Cell class
class Cell:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed

    def move(self):
        # Update position based on speed and direction
        self.angle = np.random.uniform(0, 2 * math.pi)
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

        # Apply periodic boundary conditions
        self.x %= l
        self.y %= l

    # def draw(self, screen):
    #     pygame.draw.circle(screen, CELL_COLOR, (int(self.x), int(self.y)), int(self.radius))

# Initialize cells
all_cells = [Cell(np.random.uniform(0, l), np.random.uniform(0, l), initial_radius, speed) for _ in range(n)]
cells = []

def merge_cells(cells):
    merged = []
    while cells:
        cell = cells.pop()
        has_merged = False
        for other in cells:
            dist = math.hypot(cell.x - other.x, cell.y - other.y)
            if dist < cell.radius + other.radius:
                # Merge cells
                new_area = math.pi * cell.radius ** 2 + math.pi * other.radius ** 2
                new_radius = math.sqrt(new_area / math.pi)
                weight_cell = math.pi * cell.radius ** 2 / new_area
                weight_other = math.pi * other.radius ** 2 / new_area
                new_x = weight_cell * cell.x + weight_other * other.x
                new_y = weight_cell * cell.y + weight_other * other.y
                new_speed = speed * (new_radius / initial_radius)**(-speed_decay_factor)  # Speed decreases with size
                cells.remove(other)
                merged.append(Cell(new_x, new_y, new_radius, new_speed))
                has_merged = True
                break
        if not has_merged:
            merged.append(cell)
    return merged

# Main loop
running = True
time_step = 0
while running:
    # screen.fill(BACKGROUND_COLOR)
    
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         running = False

    # Gradually add cells to the simulation
    if k == 0:
        cells.extend(all_cells)
        all_cells.clear()
    elif len(all_cells) > 0 and time_step % k == 0:
        cells.append(all_cells.pop())
    if time_step % 500 ==0:
        A  = [c.radius**2 for c in cells] 
        cluster_count = sum(np.array(A)>0.05*sum(A))
        with open(timedata_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            # writer.writerow([timestamp, l, initial_radius, speed, k, B_cell_ratio, speed_decay_factor, video_filename, time_step, len(cells), n, ""])
            writer.writerow([timestamp,k,time_step,len(cells),cluster_count])


    # Move and draw cells
    for cell in cells:
        cell.move()
        # if time_step % (TIMEOUT/10) == 0:
        #     cell.draw(screen)

    # Check for collisions and merge cells
    cells = merge_cells(cells)
        # clock.tick(30)  # Limit to 30 frames per second
    time_step += 1
    
        # End condition
    if (len(cells) == 1 and len(all_cells) == 0) or time_step>TIMEOUT:
        running = False


    # if time_step % (TIMEOUT/10) == 0:
    #     # Display time, total number of cells, and number of inserted cells
    #     time_text = font.render(f"Time: {time_step}", True, TEXT_COLOR)
    #     total_cells_text = font.render(f"Total Cells: {n}", True, TEXT_COLOR)
    #     inserted_cells_text = font.render(f"Inserted Cells: {n-len(all_cells)}", True, TEXT_COLOR)
    #     k_text = font.render(f"k: {k}", True, TEXT_COLOR)
    #     decay_rate_text = font.render(f'decay_rate: {speed_decay_factor}', True, TEXT_COLOR)
    #     screen.blit(time_text, (10, 10))
    #     screen.blit(total_cells_text, (10, 30))
    #     screen.blit(inserted_cells_text, (10, 50))
    #     screen.blit(k_text, (10, 70))
    #     screen.blit(decay_rate_text, (10, 90))
    #     # Update the display
    #     pygame.display.flip()
    #     # Record the frame
    #     frame = pygame.surfarray.array3d(screen)
    #     frame = cv2.cvtColor(np.transpose(frame, (1, 0, 2)), cv2.COLOR_RGB2BGR)
    #     out.write(frame)



# Save final image
# pygame.image.save(screen, image_path)

# Wait for a moment to show the final cell
# pygame.time.delay(1000)
# pygame.quit()

# Release the video writer
# out.release()

# Log the parameters and output
with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([timestamp, l, initial_radius, speed, k, B_cell_ratio, speed_decay_factor, video_filename, time_step, len(cells), n, ""])



print(f'runtime: {time()-s_time}')