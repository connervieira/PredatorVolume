# Copyright (C) 2024 V0LT - Conner Vieira 

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License along with this program (LICENSE)
# If not, see https://www.gnu.org/licenses/ to read the license agreement.

import os
import json
import configuration

base_directory = str(os.path.dirname(os.path.realpath(__file__))) # This variable determines the absolute path of base project directory (the directory that contains this script).

try:
    if (os.path.exists(base_directory + "/assets/config/configactive.json")):
        config = json.load(open(base_directory + "/assets/config/configactive.json")) # Load the configuration from configactive.json
    else:
        print("The configuration file doesn't appear to exist at " + predator_root_directory + "/assets/config/config.json.")
        exit()
except:
    print("The configuration database couldn't be loaded. It may be corrupted.")
    exit()



# Define some styling information
class style:
    # Define colors
    purple = '\033[95m'
    cyan = '\033[96m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    gray = '\033[1;37m'
    red = '\033[91m'

    # Define text decoration
    bold = '\033[1m'
    underline = '\033[4m'
    italic = '\033[3m'
    faint = '\033[2m'

    # Define styling end marker
    end = '\033[0m'


import sys # Required to process command line arguments.
import time # Required to add delays and handle dates/times


# This function prints debug messages with time information.
debugging_time_record = 0
def debug_message(message):
    if (config["display"]["debug_messages"] == True): # Only print the message if the debugging output configuration value is set to true.
        global debugging_time_record
        time_since_last_message = (time.time()-debugging_time_record) # Calculate the time since the last debug message.
        print(f"{style.italic}{style.faint}{time.time():.10f} ({time_since_last_message:.10f}) - {message}{style.end}") # Print the message.
        debugging_time_record = time.time() # Record the current timestamp.


import datetime # Required for converting between timestamps and human readable date/time information
from xml.dom import minidom # Required for processing GPX data


# This function clears the console output.
def clear(force=False):
    if ("--headless" not in sys.argv): # Only clear the screen if headless mode is disabled.
        if (config["general"]["display"]["debugging_output"] == False or force == True): # Only clear the console if the debugging output configuration value is disabled.
            if name == 'posix': # For Unix-like systems (MacOS, Linux, etc.)
                os.system("clear")
            elif name == 'nt': # For Windows
                os.system("cls")


# This function determines if a given string is valid JSON.
def is_json(string):
    try:
        json_object = json.loads(string) # Try to load string as JSON information.
    except ValueError as error_message: # If the process fails, then the string is not valid JSON.
        return False # Return 'false' to indicate that the string is not JSON.

    return True # If the try statement is successful, then return 'true' to indicate that the string is valid JSON.


# This function saves a string to a file.
def save_to_file(file_name, contents):
    fh = None
    success = False
    try:
        fh = open(file_name, 'w')
        fh.write(contents)
        success = True   
    except IOError as e:
        success = False
    finally:
        try:
            if fh:
                fh.close()
        except:
            success = False
    return success



# This function is used to display system notices of varying levels.
def display_message(message, level=1):
    if (level == 1): # Display the message as a notice.
        print("Notice: " + message)
    elif (level == 2): # Display the message as a warning.
        print(style.yellow + "Warning: " + message + style.end)
    elif (level == 3): # Display the message as an error.
        print(style.red + "Error: " + message + style.end)
        prompt(style.faint + "Press enter to continue..." + style.end)


# This function determines if a value is a valid number.
def is_number(value):
    try:
        value = float(value)
        return True
    except ValueError:
        return False


# This function prompts the user for an input, and handles basic input validation.
def prompt(message, optional=True, input_type=str, default=""):
    if ("--headless" in sys.argv): # Check to see if the headless flag exists in the command line arguments.
        user_input = "" # Skip the user input and use a blank value.
    else:
        user_input = input(message) # Take the user's input.

    if ("--headless" in sys.argv or (optional == True and user_input == "")): # If the this input is optional, and the user left the input blank, then simply return the default value. Alternatively, if headless mode is enabled, then force the default value.
        if (input_type == str):
            return default
        elif (input_type == int):
            return int(default)
        elif (input_type == float):
            return float(default)
        elif (input_type == bool):
            if (type(default) != bool): # Check to see if the default is not a boolean value.
                return False # Default to returning `false`.
            else:
                return default
        elif (input_type == list):
            if (type(default) != list):
                return []
            else:
                return default

    if (optional == False): # If this input is not optional, then repeatedly take an input until an input is given.
        while (user_input == ""): # Repeated take the user's input until something is entered.
            display_message("This input is not optional.", 2)
            user_input = input(message)

    if (input_type == str):
        return str(user_input)

    elif (input_type == float or input_type == int):
        while (is_number(user_input) == False):
            display_message("The input needs to be a number.", 2)
            user_input = input(message)
        return float(user_input)

    elif (input_type == bool):
        if (len(user_input) > 0):
            if (user_input[0].lower() == "y" or user_input[0].lower() == "t" or user_input[0].lower() == "1"):
                user_input = True
            elif (user_input[0].lower() == "n" or user_input[0].lower() == "f" or user_input[0].lower() == "0"):
                user_input = False

        while (type(user_input) != bool): # Run repeatedly until the input is a boolean.
            display_message("The input needs to be a boolean.", 2)
            user_input = input(message)
            if (len(user_input) > 0):
                if (user_input[0].lower() == "y" or user_input[0].lower() == "t"):
                    user_input = True
                elif (user_input[0].lower() == "n" or user_input[0].lower() == "f"):
                    user_input = False

    elif (input_type == list):
        user_input = user_input.split(",") # Convert the user's input into a list.
        user_input = [element.strip() for element in user_input] # Strip any leading or trailing white space on each element in the list.

    return user_input




# This function is used to parse GPX files into a Python dictionary.
def process_gpx(gpx_file, modernize=False): # `gpx_file` is the absolute path to a GPX file. `modernize` determines if the timestamps will be offset such that the first timestamp is equal to the current time.
    gpx_file = open(gpx_file, 'r') # Open the GPX file.
    xmldoc = minidom.parse(gpx_file) # Read the full XML GPX document.

    track = xmldoc.getElementsByTagName('trkpt') # Get all of the location information from the GPX document.
    speed = xmldoc.getElementsByTagName('speed') # Get all of the speed information from the GPX document.
    altitude = xmldoc.getElementsByTagName('ele') # Get all of the elevation information from the GPX document.
    timing = xmldoc.getElementsByTagName('time') # Get all of the timing information from the GPX document.

    offset = 0 # This is the value that all timestamps in the file will be offset by.
    if (modernize == True): # Check to see if this GPX file should be modernized, such that the first entry in the file is the current time, and all subsequent points are offset by the same amount.
        first_point_time = str(timing[0].toxml().replace("<time>", "").replace("</time>", "").replace("Z", "").replace("T", " ")) # Get the time for the first point in human readable text format.

        first_point_time = round(time.mktime(datetime.datetime.strptime(first_point_time, "%Y-%m-%d %H:%M:%S").timetuple())) # Convert the human readable timestamp into a Unix timestamp.
        offset = get_time()-first_point_time # Calculate the offset to make the first point in this GPX file the current time.

    gpx_data = {} # This is a dictionary that will hold each location point, where the key is a timestamp.

    for i in range(0, len(track)): # Iterate through each point in the GPX file.
        point_lat = track[i].getAttribute('lat') # Get the latitude for this point.
        point_lon = track[i].getAttribute('lon') # Get the longitude for this point.
        try:
            point_speed = speed[i].toxml().replace("<speed>","").replace("</speed>","")
        except:
            point_speed = 0
        try:
            point_altitude = altitude[i].toxml().replace("<ele>","").replace("</ele>","")
        except:
            point_altitude = 0
        point_time = str(timing[i].toxml().replace("<time>", "").replace("</time>", "").replace("Z", "").replace("T", " ")) # Get the time for this point in human readable text format.

        point_time = round(time.mktime(datetime.datetime.strptime(point_time, "%Y-%m-%d %H:%M:%S").timetuple())) # Convert the human readable timestamp into a Unix timestamp.

        gpx_data[point_time + offset] = {"lat": float(point_lat), "lon": float(point_lon), "spd": float(point_speed), "alt": float(point_altitude)} # Add this point to the decoded GPX data.

    return gpx_data




# This function returns the nearest timestamp key in dictionary to a given timestamp.
def closest_key(array, search_key):
    current_best = [0, get_time()]
    for key in array: # Iterate through each timestamp in the given dictionary.
        difference = abs(float(search_key) - float(key)) # Calculate the difference in time between the given timestamp, and this timestamp.
        if (difference < current_best[1]): # Check to see if this entry is closer than the current best.
            current_best = [key, difference] # Make this entry the current best.

    return current_best # Return the closest found entry.



# This function takes the corners of a plate identified by the ALPR engine, and converts them to a bounding box.
# Example input: [{"x": 737, "y": 188}, {"x": 795, "y": 189}, {"x": 795, "y": 219}, {"x": 736, "y": 217}]
# Example output: {"x", 737, "y": 188, "w": 59, "h": 31}
def convert_corners_to_bounding_box(corners):
    if (len(corners) == 4): # Check to see if the number of corners is the expected length.
        all_x = [] # This will hold all X coordinates.
        all_y = [] # This will hold all Y coordinates.
        for corner in corners:
            all_x.append(int(corner["x"]))
            all_y.append(int(corner["y"]))
        
        bounding_box = {
            "x": int(min(all_x)),
            "y": int(min(all_y)),
            "w": int(max(all_x) - min(all_x)),
            "h": int(max(all_y) - min(all_y)),
        }
        return bounding_box
    else: # The number of corners is not the expected length.
        return False
