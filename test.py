# This script serves as a diagnostic tool to test Predator Volume's functionality. It is primarily designed to allow users to test, maintain, and configure their Predator Volume instance. This utility does not have in-depth input validation, and generally trusts that the user knows what they are doing.


import os
import configuration
import utils
import alpr
from datetime import datetime # Required to print human-friendly date/time stamps.
import cv2

config = configuration.load_config() # Load the active configuration.

print("Testing Mode")
print("1. ALPR Analysis")
print("2. OSD Analysis")
selection = utils.take_selection([1, 2])

if (selection == 1): # ALPR testing.
    file = input("File: ")
    if (config["alpr"]["engine"] == "phantom"): # Check to see if the configuration indicates that the Phantom ALPR engine should be used.
        analysis_command = "alpr -c " + config["alpr"]["region"] + " -n " + str(config["alpr"]["validation"]["guesses"]) + " '" + file + "'"
        os.system(analysis_command) # Run the command.
    elif (config["alpr"]["engine"] == "openalpr"): # Check to see if the configuration indicates that the OpenALPR engine should be used.
        analysis_command = "alpr -j -c " + config["alpr"]["region"] + " -n " + str(config["alpr"]["validation"]["guesses"]) + " '" + file + "'"
        os.system(analysis_command) # Run the command.

elif (selection == 2): # OSD testing.
    print("Mode")
    print("1. Test")
    print("2. Preview")
    mode = utils.take_selection([1, 2])

    print("OSD Attribute")
    print("1. Date/Time")
    print("2. GPS")
    attribute = utils.take_selection([1, 2])

    file = input("File: ")
    if (mode == 1): # Test OSD stamp recognition
        if (attribute == 1): # Date/time OSD stamp detection test.
            output = utils.get_osd_time(file, verbose=True)
            if (output > 0):
                print(datetime.utcfromtimestamp(int(round(output))).strftime('%Y-%m-%d %H:%M:%S') + " UTC")
                print(datetime.fromtimestamp(int(round(output))).strftime('%Y-%m-%d %H:%M:%S') + " Local")
            else:
                print("Failed to recognize stamp")
        elif (attribute == 2): # GPS OSD stamp detection test.
            output = utils.get_osd_gps(file)
            print(output)
    elif (mode == 2): # Preview an OSD bounding box.
        if (attribute == 1):
            bounding_box = config["behavior"]["metadata"]["time"]["overlay"]["bounding_box"]
        if (attribute == 2):
            bounding_box = config["behavior"]["metadata"]["gps"]["overlay"]["bounding_box"]

        cap = cv2.VideoCapture(file) # Load this video as an OpenCV capture.
        while (cap.isOpened()):
            ret, frame = cap.read() # Get the next frame.
            if (ret == True):
                cropped = frame[bounding_box["y"]:bounding_box["y"]+bounding_box["h"],bounding_box["x"]:bounding_box["x"]+bounding_box["w"]] # Crop the frame down to the configured bounding box.
                cv2.imshow("Frame", cropped)
            pressed_key = cv2.waitKey(1)
            if (pressed_key == ord("q")):
                break
        cv2.destroyAllWindows()
