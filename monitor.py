import pynvml
import psutil
from typing import List, Dict, Any

class GPUMonitor:
    def __init__(self):
        try:
            pynvml.nvmlInit()
            self.driver_version = pynvml.nvmlSystemGetDriverVersion()
            self.device_count = pynvml.nvmlDeviceGetCount()
        except pynvml.NVMLError as err:
            print(f"Failed to initialize NVML: {err}")
            self.device_count = 0

    def get_system_stats(self) -> Dict[str, Any]:
        """Fetch host system stats: CPU per core, RAM, Swap."""
        cpu_percent = psutil.cpu_percent(percpu=True)
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        
        return {
            "cpu_percent": cpu_percent, # List[float]
            "memory": {
                "total": virtual_mem.total,
                "used": virtual_mem.used,
                "percent": virtual_mem.percent,
            },
            "swap": {
                "total": swap_mem.total,
                "used": swap_mem.used,
                "percent": swap_mem.percent,
            }
        }

    def get_gpu_stats(self) -> List[Dict[str, Any]]:
        stats = []
        for i in range(self.device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            
            # Name
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
                
            # Utilization
            try:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_util = util.gpu
                mem_util = util.memory
            except pynvml.NVMLError:
                gpu_util = 0
                mem_util = 0
            
            # Memory Info
            try:
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                mem_total = mem_info.total
                mem_used = mem_info.used
                mem_free = mem_info.free
            except pynvml.NVMLError:
                mem_total = 0
                mem_used = 0
                mem_free = 0

            # Temperature
            try:
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except pynvml.NVMLError:
                temp = 0
                
            # Fan Speed
            try:
                fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
            except pynvml.NVMLError:
                fan_speed = 0

            # Power Usage
            try:
                power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0 # mW to W
                power_limit = pynvml.nvmlDeviceGetEnforcedPowerLimit(handle) / 1000.0
            except pynvml.NVMLError:
                power_usage = 0
                power_limit = 0

            stats.append({
                "index": i,
                "name": name,
                "gpu_util": gpu_util,
                "memory_util_percent": mem_util,
                "memory_total": mem_total,
                "memory_used": mem_used,
                "memory_free": mem_free,
                "temperature": temp,
                "fan_speed": fan_speed,
                "power_usage": power_usage,
                "power_limit": power_limit
            })
        return stats

    def get_processes(self) -> List[Dict[str, Any]]:
        processes_info = []
        for i in range(self.device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            try:
                # This returns list of nvmlProcessInfo_t
                procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)
                # Also graphics processes
                graphics_procs = pynvml.nvmlDeviceGetGraphicsRunningProcesses(handle)
                
                # Merge and unique by pid
                all_procs = {p.pid: p for p in procs + graphics_procs}
                
                for pid, p in all_procs.items():
                    name = "Unknown"
                    try:
                        name = pynvml.nvmlSystemGetProcessName(pid)
                        if isinstance(name, bytes):
                            name = name.decode('utf-8')
                    except pynvml.NVMLError:
                        pass
                        
                    processes_info.append({
                        "pid": pid,
                        "gpu_index": i,
                        "memory_used": p.usedGpuMemory, # in bytes
                        "name": name
                    })
            except pynvml.NVMLError:
                continue
                
        return processes_info

    def close(self):
        try:
            pynvml.nvmlShutdown()
        except:
            pass

