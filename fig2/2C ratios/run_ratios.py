import asyncio
import numpy as np
import time

num_repeats = 100  # Number of repetitions per n value
max_concurrent_runs = 10  # Maximum number of concurrent tasks

times = []  # List to store the runtime of each instance

B_ratios = np.arange(1,10)*0.1
# n_values = [250,500]

# Function to start the simulation process with a delay between launches
async def run_simulation(repeat, is_const,B_ratio):
    n_B_cells = int(1000*B_ratio)
    start_time = time.time()
    print(f"Starting simulation with repeat {repeat + 1}")
    if is_const:
        process = await asyncio.create_subprocess_exec(
            "python", "cell_merging_simulation_no_graphics.py",'--n',str(n_B_cells), '--k', '0', '--B_cell_ratio',str(B_ratio),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    else:
        process = await asyncio.create_subprocess_exec(
            "python", "cell_merging_simulation_no_graphics.py",'--n',str(n_B_cells), '--B_cell_ratio',str(B_ratio),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    stdout, stderr = await process.communicate()
    end_time = time.time()
    instance_time = end_time - start_time
    times.append(instance_time)
    print(f"Completed simulation with repeat {repeat + 1} in {instance_time:.2f} seconds")
    print(stdout.decode())
    print(stderr.decode())

async def main():
    start_time = time.time()
    semaphore = asyncio.Semaphore(max_concurrent_runs)

    async def sem_run_simulation(repeat, is_const,n):
        async with semaphore:
            await run_simulation(repeat, is_const,n)

    tasks = []
    for repeat in range(num_repeats):
        for B_ratio in B_ratios:
            # Schedule the simulation with a semaphore to control concurrency
            tasks.append(sem_run_simulation(repeat, False,B_ratio))
            tasks.append(sem_run_simulation(repeat, True,B_ratio))
    
    # Run all tasks concurrently, respecting the semaphore limit
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    mean_time = np.mean(times)
    print(f"Mean time per instance: {mean_time:.2f} seconds")
    print(f"Total runtime: {total_time:.2f} seconds")

# Run the asyncio event loop
asyncio.run(main())
