# Copyright (C) 2024 V0LT - Conner Vieira 

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License along with this program (LICENSE)
# If not, see https://www.gnu.org/licenses/ to read the license agreement.

import os
import json
import configuration
import math

base_directory = str(os.path.dirname(os.path.realpath(__file__))) # This variable determines the absolute path of base project directory (the directory that contains this script).

try:
    if (os.path.exists(base_directory + "/assets/config/configactive.json")):
        config = json.load(open(base_directory + "/assets/config/configactive.json")) # Load the configuration from configactive.json
    else:
        print("The configuration file doesn't appear to exist at '" + base_directory + "/assets/config/configactive.json'.")
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
        if (config["display"]["debug_messages"] == False): # Don't clear the screen if debug output is enabled.
            if os.name == 'posix': # For Unix-like systems (MacOS, Linux, etc.)
                os.system("clear")
            elif os.name == 'nt': # For Windows
                os.system("cls")

# This function takes the user's input selection given a list of valid menu options.
def take_selection(options):
    selection = -1
    while selection not in options:
        selection = input("Selection: ")
        try:
            selection = int(selection) 
        except:
            selection = -1
        if (selection not in options):
            display_message("Please select a valid option from the list by entering the number associated with it.", 2)
    return selection


# This function prompts the user to enter the path to an existing directory.
def input_directory(text_prompt="Directory: "):
    directory = "" # This is a placeholder that will be overwritten with the user's input.
    while (directory == "" or os.path.isdir(directory) == False): # Repeatedly prompt the user to enter a valid working directory until a valid response is given.
        directory = prompt(text_prompt, optional=False)
        if (os.path.isfile(directory) == True): # Check to see if the specified path is a file.
            display_message("The specified path points to a file, not a directory.", 2)
        elif (os.path.exists(directory) == False): # Check to see if the specified path does not exist.
            display_message("The specified path does not exist.", 2)
    return directory


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
    debug_message("Waiting for user input")
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


# This function counts the number of frames in a given video file.
def count_frames(video):
    debug_message("Counting frames")
    cap = cv2.VideoCapture(video)
    if (config["behavior"]["optimization"]["frame_counting"]["method"] == "default"):
        video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Count the number of frames in the video.
    elif (config["behavior"]["optimization"]["frame_counting"]["method"] == "custom"):
        video_frame_count = 0
        while (cap.isOpened()):
            video_frame_count += 1
            ret, frame = cap.read() # Get the next frame.
            if (ret == False):
                break
    else:
        display_message("Invalid frame count method.", 3)
        video_frame_count = 0
    return video_frame_count



# This function will read each frame of the supplied video until a time-stamp is detected. It returns the Unix timestamp of the first frame of the video.
def get_osd_time(video, verbose=False):
    debug_message("Analyzing time overlay stamp")
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
                    continue

        else:
            break
        current_frame += 1
    display_message("Failed to determined video timestamp.", 2)
    return 0


# This function takes a video file-path, and uses character recognition to get the GPS information from the stamp within the provided bounding box. This function returns a frame-by-frame list of each GPS location.
def get_osd_gps(video, interval=1):
    bounding_box = config["behavior"]["metadata"]["gps"]["overlay"]["bounding_box"]
    video_frame_count = count_frames(video)
    debug_message("Analyzing GPS overlay stamp")
    cap = cv2.VideoCapture(video) # Load this video as an OpenCV capture.
    video_frame_rate = int(cap.get(cv2.CAP_PROP_FPS)) # Get the video frame-rate.
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
                text = text.replace("$", "S") 
                text = text.replace("F", "E") 
                text = text.replace("T", "E") 
                text = text.replace("O", "0") 
                text = text.replace(" . ", ".") 
                text = text.replace(". ", ".") 
                text = text.replace(" .", ".") 
                if len(text) > 0: # Check to see if text was recognized.
                    split_input = text.split()
                    if (len(split_input) == 2): # Check to make sure there are exactly two values (latitude and longitude)
                        split_input[0] = split_input[0].upper() # Convert to uppercase.
                        split_input[1] = split_input[1].upper() # Convert to uppercase.
                        if (("N" in split_input[1] or "S" in split_input[1]) and ("E" in split_input[0] or "W" in split_input[0])): # Check to see if the latitude and longitude coordinates are swapped.
                            # Swap the coordinates back to the expected order:
                            temp_split_input_0 = split_input[0]
                            split_input[0] = split_input[1]
                            split_input[1] = temp_split_input_0
                            del temp_split_input_0 # Delete the temporary value.
                        if ("S" in split_input[0] and "-" not in split_input[0]): # Check to see if this is a southern coordinate, but there is no negative sign.
                            split_input[0] = "-" + split_input[0] # Append the negative sign to the beginning of the string.
                        if ("W" in split_input[1] and "-" not in split_input[1]): # Check to see if this is a western coordinate, but there is no negative sign.
                            split_input[1] = "-" + split_input[1] # Append the negative sign to the beginning of the string.
                        split_input[0] = ''.join(c for c in split_input[0] if c.isdigit() or c in ['.', '-']) # Remove all non-numeric characters.
                        split_input[1] = ''.join(c for c in split_input[1] if c.isdigit() or c in ['.', '-']) # Remove all non-numeric characters.
                        if ("-" in str(split_input[0])): # Check to see if this value contains a negative sign.
                            split_input[0] = split_input[0][split_input[0].find('-'):len(split_input[0])] # Trim anything that comes before the minus symbol.
                        if ("-" in str(split_input[1])): # Check to see if this value contains a negative sign.
                            split_input[1] = split_input[1][split_input[1].find('-'):len(split_input[1])] # Trim anything that comes before the minus symbol.
                        try: # Try to convert the split inputs to a floating point number.
                            split_input[0] = float(split_input[0])
                            split_input[1] = float(split_input[1])
                            if (split_input[0] >= -180 and split_input[0] <= 180 and split_input[1] >= -90 and split_input[1] <= 90): # Check to see if the determined coordinates are within the valid range.
                                location = {"lat": split_input[0], "lon": split_input[1]}
                            else:
                                location = {"lat": 0, "lon": 0}
                        except: # If a problem occurs (the split_input is not a number), use a placeholder.
                            display_message("Failed to convert coordinates to numbers: " + str(json.dumps(split_input)), 2)
                            location = {"lat": 0, "lon": 0}
                    else:
                        location = {"lat": 0, "lon": 0}
                else:
                    location = {"lat": 0, "lon": 0}
        else: # Otherwise, the capture has dropped.
            break
        frame_locations.append(location)

    if (len(frame_locations) > video_frame_count): # Check to see if there are more frame locations than frames.
        if (len(frame_locations) > video_frame_count + video_frame_rate and config["behavior"]["optimization"]["frame_counting"]["skip_validation"] == False): # Only display an error if the frame location count is off by more than 1 second of video (based on the frame-rate).
            display_message("There were more frame locations (" + str(len(frame_locations)) + ") than frames in the video (" + str(video_frame_count) + ") during GPS OSD analysis.", 2)
        frame_locations = frame_locations[:video_frame_count] # Trim the frame locations down to the length of the video.
    elif (len(frame_locations) < video_frame_count): # Check to see if there are fewer frame locations than frames. This should never happen.
        if (len(frame_locations) < video_frame_count - video_frame_rate and config["behavior"]["optimization"]["frame_counting"]["skip_validation"] == False): # Only display an error if the frame location count is off by more than 1 second of video (based on the frame-rate).
            display_message("There were fewer frame locations (" + str(len(frame_locations)) + ") than frames in the video (" + str(video_frame_count) + ") during GPS OSD analysis.", 2)

    while (len(frame_locations) < video_frame_count): # Run in a loop if there are fewer frame locations than frames, and fill them with place-holders.
        frame_locations.append({"lat": 0, "lon": 0})

    return frame_locations



# This function calculates the distance between two sets of coordinates in kilometers.
def get_distance(lat1, lon1, lat2, lon2):
    try:
        # Convert the coordinates received.
        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

        if (lon1 == lon2 and lat1 == lat2): # Check to see if the coordinates are the same.
            distance = 0 # The points are the same, so they are 0 kilometers apart.
        else: # The points are different, so calculate the distance between them
            # Convert the coordinates into radians.
            lat1 = math.radians(lat1)
            lon1 = math.radians(lon1)
            lat2 = math.radians(lat2)
            lon2 = math.radians(lon2)

            # Calculate the distance.
            distance = 6371.01 * math.acos(math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2)*math.cos(lon1 - lon2))

        # Return the calculated distance.
        return distance
    except Exception as e:
        display_message("The utils.get_distance() function encountered an unexpected error: " + str(e), 2)
        return 0.0


# This function finds the video file associated with a given side-car file.
def find_associated_video(file_path):
    working_directory = os.path.dirname(file_path) # Get the working directory from the side-car file path.
    all_files = os.listdir(working_directory) # Get a list of all files in the working directory.
    sidecar_filename = os.path.splitext(os.path.basename(file_path))[0] # Get the base name of the side-car file.
    for file in all_files:
        filename_split = os.path.splitext(file) # Split this file name into its base-name and extension.
        if (filename_split[1].lower() in [".mp4", ".m4v", ".webm", ".mjpg", ".mjpeg", ".mkv", ".flv", ".ts"]): # Check to see if this is a supported video file.
            if (filename_split[0] == sidecar_filename): # Check to see if this file's name matches the side-car file name.
                associated_video_file = working_directory + "/" + file # Form the complete file-path.
                return associated_video_file # Return the associated video file-path.
    return False # If the end of the loop has been reached without finding an associated video file, then return 'False'.
