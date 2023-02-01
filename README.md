# AI Poetry Camera for Raspberry Pi

Still in development...

## Hardware
Currently using:
- Raspberry Pi 3B+ + 5V power supply
- RPi Camera Module 3
- Adafruit Mini Thermal Printer + 5V power supply

Future hardware updates for usability and portability:
- Switch to RPi Zero W so it draws less power
- Add cellular connection to RPi so you can take it anywhere
- Switch to Nano Thermal Printer so it's more portable
- Add shutter and power buttons
- Add knob to adjust poem settings
- Add battery pack to power both RPi and Thermal Printer

## Software
Python script running on the Pi (currently) automatically takes a photo when you run it, then sends it to a server ([Flask app on Replit](https://poetry-camera-prototype.carozee.repl.co/)). Receives an AI-generated poem in response.

Might add RPi img file for easy backup later, if that's not a terrible security idea.
