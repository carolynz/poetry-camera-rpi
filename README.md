# AI Poetry Camera for Raspberry Pi

Still in development...

## Hardware
Currently using:
- [Raspberry Pi 3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/)
  - [5V MicroUSB power supply](https://www.amazon.com/CanaKit-Raspberry-Supply-Adapter-Listed/dp/B00MARDJZ4) 
  - [Adafruit case](https://www.adafruit.com/product/2258)
  - [32GB MicroSD card to load the OS](https://www.canakit.com/raspberry-pi-sd-card-noobs.html)
  - Keyboard & monitor for programming
- [RPi Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/)
  - [Arducam case with tripod](https://www.amazon.com/Arducam-Raspberry-Bundle-Autofocus-Lightweight/dp/B09TKYXZFG)
- [Adafruit Mini Thermal Printer](https://www.adafruit.com/product/600)
  - [5V power supply](https://www.adafruit.com/product/276)
  - [Female DC Power Adapter](https://www.adafruit.com/product/368)
  - Wire cutters, wire stripper, tiny screwdriver for wiring together
- [EcoChit thermal receipt paper, 2.25"](https://www.amazon.com/EcoChit-Thermal-Paper-Rolls-Plants/dp/B076MMDL8Y) (phenol-free, recyclable)
  - Don't use regular thermal paper! [It's toxic](https://environmentaldefence.ca/2019/02/07/toxic-receipt-bpa-thermal-paper/)

Future hardware updates for usability and portability:
- Switch to [RPi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) so it draws less power
- Add cellular connection to RPi so you can take it anywhere
- Switch to [Nano Thermal Printer](https://www.adafruit.com/product/2752) so it's more portable
- Add shutter and power buttons
- Add LED to indicate camera is on / loading
- Add knob to adjust poem settings
- Add battery pack to power both RPi and Thermal Printer

## Software
Currently, the `main.py` script running on the Pi:
- Automatically takes a photo when you run it
- Sends photo to the server, a [Flask app on Replit](https://poetry-camera-prototype.carozee.repl.co/)
- Receives an AI-generated poem from server
- Prints poem out on thermal receipt printer

The `Adafruit_Thermal.py` script is [Adafruit's thermal printer Python library](https://github.com/adafruit/Python-Thermal-Printer).

## How to set up
At some point I will upload the .img file that you can copy to an SD card and just insert into your Raspberry Pi and go on your merry way.

Until then, here's my setup.

This was cobbled together from the following tutorials:
- [Instant Camera using Raspberry Pi and Thermal Printer](https://learn.adafruit.com/instant-camera-using-raspberry-pi-and-thermal-printer)
- [Networked Thermal Printer using Raspberry Pi and CUPS](https://learn.adafruit.com/networked-thermal-printer-using-cups-and-raspberry-pi)


1. Set up your Raspberry Pi with Camera connection.

2. Open up the Terminal on your Pi.

3. Set up Raspberry Pi hardware to take Camera & Serial inputs:
```shell
sudo raspi-config
```
4. You'll want to adjust the following settings:
    - Glamor: ON (for Camera setup on newer versions of Raspbian OS)
    - Serial Port ON (lets you access receipt printer inputs)
    - Serial Console OFF (idk what this does)

    Restart the system as needed.

5. Update the system and install requirements. I think I did something different for `wiringpi` as it is outdated; will update once I remember what I did. You can also skip `wiringpi` for now, it will only be used with the buttons (I think).
```shell
sudo apt-get update
sudo apt-get install git cups wiringpi build-essential libcups2-dev libcupsimage2-dev python3-serial python-pil python-unidecode
```

6. Install some software required to make the Adafruit Thermal Printer work.
```shell
cd
git clone https://github.com/adafruit/zj-58
cd zj-58
make
sudo ./install
```

7. Clone this repo, which contains our Poetry Camera software:
```shell
cd
git clone https://github.com/carolynz/poetry-camera-rpi.git
```

8. Set up your thermal printer, connecting it to power and your Pi. [See diagram and instructions in this tutorial.](https://learn.adafruit.com/networked-thermal-printer-using-cups-and-raspberry-pi/connect-and-configure-printer)
   Test that it works. Pay attention to your printer's baud rate (e.g. `19200`). We will use this later on.

9. Open the `poetry-camera-rpi` directory:
```shell
cd poetry-camera-rpi
```
10. *If* your printer's baud rate is different from `19200`, open `main.py` and replace that number with your own printer's baud rate:
```shell
# main.py:

# instantiate printer
printer = Adafruit_Thermal('/dev/serial0', 19200, timeout=5)
```

11. Run the poetry camera script.
```shell
python main.py
```

The camera will immediately take a photo and the receipt printer should print out a poem.

Lots of errors in these instructions, I'm sure.
