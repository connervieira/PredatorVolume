#!/bin/bash
user_home=/home/$(ls /home/ | head -n 1);

if [ ! -f "$user_home/Downloads/predator_volume_install_script_trigger.txt" ]; then # Check to see if Predator Volume has not yet been downloaded.
    echo "This script should only be run on a dedicated system running a clean installation of Ubuntu, Pop!_OS, Linux Mint, or similar Linux distribution. This script may delete or overwrite files during installation. Do not use this script on a system containing files you care about."; 
    echo "To continue, re-run this script.";
    echo "This file is created the first time you run the Predator Volume install script. It is used to determine if the script has been run previously. You can safely delete this file after installation is complete." > $user_home/Downloads/predator_volume_install_script_trigger.txt;
    exit 1;
fi

if [ "$EUID" -ne 0 ]; then # Check to see if this user is root.
    echo "Please run this script as your normal user. You will be prompted to authenticate as root when it is needed.";
else
    echo "===== Starting script =====";
    echo "You may be prompted to enter your root password during the installation."
    echo "===== Preparing environment =====";
    mkdir -p $user_home/Software/;
    cd $user_home/Software/;

    echo "===== Downloading software =====";
    if [ ! -d "$user_home/Software/PredatorVolume" ]; then # Check to see if Predator Volume has not yet been downloaded.
        git clone https://github.com/connervieira/PredatorVolume;
    fi
    if [ ! -d "$user_home/Software/Phantom" ]; then # Check to see if Phantom has not yet been downloaded.
        git clone https://github.com/connervieira/Phantom;
    fi
    
    echo "===== Installing dependencies =====";
    pip3 install --upgrade Levenshtein opencv-python
    if [ "$EUID" -ne 0 ]; then # Check to see if this user is not root.
        sudo su; # Attempt to escalate permissions.
    fi
    if [ "$EUID" -ne 0 ]; then # Check to see if this user is not root.
        echo "Failed to authenticate as root.";
        exit 1;
    fi
    apt install python3 python3-pip python3-opencv ffmpeg libopencv-dev libtesseract-dev git cmake build-essential libleptonica-dev; apt install liblog4cplus-dev libcurl3-dev


    echo "===== Building Phantom ALPR =====";
    cd $user_home/Software/Phantom/src; mkdir build; cd build;
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc ..; make; # Compile Phantom ALPR.
    make install # Install Phantom ALPR.
    cd $user_home; rm -rf $user_home/Software/Phantom/ # Remove the Phantom project directory.

    echo "===== Cleaning up =====";
    rm $user_home/Downloads/predator_volume_install_script_trigger.txt # Delete the install trigger file.
fi

