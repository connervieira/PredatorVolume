#!/bin/bash
user_home=/home/$(ls /home/ | head -n 1);
user=$(ls /home/ | head -n 1)


if [ ! -f "$user_home/Downloads/predator_volume_install_script_trigger.txt" ]; then # Check to see if Predator Volume has not yet been downloaded.
    echo "This script should only be run on a dedicated system running a clean installation of Ubuntu, Pop!_OS, Linux Mint, or similar Linux distribution. This script may delete or overwrite files during installation. Do not use this script on a system containing files you care about."; 
    echo "To continue, re-run this script.";
    echo "This file is created the first time you run the Predator Volume install script. It is used to determine if the script has been run previously. You can safely delete this file after installation is complete." > $user_home/Downloads/predator_volume_install_script_trigger.txt;
    echo "The non-root user detected on this system is $user";
    exit 1;
fi

if [ ! "$EUID" -ne 0 ]; then # Check to see if this user is root.
    echo "===== Preparing environment =====";
    sudo -u $user mkdir -p $user_home/Software/;
    cd $user_home/Software/;

    echo "===== Downloading software =====";
    if [ ! -d "$user_home/Software/PredatorVolume" ]; then # Check to see if Predator Volume has not yet been downloaded.
        sudo -u $user git clone https://github.com/connervieira/PredatorVolume;
    fi
    if [ ! -d "$user_home/Software/Phantom" ]; then # Check to see if Phantom has not yet been downloaded.
        sudo -u $user git clone https://github.com/connervieira/Phantom;
    fi
    
    echo "===== Installing dependencies =====";
    apt install -y python3 python3-pip python3-opencv ffmpeg libopencv-dev libtesseract-dev git cmake build-essential libleptonica-dev; apt install liblog4cplus-dev libcurl3-dev
    sudo -u $user pip3 install --upgrade Levenshtein opencv-python pytesseract;


    echo "===== Building Phantom ALPR =====";
    cd $user_home/Software/Phantom/src; sudo -u $user mkdir build; cd build;
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_INSTALL_SYSCONFDIR:PATH=/etc ..; make; # Compile Phantom ALPR.
    make install # Install Phantom ALPR.
    cd $user_home; rm -rf $user_home/Software/Phantom/ # Remove the Phantom project directory.

    echo "===== Cleaning up =====";
    rm $user_home/Downloads/predator_volume_install_script_trigger.txt # Delete the install trigger file.
else
    echo "Please run this script as root";
    exit 1;
fi

