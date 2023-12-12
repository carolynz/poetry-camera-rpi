# Poetry Camera
A camera that prints poems of what it sees.

We started this project as newcomers to the world of hobby electronics. The following instructions are intended for complete beginners, as we were. We simplified some of the design to optimize for easily sourcing and assembling parts; as a result, it's less compact than our photographed versions. If you are comfortable with electronics and coding, we encourage you to experiment and remix even more.

These instructions are still in progress. Try it out and let us know what's confusing, or doesn't work.

## Hardware you'll need
### 1. Computer: [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) with headers

<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/a7da1fae-9521-431c-af47-5fe07e8dd43b" width="300" height="300">

Raspberry Pis are simplified computers. They are lightweight, cheap, have limited processing power, and are more fragile than typical consumer electronic devices. It's very sensitive to the specific power sources you use — too much power and you'll fry the part, too little power and the software won't run. You also have to manually shut down the software before unplugging the power, to protect the software from being corrupted.

We chose the Pi Zero 2 for its balance of processing power (Pi Zeros are too slow) and compact size (most other Pis on the market are larger). The wire diagrams in this tutorial will apply to all Raspberry Pis, but there may be differences in software and camera compatibility, especially with older devices. We've tested this with a [Pi 3b+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/) and it works fine, but a [Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) probably requires too much power to make it a viable portable solution.

Raspberry Pi Zero 2 is often sold without headers (those 2x20 black metal connectors). The headers let you easily connect the Pi to the printer and buttons with plug-in jumper wires. If you buy the Pi without headers, you'll need to separately buy a [2x20 header](https://www.adafruit.com/product/2822) and solder them on yourself. It's not hard, but leaves more room for error. (Of course, if you know what you're doing, you can directly solder the appropriate wires to the appropriate pins without headers.)

<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/43c619a8-a416-4c18-8013-4ff36d1d1ba6" width="300"> <img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/bdfb1bda-0691-41ac-a7e5-583b66d6cc71" width="300"> 

Raspberry Pis are also recovering from a supply shortage. Check [rpilocator.com](https://rpilocator.com/) for live stock notifications on standalone parts (does not list accessory kits).

### 2. Accessories to connect the Raspberry Pi to stuff.
  <img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/d482c0de-cca5-4ce3-ae4e-0ebc0bef1693" width="300">
  
  - [Vilros sells a kit that includes all of these things](https://vilros.com/products/vilros-raspberry-pi-zero-2-w-basic-starter-kit)
    - [5V MicroUSB power supply](https://www.amazon.com/CanaKit-Raspberry-Supply-Adapter-Listed/dp/B00MARDJZ4) 
    - [Case](https://www.adafruit.com/product/2258)
    - [32GB MicroSD card to load the OS](https://www.canakit.com/raspberry-pi-sd-card-noobs.html)
    - Heatsink to prevent overheating (very important!)
    - MicroUSB to USB adapter, for the Logitech keyboard's wireless sensor.
    - MiniHDMI to HDMI adapter for monitor
  - **Keyboard & mouse**: we recommend [this Logitech wireless combo keyboard-trackpad](https://www.amazon.com/Logitech-Wireless-Keyboard-Touchpad-PC-connected-dp-B014EUQOGK/dp/B014EUQOGK) so it only takes up 1 port of your Pi.
  - **External monitor** for viewing and programming the Pi's software. It's not strictly required, but is more beginner-friendly than SSHing into your Pi. We will assume that you are using an external monitor for all these instructions.
  
    
### 3. Camera: [Raspberry Pi Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/)
  <img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/4fad7574-2933-448f-a556-d0d7990596ec" width="300">

  - **Camera accessories:**
    - [Camera case with tripod](https://www.amazon.com/Arducam-Raspberry-Bundle-Autofocus-Lightweight/dp/B09TKYXZFG) — The camera is delicate and can be easily fried via static. We fried 3 cameras in the process of making this. A protective case helps prevent this.
    - [Camera cable specifically for Pi Zero/Zero 2s](https://www.adafruit.com/product/3157) — If you are using a larger Pi, the camera cable that comes with the cable is fine


### 4. Receipt printer: [Nano Thermal Printer](https://www.adafruit.com/product/2752)

<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/c05278eb-2f72-40ec-a0ed-f0f09530b4c6" width="300">


This product has unfortunately been discontinued by Adafruit, but similar versions exist on Amazon. We are working on confirming that the Amazon part still works with the same printer drivers.
  - **Receipt printer accessories:**
    - [5V power supply](https://www.adafruit.com/product/276)
    - [Female DC Power Adapter](https://www.adafruit.com/product/368)
    - Wire cutters, wire stripper, tiny screwdriver for wiring together
    - Receipt paper: [EcoChit thermal receipt paper, 2.25"](https://www.amazon.com/EcoChit-Thermal-Paper-Rolls-Plants/dp/B076MMDL8Y) (phenol-free, recyclable)
        - Don't use regular receipt paper! [It's often filled with BPA](https://environmentaldefence.ca/2019/02/07/toxic-receipt-bpa-thermal-paper/), which is especially toxic for kids and reproductive health.


### 5. Batteries:
  - Battery for the receipt printer
  - Battery for the Raspberry pi

### 6. Buttons
<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/e8b280b5-f4b9-4495-94bb-c2e0cdd96cef" width="150">
<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/f1c8251a-77d4-42d7-ad59-12562386182a" width="150">

  - 2 [push buttons in different colors](https://www.adafruit.com/search?q=16mm%20Panel%20Mount%20Momentary%20Pushbutton)
  - 2 [quick-connect wires](https://www.adafruit.com/product/1152) to easily connect these buttons to the Pi

### 7. Miscellaneous equipment
  - Wire cutter & stripper
  - Jumper cables

## Software
- OpenAI account & API key. Each poem costs a couple cents to generate.
- 

Currently, the `main.py` script running on the Pi:
- Automatically takes a photo when you run it
- Sends photo to the server, a [Flask app on Replit](https://poetry-camera-prototype.carozee.repl.co/)
- Receives an AI-generated poem from server
- Prints poem out on thermal receipt printer

The `Adafruit_Thermal.py` script is [Adafruit's thermal printer Python library](https://github.com/adafruit/Python-Thermal-Printer).

## How to set up
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

5. Update the system and install requirements. I'm not sure you even need all of these; I can go over these again later and trim out the unnecessary ones.
```shell
$ sudo apt-get update
$ sudo apt-get install git cups build-essential libcups2-dev libcupsimage2-dev python3-serial python-pil python-unidecode
```

6. Install some software required to make the Adafruit Thermal Printer work.
```shell
$ cd
$ git clone https://github.com/adafruit/zj-58
$ cd zj-58
$ make
$ sudo ./install
```

7. Clone this repo, which contains our Poetry Camera software:
```shell
$ cd
$ git clone https://github.com/carolynz/poetry-camera-rpi.git
```

8. Set up your thermal printer, connecting it to power and your Pi. [See diagram and instructions in this tutorial.](https://learn.adafruit.com/networked-thermal-printer-using-cups-and-raspberry-pi/connect-and-configure-printer)
   Test that it works. Pay attention to your printer's baud rate (e.g. `19200`). We will use this later on.

9. Open our `poetry-camera-rpi` directory:
```shell
$ cd poetry-camera-rpi
```
10. *If* your printer's baud rate is different from `19200`, open `main.py` and replace that number with your own printer's baud rate:
```shell
# main.py:

# instantiate printer
printer = Adafruit_Thermal('/dev/serial0', 19200, timeout=5)
```

11. Run the poetry camera script.
```shell
$ python main.py
```

## TODO instructions for adding buttons

## TODO instructions for auto-start/shutoff
- Set up a `cron` job to run your python script at startup. First, open your `crontab` file to your default editor:
```shell
$ crontab -e
```

- Then add the following line to your `crontab`, to run the script when you boot up the computer.
```shell
# Run poetry camera script at start
@reboot python /home/pi/poetry-camera-rpi/main.py >> /home/pi/poetry-camera-rpi/errors.txt 2>&1
```
The `>> {...}errors.txt 2>&1` writes any error messages to `errors.txt` for debugging. A common failure mode is files cannot be found. Make sure that all your filepaths are absolute filepaths and have the right usernames and directory names.

- Reboot the system for this to take effect
```shell
sudo reboot
```

- Try clicking your shutter and power buttons to make sure they're working upon reboot. If they're not working, check your `errors.txt` file.

Lots of errors in these instructions, I'm sure.
