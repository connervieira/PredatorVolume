# This is the main script that should be run to start Predator Volume. To configure it's functionality, see the './assets/config/configactive.json' file.

# Copyright (C) 2024 V0LT - Conner Vieira 

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License along with this program (LICENSE)
# If not, see https://www.gnu.org/licenses/ to read the license agreement.

import os
import json # Required to load side-car files in query mode.
import Levenshtein # Required to calculate the difference between two plates.
import datetime # Required to print Unix timestamps as human-readable dates.
import configuration # `configuration.py`
import utils # `utils.py`
import alpr # `alpr.py`

config = configuration.load_config()

invalid_configuration_values = configuration.validate_config(config) # Validation the configuration, and record any potential problems.
for entry in invalid_configuration_values: # Iterate through each invalid configuration value in the list.
    utils.display_message("Invalid configuration value: " + entry, 3) # Print each invalid configuration value as an error.
del invalid_configuration_values # Delete the variable holding the list of invalid configuration_values.
utils.debug_message("Validated configuration values")


utils.clear()
working_directory = utils.input_directory(text_prompt="Working directory: ")
print("Please select a mode:")
print("1. Analyze")
print("2. Query")
selection = utils.take_selection([1, 2])
utils.clear()

if (selection == 1): # Analysis mode.

    working_directory_contents = os.listdir(working_directory) # Get the contents of the working directory.

    videos_to_analyze = [] # This is a placeholder that will hold all video files to analyze.
    for file in working_directory_contents: # Iterate over each file in the working directory.
        filename_split = os.path.splitext(file) # Split the name of this file into the base-name and extension.
        if (filename_split[1].lower() in [".mp4", ".m4v", ".webm", ".mjpg", ".mjpeg", ".mkv", ".flv", ".ts"]): # Check to see if this file is a supported video file.
            videos_to_analyze.append(file) # Add this video to the files to analyze.

    if (len(videos_to_analyze) > 0):
        if (len(videos_to_analyze) == 1): utils.display_message("Found " + str(len(videos_to_analyze)) + " video file to analyze.", 1)
        else: utils.display_message("Found " + str(len(videos_to_analyze)) + " video files to analyze.", 1)
        alpr.generate_dashcam_sidecar_files(working_directory, videos_to_analyze)
    else:
        utils.display_message("There were no video files to analyze in the specified directory.", 2)
elif (selection == 2): # Query mode.
    sidecar_files = [] # This is a placeholder that will hold all sidecar files found in the working directory.
    while len(sidecar_files) == 0:
        working_directory_contents = os.listdir(working_directory) # Get the contents of the working directory.

        utils.debug_message("Loading working directory")
        for file in working_directory_contents: # Iterate over each file in the working directory.
            filename_split = os.path.splitext(file) # Split the name of this file into the base-name and extension.
            if (filename_split[1].lower() == ".json"): # Check to see if this file is a valid side-car file.
                sidecar_files.append(file) # Add this file to the list of side-car files.
        if (len(sidecar_files) == 0): # Check to see if there are no side-car files.
            utils.display_message("There are no side-car files in the given directory.", 2)
            working_directory = utils.input_directory(text_prompt="Working directory: ")

    utils.debug_message("Loading side-car file data")
    all_data = {}
    for file in sidecar_files:
        absolute_sidecar_filepath = os.path.join(working_directory, file)
        with open(absolute_sidecar_filepath) as f:
            all_data[file] = json.load(f)


    while selection != 0: # Run forever, until the user quits.
        utils.clear()
        print("Please select a query:")
        print("0. Quit")
        print("1. All Plates")
        print("2. Search Plates")
        selection = utils.take_selection([0, 1, 2])
        utils.clear()

        if (selection == 0):
            continue
        if (selection == 1): # "All Plates" from main menu.
            all_plates = {}
            for file in all_data: # Iterate over each file in the loaded data.
                for frame in all_data[file]: # Iterate over each frame in this file.
                    for plate in all_data[file][frame]["results"]: # Iterate over each plate associated with this frame.
                        if plate in all_plates:
                            all_plates[plate] += 1
                        else:
                            all_plates[plate] = 1

            print("All Plates:")
            print("0. Back")
            print("1. Complete")
            print("2. Unique")
            selection = utils.take_selection([0, 1, 2])
            utils.clear()
            if (selection == 0): # Back from "All Plates"
                continue
            elif (selection == 1): # "Complete" from "All Plates"
                print("All Plates - Complete:")
                print("0. Back")
                print("1. Plates Only")
                print("2. Counted")
                selection = utils.take_selection([0, 1, 2])
                utils.clear()
                if (selection == 0): # Back from "All Plates - Complete"
                    continue
                elif (selection == 1): # "Plates Only" from "All Plates - Complete"
                    print(json.dumps(list(all_plates.keys())))
                elif (selection == 2): # "Counted" from "All Plates - Complete"
                    print(json.dumps(all_plates, indent=4))
            elif (selection == 2): # "Unique" from "All Plates"
                threshold = 0
                while threshold <= 0: # Run until the user supplies a value greater than 0.
                    threshold = utils.prompt("Distance Threshold: ", optional=True, input_type=int, default=1)
                    if (threshold <= 0):
                        utils.display_message("The distance threshold must be greater than 0", 2)
                utils.clear()
                skip_plates = [] # This will hold plates that are removed during the loop, so we know to skip them.
                for plate_a in list(all_plates.keys()):
                    for plate_b in list(all_plates.keys()):
                        if (plate_a in skip_plates or plate_b in skip_plates):
                            continue # Skip to the next iteration of the loop.
                        if (plate_a == plate_b): # Check to see if we are comparing the same plate.
                            continue # Skip to the next iteration of the loop.
                        levenshtein_distance = Levenshtein.distance(plate_a, plate_b)
                        if (levenshtein_distance <= threshold): # Check to see if the difference between these plates is within the threshold.
                            if (all_plates[plate_a] <= all_plates[plate_b]): # Check to see if plate A occurs less than plate B.
                                skip_plates.append(plate_a)
                                del all_plates[plate_a] # Remove plate A.
                            else: # Otherwise, plate B occurs less than plate A.
                                skip_plates.append(plate_b)
                                del all_plates[plate_b] # Remove plate B.

                print("All Plates - Unique:")
                print("0. Back")
                print("1. Plates Only")
                print("2. Counted")
                selection = utils.take_selection([0, 1, 2])
                utils.clear()
                if (selection == 0): # Back from "All Plates - Unique"
                    continue
                elif (selection == 1): # "Plates Only" from "All Plates - Unique"
                    print(json.dumps(list(all_plates.keys())))
                elif (selection == 2): # "Counted" from "All Plates - Unique"
                    print(json.dumps(all_plates, indent=4))
        elif (selection == 2): # "Search Plates" from main menu.
            all_plates = {}
            for file in all_data: # Iterate over each file in the loaded data.
                for frame in all_data[file]: # Iterate over each frame in this file.
                    for plate in all_data[file][frame]["results"]: # Iterate over each plate associated with this frame.
                        if plate not in all_plates:
                            all_plates[plate] = {}
                        all_plates[plate][all_data[file][frame]["meta"]["time"]] = {}
                        all_plates[plate][all_data[file][frame]["meta"]["time"]]["location"] = all_data[file][frame]["meta"]["location"]

            plate_to_find = ""
            while plate_to_find.upper() not in all_plates: # Run until the user enters a plate that exists.
                plate_to_find = utils.prompt("Plate: ", optional=False, input_type=str)
                if (plate_to_find == "q"):
                    break
                if (plate_to_find.upper() not in all_plates): # Check to see if the plate entered by the user doesn't exist.
                    utils.display_message("The provided plate does not exist in the database. (Enter `q` if you want to cancel)", 2)
            if (plate_to_find != "q"):
                plate_to_find = plate_to_find.upper() # Convert the search plate to uppercase.
                last_timestamp = 0
                times_passed = {} # This will hold the times this plate has been passed, with repeated sequential detections filtered out.
                for instance in sorted(all_plates[plate_to_find]):
                    if (instance - last_timestamp > 15): # Make sure this plate hasn't been seen in at least 15 seconds, so we can roughly distinguish times passed, and avoid showing the plate being repeatedly detected.
                        times_passed[instance] = all_plates[plate_to_find][instance]
                    last_timestamp = instance # This will hold the timestamp of the last time this plate was seen so we can filter out repeated sequential detections.

                print("Search Plates - " + plate_to_find  + ":")
                print("0. Back")
                print("1. All Detections")
                print("2. Unique Instances")

                selection = utils.take_selection([0, 1, 2])

                print("Output Format:")
                print("1. Plain Text")
                print("2. JSON")
                print("3. CSV")

                output_format = utils.take_selection([1, 2, 3])
                utils.clear()
                if (selection == 0):
                    continue
                elif (selection == 1):
                    if (output_format == 1): # Plate Search - All - Plain Text
                        print("This plate has been seen " + str(len(all_plates[plate_to_find])) + " times.")
                        for instance in all_plates[plate_to_find]:
                            print(datetime.datetime.fromtimestamp(instance).strftime('%Y-%m-%d %H:%M:%S') + " at (" + str(all_plates[plate_to_find][instance]["location"]["lat"]) + ", " + str(all_plates[plate_to_find][instance]["location"]["lon"]) + ")")
                    elif (output_format == 2): # Plate Search - All - JSON
                        print(json.dumps(all_plates[plate_to_find]))
                    elif (output_format == 3): # Plate Search - All - CSV
                        print("PLATE,DATE,LAT,LON")
                        for instance in all_plates[plate_to_find]:
                            print(plate_to_find + "," + datetime.datetime.fromtimestamp(instance).strftime('%Y-%m-%d %H:%M:%S') + "," + str(all_plates[plate_to_find][instance]["location"]["lat"]) + "," + str(all_plates[plate_to_find][instance]["location"]["lon"]))
                elif (selection == 2):
                    if (output_format == 1): # Plate Search - Unique - Plain Text
                        print("This plate has been seen on " + str(len(times_passed)) + " separate instances.")
                        for instance in times_passed:
                            print(datetime.datetime.fromtimestamp(instance).strftime('%Y-%m-%d %H:%M:%S') + " at (" + str(times_passed[instance]["location"]["lat"]) + ", " + str(times_passed[instance]["location"]["lon"]) + ")")
                    elif (output_format == 2): # Plate Search - Unique - JSON
                        print(json.dumps(times_passed))
                    elif (output_format == 3): # Plate Search - Unique - CSV
                        print("PLATE,DATE,LAT,LON")
                        for instance in times_passed:
                            print(plate_to_find + "," + datetime.datetime.fromtimestamp(instance).strftime('%Y-%m-%d %H:%M:%S') + "," + str(times_passed[instance]["location"]["lat"]) + "," + str(times_passed[instance]["location"]["lon"]))
                

        utils.prompt(utils.style.faint + "Press enter to continue" + utils.style.end)
