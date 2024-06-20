# This Flask app must be run in sudo, with the full path to this file
# "sudo python /home/USERNAME/PROJECT_DIRECTORY/wifi_portal/app.py"

###################################################
# VARIOUS SYSTEM SETUP THINGS
# - Check current branch & commit hash
#   This lets us display which version of the code is running
###################################################
import subprocess, os

# Change to the directory of your Git repository
# NOTE: this means, in order to run the app, you have to use the full path to the app.py file
# e.g. sudo python /home/pi/CamTest/wifi_portal/app.py

POETRY_CAMERA_DIRECTORY = '/home/carolynz/CamTest/'

try:
    os.chdir(POETRY_CAMERA_DIRECTORY)
except Exception as e:
    print(f"Failed to change directory: {e}")


# Get the git commit hash to display on portal -- for beta/debugging
def get_git_revision_hash():
    try:
	# get truncated commit hasn (--short)
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
    except Exception as e:
        print(f"Failed to get commit hash: {e}")
        return str(e)

# get branch name
def get_git_branch_name():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
    except Exception as e:
        print(f"Failed to get branch name: {e}")
        return str(e)

# Get the date of the latest commit
def get_git_commit_date():
    try:
        return subprocess.check_output(['git', 'log', '-1', '--format=%cd', '--date=short']).strip().decode('utf-8')
    except Exception as e:
        print(f"Failed to get commit date: {e}")
        return str(e)

commit_hash = get_git_revision_hash()
branch_name = get_git_branch_name()
commit_date = get_git_commit_date()
version_info = f"System last updated: {commit_date}\nVersion: {commit_hash}\nBranch: {branch_name}"

# Save the commit hash to a file
SOFTWARE_VERSION_FILE_PATH = POETRY_CAMERA_DIRECTORY + 'wifi_portal/current_version.txt'
with open(SOFTWARE_VERSION_FILE_PATH, 'w') as version_file:
    version_file.write(version_info)

#######################################################
# FLASK APP
# Adapted from https://www.raspberrypi.com/tutorials/host-a-hotel-wifi-hotspot/
# This creates a captive portal for the camera to let you set the wifi password on the go
# This runs as a cron job on boot
# Once you're connected to PoetryCameraSetup wifi, it should pop up automatically
# If not, navigate to poetrycamera.local in your browser
#######################################################
import json, threading, time
from flask import Flask, request, render_template, jsonify
app = Flask(__name__)

# WIFI_DEVICE specifies internet client (requires separate wifi adapter)
# The default Raspberry Pi wifi client is wlan0, but we have set it up as an Access Point
# wlan1 is the second wifi adapter we have plugged in, to connect to internet
WIFI_DEVICE = "wlan1"


config_file = POETRY_CAMERA_DIRECTORY + "wifi_portal/hotspot_config.json"


# get code version info we checked upon startup
def get_stored_version():
    try:
        with open(SOFTWARE_VERSION_FILE_PATH, 'r') as version_file:
            return version_file.read().strip()
    except Exception as e:
        return 'Version: unknown\nBranch: unknown'

# Function to load hotspot configuration
def load_hotspot_config():
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Function to save hotspot configuration
def save_hotspot_config(ssid, password = None):
    if password:
        config = {
            "ssid": ssid,
            "password": password
        }
    else:
        config = {
            "ssid": ssid
        }
    with open(config_file, 'w') as f:
        json.dump(config, f)

# Function to attempt connecting to the saved hotspot
def attempt_connect_hotspot(ssid, password = None):
    """
    config = load_hotspot_config()
    if not config:
        return "No hotspot configuration found."
    
    ssid = config.get("ssid")
    password = config.get("password")
    """
    connection_command = ["nmcli", "--colors", "no", "device", "wifi", "connect", ssid]
    if password:
        connection_command.extend(["password", password])
        
    result = subprocess.run(connection_command, capture_output=True)
    if result.stderr:
        return f"Error: {result.stderr.decode()}"
    elif result.stdout:
        return f"Success: {result.stdout.decode()}"
    return "Unknown error."

# screen where you set wifi password
@app.route('/')
def index():
    try:
	# get list of wifi networks nearby
        result = subprocess.check_output(["nmcli", "--colors", "no", "-m", "multiline", "--get-value", "SSID", "dev", "wifi", "list", "ifname", WIFI_DEVICE])
        ssids_list = result.decode().split('\n')
    except subprocess.CalledProcessError as e:
        return f"Error: Unable to retrieve WiFi networks. Likely a wifi adapter issue. {e}"
    
    # Remove 'PoetryCameraSetup' from the list, that's the camera's own wifi network
    # And remove the prefix "SSID:" from networks in the list
    # (We expect the ssids_list to look like: ["SSID:network1", "SSID:network2", "SSID:PoetryCameraSetup", ...])
    ssids_list = [ssid[5:] for ssid in ssids_list if "PoetryCameraSetup" not in ssid]

    # Remove empty strings and duplicates
    unique_ssids_list = list(set(filter(None, ssids_list)))

    return render_template('index.html', ssids_list=unique_ssids_list, version=version_info)


@app.route('/submit', methods=['POST'])
def submit():
    ssid = request.form['ssid']
    password = request.form['password']
    connection_command = ["nmcli", "--colors", "no", "device", "wifi", "connect", ssid, "ifname", WIFI_DEVICE]
    if len(password) > 0:
        connection_command.append("password")
        connection_command.append(password)
    result = subprocess.run(connection_command, capture_output=True)
    
    if result.stderr:
        stderr_message = result.stderr.decode().lower()
        if "psk: property is invalid" in stderr_message:
            return jsonify({"status": "error", "message": "Wrong password"})
        return jsonify({"status": "error", "message": stderr_message})
    elif result.stdout:
        stdout_message = result.stdout.decode().lower()
        if "successfully activated" in stdout_message:
            return jsonify({"status": "success", "message": result.stdout.decode()})
        elif "connection activation failed" in stdout_message:
            return jsonify({"status": "error", "message": "Connection activation failed."})
        elif "no network with ssid" in stdout_message:
            return jsonify({"status": "error", "message": "Could not find a wifi network with this name."})
        elif "no valid secrets" in stdout_message:
            return jsonify({"status": "error", "message": "Wrong password"})
        elif "no suitable device found" in stdout_message:
            return jsonify({"status": "error", "message": "Could not connect. Possible hardware issue with the wifi adapter."})
        elif "device not ready" in stdout_message:
            # TODO: just retry the command like 3 more times
            return jsonify({"status": "error", "message": "The device is not ready."})
        elif "invalid password" in stdout_message:
            return jsonify({"status": "error", "message": "Wrong password"})
        elif "could not be found or the password is incorrect" in stdout_message:
            return jsonify({"status": "error", "message": "The password is incorrect or the network could not be found."})
        else:
            return jsonify({"status": "error", "message": result.stdout.decode()})
    return jsonify({"status": "error", "message": "Could not connect. Please try again."})

@app.route('/save_and_connect', methods=['POST'])
def save_and_connect():
    manual_ssid = request.form['manual_ssid']
    manual_password = request.form['manual_password']
    save_hotspot_config(manual_ssid, manual_password)
    
    def hotspot_scanning():
        end_time = time.time() + 120  # Run for 2 minutes
        while time.time() < end_time:
            result = attempt_connect_hotspot()
            print(result)  # Log the result, can be changed to more sophisticated logging
            if "Success" in result:
                break
            time.sleep(5)
    
    threading.Thread(target=hotspot_scanning).start()
    return f"Attempting to connect to the {manual_ssid} network. If you are using a hotspot, go to your hotspot settings page and leave it open so it can connect. This could take up to 2 minutes."




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
