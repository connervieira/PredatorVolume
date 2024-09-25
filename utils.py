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
        print("The configuration file doesn't appear to exist at '" + predator_root_directory + "/assets/config/configactive.json'.")
        exit()
except:
    print("The configuration database couldn't be loaded. It may be corrupted.")
    exit()

import cv2 # Required to process images/videos
import pytesseract # Required to read text from the OSD
from PIL import Image # Required to load images into pytesseract
import datetime # Required to convert human-friendly dates to Unix timestamps
import time



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
debugging_time_record = time.time() # Initialize the first debug message time as the current time.
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

def take_selection(options):
    selection = ""
    while selection not in options:
        selection = input("Selection: ")
        if (selection not in options):
            print("Please select a valid option from the list by entering the number associated with it")
    selection = int(selection) 


# This function determines if a given string is valid JSON.
def is_json(string, verbose=False):
    try:
        json_object = json.loads(string) # Try to load string as JSON information.
    except ValueError as error_message: # If the process fails, then the string is not valid JSON.
        if (verbose == True):
            print(error_message) # Print the error message that caused the JSON load to fail.
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




# This function returns the nearest timestamp key in dictionary to a given timestamp.
def closest_key(array, search_key):
    current_best = [0, time.time()]
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



# This function will read each frame of the supplied video until a time-stamp is detected. It returns the Unix timestamp of the first frame of the video.
def get_osd_time(video, verbose=False):
    bounding_box = config["behavior"]["metadata"]["time"]["overlay"]["bounding_box"]
    cap = cv2.VideoCapture(video) # Load this video as an OpenCV capture.
    video_frame_rate = int(cap.get(cv2.CAP_PROP_FPS)) # Get the video frame-rate.
    current_frame = 0
    timestamp = 0 # This is a placeholder that will be overwritten with the detected on-screen time as a Unix timestamp.
    while (cap.isOpened()):
        ret, frame = cap.read() # Get the next frame.
        if (ret == True):
            cropped = frame[bounding_box["y"]:bounding_box["y"]+bounding_box["h"],bounding_box["x"]:bounding_box["x"]+bounding_box["w"]] # Crop the frame down to the configured bounding box.
            gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY) # Convert the image to grayscale.
            _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY +cv2.THRESH_OTSU)
            text = pytesseract.image_to_string(Image.fromarray(thresholded), config='--psm 11') # Read the text from the image.
            text = text.strip() # Remove any leading or trailing whitespace.
            if len(text) > 0: # Check to see if text was recognized.
                if (verbose == True):
                    print(text)
                try:
                    date_object = datetime.datetime.strptime(text, config["behavior"]["metadata"]["time"]["overlay"]["format"])
                    timestamp = int(time.mktime(date_object.timetuple()))
                    adjusted_timestamp = timestamp - (current_frame * (1/video_frame_rate))
                    if (adjusted_timestamp > 0):
                        return adjusted_timestamp
                except Exception as e:
                    print(e)
                    continue

        else:
            break
        current_frame += 1
    display_message("Failed to determined video timestamp.", 2)
    return 0


# This function takes a video file-path, and uses character recognition to get the GPS information from the stamp within the provided bounding box. This function returns a frame-by-frame list of each GPS location.
def get_osd_gps(video, interval=1):
    bounding_box = config["behavior"]["metadata"]["gps"]["overlay"]["bounding_box"]
    cap = cv2.VideoCapture(video) # Load this video as an OpenCV capture.
    video_frame_rate = int(cap.get(cv2.CAP_PROP_FPS)) # Get the video frame-rate.
    video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Count the number of frames in the video.
    frame_interval = interval*video_frame_rate # Convert the interval from seconds to number of frames.
    current_frame = -1

    frame_locations = []

    while (cap.isOpened()):
        current_frame += 1
        ret, frame = cap.read() # Get the next frame.
        if (ret == True):
            if (current_frame % frame_interval == 0): # Check to see if we are on the frame interval before running analysis.
                cropped = frame[bounding_box["y"]:bounding_box["y"]+bounding_box["h"],bounding_box["x"]:bounding_box["x"]+bounding_box["w"]] # Crop the frame down to the configured bounding box.
                gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY) # Convert the image to grayscale.
                _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY +cv2.THRESH_OTSU)
                text = pytesseract.image_to_string(Image.fromarray(thresholded), config='--psm 11') # Read the text from the image.
                text = text.strip() # Remove any leading or trailing whitespace.

                # Replace commonly confused characters.
                text = text.replace("$", "S") 
                text = text.replace("F", "E") 
                text = text.replace(" . ", ".") 
                text = text.replace(". ", ".") 
                text = text.replace(" .", ".") 
                if len(text) > 0: # Check to see if text was recognized.
                    split_input = text.split()
                    if (len(split_input) == 2): # Check to make sure there are exactly two values (lat/lon)
                        split_input[0] = ''.join(c for c in split_input[0] if c.isdigit() or c in ['.', '-']) # Remove all non-numeric characters.
                        split_input[1] = ''.join(c for c in split_input[1] if c.isdigit() or c in ['.', '-']) # Remove all non-numeric characters.
                        location = {"lat": split_input[0], "lon": split_input[1]}
                    else:
                        location = {"lat": 0, "lon": 0}
                else:
                    location = {"lat": 0, "lon": 0}
        else: # Otherwise, the capture has dropped.
            break
        frame_locations.append(location)

    if (len(frame_locations) > video_frame_count): # Check to see if there are more frame locations than frames. This should never happen.
        display_message("There were more frame locations than frames in the video during GPS OSD analysis.", 3)
        frame_locations = [] # Clear the frame locations so they can be regenerated with place-holders.
    elif (len(frame_locations) > video_frame_count): # Check to see if there are fewer frame locations than frames. This should never happen.
        display_message("There were fewer frame locations than frames in the video during GPS OSD analysis.", 3)
        frame_locations = [] # Clear the frame locations so they can be regenerated with place-holders.

    while (len(frame_locations) < video_frame_count): # Run in a loop if there are fewer frame locations than frames, and fill them with place-holders.
        frame_locations.append({"lat": 0, "lon": 0})

    return frame_locations
