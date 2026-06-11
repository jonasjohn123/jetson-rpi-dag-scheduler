from scheduler.profile_loader import (
    load_profiles
)

workers, exec_cost, comm_cost = (
    load_profiles()
)

print("Workers")
print(workers)

print()

print("Execution Cost")
print(exec_cost)

print()

print("Communication Cost")
print(comm_cost)