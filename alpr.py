# This script handles core ALPR functionality using either V0LT Phantom or OpenALPR (depending on the configuration)

# Copyright (C) 2024 V0LT - Conner Vieira 

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License along with this program (LICENSE)
# If not, see https://www.gnu.org/licenses/ to read the license agreement.


import os
import configuration

config = configuration.load_config()

import utils # The 'utils.py' script, containing various support functions.
import subprocess # Required to run the ALPR executable as a shell script.
import json
import cv2
from datetime import datetime


# This function validates a license plate given a template.
def validate_plate(plate):
    plate_valid = True # By default, the plate is valid, until we find a character that doesn't align.

    global config
    for template in config["alpr"]["validation"]["templates"]: # Iterate over each configured template.
        plate_valid = True # This will be switched to falseif any of the templates successfully validate this plate.
        if (len(template) == len(plate)): # Check to see if the template and plate are the same length.
            for x in range(len(template)): # Iterate through each character in this plate.
                if (template[x].isalpha() == plate[x].isalpha() or template[x].isnumeric() == plate[x].isnumeric()): # If the type of this character matches between the plate and the template.
                    continue # This chararacter is valid, so leave the plate validation status as true, and continue the loop.
                else: # This character in the plate does not match the template.
                    plate_valid = False
                    break # Exit the loop, since the remaining characters do not need to be analyzed.
        else: # The plate length does not match the template length.
            continue # Skip the loop now so we can try the next template.

        if (plate_valid == True): # Check to see if the plate validation status remains as true after all characters have been checked.
            return True # Return that the plate is valid.
        else: # Otherwise, this plate is invalid based on this template.
            continue # Skip to the next template (unless we're on the last template)

    return False # If all templates have been checked, and the plate valid status is false, then return false



def run_alpr(image_filepath):
    global config
    if (config["alpr"]["engine"] == "phantom"): # Check to see if the configuration indicates that the Phantom ALPR engine should be used.
        analysis_command = "alpr -c " + config["alpr"]["region"] + " -n " + str(config["alpr"]["validation"]["guesses"]) + " '" + image_filepath + "'"
        reading_output = str(os.popen(analysis_command).read()) # Run the command, and record the raw output string.
        reading_output = json.loads(reading_output) # Convert the JSON string from the command output to actual JSON data that Python can manipulate.
        if ("error" in reading_output): # Check to see if there were errors.
            print("Phantom ALPR encountered an error: " + reading_output["error"]) # Display the ALPR error.
            reading_output["results"] = [] # Set the results of the reading output to a blank placeholder list.
    elif (config["alpr"]["engine"] == "openalpr"): # Check to see if the configuration indicates that the OpenALPR engine should be used.
        analysis_command = "alpr -j -c " + config["alpr"]["region"] + " -n " + str(config["alpr"]["validation"]["guesses"]) + " '" + image_filepath + "'"
        reading_output = str(os.popen(analysis_command).read()) # Run the command, and record the raw output string.
        reading_output = json.loads(reading_output) # Convert the JSON string from the command output to actual JSON data that Python can manipulate.

    else: # If the configured ALPR engine is unknown, then return an error.
        utils.display_message("The configured ALPR engine is not recognized.", 3)
        reading_output = {}

    return reading_output



# This function will generate sidecar files containing ALPR data for a list of videos in a given directory.
def generate_dashcam_sidecar_files(scan_directory, dashcam_files):
    global config
    failed_files = [] # This will hold all of the files that could not be analyzed.
    for file in dashcam_files: # Iterate over each file in the list of files to analyze.
        file_basename = os.path.splitext(file)[0] # Get the base name of this video file, with no extension.
        print("===== Analyzing: " + file + " =====")
        utils.debug_message("Starting analysis on '" + file + "'")
        sidecar_filepath = scan_directory + "/" + file_basename + ".json"
        if (os.path.isfile(sidecar_filepath) == True): # This to see if there is already a side-car file associated with this video.
            utils.display_message("This file has already be analyzed.", 1)
            utils.debug_message("File analysis on '" + file + "' is already complete")
        else: # Otherwise, this file needs to be analyzed.
            if (config["alpr"]["engine"] == "phantom"): # Check to see if the configure ALPR engine is Phantom.
                alpr_command = ["alpr", "-c", config["alpr"]["region"], "-n", str(config["alpr"]["validation"]["guesses"]),  scan_directory + "/" + file] # Set up the OpenALPR command.
            if (config["alpr"]["engine"] == "openalpr"): # Check to see if the configure ALPR engine is OpenALPR.
                alpr_command = ["alpr", "-j", "-c", config["alpr"]["region"], "-n", str(config["alpr"]["validation"]["guesses"]),  scan_directory + "/" + file] # Set up the OpenALPR command.

            utils.debug_message("Counting frames on '" + file + "'")
            cap = cv2.VideoCapture(scan_directory + "/" + file) # Load this video as an OpenCV capture.
            video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Count the number of frames in the video.
            video_frame_rate = int(cap.get(cv2.CAP_PROP_FPS)) # Get the video frame-rate.
            cap = None # Release the video capture.

            utils.debug_message("Establishing metadata on '" + file + "'")
            starting_timestamp = utils.get_osd_time(scan_directory + "/" + file) # Get the timestamp of the first frame of the video overlay.
            starting_hour = float(datetime.fromtimestamp(starting_timestamp).strftime('%H')) # Get the starting hour (24hr) of this video.
            if (starting_hour >= float(config["behavior"]["optimization"]["ignore"]["time"]["after"]) or starting_hour <= float(config["behavior"]["optimization"]["ignore"]["time"]["before"])):
                utils.debug_message("Skipping '" + file + "' based on time ignore optimizations")
                utils.display_message("Skipping based on video timestamp.", 1)
                continue
            video_gps_track = utils.get_osd_gps(scan_directory + "/" + file) # Get the GPS track from the on-screen display video overlay.

            utils.debug_message("Running ALPR on '" + file + "'")
            alpr_process = subprocess.Popen(alpr_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) # Execute the ALPR command defined previously.
            command_output, command_error = alpr_process.communicate() # Fetch the output from the ALPR command.
            command_output = command_output.splitlines() # Split the ALPR output be lines. Each line corresponds to a frame of the video.
            utils.debug_message("Processing results on '" + file + "'")
            if (len(command_error) > 0): # Check to see if an error occurred while executing the ALPR back-end.
                display_message("An error occurred while running ALPR:", 3)
                print(command_error)
            if (abs(len(command_output) - video_frame_count) <= 10): # Check to make sure the number of frames analyzed is (almost) the same as the frame count.
                analysis_results = {} # This will hold the analysis results for this video file.
                previous_plates = {} # This will hold plates that have been detected multiple times consecutively.
                for frame_number, frame_data in enumerate(command_output): # Iterate through each frame's analysis results from the commmand output.
                    frame_timestamp = starting_timestamp + (frame_number * (1/video_frame_rate)) # Calculate the timestamp of this frame.
                    if (frame_number < len(video_gps_track)): # Check to see if this frame is in the video GPS track.
                        frame_location = video_gps_track[frame_number] # Set this frame's location to the location from the GPS track.
                    else:
                        frame_location = {"x": 0, "y": 0} # Use a blank placeholder GPS location.
                    frame_data = json.loads(frame_data) # Load the raw results for this frame.
                    frame_results = {} # This will hold the organized analysis results for this frame.
                    for result in frame_data["results"]: # Iterate through each plate detected in this frame.
                        top_guess = "" # This will be set to the top plate from the guesses, based on the validation rules.
                        for guess in result["candidates"]: # Iterate through each guess for this plate in order from most to least likely.
                            if (guess["confidence"] >= float(config["alpr"]["validation"]["confidence"])): # Check to see if this guess exceeds the minimum confidence value.
                                if (validate_plate(guess["plate"])): # Check to see if this plate passes the template validation.
                                    top_guess = guess["plate"] # This will be set to the top plate from the guesses, based on the validation rules.
                                    break # Exit the loop, since all subsequent guesses will have a lower confidence.
                        if (top_guess == ""): # Check to see if there weren't any valid guesses for this plate.
                            if (config["alpr"]["validation"]["best_effort"]): # Check to see if `best_effort` mode is enabled.
                                top_guess = result["candidates"][0]["plate"] # Use the most likely plate as the top guess.
                        if (top_guess != ""): # Check to see if the top guess is now set for this plate.
                            frame_results[top_guess] = {} # Initialize this plate in the dictionary of plates for this frame.
                            frame_results[top_guess]["coordinates"] = utils.convert_corners_to_bounding_box(result["coordinates"]) # Add the position of this plate in the image.

                    # Increment the consecutive plate counter.
                    for plate in list(frame_results.keys()): # Iterate through each plate in the list of detected plates to increment.
                        if plate in previous_plates:
                            previous_plates[plate] += 1
                        else:
                            previous_plates[plate] = 1

                    # Remove any missing plates from the consecutive list.
                    for plate in list(previous_plates.keys()):
                        if (plate not in list(frame_results.keys())):
                            del previous_plates[plate]

                    # Filter plates based on the consecutive counter.
                    for plate in list(frame_results.keys()): # Iterate over each plate in the validated results.
                        if (previous_plates[plate] < config["alpr"]["validation"]["consecutive"]): # Check to see if this plate has been visible for less than the minimum consecutive instances.
                            del frame_results[plate] # Remove this plate from the results.

                    if (len(frame_results) > 0): # Check to see if there is at least one result for this frame.
                        analysis_results[frame_number] = {}
                        analysis_results[frame_number]["results"] = frame_results # Add this frame's data to the full analysis results for this video file.
                        analysis_results[frame_number]["meta"] = {}
                        analysis_results[frame_number]["meta"]["time"] = round(frame_timestamp*100)/100
                        analysis_results[frame_number]["meta"]["location"] = frame_location
                utils.debug_message("Saving sidecar file for '" + file + "'")
                utils.save_to_file(sidecar_filepath, json.dumps(analysis_results)) # Save the analysis results for this file to the side-car file.
                utils.debug_message("Analysis finished on '" + file + "'")
                utils.display_message("Analysis complete", 1)
            else:
                failed_files.append(file)
                utils.debug_message("Analysis incomplete for '" + file + "'")
                utils.display_message("The number of frames in the video (" + str(video_frame_count) + ") does not match the number of frames analyzed (" + str(len(command_output)) + "). The analysis has been skipped for this file.", 2)
    return failed_files
