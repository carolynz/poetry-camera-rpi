import subprocess
import os

# absolute paths to the various scripts to run
script_directory = "/home/carolynz/CamTest"
wifi_setup_script = "wifi_setup.py"
main_script = "main.py"

def check_internet_connection(host="8.8.8.8", count=4, timeout=5):
  """
  Check for internet by pinging google.com
  :param host: Hostname or IP address to ping for checking internet connectivity
  :param count: Number of echo requests to send
  :param timeout: Timeout in seconds for each ping request
  :return: True if the internet is accessible, False otherwise
  """
  try:
    subprocess.check_output(
      ["ping", "-c", str(count), "-W", str(timeout), host],
      stderr=subprocess.STDOUT,
      universal_newlines=True
    )
    return True
  except subprocess.CalledProcessError:
    return False


def run_script(script_name):
  script_path = os.path.join(script_directory, script_name)
  # command = "python {}".format(script_path)
  # os.system(command)
  # note -- using subprocess.run instead of os.system since it has better mechanisms for handling output
  subprocess.run(['python', script_path], check=True)

if __name__ == "__main__":
  if check_internet_connection():
    print("internet connection available, starting main camera code")
    run_script(main_script)
  else: 
    print("no internet detected, starting network setup")
    run_script(wifi_setup_script)
