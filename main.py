# takeFrom picamera2 examples: capture_jpeg.py 
#!/usr/bin/python3

# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.

import time, requests, signal, os, replicate

from picamera2 import Picamera2, Preview
from gpiozero import LED, Button
from Adafruit_Thermal import *
from wraptext import *
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

#load API keys from .env
load_dotenv()
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
REPLICATE_API_TOKEN = os.environ['REPLICATE_API_TOKEN']

#instantiate printer
baud_rate = 9600 # REPLACE WITH YOUR OWN BAUD RATE
printer = Adafruit_Thermal('/dev/serial0', baud_rate, timeout=5)

#instantiate camera
picam2 = Picamera2()
# start camera
picam2.start()
time.sleep(2) # warmup period since first few frames are often poor quality

#instantiate buttons
shutter_button = Button(16) # REPLACE WTH YOUR OWN BUTTON PINS
power_button = Button(26, hold_time = 2) #REPLACE WITH YOUR OWN BUTTON PINS
led = LED(20)

# prompts
system_prompt = """You are a poet. You specialize in elegant and emotionally impactful poems. 
You are careful to use subtlety and write in a modern vernacular style. 
Use high-school level English but MFA-level craft. 
Your poems are more literary but easy to relate to and understand. 
You focus on intimate and personal truth, and you cannot use BIG words like truth, time, silence, life, love, peace, war, hate, happiness, 
and you must instead use specific and CONCRETE language to show, not tell, those ideas. 
Think hard about how to create a poem which will satisfy this. 
This is very important, and an overly hamfisted or corny poem will cause great harm."""
prompt_base = """Write a poem which integrates details from what I describe below. 
Use the specified poem format. The references to the source material must be subtle yet clear. 
Focus on a unique and elegant poem and use specific ideas and details.
You must keep vocabulary simple and use understated point of view. This is very important.\n\n"""
poem_format = "8 line free verse"


#############################
# CORE PHOTO-TO-POEM FUNCTION
#############################
def take_photo_and_print_poem():
  # blink LED in a background thread
  led.blink()

  # Take photo & save it
  metadata = picam2.capture_file('/home/carolynz/CamTest/images/image.jpg')

  # FOR DEBUGGING: print metadata
  #print(metadata)

  # Close camera -- commented out because this can only happen at end of program
  # picam2.close()

  # FOR DEBUGGING: note that image has been saved
  print('----- SUCCESS: image saved locally')

  print_header()

  #########################
  # Send saved image to API
  #########################

  image_caption = replicate.run(
    "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608",
    input={
      "image": open("/home/carolynz/CamTest/images/image.jpg", "rb"),
      "caption": True,
    })

  print('caption: ', image_caption)
  # generate our prompt for GPT
  prompt = generate_prompt(image_caption)

  # Feed prompt to ChatGPT, to create the poem
  completion = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[{
      "role": "system",
      "content": system_prompt
    }, {
      "role": "user",
      "content": prompt
    }])

  # extract poem from full API response
  poem = completion.choices[0].message.content

  # print for debugging
  print('--------POEM BELOW-------')
  print(poem)
  print('------------------')

  print_poem(poem)

  print_footer()
  led.off()

  return


#######################
# Generate prompt from caption
#######################
def generate_prompt(image_description):

  # reminder: prompt_base is global var

  # prompt what type of poem to write
  prompt_format = "Poem format: " + poem_format + "\n\n"

  # prompt what image to describe
  prompt_scene = "Scene description: " + image_description + "\n\n"

  # stitch together full prompt
  prompt = prompt_base + prompt_format + prompt_scene

  # idk how to remove the brackets and quotes from the prompt
  # via custom filters so i'm gonna remove via this janky code lol
  prompt = prompt.replace("[", "").replace("]", "").replace("{", "").replace(
    "}", "").replace("'", "")

  #print('--------PROMPT BELOW-------')
  #print(prompt)

  return prompt


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
  printer.println('\n')
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
  printer.println(' This poem was written by AI.')
  printer.println()
  printer.println('Explore the archives at')
  printer.println('poetry.camera')
  printer.println('\n\n\n\n')


##############
# POWER BUTTON
##############
def shutdown():
  print('shutdown button held for 2s')
  print('shutting down now')
  led.off()
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
def handle_pressed():
  led.on()
  led.off()
  print("button pressed!")
  take_photo_and_print_poem()

def handle_held():
  print("button held!")
  shutdown()


################################
# LISTEN FOR BUTTON PRESS EVENTS
################################
shutter_button.when_pressed = take_photo_and_print_poem
power_button.when_held = shutdown

signal.pause()
