import os
import sys
import subprocess

def update_desktop_file():
    """
    Update desktop shortcut file and copy to user desktop
    """
    try:
        # Get the directory where the current script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Current directory: {current_dir}")
        
        # Build desktop file path
        desktop_file_path = os.path.join(current_dir, "Freenove.desktop")
        
        # Check if file exists
        if not os.path.exists(desktop_file_path):
            # Create desktop file content
            desktop_content = """[Desktop Entry]
Version=1.0
Type=Application
Name=Freenove Computer Case
Comment=Freenove Computer Case Kit Pro for Raspberry Pi
Exec=
Icon=
Terminal=false
Categories=Application;Development;
"""
            with open(desktop_file_path, 'w') as f:
                f.write(desktop_content)
            print("Created new desktop file")
        
        # Read file content
        try:
            with open(desktop_file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            # If UTF-8 decoding fails, try other encodings
            try:
                with open(desktop_file_path, 'r', encoding='latin-1') as file:
                    lines = file.readlines()
            except Exception as e:
                raise Exception(f"Unable to read file content: {e}")
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
        
        # Build new execution path - run the shell script
        run_script_path = os.path.join(current_dir, "run_app.sh")
        if not os.path.exists(run_script_path):
            raise FileNotFoundError(f"Script file {run_script_path} does not exist")
        new_exec_line = f"Exec=bash {run_script_path}\n"

        icon_path = os.path.join(current_dir, "Freenove_Logo.xpm")
        if not os.path.exists(icon_path):
            raise FileNotFoundError(f"Icon file {icon_path} does not exist")
        new_icon_line = f"Icon={icon_path}\n"
        
        # Modify file content
        exec_updated = False
        icon_updated = False
        
        for i, line in enumerate(lines):
            if line.startswith("Exec="):
                lines[i] = new_exec_line
                exec_updated = True
                print(f"Updated execution path: {new_exec_line.strip()}")
            elif line.startswith("Icon="):
                lines[i] = new_icon_line
                icon_updated = True
                print(f"Updated icon path: {new_icon_line.strip()}")
        
        if not exec_updated:
            print("Warning: Exec line not found for update")
        
        # Write modified content
        try:
            with open(desktop_file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            print("Desktop file updated successfully")
        except Exception as e:
            raise Exception(f"Error writing file: {e}")
        
        # Set file as executable
        try:
            os.chmod(desktop_file_path, 0o777)
            # Also make the run_app.sh script executable
            os.chmod(run_script_path, 0o755)
            print("Desktop file and script set as executable")
        except Exception as e:
            raise Exception(f"Error setting file permissions: {e}")
        
        # Get home directory path and build target path
        try:
            username = os.getlogin()
            home_dir = os.path.expanduser(f"~{username}")
        except Exception:
            # If getting username fails, use default pi user
            home_dir = "/home/pi"
            print("Warning: Unable to get current username, using default path /home/pi")
        
        desktop_dir = os.path.join(home_dir, "Desktop")
        
        # Ensure desktop directory exists
        if not os.path.exists(desktop_dir):
            try:
                os.makedirs(desktop_dir, mode=0o755, exist_ok=True)
                print(f"Created desktop directory: {desktop_dir}")
            except Exception as e:
                raise Exception(f"Failed to create desktop directory: {e}")
        
        # Check if desktop directory is valid and writable
        if not os.path.isdir(desktop_dir):
            raise Exception(f"Desktop directory {desktop_dir} is not a valid directory")
        
        if not os.access(desktop_dir, os.W_OK):
            raise Exception(f"Desktop directory {desktop_dir} does not have write permission")
        
        # Build destination file path
        destination_path = os.path.join(desktop_dir, "Freenove.desktop")

        # If destination file exists, delete it
        if os.path.exists(destination_path):
            try:
                os.remove(destination_path)
                print(f"Deleted existing desktop file: {destination_path}")
            except Exception as e:
                raise Exception(f"Failed to delete existing desktop file: {e}")
                
        # Copy file to desktop using file read/write
        try:
            with open(desktop_file_path, 'r', encoding='utf-8') as src_file:
                with open(destination_path, 'w', encoding='utf-8') as dst_file:
                    content = src_file.read()
                    dst_file.write(content)
            
            # Set permissions for copied file
            os.chmod(destination_path, 0o755)
            print(f"Successfully copied desktop file to: {destination_path}")
        except Exception as e:
            raise Exception(f"Error copying file to desktop: {e}")
        
        # Remove __pycache__ folder if it exists
        pycache_path = os.path.join(current_dir, "__pycache__")
        if os.path.exists(pycache_path) and os.path.isdir(pycache_path):
            try:
                # Recursively remove __pycache__ directory and its contents using os module
                for root, dirs, files in os.walk(pycache_path, topdown=False):
                    for file in files:
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        os.rmdir(dir_path)
                os.rmdir(pycache_path)
            except Exception as e:
                print(f"Warning: Failed to remove __pycache__ folder: {e}")
        return True
            
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        return False
    except PermissionError as e:
        print(f"Permission error: {e}")
        return False
    except Exception as e:
        print(f"Operation failed: {e}")
        return False


if __name__ == "__main__":
    success = update_desktop_file()
    if success:
        print("Desktop shortcut created successfully!")
        sys.exit(0)
    else:
        print("Desktop shortcut creation failed!")
        sys.exit(1)