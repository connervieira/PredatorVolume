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
import time
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


    while True: # Run forever, until the user quits.
        utils.clear()
        print(utils.style.bold + "===== Main Menu =====" + utils.style.end)
        print("0. Quit")
        print("1. Statistics")
        print("2. All Plates")
        print("3. Search Plates")
        print("4. Recent Plates")
        print("5. Repeated Plates")
        selection = utils.take_selection([0, 1, 2, 3, 4, 5])
        utils.clear()

        if (selection == 0): # "Quit" from main menu.
            break
        if (selection == 1): # "Statistics" from main menu.
            file_count = 0 # This will count the number of files analyzed.
            frame_count = 0 # This will count the number of frames analyzed.
            plate_count = [] # This will hold all unique plates.
            for file in all_data: # Iterate over each file in the loaded data.
                file_count += 1
                for frame in all_data[file]: # Iterate over each frame in this file.
                    frame_count += 1
                    for plate in all_data[file][frame]["results"]: # Iterate over each plate associated with this frame.
                        if plate not in plate_count: # Check to see if this plate hasn't yet been added to the array.
                            plate_count.append(plate)

            print("Plates Detected: " + str(len(plate_count)))
            print("Files Analyzed: " + str(file_count))
            print("Frames Known: " + str(frame_count))
        elif (selection == 2): # "All Plates" from main menu.
            all_plates = {}
            for file in all_data: # Iterate over each file in the loaded data.
                for frame in all_data[file]: # Iterate over each frame in this file.
                    for plate in all_data[file][frame]["results"]: # Iterate over each plate associated with this frame.
                        if plate in all_plates:
                            all_plates[plate] += 1
                        else:
                            all_plates[plate] = 1

            print(utils.style.bold + "All Plates" + utils.style.end)
            print("1. Complete")
            print("2. Unique")
            selection = utils.take_selection([1, 2])
            utils.clear()
            if (selection == 1): # "Complete" from "All Plates"
                pass # Don't de-duplicate the plates.

            elif (selection == 2): # "Unique" from "All Plates"
                threshold = 0
                while threshold <= 0: # Run until the user supplies a value greater than 0.
                    threshold = utils.prompt("Difference Threshold: ", optional=True, input_type=int, default=1)
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

            if (selection == 1): # "Complete" from "All Plates"
                print(utils.style.bold + "All Plates > Complete" + utils.style.end)
            elif (selection == 2): # "Unique" from "All Plates"
                print(utils.style.bold + "All Plates > Unique" + utils.style.end)
            print("1. Plates Only")
            print("2. Counted")
            display_type = utils.take_selection([1, 2])
            utils.clear()

            if (display_type == 1): # "Plates Only" from "All Plates > [Unique/Complete]"
                if (selection == 1): # "Complete" from "All Plates"
                    print(utils.style.bold + "All Plates > Complete > Plates Only" + utils.style.end)
                elif (selection == 2): # "Unique" from "All Plates"
                    print(utils.style.bold + "All Plates > Unique > Plates Only" + utils.style.end)
            elif (display_type == 2): # "Counted " from "All Plates > [Unique/Complete]"
                if (selection == 1): # "Complete" from "All Plates"
                    print(utils.style.bold + "All Plates > Complete > Counted" + utils.style.end)
                elif (selection == 2): # "Unique" from "All Plates"
                    print(utils.style.bold + "All Plates > Unique > Counted" + utils.style.end)
            print("1. Plain Text")
            print("2. JSON")
            print("3. CSV")

            output_format = utils.take_selection([1, 2, 3])
            utils.clear()

            if (display_type == 1): # "Plates Only" from "All Plates"
                if (output_format == 1): # "All Plates > [Unique/Complete] > Plates Only" plain text output.
                    for plate in list(all_plates.keys()):
                        print(plate)
                elif (output_format == 2): # "All Plates > [Unique/Complete] > Plates Only" JSON output.
                    print(json.dumps(list(all_plates.keys())))
                elif (output_format == 3): # "All Plates > [Unique/Complete] > Plates Only" CSV output.
                    output_text = ""
                    for plate in list(all_plates.keys()):
                        output_text += plate + ","
                    output_text = output_text[:-1] # Remove the last character, since it will always be a comma.
                    print(output_text)
            elif (display_type == 2): # "Counted" from "All Plates"
                if (output_format == 1): # "All Plates > [Unique/Complete] > Counted" plain text output.
                    for plate in list(all_plates.keys()):
                        print(plate + ": " + str(all_plates[plate]))
                elif (output_format == 2): # "All Plates > [Unique/Complete] > Counted" JSON output.
                    print(json.dumps(all_plates))
                elif (output_format == 3): # "All Plates > [Unique/Complete] > Counted" CSV output.
                    print("PLATE,OCCURANCES")
                    for plate in list(all_plates.keys()):
                        print(plate + "," + str(all_plates[plate]))
        elif (selection == 3): # "Search Plates" from main menu.
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

                print(utils.style.bold + "Search Plates >  " + plate_to_find + utils.style.end)
                print("1. All Detections")
                print("2. Unique Instances")

                selection = utils.take_selection([0, 1, 2])

                if (selection == 1):
                    print(utils.style.bold + "Search Plates >  " + plate_to_find + " > All" + utils.style.end)
                elif (selection == 2):
                    print(utils.style.bold + "Search Plates >  " + plate_to_find + " > Unique" + utils.style.end)
                print("1. Plain Text")
                print("2. JSON")
                print("3. CSV")

                output_format = utils.take_selection([1, 2, 3])
                utils.clear()
                if (selection == 1):
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

        elif (selection == 4): # "Recent Plates" from main menu.
            print(utils.style.bold + "Recent Plates" + utils.style.end)
            past_days = utils.prompt("Recency Threshold (days, default 2): ", optional=True, input_type=int, default=2)
            utils.clear()

            recent_plates = {}
            old_plates = {}
            for file in all_data: # Iterate over each file in the loaded data.
                for frame in all_data[file]: # Iterate over each frame in this file.
                    for plate in all_data[file][frame]["results"]: # Iterate over each plate associated with this frame.
                        if (all_data[file][frame]["meta"]["time"] >= time.time() - (86400 * past_days)): # Check to see if this plate occurs within the specified time-frame.
                            if plate in recent_plates:
                                recent_plates[plate] += 1
                            else:
                                recent_plates[plate] = 1
                        else: # Otherwise, this plate is older than the specified time-frame.
                            if plate in old_plates:
                                old_plates[plate] += 1
                            else:
                                old_plates[plate] = 1

            print(utils.style.bold + "Recent Plates" + utils.style.end)
            print("1. New")
            print("2. Recurring")

            selection = utils.take_selection([1, 2])
            utils.clear()
            displayed_plates = []
            for plate in recent_plates.keys():
                if (selection == 1): # "Recent Plates - New"
                    if (plate not in list(old_plates.keys())): # Check to see if this plate is not present in the list of old plates.
                        displayed_plates.append(plate)
                elif (selection == 2): # "Recent Plates - Recurring"
                    if (plate in list(old_plates.keys())): # Check to see if this plate is present in the list of old plates.
                        displayed_plates.append(plate)

            if (len(displayed_plates) > 0): # Check to make sure the query returned at least one plate.
                if (selection == 1): # "Recent Plates - New"
                    print(utils.style.bold + "Recent Plates > New" + utils.style.end)
                elif (selection == 2): # "Recent Plates - Recurring"
                    print(utils.style.bold + "Recent Plates > Recurring" + utils.style.end)
                print("Output Format:")
                print("1. Plain Text")
                print("2. JSON")
                print("3. CSV")

                output_format = utils.take_selection([1, 2, 3])
                utils.clear()

                if (output_format == 1): # "Recent Plates" plain text output.
                    for plate in displayed_plates:
                        print(plate)
                elif (output_format == 2): # "Recent Plates" JSON output.
                    print(json.dumps(displayed_plates))
                elif (output_format == 3): # "Recent Plates" CSV output.
                    output_text = ""
                    for plate in displayed_plates:
                        output_text += plate + ","
                    output_text = output_text[:-1] # Remove the last character, since it will always be a comma.
                    print(output_text)
            else: # Otherwise, the query returned no plates.
                utils.display_message("The query returned no plates.", 2)
        elif (selection == 5): # "Repeated Plates" from main menu.
            print(utils.style.bold + "Repeated Plates" + utils.style.end)
            release_time = 0
            while release_time <= 0: # Run until the user supplies a value greater than 0.
                release_time = utils.prompt("Release Time (minutes, default 60): ", optional=True, input_type=float, default=60)
                if (release_time <= 0):
                    utils.display_message("The release time must be greater than 0", 2)
            utils.clear()

            tracked_plates = {}
            for file in all_data.keys(): # Iterate over each file in the loaded data.
                for frame in all_data[file]: # Iterate over each frame in this file.
                    for plate in all_data[file][frame]["results"]: # Iterate over each plate associated with this frame.
                        if (plate in tracked_plates.keys()): # Check to see if this plate is not yet in the dictionary of tracked plates.
                            following_instance_index = len(tracked_plates[plate]["following"]) - 1 # This is the index of the most recent following instance.

                            seconds_since_last_seen = all_data[file][frame]["meta"]["time"] - tracked_plates[plate]["last_seen"]["time"]
                            distance_since_last = utils.get_distance(all_data[file][frame]["meta"]["location"]["lat"], all_data[file][frame]["meta"]["location"]["lon"], tracked_plates[plate]["last_seen"]["location"]["lat"], tracked_plates[plate]["last_seen"]["location"]["lon"]) # Calculate the distance between the current frame's location and the last location this plate was seen.

                            tracked_plates[plate]["last_seen"]["time"] = all_data[file][frame]["meta"]["time"]
                            tracked_plates[plate]["last_seen"]["location"] = all_data[file][frame]["meta"]["location"]


                            if (seconds_since_last_seen < release_time*60): # Check to see if this plate is within the release time.
                                if (len(tracked_plates[plate]["following"][following_instance_index]) == 0): # Check to see if the most recent following instance hasn't yet been initialized.
                                    tracked_plates[plate]["following"][following_instance_index] = {
                                        "start": {"time": all_data[file][frame]["meta"]["time"], "location": all_data[file][frame]["meta"]["location"]},
                                        "track": {"distance": 0.0, "time": 0.0, "frames": 0}
                                    }
                                tracked_plates[plate]["following"][following_instance_index]["track"]["distance"] += distance_since_last
                                tracked_plates[plate]["following"][following_instance_index]["track"]["time"] += seconds_since_last_seen
                                tracked_plates[plate]["following"][following_instance_index]["track"]["frames"] += 1
                            else: # Otherwise, this plate has exceeded the release time.
                                if (len(tracked_plates[plate]["following"][following_instance_index]) != 0): # Check to see if the next following instance hasn't yet been created.
                                    tracked_plates[plate]["following"].append({}) # Create a new following instance.
                        else: # Otherwise, this plate is not yet being tracked, and needs to be initialized.
                            tracked_plates[plate] = {
                                "last_seen": {
                                    "time": all_data[file][frame]["meta"]["time"],
                                    "location": all_data[file][frame]["meta"]["location"]
                                },
                                "following": [{
                                    "start": {
                                        "time": all_data[file][frame]["meta"]["time"],
                                        "location": all_data[file][frame]["meta"]["location"]
                                    },
                                    "track": {
                                        "distance": 0,
                                        "time": 0,
                                        "frames": 0
                                    }
                                }]
                            }


            print(utils.style.bold + "Repeated Plates" + utils.style.end)
            print("1. Show All")
            print("2. Distance")
            print("3. Time")
            following_mode = utils.take_selection([1, 2, 3])
            utils.clear()

            if (following_mode == 1): # Selected "Show All" from "Repeated Plates"
                print(utils.style.bold + "Repeated Plates > Show All" + utils.style.end)
                print("1. Indent")
                print("2. Raw")
                output = utils.take_selection([1, 2])
                utils.clear()
                if (output == 1): # "Indent" selected from "Repeated Plates > Show All"
                    print(json.dumps(tracked_plates, indent=4))
                elif (output == 2): # "Raw" selected from "Repeated Plates > Show All"
                    print(json.dumps(tracked_plates))
            elif (following_mode == 2): # Selected "Distance" from "Repeated Plates".
                threshold_distance = 0
                while threshold_distance <= 0: # Run until the user supplies a value greater than 0.
                    threshold_distance = utils.prompt("Threshold Distance (kilometers, default 4): ", optional=True, input_type=float, default=4)
                    if (threshold_distance<= 0):
                        utils.display_message("The threshold time must be greater than 0", 2)
                # TODO: Show alerts that meet the threshold.
            elif (following_mode == 3): # Selected "Time" from "Repeated Plates".
                threshold_time = 0
                while threshold_time <= 0: # Run until the user supplies a value greater than 0.
                    threshold_time = utils.prompt("Threshold Time (minutes, default 30): ", optional=True, input_type=float, default=30)
                    if (threshold_time <= 0):
                        utils.display_message("The threshold time must be greater than 0", 2)
                # TODO: Show alerts that meet the threshold.

                

        utils.prompt(utils.style.faint + "Press enter to continue" + utils.style.end)
