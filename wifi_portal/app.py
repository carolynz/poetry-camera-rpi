###################################################
# VARIOUS SYSTEM SETUP THINGS
# - Check current branch & commit hash
#   This lets us display which version of the code is running
###################################################
import subprocess, os

# Get the git commit hash to display on portal -- for beta/debugging
def get_git_revision_hash():
    try:
	# get truncated commit hasn (--short)
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
    except Exception as e:
        return str(e)

# get branch name
def get_git_branch_name():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode('utf-8')
    except Exception as e:
        return str(e)

# Get the date of the latest commit
def get_git_commit_date():
    try:
        return subprocess.check_output(['git', 'log', '-1', '--format=%cd', '--date=short']).strip().decode('utf-8')
    except Exception as e:
        return str(e)

commit_hash = get_git_revision_hash()
branch_name = get_git_branch_name()
commit_date = get_git_commit_date()
version_info = f"System last updated: {commit_date}\nVersion: {commit_hash}\nBranch: {branch_name}"

# Save the commit hash to a file
VERSION_FILE_PATH= '/home/carolynz/CamTest/wifi_portal/current_version.txt'
with open(VERSION_FILE_PATH, 'w') as version_file:
    version_file.write(version_info)

#######################################################
# FLASK APP
# Adapted from https://www.raspberrypi.com/tutorials/host-a-hotel-wifi-hotspot/
# This creates a captive portal for the camera to let you set the wifi password on the go
# This runs as a cron job on boot
# Once you're connected to PoetryCameraSetup wifi, it should pop up automatically
# If not, navigate to poetrycamera.local in your browser
#######################################################
from flask import Flask, request, render_template
app = Flask(__name__)

# WIFI_DEVICE specifies internet client (requires separate wifi adapter)
# default Raspberry Pi wifi client is wlan0, which we have set up as an access point
WIFI_DEVICE = "wlan1"

# get code version info we checked upon startup
def get_stored_version():
    try:
        with open(VERSION_FILE_PATH, 'r') as version_file:
            return version_file.read().strip()
    except Exception as e:
        return 'Version: unknown\nBranch: unknown'

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
    ssids_list = [ssid.lstrip("SSID:") for ssid in ssids_list if "PoetryCameraSetup" not in ssid]
    
    return render_template('index.html', ssids_list=ssids_list, version=version_info)


@app.route('/submit',methods=['POST'])
def submit():
  if request.method == 'POST':
    print(*list(request.form.keys()), sep = ", ")
    ssid = request.form['ssid']
    password = request.form['password']
    connection_command = ["nmcli", "--colors", "no", "device", "wifi", "connect", ssid, "ifname", wifi_device]
    if len(password) > 0:
      connection_command.append("password")
      connection_command.append(password)
    result = subprocess.run(connection_command, capture_output=True)
    if result.stderr:
        return "Error: failed to connect to wifi network: <i>%s</i>" % result.stderr.decode()
    elif result.stdout:
        return "Success: <i>%s</i>" % result.stdout.decode()
    return "Error: failed to connect."


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
