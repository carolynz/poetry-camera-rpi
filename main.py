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
from PIL import Image
import sentry_sdk


##############################
# GLOBAL CONSTANTS
##############################
PROJECT_DIRECTORY = '/home/carolynz/CamTest/'
WIFI_QR_IMAGE_PATH = PROJECT_DIRECTORY + 'wifi-qr.bmp'
PRINTER_BAUD_RATE = 9600 # REPLACE WITH YOUR OWN BAUD RATE
PRINTER_HEAT_TIME = 190 # darker prints than Adafruit library default (130), max 255

###################
# INITIALIZE
###################
def initialize():
  # Set up status LED
  global led
  led = LED(26)
  led.blink() # blink LED while setting up

  # Load environment variables
  load_dotenv()

  # Get unique device ID -- need to do this first for error logging
  global device_id
  device_id = os.environ['DEVICE_ID']

  # Sentry for error logging & handle uncaught exceptions
  sentry_sdk.init(
    dsn="https://5a8f9bfc5cac11b2d20ae3523fe78e0c@o4506033759649792.ingest.us.sentry.io/4507324515418112",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
  )

  # Make sure device ID is passed in error logging
  sentry_sdk.set_tag("device_id", device_id)

  # Set up printer
  global printer
  try:
    printer = Adafruit_Thermal('/dev/serial0', PRINTER_BAUD_RATE, timeout=5)
    printer.begin(PRINTER_HEAT_TIME)
  except Exception as e:
    print(f"Error while initializing {device_id} printer: {e}")
    blink_sos_indefinitely()
    return

  # Set up camera
  global picam2, camera_at_rest
  try:
    picam2 = Picamera2()
    picam2.start()
    sleep(2) # camera warm-up time
  except Exception as e:
    print(f"Error while initializing {device_id} camera: {e}")
    printer.println("uh-oh, can't get camera input.")
    printer.println("probably a loose camera cable or broken camera module.")
    printer.feed()
    printer.println("support@poetry.camera")
    printer.feed(3)
    blink_sos_indefinitely()
    return

  # prevent double-click bugs by checking whether the camera is resting
  # (i.e. not in the middle of the whole photo-to-poem process):
  camera_at_rest = True

  # Set up shutter button
  global shutter_button
  shutter_button = Button(16)

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

  # Server URL
  global SERVER_URL
  SERVER_URL = "https://poetry-camera-cf.hi-ea7.workers.dev/"
  #SERVER_URL = "https://pc-staging.hi-ea7.workers.dev/"

  # Check internet connectivity upon startup
  global internet_connected 
  internet_connected = False
  check_internet_connection()

  # Turn on LED to indicate setup is complete
  if internet_connected == True:
    led.on()

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
  directory = PROJECT_DIRECTORY + 'images/'
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
    image_data = f"data:image/jpeg;base64,{base64_image}"

    # Get current knob number
    global current_knob
    get_current_knob()

    # Send POST request to API
    print("sending request...")
    response = requests.post(
      SERVER_URL,
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
    #print_poem("\n\nTroubleshooting:")
    #print_poem("1. Check your wifi connection.")
    #print_poem("2. Try restarting the camera by holding the shutter button for 10 seconds, waiting for it to shut down, unplugging power, and plugging it back in.")
    #print_poem("3. You may just need to wait a bit and it will pass.")
    #print_footer()
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
  printer.feed()
  printer.println('a poem by')
  printer.println('@poetry.camera')
  printer.feed(4)

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
  current_knob = 0

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

def printWifiQr():
  printer.println('step 1:            step 2:')
  printer.feed()
  printer.begin(255) #set heat time to max, for darkest print
  printer.printImage(WIFI_QR_IMAGE_PATH)
  printer.begin(PRINTER_HEAT_TIME) # reset heat time

# Checks internet connection upon startup
def check_internet_connection():
  print("Checking internet connection upon startup")
  printer.feed()
  printer.justify('C') # center align header text
  printer.println("poetry camera")

  global internet_connected
  try:
    # Check for internet connectivity
    subprocess.check_call(['ping', '-c', '1', 'google.com'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    internet_connected = True
    print("CAMERA ONLINE")
    printer.println("online, connected, awake")
    printer.println("ready to print verse")
    #printer.feed()
    #printer.println('step 1:            step 2:')
    #printer.feed()
    #printWifiQr()

    # Get the name of the connected Wi-Fi network
    # try:
    #   network_name = subprocess.check_output(['iwgetid', '-r']).decode().strip()
    #   print(f"Connected to network: {network_name}")
    #   printer.println(f"connected to: {network_name}")
    # except Exception as e:
    #   print("Error while getting network name: ", e)
    
  except subprocess.CalledProcessError:
    internet_connected = False
    print("no internet on startup!")
    printer.println("offline, disconnected")
    printer.println('scan codes to connect')
    printer.feed()
    printWifiQr()

  printer.feed(3)

###############################
# CHECK INTERNET CONNECTION PERIODICALLY, PRINT ERROR MESSAGE IF DISCONNECTED
###############################
# NOTE: VERY BUGGY AND STRANGE, LIKELY SOME STATE MANAGEMENT ISSUE
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
        printer.println('back online / just in time')
        printer.feed(3)
        internet_connected = True
      
      led.on()

    # if we don't have internet, exception will be thrown      
    except subprocess.CalledProcessError as e:
      # HACKY WAY TO AVOID THE RETURN CODE 1 BUG
      # FIX IT ASAP
      if e.returncode == 2:
        # if we were previously connected but lost internet, print error message & blink LED to indicate waiting status
        led.blink()
        if internet_connected:
          print(f"{time_string} internet connection lost: {e}")
          printer.feed()
          printer.println(time_string)
          printer.println("lost my internet")
          printer.println('scan codes to get back online')
          printer.println('verses will resume')
          printer.feed()
          printWifiQr()
          printer.feed(3)
          internet_connected = False
      else: # if we encounter return code 1
        print(f"{time_string} Other return code in periodic_internet_check: {e}")

    except Exception as e:
      print(f"{time_string} Other exception in periodic_internet_check: {e}")
      # if we were previously connected but lost internet, print error message
      if internet_connected:
        printer.feed()
        printer.println(f"{time_string}: idk status, exception: {e}")
        printer.feed(3)
        internet_connected = False

    sleep(interval) #makes thread idle during sleep period, freeing up CPU resources

def start_periodic_internet_check():
  # Start the background thread
  interval = 5  # Check every 5 seconds
  thread = threading.Thread(target=periodic_internet_check, args=(interval,))
  thread.daemon = True  # Daemonize thread
  thread.start()

# Error state when something blocks main camera code from running
# Blink SOS in morse code... the drama!
def blink_sos_indefinitely():
  while True:
    # blink S (3 short blinks)
    for _ in range(3):
      led.on()
      sleep(0.25)
      led.off()
      sleep(0.25)
    sleep(0.25)
    # blink O (3 long blinks)
    for _ in range(3):
      led.on()
      sleep(0.75)
      led.off()
      sleep(0.25)
    sleep(0.25)
    # blink S (3 short blinks)
    for _ in range(3):
      led.on()
      sleep(0.25)
      led.off()
      sleep(0.25)
    sleep(1)

# Main function
if __name__ == "__main__":
    initialize()
    # Keep script running to listen for button presses
    signal.pause()
