#!/bin/bash

# It is used to gather the os and kernel information for a talon board and write it to a file, which will be copied over to the artifacts/results/test_parameters folder
# Author: Sheldon Downie | sheldon.downie@mda.space
# Date: May 22 2024

talon_target_id=$1
talon_ip=$2

cleanup_exit(){
    if [ -e "$TEMP_DIR" ]; then
        echo "removing $TEMP_DIR before exit"
        rm -rf "$TEMP_DIR"
    fi
    echo "Exit code $1"  
    exit "$1"
}

# add headers if file doesn't exist already
if [ ! -f talon_board_info.txt ]; then
    echo -e "TALON-DX BOARD\tIP\tOS\tKERNEL" > talon_board_info.txt
fi

os_info=$(ssh -o StrictHostKeyChecking=no root@"$talon_ip" -n "cat /etc/os-release | grep PRETTY_NAME | cut -d '\"' -f2")
kernel_info=$(ssh -o StrictHostKeyChecking=no root@"$talon_ip" -n "cat /proc/version")
echo -e "$talon_target_id\t$talon_ip\t$os_info\t$kernel_info" >> talon_board_info.txt

# align the columns nicely
column -ts $'\t' talon_board_info.txt

cleanup_exit 0
