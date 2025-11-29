from api_oled import OLED
from api_expansion import Expansion
from api_systemInfo import SystemInformation
import threading
import atexit
import signal
import time
import sys

class OLED_TASK:

    def __init__(self):
        # Initialize OLED and Expansion objects
        self.oled = None
        self.expansion = None
        self.font_size = 12
        self.cleanup_done = False
        self.stop_event = threading.Event()  # Keep for signal handling
        
        # Cache hwmon path lookup for performance
        self._fan_pwm_path = None

        try:
            self.oled = OLED(rotate_angle=180)
        except Exception as e:
            sys.exit(1)

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


    def get_computer_temperature(self):
        # Get the computer temperature using Expansion object
        try:
            return self.expansion.get_temp()
        except Exception as e:
            return 0

    def get_computer_fan_mode(self):
        # Get the computer fan mode using Expansion object
        try:
            return self.expansion.get_fan_mode()
        except Exception as e:
            return 0

    def get_computer_fan_duty(self):
        # Get the computer fan duty cycle using Expansion object
        try:
            return self.expansion.get_fan_duty()
        except Exception as e:
            return 0

    def get_computer_led_mode(self):
        # Get the computer LED mode using Expansion object
        try:
            return self.expansion.get_led_mode()
        except Exception as e:
            return 0
    
    def set_computer_fan_duty(self, duty):
        """Set the fan duty cycle for the computer"""
        try:
            self.expansion.set_fan_duty(duty[0], duty[1], duty[2])
        except Exception as e:
            print(e)

    def cleanup(self):
        # Perform cleanup operations
        if self.cleanup_done:
            return
        self.cleanup_done = True
        try:
            if self.oled:
                self.oled.close()
        except Exception as e:
            print(e)
    def handle_signal(self, signum, frame):
        # Handle signal to stop the application
        self.stop_event.set()
        self.cleanup()
        sys.exit(0)

    def oled_ui_1_show(self, date, weekday, time):
        self.oled.clear()
        # Draw a large box, same size as screen, no fill, then draw 2 horizontal lines, dividing into 3 rows
        self.oled.draw_rectangle((0, 0, self.oled.width-1, self.oled.height-1), outline="white")
        self.oled.draw_line(((0, 16), (self.oled.width-1, 16)), fill="white")
        self.oled.draw_line(((0, 48), (self.oled.width-1, 48)), fill="white")
        # First row writes date, second row writes time, third row writes weekday
        self.oled.draw_text(date, position=((0,0),(128,16)), directory="center", offset=(0, 1), font_size=self.font_size)
        self.oled.draw_text(time, position=((0,16),(128,48)), directory="center", offset=(0, 2), font_size=24)
        self.oled.draw_text(weekday, position=((0,48),(128,64)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.show()
    
    def oled_ui_2_show(self, ip_address, cpu_usage, memory_usage, disk_usage):
        self.oled.clear()
        # Draw basic interface outline
        self.oled.draw_rectangle((0, 0, self.oled.width-1, self.oled.height-1), outline="white")
        self.oled.draw_line(((0, 16), (self.oled.width-1, 16)), fill="white")
        self.oled.draw_line(((43,16),(43, self.oled.height-1)), fill="white")
        self.oled.draw_line(((86,16),(86, self.oled.height-1)), fill="white")
        # Write Raspberry Pi IP address in first row, write "CPU" in first box of second row, "MEM" in second box, "DISK" in third box
        self.oled.draw_text("IP:"+ip_address, position=((0,0),(128,16)),  directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.draw_text("CPU",  position=((0,16),(42,32)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.draw_text("MEM",  position=((43,16),(86,32)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.draw_text("DISK", position=((87,16),(128,32)), directory="center", offset=(0, 0), font_size=self.font_size)
        # Put CPU usage in first box of third row, memory usage in second box, disk usage in third box
        self.oled.draw_circle_with_percentage((21,46), 16, cpu_usage, outline="white", fill="white")
        self.oled.draw_circle_with_percentage((64,46), 16, memory_usage, outline="white", fill="white")
        self.oled.draw_circle_with_percentage((107,46), 16, disk_usage, outline="white", fill="white")
        self.oled.show()
    
    def oled_ui_3_show(self, pi_temperature, cpu_temperature):
        self.oled.clear()
        # Draw basic interface outline
        self.oled.draw_rectangle((0, 0, self.oled.width-1, self.oled.height-1), outline="white")
        self.oled.draw_line(((64, 0), (64, self.oled.height-1)), fill="white")
        # First row first column shows Pi temperature, first row second column shows PC temperature
        self.oled.draw_text("Pi", position=((0,0),(64,16)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.draw_text("Case", position=((65,0),(128,16)), directory="center", offset=(0, 0), font_size=self.font_size)
        # Draw a dial in the center of each column of the second row
        self.oled.draw_dial(center_xy=(32,34), radius=16, angle=(225, 315), directory="CW", tick_count=10, percentage=pi_temperature, start_value=0, end_value=100)
        self.oled.draw_dial(center_xy=(96,34), radius=16, angle=(225, 315), directory="CW", tick_count=10, percentage=cpu_temperature, start_value=0, end_value=100)
        # First row first column shows Pi temperature, first row second column shows CPU temperature
        self.oled.draw_text("{}℃".format(round(pi_temperature)), position=((0,48),(64,64)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.draw_text("{}℃".format(cpu_temperature), position=((65,48),(128,64)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.show()

    def oled_ui_4_show(self, duty):
        self.oled.clear()
        # Draw basic interface outline
        self.oled.draw_rectangle((0, 0, self.oled.width-1, self.oled.height-1), outline="white")
        self.oled.draw_line(((43, 0), (43, self.oled.height-1)), fill="white")
        self.oled.draw_line(((86, 0), (86, self.oled.height-1)), fill="white")
        # Write titles in first row
        self.oled.draw_text("Pi",  position=((0,0),(42,16)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.draw_text("C1",  position=((43,0),(86,16)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.draw_text("C2",  position=((87,0),(128,16)), directory="center", offset=(0, 0), font_size=self.font_size)
        # Draw dials in second row
        percentage_value = [round(duty[i]/255*100) for i in range(3)]
        self.oled.draw_dial(center_xy=(21,34), radius=16, angle=(225, 315), directory="CW", tick_count=10, percentage=percentage_value[0], start_value=0, end_value=100)
        self.oled.draw_dial(center_xy=(63,34), radius=16, angle=(225, 315), directory="CW", tick_count=10, percentage=percentage_value[1], start_value=0, end_value=100)
        self.oled.draw_dial(center_xy=(105,34), radius=16, angle=(225, 315), directory="CW", tick_count=10, percentage=percentage_value[2], start_value=0, end_value=100)
        # Print duty cycle percentage values in third row
        self.oled.draw_text("{}%".format(percentage_value[0]), position=((0,48),(42,64)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.draw_text("{}%".format(percentage_value[1]), position=((43,48),(85,64)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.draw_text("{}%".format(percentage_value[2]), position=((86,48),(128,64)), directory="center", offset=(0, 0), font_size=self.font_size)
        self.oled.show()

    def run_oled_loop(self):
        """Main monitoring loop - single-threaded infinite loop for both OLED display and fan control"""
        oled_counter = 0  # Counter to control OLED update frequency
        screen_start_time = time.time()  # 记录当前屏幕开始显示的时间
        current_screen = 0  # 当前显示的屏幕索引
        screen_duration = 3.0  # 每个屏幕显示3秒
        
        while not self.stop_event.is_set():
            # Update data every 0.3 seconds
            current_date = self.system_information.get_raspberry_pi_date()
            current_weekday = self.system_information.get_raspberry_pi_weekday()
            current_time = self.system_information.get_raspberry_pi_time()
            ip_address = self.system_information.get_raspberry_pi_ip_address()
            cpu_usage = self.system_information.get_raspberry_pi_cpu_usage()
            memory_usage = self.system_information.get_raspberry_pi_memory_usage()
            disk_usage = self.system_information.get_raspberry_pi_disk_usage()
            cpu_temperature = self.system_information.get_raspberry_pi_cpu_temperature()

            computer_temperature = self.get_computer_temperature()
            led_mode = self.get_computer_led_mode() 
            fan_mode = self.get_computer_fan_mode()
            computer_fan_duty = self.get_computer_fan_duty()
            current_pi_duty = self.system_information.get_raspberry_pi_fan_duty()
            
            # 检查是否需要切换屏幕（基于时间而不是计数器）
            elapsed_time = time.time() - screen_start_time
            if elapsed_time >= screen_duration:
                current_screen = (current_screen + 1) % 4
                screen_start_time = time.time()
            
            # Update OLED every 0.3 seconds
            try:
                # 使用稳定的current_screen变量来决定显示哪个界面
                if current_screen == 0:
                    self.oled_ui_1_show(current_date, current_weekday, current_time)
                elif current_screen == 1:
                    self.oled_ui_2_show(ip_address, cpu_usage, memory_usage[0], disk_usage[0])
                elif current_screen == 2:
                    self.oled_ui_3_show(cpu_temperature, computer_temperature)
                elif current_screen == 3:
                    duty = [current_pi_duty, computer_fan_duty[0], computer_fan_duty[1]]
                    self.oled_ui_4_show(duty)
            except Exception as e:
                print(e)
            
            # # Print data every 4 updates (1.2 seconds)
            # if oled_counter % 4 == 0:
            #     # Use single print statement to reduce I/O
            #     print("raspberry today:        ", current_date)
            #     print("raspberry weekday:      ", current_weekday)
            #     print("raspberry current time: ", current_time)
            #     print("raspberry ip address:   ", ip_address) 
            #     print("raspberry cpu usage:     {}%".format(cpu_usage))
            #     print("raspberry memory usage:  {}% (used: {} G, totol: {} G)".format(memory_usage[0], memory_usage[1], memory_usage[2]))
            #     print("raspberry disk usage:    {}% (used: {} G, totol: {} G)".format(disk_usage[0], disk_usage[1], disk_usage[2]))
            #     print("raspberry temperature:   {}℃".format(cpu_temperature))
            #     print("computer temperature:    {}℃".format(computer_temperature))
            #     print("computer led mode:      ", led_mode)
            #     print("computer fan mode:      ", fan_mode)
            #     print("raspberry fan duty:     ", current_pi_duty)
            #     print("computer fan duty:      ", computer_fan_duty)
            #     print("")
            
            # oled_counter += 1
            time.sleep(0.3)  # Base interval of 0.3 second


if __name__ == "__main__":
    oled_task= None
    try:
        oled_task = OLED_TASK()

        # Use simple infinite loop instead of threading
        oled_task.run_oled_loop()

    except KeyboardInterrupt:
        print("\nShutdown requested by user (Ctrl+C)")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if oled_task is not None:
            oled_task.stop_event.set()
            oled_task.cleanup()
    