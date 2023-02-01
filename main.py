# From picamera2 examples: capture_jpeg.py 
#!/usr/bin/python3

# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.

import time
import requests

from picamera2 import Picamera2, Preview
from Adafruit_Thermal import *
from datetime import datetime

#instantiate printer
printer = Adafruit_Thermal('/dev/serial0', 19200, timeout=5)

#instantiate camera
picam2 = Picamera2()

# NEXT 3 LINES FOR DEBUGGING: computer preview of image
# Slows down the program considerably
# Only use for checking camera object
preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})
picam2.configure(preview_config)
picam2.start_preview(Preview.QTGL)

# start camera
picam2.start()
time.sleep(2)

# Take photo & save it
metadata = picam2.capture_file('images/test.jpg')

# FOR DEBUGGING: print metadata
#print(metadata)

# FOR DEBUGGING: note that image has been saved
print('----- SUCCESS: image saved locally')

# TODO? Takes a photo and saves to memory
#image = picam2.capture_image()
#print(image)

# Close camera
picam2.close()

#######################
# Receipt printer:
# Date/time/location frontmatter
#######################

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
printer.println()

# TODO: get and print location

printer.println("`'. .'`'. .'`'. .'`'. .'`'. .'`")
printer.println("   `     `     `     `     `   ")



#########################
# Send saved image to API
#########################
api_url = 'https://poetry-camera-prototype.carozee.repl.co/pic_to_poem'

# OLD: get PIL Image object from memory
# files = {'file': image}

# Read file that was saved to disk as a byte array
with open('images/test.jpg', 'rb') as f:
  byte_im = f.read()
  
  # prep format for API call
  image_filename = 'rpi-' + now.strftime('%Y-%m-%d-at-%I.%M-%p')
  files = {'file': (image_filename, byte_im, 'image/jpg')}

# Send byte array in API
response = requests.post(api_url, files=files)
response_data = response.json()

# FOR DEBUGGING: print response to console for debugging
# print(response_data)

############
# print poem
############
printer.justify('L') # left align poem text
printer.println(response_data['poem'])
printer.println()

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
