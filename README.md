# AI Poetry Camera for Raspberry Pi

Still in development...

## Hardware
Currently using:
- [Raspberry Pi 3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/) + [5V MicroUSB power supply](https://www.amazon.com/CanaKit-Raspberry-Supply-Adapter-Listed/dp/B00MARDJZ4)
- [RPi Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/)
- [Adafruit Mini Thermal Printer](https://www.adafruit.com/product/600)
  - Accessories: 5V power supply, Female DC Power Adapter, wire cutters, wire stripper, tiny screwdriver
- [EcoChit thermal receipt paper, 2.25"](https://www.amazon.com/EcoChit-Thermal-Paper-Rolls-Plants/dp/B076MMDL8Y) (phenol-free, recyclable)
  - Don't use regular thermal paper! [It's toxic](https://environmentaldefence.ca/2019/02/07/toxic-receipt-bpa-thermal-paper/)

Future hardware updates for usability and portability:
- Switch to [RPi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/) so it draws less power
- Add cellular connection to RPi so you can take it anywhere
- Switch to [Nano Thermal Printer](https://www.adafruit.com/product/2752) so it's more portable
- Add shutter and power buttons
- Add knob to adjust poem settings
- Add battery pack to power both RPi and Thermal Printer

## Software
Python script running on the Pi (currently) automatically takes a photo when you run it, then sends it to a server ([Flask app on Replit](https://poetry-camera-prototype.carozee.repl.co/)). Receives an AI-generated poem in response.


## How to set up
At some point I will upload the .img file that you can copy to an SD card and just insert into your Raspberry Pi and go on your merry way.

Until then, here's my setup.
This was cobbled together from the following tutorials:
- [Instant Camera using Raspberry Pi and Thermal Printer](https://learn.adafruit.com/instant-camera-using-raspberry-pi-and-thermal-printer)
- [Networked Thermal Printer using Raspberry Pi and CUPS](https://learn.adafruit.com/networked-thermal-printer-using-cups-and-raspberry-pi)


Set up your Raspberry Pi with Camera connection.

Open up the Terminal on your RPi.

Set up Raspberry Pi hardware to take Camera & Serial inputs:
```shell
sudo raspi-config
```
You'll want to adjust the following settings:
- Glamor: ON (for newer versions of Raspbian OS)
- Serial Port ON (lets you access receipt printer inputs)
- Serial Console OFF (idk what this does)

Update the system and install prerequisites. I think I did something different for `wiringpi` as it is outdated; will update once I remember what I did.
```shell
sudo apt-get update
sudo apt-get install git cups wiringpi build-essential libcups2-dev libcupsimage2-dev python3-serial python-pil python-unidecode
```

Install some software required to make the Adafruit Thermal Printer work.
```shell
cd
git clone https://github.com/adafruit/zj-58
cd zj-58
make
sudo ./install
```

Clone this repo, which contains our Poetry Camera software:
```shell
cd
git clone https://github.com/carolynz/poetry-camera-rpi.git
```


Connect your thermal printer to power and Raspberry Pi GPIO pins (likely 14 & 15). [See diagram and instructions in this tutorial.](https://learn.adafruit.com/networked-thermal-printer-using-cups-and-raspberry-pi/connect-and-configure-printer)


Open the `poetry-camera-rpi` directory:
```shell
cd poetry-camera-rpi
```

Run the poetry camera script.
```shell
python camtest.py
```

The camera will immediately take a photo and the receipt printer should print out a poem.

Lots of errors in these instructions, I'm sure.
