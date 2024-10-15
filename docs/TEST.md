# Testing

This document explains how to use the test utilities found in the `test.py` script.

To start the testing utilities, run `test.py` with Python (`python3 test.py`)

To make a menu selection, enter the number associated with it, then press enter.

- **Testing Mode**: This is the root of the testing utility menu.
    - **ALPR Analysis**: This section contains tools for testing license plate recognition behavior.
        - **File**: Enter a file-path to a photo or video to analyze with the ALPR back-end.
    - **OSD Analysis**: This section contains tools for testing on-screen-display recognition behavior.
        - **Test**: This mode will print out the results from OSD analysis.
            - **Date/Time**: This will test the recognition of the date/time stamp.
            - **GPS**: This will test the recognition of the GPS stamp. This make take several seconds, since the entire video is analyzed before the results are displayed.
        - **Preview**: This mode will show the region of the the video where analysis is conducted.
            - **Date/Time**: This will show the region of the video where the date/time stamp is configured to be (`behavior>metadata>time>overlay>bounding_box`).
            - **GPS**: This will show the region of the video where the GPS stamp is configured to be (`behavior>metadata>gps>overlay>bounding_box`).
