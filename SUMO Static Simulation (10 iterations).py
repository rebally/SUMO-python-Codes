import os

# Define the number of runs (seeds)
num_runs = 10  

# SUMO base command with rerouting probability set to 20%
base_cmd = (
    "sumo -n calgarystep4.net.xml --route-files step4duarouter.xml "
    "--duration-log.statistics true -b 21600 -e 32400 --time-to-teleport -1 "
    "--step-length 0.3 --routing-algorithm astar --time-to-impatience -1 "
    "--device.rerouting.probability 0.2"  # 20% Rerouting Probability
)

# Define FCD output file that will be overwritten in each run (keeping only the last one)
fcd_file = "step4fcd.xml"

# Loop for multiple simulation runs
for i in range(1, num_runs + 1):
    seed_value = i  # Different seed per run
    tripinfo_file = f"step4tripinfo_{i}.xml"
    vehrou_file = f"step4vehrou_{i}.xml"
    
    # Build the command
    cmd = (
        f"{base_cmd} --seed {seed_value} --random "
        f"--tripinfo-output {tripinfo_file} "
        f"--vehroute-output {vehrou_file} "
        f"--fcd-output {fcd_file}"  # Overwrite FCD file in each iteration
    )
    
    print(f"Running simulation {i} with seed {seed_value}...")
    os.system(cmd)

print("All simulations completed! ✅ Only the last FCD file ('step4fcd.xml') is kept.")
