#!/usr/bin/python3
# test comment

# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.

import requests, signal, os, base64, subprocess, threading
from gpiozero import LED, Button
from Adafruit_Thermal import *
from wraptext import *
from datetime import datetime
from time import time, sleep


##############################
# GLOBAL CONSTANTS FOR PROMPTS
##############################

def initialize():
  # Set up printer
  global printer
  BAUD_RATE = 9600 # REPLACE WITH YOUR OWN BAUD RATE
  printer = Adafruit_Thermal('/dev/serial0', BAUD_RATE, timeout=5)

  # Set up shutter button & status LED
  global shutter_button, led
  shutter_button = Button(16)
  led = LED(26)
  led.on()

  # button event handlers
  shutter_button.when_pressed = on_press
  shutter_button.when_released = on_release


#############################
# CORE PHOTO-TO-POEM FUNCTION
#############################
# Called when shutter button is pressed
def testprint():
  # blink LED in a background thread
  led.blink()

  print_header()

  print_footer()

  led.on()

  return

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
  #printer.println('poetry camera @ runway rna')
  #printer.println('\n')
  #printer.println('more at poetry.camera')
  printer.println('a poem by')
  printer.println('@poetry.camera')
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
def get_poem_format():
  poem_format = '4 line free verse. Do not rhyme. DO NOT EXCEED 4 LINES.'

  if knob1.is_pressed:
    poem_format = '4 line free verse. Do not rhyme. DO NOT EXCEED 4 LINES.'
  elif knob2.is_pressed:
    poem_format = 'Modern Sonnet. The poem must match the format of a sonnet, but it should be written in modern vernacular english, it must not be written in olde english.'
  elif knob3.is_pressed:
    poem_format = 'limerick. DO NOT EXCEED 5 LINES.'
  elif knob4.is_pressed:
    poem_format = 'couplet. You must write a poem that is only two lines long. Make sure to incorporate elements from the image. It must be only two lines.'
  elif knob5.is_pressed:
    poem_format = 'poem where each word begins with the same letter. It must be four lines or less.'
  elif knob6.is_pressed:
    poem_format = 'poem where each word is a verb. It must be four lines or less.'
  elif knob7.is_pressed:
    poem_format = 'haiku. You must match the 5 syllable, 7 syllable, 5 syllable format. It must not rhyme'
  elif knob8.is_pressed:
    poem_format = '8 line rhyming poem. Do not exceed 8 lines.'
  print('----- POEM FORMAT: ' + poem_format)

  return poem_format


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
  try:
    # Check for internet connectivity
    subprocess.check_call(['ping', '-c', '1', 'google.com'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("WE ARE ONLINE")
    printer.println("and i am ONLINE!")
    
    # Get the name of the connected Wi-Fi network
    # network_name = subprocess.check_output(['iwgetid', '-r']).decode().strip()
    # if network_name:
    #   print(f"Connected to network: {network_name}")
    #   printer.println(f"connected to: {network_name}")
    # else:
    #   print("Connected to network, but could not retrieve network name.")
    #   printer.println("but i can't find the network name.")
    
  except subprocess.CalledProcessError:
    print("no internet!")
    printer.println("but i'm OFFLINE!")
    printer.println("i need internet to work!")
    printer.println('please connect to the PoetryCameraSetup wifi network (pw: "password") on your phone to fix me!')

  printer.println("\n\n\n\n\n")

###############################
# CHECK INTERNET CONNECTION PERIODICALLY, PRINT ERROR MESSAGE IF DISCONNECTED
###############################
def periodic_internet_check(interval):
  while True:
    now = datetime.now()
    time_string = now.strftime('%-I:%M %p')
    try:
      # Check for internet connectivity
      subprocess.check_call(['ping', '-c', '1', 'google.com'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
      # print("Internet connection is active.")
    except subprocess.CalledProcessError:
      # print("Internet connection lost. Please check your network settings.")
      printer.println("\n")
      printer.println(time_string + ": oh no, i lost internet!")
      printer.println('please connect to PoetryCameraSetup wifi network (pw: "password") on your phone to fix me!')
      printer.println('\n\n\n\n\n')
    sleep(interval) #makes thread idle during sleep period, freeing up CPU resources

def start_periodic_internet_check():
  # Start the background thread
  interval = 30  # Check every 30sec
  thread = threading.Thread(target=periodic_internet_check, args=(interval,))
  thread.daemon = True  # Daemonize thread
  thread.start()

# Main function
if __name__ == "__main__":
    initialize()
    # Keep script running to listen for button presses
    signal.pause()
