# Installation

This document contains information regarding installing Predator Volume.

1. Install an ALPR engine.
    - Predator Volume depends on an ALPR engine to detect license plates. Currently, the following two engines are supported:
        - [Phantom ALPR](https://v0lttech.com/phantom.php): This is the recommended ALPR engine, and is developed specifically to be used with Predator and its variants. Phantom ALPR is heavily based on OpenALPR.
        - [OpenALPR](https://github.com/openalpr/openalpr/): This project is unaffiliated with V0LT, but is a popular ALPR engine. If you already have OpenALPR installed, you can configure Predator Volume to use it.
2. Install system dependencies.
    - Predator Volume depends on the following system packages: `python3 python3-pip python3-opencv ffmpeg`
    - System dependencies can be installed using your operating system's package manager. On Debian/Ubuntu based system, the `apt install` command is used for this purpose.
3. Install Python dependencies.
    - Predator Volume depends on the following non-standard Python libraries: `Levenshtein opencv-python pytesseract`
