# From picamera2 examples: capture_jpeg.py 
#!/usr/bin/python3

import time, requests, signal, os

from gpiozero import LED, Button

#instantiate buttons
shutter_button = Button(16, hold_time = 2)
led = LED(20)

def handle_pressed():
  print("button pressed!")
  led.on()

def handle_held():
  print("button held!")

def handle_released():
  print("button released!")
  led.off()


#################################
# For RPi debugging:
# Handle Ctrl+C script termination gracefully
# (Otherwise, it shuts down the entire Pi -- bad)
#################################
def handle_keyboard_interrupt(sig, frame):
  print('Ctrl+C received, stopping script')
  led.off() #make sure LED is off before exiting
  #weird workaround I found from rpi forum to shut down script without crashing the pi
  os.kill(os.getpid(), signal.SIGUSR1)


################################
# LISTEN FOR BUTTON PRESS EVENTS
################################
shutter_button.when_pressed = handle_pressed
shutter_button.when_held = handle_held
shutter_button.when_released = handle_released

# Handle Ctrl+C gracefully
signal.signal(signal.SIGINT, handle_keyboard_interrupt)

# Test LED independently
led.on()
time.sleep(1)
led.off()

signal.pause()
