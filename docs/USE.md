# Usage

This document contains information about how to effectively use Predator Volume

## Start-up

Provided Predator Volume has already been installed and configured, you can start it running `main.py` using Python3. (Ex: `python3 main.py`)

## Modes

Predator Volume operates in one of two modes.

### Analysis Mode

This is the mode that you should generally start with. Analysis mode analyzes all of the video files in a directory, and saves the results to a "side-car" file containing JSON data. The side-car file shares the name of the video it is associated with.

To use analysis mode, follow these steps:
1. After starting Predator, specify the absolute path to a working directory containing the video files you want to analyze, then press return.
2. At the next prompt, enter `1` and press return to select the "Analyze" option.
3. Analysis should begin on the first video. At this point, you can leave the process to run unattentended.
    - Videos that already have side-car files with be skipped automatically.
    - Each video will likely take several minutes to analyze.
    - If a problem occurs a message will appear in the console.
        - Generally, Predator Volume will attempt to skip the video with the problem, and continue analyzing subsequent video.
    - After the analysis is complete, the script will terminate.

### Query Mode

Once you have generated (or otherwise obtained) side-car files, you can use query mode to process the results and find insights. Query mode does not depend on the associated video files, and only needs the side-car files.

To use query mode, follow these steps:
1. After starting Predator, specify the absolute path to a working directory containing side-car files, then press return.
2. At the next prompt, enter `2` and press return to select the "Query" option.
3. The next screen shows the root menu for query mode. This is the starting point for all queries.
    - To select a menu option, enter the number associated with it, then press return.
    - To learn more about each query menu option, see [/docs/QUERY.md](/docs/QUERY.md)
4. After you've finished, you can terminate the script by pressing `Ctrl + C`, or by selecting the "Quit" option on the main menu.
