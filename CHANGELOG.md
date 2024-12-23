# Change-log

This document contains a list of all of the changes in each version of Predator Volume.


## Version 1.0

2024-10-16

- Finished core functionality.
    - Implemented "analysis mode" to analyze dash-cam videos and generate side-car files with ALPR data.
    - Implemented "query mode" to gain insight from data contained within side-car files.
        - Implemented "Statistics" query, to get a basic overview of the analysis data.
        - Implemented "All Plates" query to list all detected plates.
        - Implemented "Search Plates" query to allow the user to find instances of a plate being detected.
        - Implemented "Recent Plates" query to allow the user to filter by plates that are new, or have been seen before.
        - Implemented "Repeated Plates" query to allow the user to find plates that may have been following them.

## Version 1.1

*Release date to be determined*

- Updated frame counting behavior.
- Added configurable defaults for certain inputs.
- Improved fault tolerance when a corrupt frame is encountered during on-screen timestamp display recognition.
- Fixed a crash when a given repeated plate only appeared once in an instance.
