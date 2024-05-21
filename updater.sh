#!/bin/bash

# wait 10 sec before starting, just to be safe that existing scripts are up and running
sleep 10

# Function to check internet connectivity
check_internet() {
    wget -q --spider http://google.com
    if [ $? -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Wait until an internet connection is available
until check_internet; do
    echo "$(date) - Waiting for internet connection..."
    sleep 5
done

echo "$(date) - Checking for updates..."

cd /home/carolynz/CamTest
git pull origin v4-dev  # Adjust branch name if different

echo "$(date) - Update completed"
