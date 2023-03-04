# From picamera2 examples: capture_jpeg.py 
#!/usr/bin/python3

# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.

import time, requests, signal, os

from picamera2 import Picamera2, Preview
from gpiozero import LED, Button
from Adafruit_Thermal import *
from wraptext import *
from datetime import datetime

#instantiate printer
printer = Adafruit_Thermal('/dev/serial0', 9600, timeout=5)

#instantiate camera
picam2 = Picamera2()
# start camera
picam2.start()
time.sleep(2) # warmup period since first few frames are often poor quality

# NEXT 3 LINES FOR DEBUGGING: computer preview of image
# Slows down the program considerably
# Only use for checking camera object
# TODO: WHY DOES THIS PREVIEW NOT WORK OVER SSH?
#preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})
#picam2.configure(preview_config)
#picam2.start_preview(Preview.QTGL)

#instantiate buttons
shutter_button = Button(16)
power_button = Button(26, hold_time = 2)

# different rotary switch knob positions
knob1 = Button(17)
knob2 = Button(27)
knob3 = Button(22)
knob4 = Button(5)
knob5 = Button(6)
knob6 = Button(13)
knob7 = Button(19)
knob8 = Button(25)
knob9 = Button(24)
knob10 = Button(23)
current_knob = None


#############################
# CORE PHOTO-TO-POEM FUNCTION
#############################
def take_photo_and_print_poem():
  # Take photo & save it
  metadata = picam2.capture_file('/home/carolynz/CamTest/images/image.jpg')

  # FOR DEBUGGING: print metadata
  #print(metadata)

  # TODO? Takes a photo and saves to memory
  #image = picam2.capture_image()
  #print(image)

  # Close camera -- commented out because this can only happen at end of program
  # picam2.close()

  # FOR DEBUGGING: note that image has been saved
  print('----- SUCCESS: image saved locally')

  #######################
  # Receipt printer:
  # Date/time/location frontmatter
  #######################

  # Note: important to put this section as high up as possible
  # to get printing to happen quickly & improve perceived performance

  # Get current date+time -- will use for printing and file naming
  now = datetime.now()

  # Format printed datetime like:
  # Jan 1, 2023
  # 8:11 PM
  printer.justify('C') # center align header text
  date_string = now.strftime('%b %-d, %Y')
  time_string = now.strftime('%-I:%M %p')
  printer.println('\n')
  printer.println(date_string)
  printer.println(time_string)


  # TODO: get and print location

  # optical spacing adjustments
  printer.setLineHeight(56) # I want something slightly taller than 1 row
  printer.println()
  printer.setLineHeight() # Reset to default (32)

  printer.println("`'. .'`'. .'`'. .'`'. .'`'. .'`")
  printer.println("   `     `     `     `     `   ")

  #########################
  # Send saved image to API
  #########################
  api_url = 'https://poetry-camera.carozee.repl.co/pic_to_poem'

  # OLD: get PIL Image object from memory
  # files = {'file': image}

  # Read file that was saved to disk as a byte array
  with open('/home/carolynz/CamTest/images/image.jpg', 'rb') as f:
    byte_im = f.read()

    # prep format for API call
    image_filename = 'rpi-' + now.strftime('%Y-%m-%d-at-%I.%M-%p')
    files = {'file': (image_filename, byte_im, 'image/jpg')}

  # Get poem format
  poem_format = get_poem_format()

  # Send byte array in API
  response = requests.post(api_url, files=files, data={'poem_format': poem_format})
  response_data = response.json()

  # FOR DEBUGGING: print response to console for debugging
  #print(response_data['poem'])

  ############
  # print poem
  ############

  # wrap text to 32 characters per line (max width of receipt printer)
  printable_poem = wrap_text(response_data['poem'], 32)

  printer.justify('L') # left align poem text
  printer.println(printable_poem)

  ##############
  # print footer
  ##############
  printer.justify('C') # center align footer text
  printer.println("   .     .     .     .     .   ")
  printer.println("_.` `._.` `._.` `._.` `._.` `._")
  printer.println('\n')
  printer.println(' This poem was written by AI.')
  printer.println()
  printer.println('Explore the archives at')
  printer.println('poetry.camera')
  printer.println('\n\n\n\n')

  print('----- DONE PRINTING')
  return

##############
# POWER BUTTON
##############
def shutdown():
  print('shutdown button held for 2s')
  print('shutting down now')
  os.system('sudo shutdown -h now')

##################################
# KNOB: GET POEM FORMAT
##################################
def get_poem_format():
  # default
  # note: if no poem format is passed to API,
  # the prompt will default to "2 verses of 4 lines, ABAB rhyme scheme" (knob 1) 
  poem_format = '8 lines or less, ABAB rhyme scheme'

  if knob1.is_pressed:
    # default/auto
    poem_format = '8 lines or less, ABAB rhyme scheme'
  elif knob2.is_pressed:
    poem_format = 'haiku'
  elif knob3.is_pressed:
    poem_format = 'limerick'
  elif knob4.is_pressed:
    poem_format = 'sonnet'
  elif knob5.is_pressed:
    poem_format = 'short poem about the people in this scene. what they look like, how they feel, what their stories are. if there are multiple people, what their relationships might be to each other.'
  elif knob6.is_pressed:
    poem_format = 'short poem about the landscape, background, or location of this scene'
  elif knob7.is_pressed:
    poem_format = 'short poem about the text described in this scene'
  elif knob8.is_pressed:
    poem_format = 'short poem in the style of T.S. Eliot'
  elif knob9.is_pressed:
    poem_format = 'short poem in the style of William Shakespeare'
  elif knob10.is_pressed:
    poem_format = 'short poem in the style of Emily Dickinson'

  # For debugging
  print('----- POEM FORMAT: ' + poem_format)

  return poem_format


#################################
# For RPi debugging:
# Handle Ctrl+C script termination gracefully
# (Otherwise, it shuts down the entire Pi -- bad)
#################################
def handle_keyboard_interrupt(sig, frame):
  print('Ctrl+C received, stopping script')

  #weird workaround I found from rpi forum to shut down script without crashing the pi
  os.kill(os.getpid(), signal.SIGUSR1)

signal.signal(signal.SIGINT, handle_keyboard_interrupt)


################################
# LISTEN FOR BUTTON PRESS EVENTS
################################
shutter_button.when_pressed = take_photo_and_print_poem
power_button.when_held = shutdown

# knob switch events


signal.pause()
