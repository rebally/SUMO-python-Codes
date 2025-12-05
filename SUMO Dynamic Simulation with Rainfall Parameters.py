import os
import sys
import time
import traci
import xml.etree.ElementTree as ET

# Set SUMO_HOME environment variable
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")

# Define simulation parameters
sumo_binary = "sumo"
sumo_config = "dynamicrainsumo-step1.sumocfg"
simulation_start_time = 21600  # 6:00 AM
simulation_end_time = 32400    # 9:00 AM
num_runs = 10  # Number of random seed runs

# Corrected file path for duarouter.xml
duarouter_file_path = r"D:\SUMO Files for Calgary Simulation\All Simulations\1600 vehicles 20 TAZ-A star (8-8)\step1duarouter.xml"

# Run simulations with multiple seeds
for run in range(1, num_runs + 1):
    seed_value = run  # Different seed per run
    print(f"\n🔄 Running simulation {run} with seed {seed_value}...\n")

    # Ensure SUMO is not already running
    if traci.isLoaded():
        traci.close()
        time.sleep(1)  # Wait to ensure SUMO fully closes

    # Include the additional file "rainadd.xml" via the -a option
    sumo_cmd = [
        sumo_binary, "-c", sumo_config, "-a", "rainadd.xml",
        "--start", "--quit-on-end",
        "--seed", str(seed_value), "--random",
        "--step-length", "0.3", "--routing-algorithm", "astar",
        "--time-to-teleport", "300",  # Removes stuck vehicles after 5 minutes
        "--time-to-impatience", "-1",
        "--device.rerouting.probability", "1.0",  # Rerouting applied globally

        # Unique tripinfo & vehroute files for each run
        "--tripinfo-output", f"dynamicrainstep1tripinfo_{seed_value}.xml",
        "--vehroute-output", f"dynamicrainstep1vehrou_{seed_value}.xml",

        # FCD output - Only the last run keeps it
        "--fcd-output", "dynamicrainstep1fcd.xml" if run == num_runs else "/dev/null"
    ]

    try:
        traci.start(sumo_cmd)

        # Retrieve all traffic light IDs
        traffic_light_ids = traci.trafficlight.getIDList()
        print(f"🚦 Available traffic light IDs: {traffic_light_ids}")

        configured_vehicles = set()
        max_decel_rate = 0.5  # Gradual deceleration rate

        # Function to configure vehicle parameters and adjust speed
        def configure_and_adjust_vehicles():
            for vehicle_id in traci.vehicle.getIDList():
                # Configure vehicle parameters if not done already
                if vehicle_id not in configured_vehicles:
                    try:
                        vType = traci.vehicle.getTypeID(vehicle_id)
                        # Assign default values based on vehicle type
                        if vType == "bus":
                            accel, decel, sigma, max_speed = 1.5, 3.0, 0.6, 30.0
                        elif vType == "passenger":
                            accel, decel, sigma, max_speed = 2.6, 4.5, 0.5, 33.3
                        elif vType == "truck":
                            accel, decel, sigma, max_speed = 1.2, 2.5, 0.7, 25.0
                        else:
                            print(f"⚠️ Warning: Vehicle {vehicle_id} has an unknown type '{vType}'. Assigning default values.")
                            accel, decel, sigma, max_speed = 1.0, 2.0, 0.5, 25.0

                        traci.vehicle.setAccel(vehicle_id, accel)
                        traci.vehicle.setDecel(vehicle_id, decel)
                        traci.vehicle.setTau(vehicle_id, sigma)
                        traci.vehicle.setMaxSpeed(vehicle_id, max_speed)
                        configured_vehicles.add(vehicle_id)
                    except traci.exceptions.TraCIException as e:
                        print(f"⚠️ Error setting parameters for vehicle {vehicle_id}: {e}")

                # Adjust dynamic speed
                try:
                    # Recompute vehicle type and corresponding max_speed for safety
                    vType = traci.vehicle.getTypeID(vehicle_id)
                    if vType == "bus":
                        computed_max_speed = 30.0
                    elif vType == "passenger":
                        computed_max_speed = 33.3
                    elif vType == "truck":
                        computed_max_speed = 25.0
                    else:
                        computed_max_speed = 25.0

                    current_speed = traci.vehicle.getSpeed(vehicle_id)
                    new_speed = max(current_speed - max_decel_rate, computed_max_speed)
                    traci.vehicle.setMaxSpeed(vehicle_id, new_speed)
                except traci.exceptions.TraCIException as e:
                    print(f"Error adjusting speed for vehicle {vehicle_id}: {e}")

        # Main simulation loop
        start_time = time.time()
        while traci.simulation.getTime() < simulation_end_time:
            if traci.simulation.getTime() >= simulation_start_time:
                traci.simulationStep()
                configure_and_adjust_vehicles()
        traci.close()

    except Exception as e:
        print(f"⚠️ Error in simulation {run}: {e}")

    finally:
        if traci.isLoaded():
            traci.close()
        time.sleep(1)  # Ensure SUMO fully shuts down before restarting

print("\n✅ All simulations completed! Only the last FCD file ('dynamicrainstep1fcd.xml') is kept.")
