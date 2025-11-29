import os
import sys
import time
import psutil
import atexit
import signal
import threading
import datetime
import socket

class SystemInformation:

    def __init__(self):
        pass

    def get_raspberry_pi_ip_address(self):
        """Get the IP address of the Raspberry Pi"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception:
            return "0.0.0.0"

    def get_raspberry_pi_date(self):
        """Get the current date in YYYY-MM-DD format using native Python datetime"""
        try:
            return datetime.date.today().strftime('%Y-%m-%d')
        except Exception:
            return "1990-1-1"

    def get_raspberry_pi_weekday(self):
        """Get the current weekday name using native Python datetime"""
        try:
            return datetime.date.today().strftime('%A')
        except Exception:
            return "Error"

    def get_raspberry_pi_time(self):
        """Get the current time in HH:MM:SS format using native Python datetime"""
        try:
            return datetime.datetime.now().strftime('%H:%M:%S')
        except Exception:
            return '0:0:0'

    def get_raspberry_pi_cpu_usage(self):
        """Get the CPU usage percentage"""
        try:
            return psutil.cpu_percent(interval=0)
        except Exception:
            return 0

    def get_raspberry_pi_memory_usage(self):
        """Get the memory usage percentage"""
        try:
            memory = psutil.virtual_memory()
            return [memory.percent,round(memory.used//1024//1024/1024,3),round(memory.total//1024//1024/1024,3)]
        except Exception:
            return 0

    def get_raspberry_pi_disk_usage(self, path='/'):
        """Get the disk usage percentage for all disk partitions"""
        try:
            total_used = 0
            total_size = 0
            
            # Get all disk partitions
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    # Get partition usage information
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_used += usage.used
                    total_size += usage.total
                except PermissionError:
                    # Some partitions may not have access permissions, skip
                    continue
                except Exception:
                    # Skip other exceptions
                    continue
            
            # If no partition information is found, return default values
            if total_size == 0:
                return [0, 0, 0]
            
            # Calculate total usage percentage
            total_percent = round((total_used / total_size) * 100, 2)
            
            # Convert to GB and round to appropriate decimal places
            used_gb = round(total_used / (1024**3), 3)
            total_gb = round(total_size / (1024**3), 3)
            
            return [total_percent, used_gb, total_gb]
        except Exception:
            return [0, 0, 0]

    def get_raspberry_pi_fan_duty(self, max_retries=3, retry_delay=0.1):
        """Get fan PWM using cached path and direct file read instead of subprocess"""
        for attempt in range(max_retries + 1):
            try:
                base_path = '/sys/devices/platform/cooling_fan/hwmon/'
                hwmon_dirs = [d for d in os.listdir(base_path) if d.startswith('hwmon')]
                if not hwmon_dirs:
                    raise FileNotFoundError("No hwmon directory found")
                fan_input_path = os.path.join(base_path, hwmon_dirs[0], 'pwm1')
                
                # Direct file read instead of subprocess
                with open(fan_input_path, 'r') as f:
                    pwm_value = int(f.read().strip())
                    return max(0, min(255, pwm_value))  # Clamp between 0-255
                    
            except (OSError, ValueError) as e:
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    return -1
            except Exception:
                return -1
        return -1

    def get_raspberry_pi_cpu_temperature(self):
        """Get the CPU temperature in Celsius using direct file read"""
        try:
            with open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r') as f:
                temp_raw = int(f.read().strip())
                return temp_raw / 1000.0
        except Exception:
            return 0


if __name__ == "__main__":
    system_information = SystemInformation()
    print(system_information.get_raspberry_pi_ip_address())
    print(system_information.get_raspberry_pi_date())
    print(system_information.get_raspberry_pi_weekday())
    print(system_information.get_raspberry_pi_time())
    print(system_information.get_raspberry_pi_cpu_usage())
    print(system_information.get_raspberry_pi_memory_usage())
    print(system_information.get_raspberry_pi_disk_usage())
    print(system_information.get_raspberry_pi_fan_duty())
    print(system_information.get_raspberry_pi_cpu_temperature())
    