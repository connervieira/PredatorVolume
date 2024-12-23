# Query

This document describes each option avaiable in query mode.

- **0 - Quit**: This option will terminate the script.
- **1 - Statistics**: This option prints basic statistics about the available side-car files.
- **2 - All Plates**: This will open a menu with queries for printing all detected plates.
    - **1 - Complete**: This will simply fetch all detected plates, with no additional filtering.
        - **1 - Plates Only**: Print only a list of the plates.
            - **1 - Plain Text**: Print the results as a plain-text human-friendly format.
            - **2 - JSON**: Print the results as a JSON string.
            - **3 - CSV**: Print the results as comma separated values.
        - **2 - Counted**: Print the plates, as well as how many times they were detected.
            - **1 - Plain Text**: Print the results as a plain-text human-friendly format.
            - **2 - JSON**: Print the results as a JSON string.
            - **3 - CSV**: Print the results as comma separated values.
    - **2 - Unique**: This allows the user to combine duplicate plates with slight variations into a single plate to filter out noise.
        - **Difference Threshold**: This is an input that determines how many differences there can be before a plate is considered different from another plate (Levenshtein distance).
            - **1 - Plates Only**: Print only a list of the plates.
                - **1 - Plain Text**: Print the results as a plain-text human-friendly format.
                - **2 - JSON**: Print the results as a JSON string.
                - **3 - CSV**: Print the results as comma separated values.
            - **2 - Counted**: Print the plates, as well as how many times they were detected.
                - **1 - Plain Text**: Print the results as a plain-text human-friendly format.
                - **2 - JSON**: Print the results as a JSON string.
                - **3 - CSV**: Print the results as comma separated values.
- **3 - Search Plates**: This option allows the user to find all instances were a certain plate was detected.
    - **Plate**: This is an input for the plate you'd like to search for. Entering a lower-case `q` will return to the main menu.
        - **1 - All Detections**: This will return every single time the plate was detected on a frame-by-frame basis.
            - **1 - Plain Text**: Print the results as a plain-text human-friendly format.
            - **2 - JSON**: Print the results as a JSON string.
            - **3 - CSV**: Print the results as comma separated values.
        - **2 - Unique Instances**: This will combine repeated detections within a given timeframe into a single instance.
            - **1 - Plain Text**: Print the results as a plain-text human-friendly format.
            - **2 - JSON**: Print the results as a JSON string.
            - **3 - CSV**: Print the results as comma separated values.
- **4 - Recent Plates**: This will open a menu with queries for plates that were detected recently.
    - **Recency Threshold**: This is an input that determine how many days old a detection can be to be considered "recent". For example, a recency threshold of 3 days will consider all detections within the past 3 days to be "recent". This value is relative to the most recent detected frame, not the true current time.
        - **1 - New**: This will return plates that were detected recently, but haven't been seen before.
            - **1 - Plain Text**: Print the results as a plain-text human-friendly format.
            - **2 - JSON**: Print the results as a JSON string.
            - **3 - CSV**: Print the results as comma separated values.
        - **2 - Recurring**: This will return plates that were detected recently, and have been seen before.
            - **1 - Plain Text**: Print the results as a plain-text human-friendly format.
            - **2 - JSON**: Print the results as a JSON string.
            - **3 - CSV**: Print the results as comma separated values.
- **5 - Repeated Plates**: This option allows the user to identify plates that may have been following them over a period of time.
    - **Release Time**: This is an input that specifies the length of time (in minutes) after which a plate will be "forgiven". If plate isn't detected for this length of time, then it will be considered to be no longer following. If the plate is detected again in the future, it will start a new instance of following.
        - **1 - Show All**: This option will simply dump the full following analysis results. This is useful for debugging or external processing.
            - **1 - Indent**: This will pretty-print the results as an indented JSON string.
            - **2 - Raw**: This will print the results as an unformatted JSON string.
        - **2 - Distance**: This will show plates that have followed for a certain distance.
            - **Distance Threshold**: This is an input that specifies the minimum distance (in kilometers) that a plate needs to follow to trigger an alert.
                - **1 - Plain Text**: Print the results as a plain-text human-friendly format.
                - **2 - JSON**: Print the results as a JSON string.
                - **3 - CSV**: Print the results as comma separated values.
        - **3 - Time**: This will show plates that have followed for a certain length of time.
            - **Distance Threshold**: This is an input that specifies the minimum length of time (in minutes) that a plate needs to follow to trigger an alert.
                - **1 - Plain Text**: Print the results as a plain-text human-friendly format.
                - **2 - JSON**: Print the results as a JSON string.
                - **3 - CSV**: Print the results as comma separated values.
