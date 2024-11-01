import simpy
import random
import matplotlib.pyplot as plt
import time

# Updated Simulation parameters for more reneging and balking
RANDOM_SEED = 10
NUM_TELLERS = 2         # Reduced number of tellers to increase load
INTER_ARRIVAL_TIME = 2   # Customers arrive more frequently
SERVICE_TIME = 5         # Service time remains the same
MAX_QUEUE_LENGTH = 3     # Reduced queue length to trigger balking earlier
MAX_WAIT_TIME = 6        # Reduced patience for reneging
SIMULATION_TIME = 100    # Total simulation time

# Function to run the simulation
def run_simulation():
    global balked_customers, reneged_customers, served_customers, waiting_times, queue_lengths, total_time_tellers_busy
    balked_customers = 0
    reneged_customers = 0
    served_customers = 0
    waiting_times = []
    queue_lengths = []
    total_time_tellers_busy = 0

    # Customer arrival process
    def customer(env, name, bank):
        global balked_customers, reneged_customers, served_customers, total_time_tellers_busy

        arrival_time = env.now

        # Balking: Customer leaves if queue is too long
        if len(bank.queue) >= MAX_QUEUE_LENGTH:
            balked_customers += 1
            return  # Customer leaves the system

        # Customer joins queue but may renege if waiting too long
        with bank.request() as req:
            patience = MAX_WAIT_TIME
            result = yield req | env.timeout(patience)

            if req in result:
                # Customer is served
                wait_time = env.now - arrival_time
                waiting_times.append(wait_time)
                total_time_tellers_busy += random.expovariate(1.0 / SERVICE_TIME)
                yield env.timeout(random.expovariate(1.0 / SERVICE_TIME))
                served_customers += 1
            else:
                # Customer reneges
                reneged_customers += 1

    # Customer generator
    def customer_generator(env, bank):
        i = 0
        while True:
            yield env.timeout(random.expovariate(1.0 / INTER_ARRIVAL_TIME))
            i += 1
            env.process(customer(env, f"Customer {i}", bank))

    # Monitor queue length
    def monitor_queue_length(env, bank):
        while True:
            queue_lengths.append(len(bank.queue))
            yield env.timeout(1)

    # Run the simulation
    env = simpy.Environment()
    bank = simpy.Resource(env, capacity=NUM_TELLERS)
    env.process(customer_generator(env, bank))
    env.process(monitor_queue_length(env, bank))
    env.run(until=SIMULATION_TIME)

# Run the simulation multiple times
num_runs = 10
throughput_results = []
waiting_time_results = []
balking_results = []
reneging_results = []
queue_length_results = []
utilization_results = []

for run in range(num_runs):
    run_simulation()
    # Calculate metrics
    throughput = served_customers / SIMULATION_TIME
    avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0
    avg_queue_length = sum(queue_lengths) / len(queue_lengths) if queue_lengths else 0
    server_utilization = total_time_tellers_busy / (NUM_TELLERS * SIMULATION_TIME)

    # Store results
    throughput_results.append(throughput)
    waiting_time_results.append(avg_waiting_time)
    balking_results.append(balked_customers)
    reneging_results.append(reneged_customers)
    queue_length_results.append(avg_queue_length)
    utilization_results.append(server_utilization)

    print(f"Run {run + 1}:")
    print(f" - Served customers: {served_customers}")
    print(f" - Balked customers: {balked_customers}")
    print(f" - Reneged customers: {reneged_customers}")
    print(f" - Average waiting time: {avg_waiting_time:.2f} minutes")
    print(f" - Average queue length: {avg_queue_length:.2f}")
    print(f" - Server utilization: {server_utilization:.2f}")
    print(f" - Throughput: {throughput:.2f} customers per minute\n")

# Summary of all runs
print(f"\nSummary after {num_runs} runs:")
print(f"Average throughput: {sum(throughput_results)/num_runs:.2f} customers per minute")
print(f"Average waiting time: {sum(waiting_time_results)/num_runs:.2f} minutes")
print(f"Average queue length: {sum(queue_length_results)/num_runs:.2f}")
print(f"Average server utilization: {sum(utilization_results)/num_runs:.2f}")
print(f"Average balked customers: {sum(balking_results)/num_runs:.2f}")
print(f"Average reneged customers: {sum(reneging_results)/num_runs:.2f}")

# Plotting the results
plt.figure(figsize=(12, 10))

# Throughput plot
plt.subplot(3, 2, 1)
plt.plot(range(1, num_runs + 1), throughput_results, marker='o')
plt.title('Throughput over multiple runs')
plt.xlabel('Run number')
plt.ylabel('Throughput (customers per minute)')

# Waiting time plot
plt.subplot(3, 2, 2)
plt.plot(range(1, num_runs + 1), waiting_time_results, marker='o')
plt.title('Average Waiting Time over multiple runs')
plt.xlabel('Run number')
plt.ylabel('Waiting Time (minutes)')

# Queue length plot
plt.subplot(3, 2, 3)
plt.plot(range(1, num_runs + 1), queue_length_results, marker='o')
plt.title('Average Queue Length over multiple runs')
plt.xlabel('Run number')
plt.ylabel('Queue Length (customers)')

# Server utilization plot
plt.subplot(3, 2, 4)
plt.plot(range(1, num_runs + 1), utilization_results, marker='o')
plt.title('Server Utilization over multiple runs')
plt.xlabel('Run number')
plt.ylabel('Server Utilization (%)')

# Balking plot
plt.subplot(3, 2, 5)
plt.plot(range(1, num_runs + 1), balking_results, marker='o')
plt.title('Balking over multiple runs')
plt.xlabel('Run number')
plt.ylabel('Balked Customers')

# Reneging plot
plt.subplot(3, 2, 6)
plt.plot(range(1, num_runs + 1), reneging_results, marker='o')
plt.title('Reneging over multiple runs')
plt.xlabel('Run number')
plt.ylabel('Reneged Customers')

# Plot to show customers served, balked, and reneged over multiple runs
plt.figure(figsize=(10, 6))

# Add served, balked, and reneged customers to the plot
plt.plot(range(1, num_runs + 1), [SIMULATION_TIME * throughput for throughput in throughput_results], marker='o', label='Served Customers')
plt.plot(range(1, num_runs + 1), balking_results, marker='o', label='Balked Customers')
plt.plot(range(1, num_runs + 1), reneging_results, marker='o', label='Reneged Customers')

# Labels and title
plt.title('Customers Served, Balked, and Reneged over Multiple Runs')
plt.xlabel('Run number')
plt.ylabel('Number of Customers')
plt.legend()
plt.grid(True)
plt.show()

plt.tight_layout()
plt.show()
