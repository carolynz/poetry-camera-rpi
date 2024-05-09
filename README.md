# Poetry Camera
A camera that prints poems of what it sees.

We started this project as newcomers to the world of hobby electronics. The following instructions are intended for complete beginners, as we were. We simplified some of the design to optimize for easily sourcing and assembling parts; as a result, it's less compact than our photographed versions. If you are comfortable with electronics and coding, we encourage you to experiment and remix even more. 

⚠️ These instructions are still in progress. ⚠️  Try it out and let us know what's confusing, or doesn't work.

## Hardware you'll need
### 1. Computer: [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) with headers

<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/a7da1fae-9521-431c-af47-5fe07e8dd43b" width="300" height="300">

Raspberry Pis are simplified computers. They are lightweight, cheap, have limited processing power, and are more fragile than typical consumer electronic devices. It's very sensitive to the specific power sources you use — too much power and you'll fry the part, too little power and the software won't run. You also have to manually shut down the software before unplugging the power, to protect the software from being corrupted.

We chose the Pi Zero 2 for its balance of processing power (Pi Zeros are too slow) and compact size (most other Pis on the market are larger). The wire diagrams in this tutorial will apply to all Raspberry Pis, but there may be differences in software and camera compatibility, especially with older devices. We've tested this with a [Pi 3b+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/) and it works fine, but a [Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) probably requires too much power to make it a viable portable solution.

Raspberry Pi Zero 2 is often sold without headers (those 2x20 black metal connectors). The headers let you easily connect the Pi to the printer and buttons with plug-in jumper wires. If you buy the Pi without headers, you'll need to separately buy a [2x20 header](https://www.adafruit.com/product/2822) and solder them on yourself. If you don't want to solder, you can use [hammer-on headers](https://www.adafruit.com/product/3662) and [this installation rig](https://www.amazon.com/vilros-raspberry-headers-easy-installation-soldering/dp/b0cgryyy63).

<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/43c619a8-a416-4c18-8013-4ff36d1d1ba6" width="300">
<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/ebbbc23e-1e92-4d5a-84de-f761f32720f3" width="300">


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
  <img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/4fad7574-2933-448f-a556-d0d7990596ec" width="200">

  Mostly straightforward, but be careful of damaging the hardware. The Raspberry Pi camera is delicate and can be easily fried via static. We broke 3 cameras in the process of making this project. Just make sure to always store it in a static-shielding bag when you're not using it.

  If you are connecting the camera to a Pi Zero 2, note that the Zero 2's camera connection collar is also very delicate. We broke a Pi Zero 2 camera collar in the process of making this as well and had to just get a new Pi 🥲

  We have not tested these instructions with older models of Raspberry Pi cameras.

  - **Camera accessories:**
    - [Camera case with tripod](https://www.amazon.com/Arducam-Raspberry-Bundle-Autofocus-Lightweight/dp/B09TKYXZFG) — Helps proteect the delicate camera hardware during development.
    - [Camera cable sized specifically for Pi Zero & Zero 2](https://www.adafruit.com/product/3157) — If you are using a larger Pi, you only need default cable that comes with the camera. If you got your Zero 2 camera cable in a kit, it is likely the short ~2 inch cable. Make sure to get a long enough cable that gives you more flexibility in where you place your camera.
    - Optional: Tweezer for opening/closing the delicate camera collar on Pi Zero 2


### 4. Receipt printer: [Mini Thermal Printer w/ TTL Serial connection](https://www.adafruit.com/product/2752)

<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/209bbe14-b494-4826-8851-61561f4f34ac" width="300">

We used the Adafruit thermal printer line for this project, but they have subsequently been discontinued. Similar printers exist on Amazon and Aliexpress; the ones we've bought work with the [same printer drivers](https://github.com/adafruit/zj-58) (which are also no longer maintained by Adafruit, but still seem to work). 

The [Nano Thermal Printer](https://www.adafruit.com/product/2752) or [Tiny Thermal Printer]([https://www.adafruit.com/product/2753](https://www.adafruit.com/product/2751)) are more compact, but have [slightly different wiring](https://learn.adafruit.com/mini-thermal-receipt-printer/making-connections#for-product-number-2751-tiny-3133460).

The important thing is that the thermal printer has a TTL serial connection so you can easily connect it to the Pi. **Search "TTL embedded thermal printer"** on Amazon or Aliexpress to find your parts. 

  - **Similar receipt printers on Amazon:**
    - [Dupe for Adafruit Mini printer](https://www.amazon.com/HUIOP-Embedded-Printing-Commands-Apparatus/dp/B0CS3NRPV3)
    - [Dupe for Adafruit Tiny printer](https://www.amazon.com/XIXIAN-Thermal-Embedded-Interface-Printing/dp/B0C5XGJWC4)

  - **Receipt printer accessories:**
    - [5V power supply](https://www.adafruit.com/product/276)
    - [Female DC Power Adapter](https://www.adafruit.com/product/368) to connect receipt to power supply
    - Wire cutters, wire stripper, tiny screwdriver for wiring together
    - Receipt paper: [EcoChit thermal receipt paper, 2.25"](https://www.amazon.com/EcoChit-Thermal-Paper-Rolls-Plants/dp/B076MMDL8Y) (phenol-free, recyclable)
        - Don't use regular receipt paper! [It's often filled with BPA](https://environmentaldefence.ca/2019/02/07/toxic-receipt-bpa-thermal-paper/), which is especially toxic for kids and reproductive health.


### 5. Batteries:
<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/b3507b14-3b12-4fbc-99fa-ffc5c589bf93" width="300">
<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/5196a5ee-d70e-4b69-91fd-e165cc368f7e" width="300">
<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/f1340f50-e492-4696-bd9f-2196155552ec" width="300">

If you want your camera to be portable, you'll need some batteries! The Pi requires a steady 5V of power @ 1.2A, while the printer needs 5-9V and draws ~2A while printing.

**Recommended power supply: 6xAA batteries**

It's not the lightest solution, but it's a beginner-friendly starting point.
  - [6 x AA battery holder with DC plug](https://www.adafruit.com/product/248)
  - 6 x AA batteries — rechargeable NiMH batteries (e.g., Eneloop) provide 7.2V, non-rechargeable alkaline batteries (e.g., Duracell) provide 9V. Either works. Of course, don't mix batteries!
  - [In-line power switch for DC barrel jack](https://www.adafruit.com/product/1125) to control flow of power to circuit
  - [DC wire terminal block](https://www.adafruit.com/product/368) to connect batteries to circuit
  - [Step-down (buck) converter — 5V @ 3A output](https://www.adafruit.com/product/1385) steps down the battery voltage to 5V for the Raspberry Pi
  - [MicroUSB shell](https://www.adafruit.com/product/1826) to power the Pi, or cut open a MicroUSB cable
  - Soldering iron

**Other solutions that could work:**
  - Put the above circuit on a PCB so you just need to plug in the connectors instead of soldering — we did this for our project! Will upload gerber files in the future.
  - 7.2V lithium batteries, e.g. 2x 18650s
  - [7.4V NiMH batteries for RC cars](https://www.amazon.com/s?k=7.2v+rc+battery&i=toys-and-games&crid=1FRMK7CHC0RRQ&sprefix=7.2v+rc+battery,toys-and-games,127)
  - If you don't need it to be *super* portable, get a [portable power station](https://www.amazon.com/gp/product/B0CH2Z2JM9) to plug in the Pi and printer
  - If you don't want to solder, you could power the Pi and printer through two separate batteries. However, we've run into overheating issues with the commonly-recommended [PiSugar 3 battery](https://www.tindie.com/products/pisugar/pisugar-3-battery-for-raspberry-pi-zero/).
    
**Power supplies that DON'T work:**
  - Typical 9V alkaline batteries do *not* work as they do not provide enough current
  - Standard phone banks don't provide continuous power to the Raspberry Pi, causing it to shut down after a few minutes
  - Just plugging both devices in to a single 5V power bank — it can't handle the current draw while printing. Either the Pi shuts down during printing, or the printer doesn't have enough power to print.


### 6. Shutter button & LED
<img src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/90120571-7d96-4e9a-b14c-e1e6228f2403" width="300">

Any LED + momentary pushbutton will work for the shutter button. We use the LED as a status indicator for things like ready, loading, etc.

  - [Illuminated pushbutton](https://www.adafruit.com/search?q=16mm%20Panel%20Mount%20Momentary%20Pushbutton). This button doesn't have a satisfying click, but the built-in LED also includes resistors, which is convenient.
  - 2 [quick-connect wires](https://www.adafruit.com/product/1152) to easily connect these buttons to the Pi

### 7. Miscellaneous equipment
  - Wire cutter & stripper
  - Soldering iron & accessories
  - Jumper cables

## Software
This code currently uses OpenAI's models to turn the image into a poem. It also uses thermal printer drivers from [Adafruit's thermal printer Python library](https://github.com/adafruit/Python-Thermal-Printer).

You'll need to get your own [OpenAI account & API key](https://openai.com/index/openai-api). Each request costs a couple of cents.

Currently, the `main.py` script running on the Pi:
- Takes a photo when you click the shutter button
- Sends the photo to GPT-4 Vision to caption the photo
- When we receive the caption, we ask GPT-4 to turn the caption into a poem
- When we receive the poem, print the poem out on thermal receipt printer


# Putting it all together
This was adapted from the following tutorials:
- [Instant Camera using Raspberry Pi and Thermal Printer](https://learn.adafruit.com/instant-camera-using-raspberry-pi-and-thermal-printer)
- [Networked Thermal Printer using Raspberry Pi and CUPS](https://learn.adafruit.com/networked-thermal-printer-using-cups-and-raspberry-pi)

### Part 1. Check that your Raspberry Pi & camera works
1. Connect your Raspberry Pi to your Camera module.

2. Insert your SD card with a fresh install of any Raspberry Pi OS onto the Pi.

3. Connect your Pi to a monitor via mini HDMI.

5. Plug in power. You should see a green light on the Pi, and a start-up screen on the monitor.
  
7. Once the Pi is on, open up the Terminal on your Pi to start making changes.

8. Set up Raspberry Pi hardware to take Camera & Serial inputs:
```shell
sudo raspi-config
```

9. You'll want to adjust the following settings:
    - Glamor: ON (for Camera setup on newer versions of Raspbian OS)
    - Serial Port ON (lets you access receipt printer inputs)
    - Serial Console OFF (idk what this does)

    Restart the system as needed.

[Tutorial TODO: include a basic camera test script & show desired behavior]

### Part 2. Check that your printer works
1. Update the system and install requirements. I'm not sure you even need all of these; I can go over these again later and trim out the unnecessary ones.
```shell
$ sudo apt-get update
$ sudo apt-get install git cups build-essential libcups2-dev libcupsimage2-dev python3-serial python-pil python-unidecode
```

2. Install some software required to make the Adafruit Thermal Printer work.
```shell
$ cd
$ git clone https://github.com/adafruit/zj-58
$ cd zj-58
$ make
$ sudo ./install
```

3. Clone this repo, which contains our Poetry Camera software:
```shell
$ cd
$ git clone https://github.com/carolynz/poetry-camera-rpi.git
```

4. Set up your thermal printer, connecting it to power and your Pi. [See diagram and instructions in this tutorial.](https://learn.adafruit.com/networked-thermal-printer-using-cups-and-raspberry-pi/connect-and-configure-printer)
   Test that it works. Pay attention to your printer's baud rate (e.g. `19200`). We will use this later on.

5. Open our `poetry-camera-rpi` directory:
```shell
$ cd poetry-camera-rpi
```

6. *If* your printer's baud rate is different from `19200`, open `main.py` and replace that number with your own printer's baud rate:
```shell
# main.py:

# instantiate printer
printer = Adafruit_Thermal('/dev/serial0', 19200, timeout=5)
```

[TODO] need a setup script to test that the printer works

### Part 3. Set up the AI
1. Set up an OpenAI account and create an API key.

2. Navigate to your directory with the Poetry Camera code and create a `.env` file, which will store sensitive details like your OpenAI API key:
```nano .env```

3. In the .env, add your API key:
```OPENAI_API_KEY=pasteyourAPIkeyhere```

[TODO] add an openai test script


### Part 4. Get it working end-to-end
[TODO] include wiring diagram

1. Connect buttons

2. Run the poetry camera script.
```shell
$ python main.py
```

3. Check that the shutter button lights up, indicating that the camera is ready to take a picture

4. Click the shutter button and wait for the poem to print out.

[TODO] troubleshooting instructions different common error messages

## Part 5. Automatically run the Poetry Camera code when the camera turns on

1. Set up a `cron` job to run your python script at startup. First, open your `crontab` file to your default editor:
```shell
$ crontab -e
```

2 Then add the following line to your `crontab`, to run the script when you boot up the computer.
```shell
# Run poetry camera script at start
@reboot python /home/pi/poetry-camera-rpi/main.py >> /home/pi/poetry-camera-rpi/errors.txt 2>&1
```
The `>> {...}errors.txt 2>&1` writes any error messages to `errors.txt` for debugging. A common failure mode is files cannot be found. Make sure that all your filepaths are absolute filepaths and have the right usernames and directory names.

- Reboot the system for this to take effect
```shell
sudo reboot
```
Now reboot your camera and wait for the LED light to turn on!


## Part 6. Make the power circuit
[TODO] clean this up & explain steps :)

<img width="1217" alt="image" src="https://github.com/carolynz/poetry-camera-rpi/assets/1395087/dca36686-fcfa-43ba-86f6-155bd1aab0e5">

## Part 7: Change wifi networks on-the-go
The camera needs wifi to work. You could always hardcode in your mobile hotspot by editing `wpa_supplicant.conf`. If you want to connect to new wifi networks on the fly, just follow this simple tutorial.

To do the above tutorial, you'll need a second wifi adapter, plugged into your microUSB port. Definitely get a plug-and-play wifi adapter that works for Linux/Raspberry Pi.

Wifi adapter options that seem to work:
- [From Pi Hut (UK)](https://thepihut.com/products/usb-wifi-adapter-for-the-raspberry-pi)
- [LOTEKOO, from Amazon](https://www.amazon.com/dp/B06Y2HKT75)
- [Canakit, from Amazon](https://www.amazon.com/dp/B00GFAN498)

MicroUSB to USB adapters:
- [From Amazon](https://www.amazon.com/Ksmile%C2%AE-Female-Adapter-SamSung-tablets/dp/B01C6032G0)
- [Super slim, from Adafruit](https://www.adafruit.com/product/2910)
