from monitor import GPUMonitor
import psutil
import time

print("Testing psutil...")
print(f"CPU Count: {psutil.cpu_count()}")
print(f"Per CPU: {psutil.cpu_percent(percpu=True)}")

m = GPUMonitor()
print("Fetching system stats...")
stats = m.get_system_stats()
print(stats)
print("Done.")
