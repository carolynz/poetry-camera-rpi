#!/bin/bash


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
    echo "Waiting for internet connection..."
    sleep 5
done

cd /home/carolynz/CamTest
git pull origin v4-dev  # Adjust branch name if different

echo "Update completed"
