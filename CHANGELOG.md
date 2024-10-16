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
