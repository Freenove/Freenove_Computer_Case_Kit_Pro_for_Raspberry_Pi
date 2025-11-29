from api_expansion import Expansion
from api_systemInfo import SystemInformation
import threading
import atexit
import signal
import time
import sys

class FAN_TASK:

    def __init__(self):
        self.expansion = None
        self.cleanup_done = False
        self.stop_event = threading.Event()  # Keep for signal handling

        try:
            self.expansion = Expansion()                            # Initialize Expansion object
        except Exception as e:
            sys.exit(1)

        try:
            self.system_information = SystemInformation()
        except Exception as e:
            sys.exit(1)

        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

    def cleanup(self):
        # Perform cleanup operations
        if self.cleanup_done:
            return
        self.cleanup_done = True
        try:
            if self.expansion:
                self.expansion.set_fan_mode(0)
        except Exception as e:
            print(e)
        try:
            if self.expansion:
                self.expansion.set_fan_duty(0, 0, 0)
        except Exception as e:
            print(e)
        try:
            if self.expansion:
                self.expansion.end()
        except Exception as e:
            print(e)

    def handle_signal(self, signum, frame):
        # Handle signal to stop the application
        self.stop_event.set()
        self.cleanup()
        sys.exit(0)

    def run_fan_loop(self):
        """Main monitoring loop - single-threaded infinite loop for both OLED display and fan control"""
        self.expansion.set_fan_mode(1)
        self.expansion.set_fan_frequency(50000) 
        self.expansion.set_fan_duty(50, 50, 50)
        self.expansion.set_fan_threshold(50, 100)
        self.expansion.set_fan_temp_mode_speed(75, 125, 175)
        self.expansion.set_fan_pi_following(0, 100)
        self.expansion.set_fan_power_switch(1)
        while not self.stop_event.is_set():
            pi_duty = self.system_information.get_raspberry_pi_fan_duty()
            for i in range(0,255,1):
                self.expansion.set_fan_duty(i, i, i)
                time.sleep(0.01)
            for i in range(255,0,-1):
                self.expansion.set_fan_duty(i, i, i)
                time.sleep(0.01)
            

if __name__ == "__main__":
    fan_task= None
    try:
        fan_task = FAN_TASK()

        # Use simple infinite loop instead of threading
        fan_task.run_fan_loop()

    except KeyboardInterrupt:
        print("\nShutdown requested by user (Ctrl+C)")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if fan_task is not None:
            fan_task.stop_event.set()
            fan_task.cleanup()
    
