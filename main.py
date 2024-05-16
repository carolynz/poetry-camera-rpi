#!/usr/bin/python3
# test comment

# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.

import requests, signal, os, base64, subprocess, threading
from picamera2 import Picamera2, Preview
from libcamera import controls
from gpiozero import LED, Button
from Adafruit_Thermal import *
from wraptext import *
from datetime import datetime
from dotenv import load_dotenv
from time import time, sleep


##############################
# GLOBAL CONSTANTS FOR PROMPTS
##############################

def initialize():
  # Load environment variables
  load_dotenv()

  # Get unique device ID
  global device_id
  device_id = os.environ['DEVICE_ID']

  # Set up printer
  global printer
  BAUD_RATE = 9600 # REPLACE WITH YOUR OWN BAUD RATE
  printer = Adafruit_Thermal('/dev/serial0', BAUD_RATE, timeout=5)

  # Set up camera
  global picam2, camera_at_rest
  picam2 = Picamera2()
  picam2.start()
  sleep(2) # camera warm-up time
  
  # prevent double-click bugs by checking whether the camera is resting
  # (i.e. not in the middle of the whole photo-to-poem process):
  camera_at_rest = True

  # Set up shutter button & status LED
  global shutter_button, led
  shutter_button = Button(16)
  led = LED(26)
  led.on()

  # button event handlers
  shutter_button.when_pressed = on_press
  shutter_button.when_released = on_release

  # Set up knob, if you are using a knob
  global current_knob, knobs

  knob1 = Button(17)
  knob2 = Button(27)
  knob3 = Button(22)
  knob4 = Button(5)
  knob5 = Button(6)
  knob6 = Button(13)
  knob7 = Button(19)
  knob8 = Button(25)

  knobs = [knob1, knob2, knob3, knob4, knob5, knob6, knob7, knob8]
  get_current_knob()

  # Check internet connectivity upon startup
  global internet_connected 
  internet_connected = False
  check_internet_connection()

  # And periodically check internet in background thread
  start_periodic_internet_check()


#############################
# CORE PHOTO-TO-POEM FUNCTION
#############################
# Called when shutter button is pressed
def take_photo_and_print_poem():
  # prevent double-clicks by indicating camera is active
  global camera_at_rest
  camera_at_rest = False

  # blink LED in a background thread
  led.blink()

  # FOR DEBUGGING: filename  
  directory = '/home/carolynz/CamTest/images/'
  # timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
  #photo_filename = directory + 'image_' + timestamp + '.jpg'
  photo_filename = directory + 'image.jpg'

  # Take photo & save it
  metadata = picam2.capture_file(photo_filename)

  # FOR DEBUGGING: print metadata
  #print(metadata)

  # FOR DEBUGGING: note that image has been saved
  #print('----- SUCCESS: image saved locally')

  print_header()

  #########################
  # Send saved image to API
  #########################
  try:
    # Encode image as base64
    base64_image = encode_image(photo_filename)
    #format into expected string for api
    image_data = f"data:image/png;base64,{base64_image}"

    # Get current knob number
    global current_knob
    get_current_knob()

    # Send POST request to API
    print("sending request...")
    response = requests.post(
      "https://poetry-camera-cf.hi-ea7.workers.dev/",
      json={"image": image_data, "deviceId": device_id, "knob": current_knob}
    )



    # Check if request was successful
    if response.status_code != 200:
      raise Exception(f"Request failed with status code {response.status_code}")

    # Parse JSON response
    poem_response = response.json()
    print("backend response:")
    print(poem_response)

    # Extract poem & caption from full API response
    poem = poem_response['poem']
    caption=poem_response['caption']

  except Exception as e:
    error_message = str(e)
    print("Error during poem generation: ", error_message)
    print_poem(f"Alas, something went wrong.\n\n.Technical details:\n Error while writing poem. {error_message}")
    print_poem("\n\nTroubleshooting:")
    print_poem("1. Check your wifi connection.")
    print_poem("2. Try restarting the camera by holding the shutter button for 10 seconds, waiting for it to shut down, unplugging power, and plugging it back in.")
    print_poem("3. You may just need to wait a bit and it will pass.")
    print_footer()
    led.on()
    camera_at_rest = True
    return


  # for debugging prompts

  print('----- CAPTION -----')
  print(caption)
  print('-------------------')
  print('------ POEM -------')
  print(poem)
  print('-------------------')

  print_poem(poem)

  print_footer()

  led.on()

  # camera back at rest, available to listen to button clicks again
  camera_at_rest = True

  return


# Function to encode the image as base64 for api request
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


###########################
# RECEIPT PRINTER FUNCTIONS
###########################

def print_poem(poem):
  # wrap text to 32 characters per line (max width of receipt printer)
  printable_poem = wrap_text(poem, 32)

  printer.justify('L') # left align poem text
  printer.println(printable_poem)


# print date/time/location header
def print_header():
  # Get current date+time -- will use for printing and file naming
  now = datetime.now()

  # Format printed datetime like:
  # Jan 1, 2023
  # 8:11 PM
  printer.justify('C') # center align header text
  date_string = now.strftime('%b %-d, %Y')
  time_string = now.strftime('%-I:%M %p')
  #printer.println('\n')
  printer.println(date_string)
  printer.println(time_string)

  # optical spacing adjustments
  printer.setLineHeight(56) # I want something slightly taller than 1 row
  printer.println()
  printer.setLineHeight() # Reset to default (32)

  printer.println("`'. .'`'. .'`'. .'`'. .'`'. .'`")
  printer.println("   `     `     `     `     `   ")


# print footer
def print_footer():
  printer.justify('C') # center align footer text
  printer.println("   .     .     .     .     .   ")
  printer.println("_.` `._.` `._.` `._.` `._.` `._")
  printer.println('\n')
  printer.println('a poem by')
  printer.println('@poetry.camera')
  printer.println('\n')
  printer.println('billion dollar boy x snapchat')
  printer.println('\n\n\n\n\n')

##############
# POWER BUTTON
##############
def shutdown():
  print('shutting down...')

  # blink LED before shutting down
  for _ in range(5):
    led.on()
    sleep(0.25)
    led.off()
    sleep(0.25)

  os.system('sudo shutdown -h now')

################################
# For RPi debugging:
# Handle Ctrl+C script termination gracefully
# (Otherwise, it shuts down the entire Pi -- bad)
#################################
def handle_keyboard_interrupt(sig, frame):
  print('Ctrl+C received, stopping script')
  led.off()

  #weird workaround I found from rpi forum to shut down script without crashing the pi
  os.kill(os.getpid(), signal.SIGUSR1)

signal.signal(signal.SIGINT, handle_keyboard_interrupt)


#################
# Button handlers
#################

def on_press():
  # track when button was pressed
  global press_time
  press_time = time()

  led.off()

def on_release():
  # calculate how long button was pressed
  global press_time
  release_time = time()

  led.on()

  duration = release_time - press_time

  # if user clicked button
  # the > 0.05 check is to make sure we aren't accidentally capturing contact bounces
  # https://www.allaboutcircuits.com/textbook/digital/chpt-4/contact-bounce/
  if duration > 0.05 and duration < 2:
    if camera_at_rest:
      take_photo_and_print_poem()
    else:
      print("ignoring double click while poem is printing")
  elif duration > 9: #if user held button
    shutdown()


################################
# KNOB: GET POEM FORMAT
################################
def get_current_knob():
  global current_knob, knobs
  current_knob = 1

  # set current knob number
  for i, knob in enumerate(knobs, start=1):
    if knob.is_pressed:
      current_knob = i
      break
  print('----- CURRENT KNOB: ' + str(current_knob))

  return current_knob


################################
# CHECK INTERNET CONNECTION
################################
# Checks internet connection upon startup
def check_internet_connection():
  print("Checking internet connection upon startup")
  printer.println("\n")
  printer.justify('C') # center align header text
  printer.println("hello, i am")
  printer.println("poetry camera")

  global internet_connected
  try:
    # Check for internet connectivity
    subprocess.check_call(['ping', '-c', '1', 'google.com'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    internet_connected = True
    print("i am ONLINE")
    printer.println("and i am ONLINE!")
    
    # Get the name of the connected Wi-Fi network
    # try:
    #   network_name = subprocess.check_output(['iwgetid', '-r']).decode().strip()
    #   print(f"Connected to network: {network_name}")
    #   printer.println(f"connected to: {network_name}")
    # except Exception as e:
    #   print("Error while getting network name: ", e)
    
  except subprocess.CalledProcessError:
    internet_connected = False
    print("no internet!")
    printer.println("but i'm OFFLINE!")
    printer.println("i need internet to work!")
    printer.println('connect to PoetryCameraSetup wifi network (pw: "password") on your phone or laptop to fix me!')

  printer.println("\n\n\n\n\n")

###############################
# CHECK INTERNET CONNECTION PERIODICALLY, PRINT ERROR MESSAGE IF DISCONNECTED
###############################
def periodic_internet_check(interval):
  global internet_connected, camera_at_rest

  while True:
    now = datetime.now()
    time_string = now.strftime('%-I:%M %p')
    try:
      # Check for internet connectivity
      subprocess.check_call(['ping', '-c', '1', 'google.com'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
      # if we don't have internet, exception will be called      

      # If previously disconnected but now have internet, print message
      if not internet_connected:
        print(time_string + ": I'm back online!")
        internet_connected = True

    # if we don't have internet, exception will be thrown      
    # except subprocess.CalledProcessError:
    except (requests.ConnectionError, requests.Timeout) as e:

      # if we were previously connected but lost internet, print error message
      if internet_connected:
        print(time_string + ": Internet connection lost. Please check your network settings.")
        printer.println("\n")
        printer.println(time_string + ": oh no, i lost internet!")
        # printer.println('please connect to PoetryCameraSetup wifi network (pw: "password") on your phone to fix me!')
        printer.println(e)
        printer.println('\n\n\n\n\n')
        internet_connected = False

    except Exception as e:
      print(f"{time_string} Other error: {e}")
      # if we were previously connected but lost internet, print error message
      if internet_connected:
        printer.println(f"{time_string}: idk status, exception: {e}")
        internet_connected = False

    sleep(interval) #makes thread idle during sleep period, freeing up CPU resources

def start_periodic_internet_check():
  # Start the background thread
  interval = 10  # Check every 10 seconds
  thread = threading.Thread(target=periodic_internet_check, args=(interval,))
  thread.daemon = True  # Daemonize thread
  thread.start()

# Main function
if __name__ == "__main__":
    initialize()
    # Keep script running to listen for button presses
    signal.pause()
