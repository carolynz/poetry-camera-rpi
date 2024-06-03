#!/bin/bash

# Sentry for error handling - NOT using any of this yet since I'll need time to test
# Some complaints about sentry modifying bash script behavior: https://github.com/getsentry/sentry-cli/issues/1200
#export SENTRY_DSN = https://e3b0c46ba2a11dc9d708d69d4e45d3cf@o4506033759649792.ingest.us.sentry.io/4507326584193024
#eval "$(sentry-cli bash-hook)"

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

# TODO proper error handling for when pulls fail
cd /home/carolynz/CamTest
git pull origin v4-dev  # Adjust branch name if different

echo "$(date) - Update completed"
