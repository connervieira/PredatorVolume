# Predator Volume

A variant of V0LT Predator focused on bulk dash-cam video analysis.

![Predator Volume logo](assets/images/branding/Logo.png)


## Description

[Predator](https://v0lttech.com/predator.php) is a multi-purpose license plate recognition platform designed to be the ultimate dash-cam for technical hobbyists and customers with unique needs. Predator Volume is a modified variant of Predator focused on analyzing bulk pre-recorded video recorded by third-party dash-cams. Predator Volume analyzes all video files in a given directory, and generates a JSON file containing ALPR results, GPS locations, and image timestamps. These JSON side-car files can then be queried to gain insight into the results.


## Features

### Bulk Processing

Predator Volume is designed to comfortably handle large amounts of data, especially from the same source. Simply connect your media, provide the file-path, and let Predator Volume run unattended.

### Phantom ALPR

Predator Volume uses the same ALPR engine used by vanilla [Predator](https://v0lttech.com/predator.php), meaning you'll benefit from the same reliability, customizability, and fault tolerance.

### Offline Capable

Just like vanilla Predator, Predator Volume can run entirely offline, using your local processing power to analyze video.

### Frame Perfect

Predator Volume analyzes every single frame in each video, making it possible to detect all plates in a video, even on hardware that would otherwise struggle to run in real-time.

### Highly Extensible

The side-car files used by Predator Volume are just simple JSON file. As such, experienced developers can write their own software to interact with the data.

### OSD Analysis

Predator Volume can read information directory from the on-screen-display, meaning you don't need to rely on your dash-cam using standard metadata formats.


## Documentation

To learn more about how to install, configure, and use Predator Volume, see [DOCUMENTATION.md](DOCUMENTATION.md)
