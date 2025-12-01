# -*- coding: utf-8 -*-
import smbus
import time

class Expansion:
    IIC_ADDRESS = 0x21
    
    REG_I2C_ADDRESS = 0x00              # Set IIC address
    REG_LED_SPECIFIED = 0x01            # Set specified LED color
    REG_LED_ALL = 0x02                  # Set all LED colors
    REG_LED_MODE = 0x03                 # Set LED mode
    REG_FAN_MODE = 0x04                 # Set fan mode
    REG_FAN_FREQUENCY = 0x05            # Set fan frequency
    REG_FAN_DUTY = 0x06                 # Set fan duty cycle
    REG_FAN_THRESHOLD = 0x07            # Set temperature threshold
    REG_POWER_ON_CHECK = 0x08           # Set power on check function
    REG_FAN_TEMP_MODE_SPEED = 0x09      # Set fan auto mode three-stage speed
    REG_FAN_POWER_SWITCH = 0x0a         # Set fan power switch
    REG_FAN_PI_FOLLOWING = 0x0b         # Set fan to follow Raspberry Pi PWM duty cycle range

    REG_FAN_POWER_SWITCH_READ = 0xf0     # Get fan power switch status
    REG_FAN_TEMP_MODE_SPEED_READ = 0xf1  # Get fan auto mode three-stage speed
    REG_MOTOR_SPEED_READ = 0xf2          # Get fan motor speed
    REG_I2C_ADDRESS_READ = 0xf3          # Get I2C address
    REG_LED_SPECIFIED_READ = 0xf4        # Get specified LED color
    REG_LED_ALL_READ = 0xf5              # Get all LED colors
    REG_LED_MODE_READ = 0xf6             # Get LED mode
    REG_FAN_MODE_READ = 0xf7             # Get fan mode
    REG_FAN_FREQUENCY_READ = 0xf8        # Get fan frequency
    REG_FAN_DUTY_READ = 0xf9             # Get fan duty cycle
    REG_FAN_PI_FOLLOWING_READ = 0xfa     # Get fan following Raspberry Pi PWM duty cycle range value
    REG_FAN_THRESHOLD_READ = 0xfb        # Get temperature threshold
    REG_TEMP_READ = 0xfc                 # Get temperature
    REG_BRAND = 0xfd                     # Get brand
    REG_VERSION = 0xfe                   # Get version
    REG_SAVE_FLASH = 0xff                # Save data

    def __init__(self, bus_number=1, address=IIC_ADDRESS):
        # Initialize I2C bus and address
        self.bus_number = bus_number
        self.bus = smbus.SMBus(self.bus_number)
        self.address = address

    def write(self, reg, values):
        # Write data to I2C register
        try:
            if isinstance(values, list):
                self.bus.write_i2c_block_data(self.address, reg, values)
            else:
                self.bus.write_byte_data(self.address, reg, values)
        except IOError as e:
            #print("Error writing to I2C bus:", e)
            pass

    def read(self, reg, length=1):
        # Read data from I2C register
        if length == 1:
            return self.bus.read_byte_data(self.address, reg)
        else:
            return self.bus.read_i2c_block_data(self.address, reg, length)

    def end(self):
        # Close I2C bus
        self.bus.close()

    def set_i2c_addr(self, addr):
        # Set I2C address
        self.address = addr
        cmd = [0xaa, 0xbb, self.address]
        self.write(self.REG_I2C_ADDRESS, cmd)

    def set_led_color(self, led_id, r, g, b):
        # Set color for specified LED
        cmd = [led_id, r, g, b]
        self.write(self.REG_LED_SPECIFIED, cmd)

    def set_all_led_color(self, r, g, b):
        # Set color for all LEDs
        cmd = [r, g, b]
        self.write(self.REG_LED_ALL, cmd)

    def set_led_mode(self, mode):
        # Set LED running mode
        self.write(self.REG_LED_MODE, mode)

    def set_fan_mode(self, mode):
        # Set fan running mode
        self.write(self.REG_FAN_MODE, mode)

    def set_fan_frequency(self, freq):
        # Set fan frequency
        frequency = [
            freq & 0xFF,
            (freq >> 8) & 0xFF,
            (freq >> 16) & 0xFF,
            (freq >> 24) & 0xFF
        ]
        self.write(self.REG_FAN_FREQUENCY, frequency)

    def set_fan_duty(self, duty0, duty1, duty2):
        # Set fan duty cycle
        duty = [duty0, duty1, duty2]
        self.write(self.REG_FAN_DUTY, duty)

    def set_fan_threshold(self, low_threshold, high_threshold, schmitt = 3):
        # Set fan temperature threshold
        cmd = [low_threshold, high_threshold, schmitt]
        self.write(self.REG_FAN_THRESHOLD, cmd)

    def set_power_on_check(self, state):
        # Set power-on check state
        self.write(self.REG_POWER_ON_CHECK, state)

    def set_fan_temp_mode_speed(self, low_speed, mid_speed, high_speed):
        # Set fan temperature mode speed
        cmd = [low_speed, mid_speed, high_speed]
        self.write(self.REG_FAN_TEMP_MODE_SPEED, cmd)

    def set_fan_power_switch(self, state):
        # Set fan power switch state
        self.write(self.REG_FAN_POWER_SWITCH, state)

    def set_fan_pi_following(self, min_duty, max_duty):
        # Set fan PI following state
        cmd = [min_duty, max_duty]
        self.write(self.REG_FAN_PI_FOLLOWING, cmd)

    def get_fan_power_switch(self):
        # Get fan power switch state
        return self.read(self.REG_FAN_POWER_SWITCH_READ)

    def get_fan_temp_mode_speed(self):
        # Get fan temperature mode speed
        return self.read(self.REG_FAN_TEMP_MODE_SPEED_READ, 3)

    def get_motor_speed(self):
        # Get fan motor speed
        buf = self.read(self.REG_MOTOR_SPEED_READ, 10)
        speed = [(buf[i*2+1]<<8) | buf[i*2] for i in range(5)]
        return speed

    def get_iic_addr(self):
        # Get I2C address
        return self.read(self.REG_I2C_ADDRESS_READ)

    def get_led_color(self, led_id):
        # Get color for specified LED
        self.write(self.REG_LED_SPECIFIED, led_id)
        return self.read(self.REG_LED_SPECIFIED_READ, 3)

    def get_all_led_color(self):
        # Get color for all LEDs
        return self.read(self.REG_LED_ALL_READ, 18)

    def get_led_mode(self):
        # Get LED running mode
        return self.read(self.REG_LED_MODE_READ)

    def get_fan_mode(self):
        # Get fan running mode
        return self.read(self.REG_FAN_MODE_READ)

    def get_fan_frequency(self):
        # Get fan frequency
        arr = self.read(self.REG_FAN_FREQUENCY_READ, 4)
        freq = (arr[3] << 24) | (arr[2] << 16) | (arr[1] << 8) | arr[0]
        return freq

    def get_fan_duty(self):
        # Get fan duty cycle 1 value
        return self.read(self.REG_FAN_DUTY_READ, 3)

    def get_fan_pi_following(self):
        # Get fan PI following state
        return self.read(self.REG_FAN_PI_FOLLOWING_READ, 2)

    def get_fan_threshold(self):
        # Get fan temperature threshold
        return self.read(self.REG_FAN_THRESHOLD_READ, 3)

    def get_temp(self):
        # Get temperature value
        return self.read(self.REG_TEMP_READ)

    def get_brand(self):
        # Get brand information
        brand_bytes = self.read(self.REG_BRAND, 9)
        return ''.join(chr(b) for b in brand_bytes).rstrip('\x00')

    def get_version(self):
        # Get version information
        version_bytes = self.read(self.REG_VERSION, 14)
        return ''.join(chr(b) for b in version_bytes).rstrip('\x00')

    def set_save_flash(self, state):
        # Save configuration to flash
        self.write(self.REG_SAVE_FLASH, state)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()

if __name__ == '__main__':
    expansion_board = Expansion()
    try:
        '''
        # Below is the default configuration for extension, which you can comment out if you are not using it.
        # As long as expansion_board.set_save_flash(1) is not used, 
        # all configurations will be temporary,
        # and will revert to default Settings when expansion_board.set_save_flash(1) is powered off.
        '''
        ''''
        print("Config expansion board ...")
        expansion_board.set_i2c_addr(expansion_board.IIC_ADDRESS)  # set i2c address
        expansion_board.set_all_led_color(0, 0, 50)                # set all led color: r,g,b. 0~255
        expansion_board.set_led_mode(4)                            # led mode: 0: close, 1: RGB, 2: Following, 3: Breathing, 4: Rainbow
        expansion_board.set_fan_mode(3)                            # fan mode: 0: close, 1: Manual Mode, 2: Auto Temp Mode, 3: PI PWM Following Mode
        expansion_board.set_fan_frequency(50000)                   # Set fan frequency, 100-1000000
        expansion_board.set_fan_duty(0, 0, 0)                      # Set the fan1 fan2 fan3 duty cycle, 0~255
        expansion_board.set_fan_threshold(30, 50, 3)               # Set the temperature threshold, (low temperature, high temperature)
        expansion_board.set_fan_temp_mode_speed(75, 125, 175)      # Set fan temperature mode speed, (low duty, mid duty, high duty), 0~255
        expansion_board.set_fan_pi_following(0, 150)               # Set fan PI following map value, (min duty, max duty), 0~255
        expansion_board.set_power_on_check(1)                      # Set power-on check state, 1: Enable, 0: Disable
        expansion_board.set_fan_power_switch(1)                    # Set fan power switch, 1: Enable, 0: Disable
        expansion_board.set_save_flash(1)                          # Save configuration to flash, 1: Enable, 0: Disable
        time.sleep(0.5)
        print("Config expansion board done!")
        '''

        count = 0
        direction = 1
        expansion_board.set_led_mode(3)                       # led mode: 0: close, 1: RGB, 2: Following, 3: Breathing, 4: Rainbow
        expansion_board.set_all_led_color(0, 50, 0)           # set all led color: r,g,b. 0~255
        expansion_board.set_fan_power_switch(1)               # Set fan power switch
        expansion_board.set_fan_mode(3)                       # fan mode: 0: close, 1: Manual Mode, 2: Auto Temp Mode, 3: PI PWM Following Mode
        expansion_board.set_fan_frequency(50000)              # Set fan frequency (fan mode 1)
        expansion_board.set_fan_duty(255, 255, 255)              # Set the fan duty cycle (fan mode 1)
        expansion_board.set_fan_threshold(30, 50, 3)          # Set the temperature threshold (fan mode 2)
        expansion_board.set_fan_temp_mode_speed(75, 125, 175) # Set fan temperature mode speed (fan mode 2)
        expansion_board.set_fan_pi_following(0, 255)          # Set fan PI following map value (fan mode 3)   
        time.sleep(3)
        while True:
            if direction == 1:
                if count >= 250:
                    direction = -1
            else:
                if count <= 10:
                    direction = 1
            count = count + direction
            if count % 10 == 0:
                print("get iic addr: 0x{:02X}".format(expansion_board.get_iic_addr()))
                print("get all led color:", expansion_board.get_all_led_color())
                print("get led mode:", expansion_board.get_led_mode())
                print("get fan mode:", expansion_board.get_fan_mode())
                print("get fan frequency:", expansion_board.get_fan_frequency())
                print("get fan duty:", expansion_board.get_fan_duty())
                print("get fan threshold:", expansion_board.get_fan_threshold())
                print("get fan pi following:", expansion_board.get_fan_pi_following())
                print("get fan power switch:", expansion_board.get_fan_power_switch())
                print("get temp:", expansion_board.get_temp())
                print("get brand:", expansion_board.get_brand())
                print("get version:", expansion_board.get_version())
                #expansion_board.set_fan_duty(count, count, count)
                print("get motor speed: ", expansion_board.get_motor_speed())
                print("")
            time.sleep(0.01)

    except Exception as e:
        print("Exception:", e)
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
    finally:
        expansion_board.set_led_mode(4)
        expansion_board.set_all_led_color(0, 0, 0)
        expansion_board.set_fan_mode(3)
        expansion_board.set_fan_duty(0, 0, 0)
        expansion_board.end()