# Configure

This document contains information about configuring and customizing Predator Volume.


## Files

Predator Volume uses 3 files in relation to configuration:
- ./assets/config/configactive.json
- ./assets/config/configdefault.json
- ./assets/config/configoutline.json

### Active Configuration

This is where Predator Volume stores the active configuration file. This is the file you edit to configure Predator Volume.

### Default Configuration

This is where Predator Volume stores the default configuration values. Generally, you should not modify this file. This file is updated when Predator Volume updates, and is used to automatically update your active configuration file when values are added or removed.

### Outlined Configuration

This file contains based validation rules for each configuration value. This allows Predator Volume to run basic sanity checks on your active configuration file to find potentially broken configuration values.


## Values

Below is a list of all configuration values supported by Predator Volume.

- `alpr` contains settings that control how license plate recongition is performed.
    - `engine` defines which engine is used by the ALPR back-end. This can be set to one of the following values:
        - `"phantom"` is the default, and assume that you have installed [Phantom ALPR](https://v0lttech.com/phantom.php).
        - `"openalpr"` is the secondary option, and can be used if you only have OpenALPR installed, and can't install Phantom.
    - `region` defines the region for license plates to be detected as a country code. Below are common values for this setting.
        - `"us"`: United States
        - `"eu"`: European Union
        - `"au"`: Austraila
        - `"fr"`: France
    - `validation` contains settings for validating detected plates.
        - `confidence` is a floating point value that determines the minimum confidence for a plate to be considered (ranging from 0 to 1, where 1 is absolute confidence)
        - `guesses` is an integer number that determines how many guesses the ALPR engine will take as to the contents of each plate.
        - `best_effort` determines whether Predator Volume will accept the most likely guess for a plate if all plate guesses fail the configured validation criteria. When disable, only plates with valid guesses will be processed.
        - `consecutive` is an integer number that determines the minimum number of consecutive frames that a plate has to be visible before it is considered.
            - Setting this to 0 will accept all detected plates immediately.
            - Higher values will help to filter out unreliable plate readings, but may also cause plates that are only briefly visible to be rejected.
        - `templates` is a list of strings that define license plate templates.
            - The type of each character in a plate guess (number or letter) must match the type of character in the the license plate template.
            - For example, the license plate template "AAA0000" will accept any plate that has 3 letters followed by four numbers.
                - "XYZ1234" will pass this template, since all of the characters match the template.
                - "ABC123X" will fail this template, since the X is a letter, not a number.
                - "ABC123" will fail this template, since the last number is missing.
            - If a plate guess matches any of the configured templates, it will pass validation.
- `display` contains settings that control the console output.
    - `debug_messages` is a boolean that determines whether verbose debugging messages will be printed to the console during use.
        - Enabling this value also disables console clearing, so messages are not cleared from the screen.
- `behavior` controls the general behavior of Predator Volume.
    - `optimization` contains settings for optimizing the analysis process.
        - `ignore` contains criteria that will cause videos to be ignored by the analysis process.
            - `time` sets a daily time-frame between which videos will be ignored. This is generally used to ignore videos captured at night. Videos outside of this range will be processed like normal.
                - `after` sets the hour (in 24hr format) after which videos will be ignored.
                - `before` sets the hour (in 24hr format) before which videos will be ignored.
        - `frame_counting` contains settings that determine how Predator Volume will double-check frame counts between video files, OSD analysis, and ALPR analysis.
            - `method` determines the method that will be used to find the frame count in video files. This can only be set to the following values:
                - "default" will use the built in OpenCV method to determine the number of frames in a video file.
                - "custom" will use a custom implementation that individually counts each frame in a video file. This method is much slower, but much more accurate.
            - `skip_validation` is a boolean value that determines if Predator Volume will skip checking for differences in frame count between the video file and analysis results.
                - Setting this to 'false' will cause Predator Volume to enforce that the analysis results and video frame count be similar in length. This can help to filter out corrupted video files.
                - Setting this to 'true' will allow Predator Volume to continue with the analysis process, even if a certain file doesn't pass frame count validation.
    - `metadata` determines how metadata for videos will be determined.
        - `time` controls how the starting time of videos will be determined.
            - `method` defines the method used to get the starting time. Currently, the only supported method is `"overlay"`.
            - `overlay` configures how the time is determined from the on-screen dash-cam overlay.
                - `format` defines the format of the date/time stamp used by the dash-cam (see <https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior> to learn what each symbol means).
                - `bounding_box` defines the region in the video where the dash-cam date/time stamp is shown.
                    - `x` is the X coordinate of the top left corner of the stamp, measured from the left of the video.
                    - `y` is the Y coordinate of the top left corner of the stamp, measured from the top of the video.
                    - `w` is the width of the region containing the stamp.
                    - `h` is the height of the region containing the stamp.
        - `gps` controls how the GPS position of videos will be determined.
            - `method` defines the method used to get the GPS position. Currently, the only supported method is `"overlay"`.
            - `overlay` configures how the GPS position is determined from the on-screen dash-cam overlay.
                - `bounding_box` defines the region in the video where the dash-cam GPS stamp is shown.
                    - `x` is the X coordinate of the top left corner of the stamp, measured from the left of the video.
                    - `y` is the Y coordinate of the top left corner of the stamp, measured from the top of the video.
                    - `w` is the width of the region containing the stamp.
                    - `h` is the height of the region containing the stamp.
