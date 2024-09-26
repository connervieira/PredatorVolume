# This is the main script that should be run to start Predator Volume. To configure it's functionality, see the './assets/config/configactive.json' file.

# Copyright (C) 2024 V0LT - Conner Vieira 

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License along with this program (LICENSE)
# If not, see https://www.gnu.org/licenses/ to read the license agreement.

import os
import json # Required to load side-car files in query mode.
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
        print("1. All Unique Plates")
        selection = utils.take_selection([0, 1])
        utils.clear()

        if (selection == 0):
            continue
        utils.debug_message("Running query")
        if (selection == 1): # "All Unique Plates" query.
            print("All Unique Plates")
            all_plates = []
            for file in all_data: # Iterate over each file in the loaded data.
                for frame in all_data[file]: # Iterate over each frame in this file.
                    for plate in all_data[file][frame]["results"]: # Iterate over each plate associated with this frame.
                        if plate not in all_plates:
                            all_plates.append(plate)
            print(all_plates)
        utils.prompt(utils.style.faint + "Press enter to continue" + utils.style.end)
