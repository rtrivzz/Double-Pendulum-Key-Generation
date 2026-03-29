import numpy as np
from scipy.integrate import odeint
import time
import multiprocessing
import hashlib
from operations import hash_data
import os

class Pendulum:
    def __init__(self, id, L1, L2, m1, m2, g, theta1, theta1_dot, theta2, theta2_dot, queue):
        self.id = id
        self.L1 = L1
        self.L2 = L2
        self.m1 = m1
        self.m2 = m2
        self.g = g
        self.y0 = [theta1, theta1_dot, theta2, theta2_dot]
        self.total_time = 0
        self.dt = 1  # one-second intervals
        self.running = multiprocessing.Value('b', True)  # Shared boolean value
        self.queue = queue  # Queue to store theta values

    def double_pendulum_equations(self, y, t):
        theta1, theta1_dot, theta2, theta2_dot = y
        delta_theta = theta2 - theta1

        denominator1 = (self.m1 + self.m2) * self.L1 - self.m2 * self.L1 * np.cos(delta_theta) * np.cos(delta_theta)
        denominator2 = (self.L2 / self.L1) * denominator1

        theta1_ddot = (self.m2 * self.L1 * theta1_dot * theta1_dot * np.sin(delta_theta) * np.cos(delta_theta) +
                       self.m2 * self.g * np.sin(theta2) * np.cos(delta_theta) +
                       self.m2 * self.L2 * theta2_dot * theta2_dot * np.sin(delta_theta) -
                       (self.m1 + self.m2) * self.g * np.sin(theta1)) / denominator1

        theta2_ddot = (-self.m2 * self.L2 * theta2_dot * theta2_dot * np.sin(delta_theta) * np.cos(delta_theta) +
                       (self.m1 + self.m2) * self.g * np.sin(theta1) * np.cos(delta_theta) -
                       (self.m1 + self.m2) * self.L1 * theta1_dot * theta1_dot * np.sin(delta_theta) -
                       (self.m1 + self.m2) * self.g * np.sin(theta2)) / denominator2

        return [theta1_dot, theta1_ddot, theta2_dot, theta2_ddot]

    def run_simulation(self, duration):
        t = np.linspace(self.total_time, self.total_time + duration, 100)
        sol = odeint(self.double_pendulum_equations, self.y0, t)
        self.y0 = sol[-1]
        self.total_time += duration
        # self.print_state()
        self.queue.put((self.y0[0], self.y0[2]))  # Put theta1 and theta2 in queue
        # time.sleep(1)

    def run_indefinitely(self):
        while self.running.value:
            self.run_simulation(self.dt)

    def stop(self):
        self.running.value = False

    def print_state(self):
        theta1_deg = self.y0[0]
        theta2_deg = self.y0[2]
        print(f"[{self.id}] Time: {self.total_time:.2f}s, Theta1: {theta1_deg}, Theta2: {theta2_deg}")

def consume_from_queue(queue, key_count):
    while True:
        # Consume 4 theta values from the queue (2 sets of theta1 and theta2)
        theta1_1, theta2_1 = queue.get()
        theta1_2, theta2_2 = queue.get()

        # # Hashing function
        # hash_result = hashlib.sha256(str([theta1_1, theta2_1, theta1_2, theta2_2]).encode()).hexdigest()
        hash_result = hash_data([(theta1_1, theta2_1), (theta1_2, theta2_2)])

        # Increment the key count
        with key_count.get_lock():
            key_count.value += 1

        # Print the hash result and write to keys.txt
        with open("keys.txt", "a") as f:
            f.write(f"{hash_result}\n")
        # print(f"\n[KEY] {hash_result}\n")
        # Print the current key count
        print(f"Total keys generated: {key_count.value}")

if __name__ == "__main__":
    # Create a shared queue for communication between pendulums and consumer
    shared_queue = multiprocessing.Queue()

    # Create a shared value for the key count
    key_count = multiprocessing.Value('i', 0)

    # Define ranges for the pendulum parameters
    MIN_L = 1
    MAX_L = 10
    MIN_M = 1
    MAX_M = 10
    MIN_G = 1
    MAX_G = 10
    MIN_THETA = -np.pi
    MAX_THETA = np.pi
    MIN_THETA_DOT = -1
    MAX_THETA_DOT = 1

    # Create 10 pendulums with random parameters
    pendulum1 = Pendulum(id=1, L1=np.random.uniform(MIN_L, MAX_L), L2=np.random.uniform(MIN_L, MAX_L), m1=np.random.uniform(MIN_M, MAX_M), m2=np.random.uniform(MIN_M, MAX_M), g=np.random.uniform(MIN_G, MAX_G), theta1=np.random.uniform(MIN_THETA, MAX_THETA), theta1_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), theta2=np.random.uniform(MIN_THETA, MAX_THETA), theta2_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), queue=shared_queue)
    pendulum2 = Pendulum(id=2, L1=np.random.uniform(MIN_L, MAX_L), L2=np.random.uniform(MIN_L, MAX_L), m1=np.random.uniform(MIN_M, MAX_M), m2=np.random.uniform(MIN_M, MAX_M), g=np.random.uniform(MIN_G, MAX_G), theta1=np.random.uniform(MIN_THETA, MAX_THETA), theta1_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), theta2=np.random.uniform(MIN_THETA, MAX_THETA), theta2_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), queue=shared_queue)
    pendulum3 = Pendulum(id=3, L1=np.random.uniform(MIN_L, MAX_L), L2=np.random.uniform(MIN_L, MAX_L), m1=np.random.uniform(MIN_M, MAX_M), m2=np.random.uniform(MIN_M, MAX_M), g=np.random.uniform(MIN_G, MAX_G), theta1=np.random.uniform(MIN_THETA, MAX_THETA), theta1_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), theta2=np.random.uniform(MIN_THETA, MAX_THETA), theta2_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), queue=shared_queue)
    pendulum4 = Pendulum(id=4, L1=np.random.uniform(MIN_L, MAX_L), L2=np.random.uniform(MIN_L, MAX_L), m1=np.random.uniform(MIN_M, MAX_M), m2=np.random.uniform(MIN_M, MAX_M), g=np.random.uniform(MIN_G, MAX_G), theta1=np.random.uniform(MIN_THETA, MAX_THETA), theta1_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), theta2=np.random.uniform(MIN_THETA, MAX_THETA), theta2_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), queue=shared_queue)
    pendulum5 = Pendulum(id=5, L1=np.random.uniform(MIN_L, MAX_L), L2=np.random.uniform(MIN_L, MAX_L), m1=np.random.uniform(MIN_M, MAX_M), m2=np.random.uniform(MIN_M, MAX_M), g=np.random.uniform(MIN_G, MAX_G), theta1=np.random.uniform(MIN_THETA, MAX_THETA), theta1_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), theta2=np.random.uniform(MIN_THETA, MAX_THETA), theta2_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), queue=shared_queue)
    pendulum6 = Pendulum(id=6, L1=np.random.uniform(MIN_L, MAX_L), L2=np.random.uniform(MIN_L, MAX_L), m1=np.random.uniform(MIN_M, MAX_M), m2=np.random.uniform(MIN_M, MAX_M), g=np.random.uniform(MIN_G, MAX_G), theta1=np.random.uniform(MIN_THETA, MAX_THETA), theta1_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), theta2=np.random.uniform(MIN_THETA, MAX_THETA), theta2_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), queue=shared_queue)
    pendulum7 = Pendulum(id=7, L1=np.random.uniform(MIN_L, MAX_L), L2=np.random.uniform(MIN_L, MAX_L), m1=np.random.uniform(MIN_M, MAX_M), m2=np.random.uniform(MIN_M, MAX_M), g=np.random.uniform(MIN_G, MAX_G), theta1=np.random.uniform(MIN_THETA, MAX_THETA), theta1_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), theta2=np.random.uniform(MIN_THETA, MAX_THETA), theta2_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), queue=shared_queue)
    pendulum8 = Pendulum(id=8, L1=np.random.uniform(MIN_L, MAX_L), L2=np.random.uniform(MIN_L, MAX_L), m1=np.random.uniform(MIN_M, MAX_M), m2=np.random.uniform(MIN_M, MAX_M), g=np.random.uniform(MIN_G, MAX_G), theta1=np.random.uniform(MIN_THETA, MAX_THETA), theta1_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), theta2=np.random.uniform(MIN_THETA, MAX_THETA), theta2_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), queue=shared_queue)
    pendulum9 = Pendulum(id=9, L1=np.random.uniform(MIN_L, MAX_L), L2=np.random.uniform(MIN_L, MAX_L), m1=np.random.uniform(MIN_M, MAX_M), m2=np.random.uniform(MIN_M, MAX_M), g=np.random.uniform(MIN_G, MAX_G), theta1=np.random.uniform(MIN_THETA, MAX_THETA), theta1_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), theta2=np.random.uniform(MIN_THETA, MAX_THETA), theta2_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), queue=shared_queue)    
    pendulum10 = Pendulum(id=10, L1=np.random.uniform(MIN_L, MAX_L), L2=np.random.uniform(MIN_L, MAX_L), m1=np.random.uniform(MIN_M, MAX_M), m2=np.random.uniform(MIN_M, MAX_M), g=np.random.uniform(MIN_G, MAX_G), theta1=np.random.uniform(MIN_THETA, MAX_THETA), theta1_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), theta2=np.random.uniform(MIN_THETA, MAX_THETA), theta2_dot=np.random.uniform(MIN_THETA_DOT, MAX_THETA_DOT), queue=shared_queue)

    # Clear the keys.txt file if it exists
    if os.path.exists("keys.txt"):
        with open("keys.txt", "w") as f:
            pass

    # Run the simulations indefinitely
    process1 = multiprocessing.Process(target=pendulum1.run_indefinitely)
    process2 = multiprocessing.Process(target=pendulum2.run_indefinitely)
    process3 = multiprocessing.Process(target=pendulum3.run_indefinitely)
    process4 = multiprocessing.Process(target=pendulum4.run_indefinitely)
    process5 = multiprocessing.Process(target=pendulum5.run_indefinitely)
    process6 = multiprocessing.Process(target=pendulum6.run_indefinitely)
    process7 = multiprocessing.Process(target=pendulum7.run_indefinitely)
    process8 = multiprocessing.Process(target=pendulum8.run_indefinitely)
    process9 = multiprocessing.Process(target=pendulum9.run_indefinitely)
    process10 = multiprocessing.Process(target=pendulum10.run_indefinitely)

    consumer_process = multiprocessing.Process(target=consume_from_queue, args=(shared_queue, key_count))

    process1.start()
    process2.start()
    process3.start()
    process4.start()
    process5.start()
    process6.start()
    process7.start()
    process8.start()
    process9.start()
    process10.start()
    consumer_process.start()

    # To stop the simulations, you can call pendulum1.stop() and pendulum2.stop()
    # For example, stop after 10 seconds
    time.sleep(10000000)
    pendulum1.stop()
    pendulum2.stop()
    pendulum3.stop()
    pendulum4.stop()
    pendulum5.stop()
    pendulum6.stop()
    pendulum7.stop()
    pendulum8.stop()
    pendulum9.stop()
    pendulum10.stop()

    # Wait for processes to finish
    process1.join()
    process2.join()
    process3.join()
    process4.join()
    process5.join()
    process6.join()
    process7.join()
    process8.join()
    process9.join()
    process10.join()

    # Stop the consumer (You can use a sentinel value to stop the consumer gracefully if needed)
    consumer_process.terminate()
    consumer_process.join()