import json
import os
from api_expansion import Expansion

class ConfigManager:
    def __init__(self, config_file='app_config.json'):
        """
        Initialize configuration manager
        
        Args:
            config_file (str): Configuration file path
        """
        self.expansion = Expansion()
        self.config_file = config_file
        self.config_data = {}
        self.load_config()

    def load_config(self):
        """
        Load configuration data from JSON file
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                # If file does not exist, create default configuration
                self.create_config_file()
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            # Create default configuration
            self.config_data = {}
    
    def save_config(self):
        """
        Save configuration data to JSON file
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving configuration file: {e}")
    
    def get_value(self, section, key):
        """
        Get configuration value
        
        Args:
            section (str): Configuration section name
            key (str): Configuration item name
            
        Returns:
            Configuration item value
        """
        return self.config_data.get(section, {}).get(key, None)
    
    def set_value(self, section, key, value):
        """
        Set configuration value
        
        Args:
            section (str): Configuration section name
            key (str): Configuration item name
            value: Value to set
        """
        if section not in self.config_data:
            self.config_data[section] = {}
        self.config_data[section][key] = value
    
    def get_section(self, section):
        """
        Get entire configuration section
        
        Args:
            section (str): Configuration section name
            
        Returns:
            dict: Configuration section data
        """
        self.load_config()
        return self.config_data.get(section, {})
    
    def set_section(self, section, data):
        """
        Set entire configuration section
        
        Args:
            section (str): Configuration section name
            data (dict): Data to set
        """
        self.config_data[section] = data
    
    def get_all_config(self):
        """
        Get all configuration data
        
        Returns:
            dict: All configuration data
        """
        return self.config_data
    
    def set_all_config(self, config_data):
        """
        Set all configuration data
        
        Args:
            config_data (dict): All configuration data
        """
        self.config_data = config_data
 
    def delete_config_file(self):
        """ Delete configuration file """
        try:
            os.remove(self.config_file)
        except Exception as e:
            print(f"Error deleting configuration file: {e}")

    def create_config_file(self):
        # Initialize default values
        led_mode_default = 0
        fan_mode_default = 0
        fan_temp_threshold_default = [30, 50, 3]
        fan_temp_speed_default = [75, 125, 175]
        fan_map_default = [0, 255]
        
        # Safely get configuration from expansion board
        try:
            led_mode = self.expansion.get_led_mode()
            if led_mode == 4:
                led_mode_default = 0
            elif led_mode == 3:
                led_mode_default = 1
            elif led_mode == 2:
                led_mode_default = 2
            elif led_mode == 1:
                led_mode_default = 3
            elif led_mode == 0:
                led_mode_default = 5
                
            fan_mode = self.expansion.get_fan_mode()
            if fan_mode == 2:
                fan_mode_default = 0
            elif fan_mode == 3:
                fan_mode_default = 1
            elif fan_mode == 1:
                fan_mode_default = 2
            elif fan_mode == 0:
                fan_mode_default = 4
                
            fan_temp_threshold_default = self.expansion.get_fan_threshold()
            fan_temp_speed_default = self.expansion.get_fan_temp_mode_speed()
            fan_map_default = self.expansion.get_fan_pi_following()
        except Exception as e:
            print(f"Error getting configuration from expansion board: {e}")
        try:
            if not os.path.exists(self.config_file):
                self.config_data = {
                    "Monitor": {
                        "screen_orientation": 0,
                        "follow_led_color": 0
                    },
                    "LED": {
                        "mode": led_mode_default,
                        "red_value": 0,
                        "green_value": 0,
                        "blue_value": 255,
                        "task_name": "task_led.py",
                        "is_run_on_startup": True
                    },
                    "Fan": {
                        "mode": fan_mode_default,
                        "mode1_fan_group1": 75,
                        "mode1_fan_group2": 75,
                        "mode1_fan_group3": 75,
                        "mode2_low_temp_threshold": fan_temp_threshold_default[0],
                        "mode2_high_temp_threshold": fan_temp_threshold_default[1],
                        "mode2_temp_schmitt": fan_temp_threshold_default[2],
                        "mode2_low_speed": fan_temp_speed_default[0],
                        "mode2_middle_speed": fan_temp_speed_default[1],
                        "mode2_high_speed": fan_temp_speed_default[2],
                        "mode3_min_speed_mapping": fan_map_default[0],
                        "mode3_max_speed_mapping": fan_map_default[1],
                        "task_name": "task_fan.py",
                        "is_run_on_startup": True
                    },
                    "OLED": {
                        "task_name": "task_oled.py",
                        "is_run_on_startup": True
                    },
                    "Service": {
                        "is_exist_on_rpi": False,
                        "is_run_on_startup": False
                    }
                }
                self.save_config()
            else:
                print(f"Configuration file already exists: {self.config_file}")
        except Exception as e:
            print(f"Error creating configuration file: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()


if __name__ == '__main__':
    # Create configuration manager instance (automatically loads configuration file)
    config_manager = ConfigManager('app_config.json')

    # Directly operate on all configuration data
    all_config = config_manager.get_all_config()
    print(f"All config: {all_config}")

    # Read configuration value
    led_mode = config_manager.get_value('LED', 'mode')
    print(f"LED Mode: {led_mode}")

    # Get entire configuration section
    fan_config = config_manager.get_section('Fan')
    print(f"FAN config: {fan_config}")

    # Modify configuration value
    config_manager.set_value('LED', 'mode', 1)
    config_manager.set_value('LED', 'red_value', 255)

    # Save modified configuration
    config_manager.save_config()

    # Get modified configuration data
    updated_config = config_manager.get_all_config()
    print(f"Updated config: {updated_config}")

    # Modify configuration value
    config_manager.set_value('LED', 'mode', 2)
    config_manager.set_value('LED', 'red_value', 0)

    # Save modified configuration
    config_manager.save_config()