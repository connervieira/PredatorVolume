# This is the main script that should be run to start Predator Volume. To configure it's functionality, see the './assets/config/configactive.json' file.

# Copyright (C) 2024 V0LT - Conner Vieira 

# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License along with this program (LICENSE)
# If not, see https://www.gnu.org/licenses/ to read the license agreement.

import os
import configuration
import utils
import alpr

config = configuration.load_config()

working_directory = "" # This is a placeholder that will be overwritten with the user's input.
while (working_directory == "" or os.path.isdir(working_directory) == False): # Repeatedly prompt the user to enter a valid working directory until a valid response is given.
    working_directory = utils.prompt("Working directory: ", optional=False)
    if (os.path.isfile(working_directory) == True): # Check to see if the specified path is a file.
        utils.display_message("The specified path points to a file, not a directory.", 2)
    elif (os.path.exists(working_directory) == False): # Check to see if the specified path does not exist.
        utils.display_message("The specified path does not exist.", 2)

working_directory_contents = os.listdir(working_directory) # Get the contents of the working directory.

videos_to_analyze = [] # This is a placeholder that will hold all video files to analyze.
for file in working_directory_contents: # Iterate over each file in the working directory.
    filename_split = os.path.splitext(file) # Split the name of this file into the base-name and extension.
    if (filename_split[1].lower() in [".mp4", ".m4v", ".webm", ".mjpg", ".mjpeg", ".mkv", ".flv", ".ts"]): # Check to see if this file is a supported video file.
        videos_to_analyze.append(file) # Add this video to the files to analze.

if (len(videos_to_analyze) > 0):
    if (len(videos_to_analyze) == 1): utils.display_message("Found " + str(len(videos_to_analyze)) + " video file to analyze.", 1)
    else: utils.display_message("Found " + str(len(videos_to_analyze)) + " video files to analyze.", 1)
    alpr.generate_dashcam_sidecar_files(working_directory, videos_to_analyze)
else:
    utils.display_message("There were no video files to analyze in the specified directory.", 2)
