# From picamera2 examples: capture_jpeg.py 

#!/usr/bin/python3

# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.

import time
import requests

from picamera2 import Picamera2, Preview
from Adafruit_Thermal import *

printer = Adafruit_Thermal('/dev/serial0', 19200, timeout=5)

picam2 = Picamera2()

# FOR DEBUGGING: computer preview of image
# preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})
# picam2.configure(preview_config)
# picam2.start_preview(Preview.QTGL)

picam2.start()
time.sleep(2)

# Takes photo & saves it
# TODO: make saved images have a unique filename
metadata = picam2.capture_file('images/test.jpg')
# FOR DEBUGGING: print metadata
#print(metadata)
# FOR DEBUGGING: note that image has been saved
print('----- SUCCESS: image saved locally')

# receipt printer prints status update
printer.println('\n\nAI poetry camera')
#printer.println('\n\nThinking...')
#printer.println('\n\nWriting...')

# Takes a photo and saves to memory
#image = picam2.capture_image()
#print(image)

# Close camera
picam2.close()

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
  files = {'file': ('test.jpg', byte_im, 'image/jpg')}

# Send byte array in API
response = requests.post(api_url, files=files)
response_data = response.json()

# FOR DEBUGGING: print response to console for debugging
# print(response_data)

# print poem!!!
printer.println('\n')
printer.println(response_data['poem'])
printer.println('\n\n\n\n')
