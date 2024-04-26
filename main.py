#!/usr/bin/python3
# test comment

# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.

import requests, signal, os, base64, threading
from picamera2 import Picamera2, Preview
from libcamera import controls
from gpiozero import LED, Button
from Adafruit_Thermal import *
from wraptext import *
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from time import time, sleep
from google.cloud import storage
from google.oauth2 import service_account

# server -- for workshop, each kit has a different server
api_url = 'https://poecam-workshop-template-carozee.replit.app/image-to-text'

#instantiate printer
baud_rate = 9600 # REPLACE WITH YOUR OWN BAUD RATE
printer = Adafruit_Thermal('/dev/serial0', baud_rate, timeout=5)

#instantiate camera
picam2 = Picamera2()
picam2.start()
sleep(2)

#instantiate buttons
shutter_button = Button(16)
led = LED(26)
led.on()

# prevent double-click bugs by checking whether the camera is resting
# (i.e. not in the middle of the whole photo-to-poem process):
camera_at_rest = True

#############################
# CORE PHOTO-TO-POEM FUNCTION
#############################
def take_photo_and_print_poem():
  # prevent double-clicks by indicating camera is active
  global camera_at_rest
  camera_at_rest = False

  # blink LED in a background thread
  led.blink()

  # FOR DEBUGGING: filename
  directory = '/home/carolynz/CamTest/images/'
  photo_filename = directory + 'image.jpg'

  # Take photo & save it
  metadata = picam2.capture_file(photo_filename)

  # FOR DEBUGGING: print metadata
  #print(metadata)

  # FOR DEBUGGING: upload photo to gcs in a background thread
  #start_upload_thread(bucket_name, photo_filename, destination_blob_name)

  print('----- SUCCESS: image saved locally')

  print_header()

  #########################
  # Send saved image to API
  #########################
  try:
    # Send saved image to API
    # Read file that was saved to disk as a byte array
    print('trying to open image to send')
    with open('/home/carolynz/CamTest/images/image.jpg', 'rb') as f:
      byte_im = f.read()

      # prep format for API call
      image_filename = 'rpi-' + datetime.now().strftime('%Y-%m-%d-at-%I.%M-%p')
      files = {'file': (image_filename, byte_im, 'image/jpg')}

    # Send byte array in API
    print('posting request...')
    response = requests.post(api_url, files=files)
    print('req posted, awaiting response...')
    response_data = response.json()
    print('response_data: ', response_data)

  except Exception as e:
    error_message = str(e)
    print(response.status_code)
    print("Error: ", error_message)
    print_poem("Error: " + error_message)
    camera_at_rest = True
    return


  # extract poem
  poem = response_data['poem']

  # for debugging prompts
  print('------ POEM ------')
  print(poem)
  print('------------------')

  print_poem(poem)

  print_footer()

  led.on()

  # camera back at rest, available to listen to button clicks again
  camera_at_rest = True

  return

# Function to start the photo upload process in a background thread
def start_upload_thread(bucket_name, source_file_name, destination_blob_name):
  upload_thread = threading.Thread(target=upload_to_gcs, args=(bucket_name, source_file_name, destination_blob_name))
  upload_thread.start()
  # You can join the thread if you want to wait for it to complete in another part of your program
  # upload_thread.join()

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
  printer.println('poetry camera workshop')
  printer.println('@ sva mfa ixd')
  printer.println('\n')
  printer.println('more at poetry.camera')
  #printer.println('a poem by')
  #printer.println('@poetry.camera')
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


###############################
# LISTEN FOR BUTTON PRESS EVENTS
################################
shutter_button.when_pressed = on_press
shutter_button.when_released = on_release


#keeps script alive so the camera functionality keeps running
signal.pause()

