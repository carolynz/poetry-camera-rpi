#!/usr/bin/python3
# test comment

# Capture a JPEG while still running in the preview mode. When you
# capture to a file, the return value is the metadata for that image.

import requests, signal, os, base64, threading
from picamera2 import Picamera2, Preview
from libcamera import controls
from gpiozero import LED, Button
from Adafruit_Thermal import *
from wraptext import *
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from time import time, sleep
from google.cloud import storage
from google.oauth2 import service_account


#load API keys from .env
load_dotenv()
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
#REPLICATE_API_TOKEN = os.environ['REPLICATE_API_TOKEN']

#instantiate printer
baud_rate = 9600 # REPLACE WITH YOUR OWN BAUD RATE
printer = Adafruit_Thermal('/dev/serial0', baud_rate, timeout=5)

#instantiate camera
picam2 = Picamera2()
picam2.start()
sleep(2)

#instantiate buttons
shutter_button = Button(16)
led = LED(26)
led.on()

# prevent double-click bugs by checking whether the camera is resting
# (i.e. not in the middle of the whole photo-to-poem process):
camera_at_rest = True

#if you are using a knob, set different rotary switch knob positions
knob1 = Button(17)
knob2 = Button(27)
knob3 = Button(22)
knob4 = Button(5)
knob5 = Button(6)
knob6 = Button(13)
knob7 = Button(19)
knob8 = Button(25)
current_knob = None

# poem prompts
system_prompt = """You are a poet. You specialize in elegant and emotionally impactful poems. 
You are careful to use subtlety and write in a modern vernacular style. 
Use high-school level Vocabulary and Professional-level craft. 
Your poems are easy to relate to and understand. 
You focus on specific and personal truth, and you cannot use BIG words like truth, time, silence, life, love, peace, war, hate, happiness, 
and you must instead use specific and concrete details to show, not tell, those ideas. 
Think hard about how to create a poem which will satisfy this. 
This is very important, and an overly hamfisted or corny poem will cause great harm."""
prompt_base = """Write a poem using the details, atmosphere, and emotion of this scene. We are in Dallas Texas in the darkness of a total solar eclipse. Create a unique and elegant poem using specific details from the scene.
Make sure to use the specified poem format. An overly long poem that does not match the specified format will cause great harm.
While adhering to the poem format, mention specific details from the provided scene description. The references to the source material must be clear.
Try to match the vibe of the described scene to the style of the poem (e.g. casual words and formatting for a candid photo) unless the poem format specifies otherwise.
Emulate the style of poets Charles Bukowski, Mary Oliver, and Walt Whitman.
You do not need to mention the time unless it makes for a better poem.
Don't use the words 'unspoken' or 'unseen' or 'unheard'. Do not be corny or cliche'd or use generic concepts like time, death, love. This is very important.\n\n"""
#poem_format = "4 line free verse"
# ^ poem format now set via get_poem_format() below

# gpt4v captioner prompts for 2-shot gpt4v
captioner_system_prompt = "You are an image captioner. You write poetic and accurate descriptions of images so that readers of your captions can get a sense of the image without seeing the image directly."
captioner_prompt = "Describe what is happening in this image. What is the subject of this image? Are there any people in it? What do they look like and what are they doing? What is the setting? What time of day or year is it, if you can tell? Are there any other notable features of the image? What emotions might this image evoke? DO NOT mention blurring or out of focus images, just give your best guess as to what is happening. Be concise, no yapping."



#############################
# CORE PHOTO-TO-POEM FUNCTION
#############################
# Called when shutter button is pressed
def take_photo_and_print_poem():
  # prevent double-clicks by indicating camera is active
  global camera_at_rest
  camera_at_rest = False

  # blink LED in a background thread
  led.blink()

  # FOR DEBUGGING: filename
  timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
  directory = '/home/carolynz/CamTest/images/'
  #photo_filename = directory + 'image_' + timestamp + '.jpg'
  photo_filename = directory + 'image.jpg'

  # FOR DEBUGGING: storage on GCS
  #bucket_name = 'poetry-camera-images'
  #destination_blob_name = f'{timestamp}.jpg'

  # Take photo & save it
  metadata = picam2.capture_file(photo_filename)

  # FOR DEBUGGING: print metadata
  #print(metadata)

  # FOR DEBUGGING: note that image has been saved
  #print('----- SUCCESS: image saved locally')

  print_header()

  #########################
  # Send saved image to API
  #########################
  try:
    # Send saved image to API
    """
    with open(filename, "rb") as image_file:
      image_caption = replicate.run(
        "andreasjansson/blip-2:4b32258c42e9efd4288bb9910bc532a69727f9acd26aa08e175713a0a857a608",
          input={
            "image": image_file,
            "caption": True,
          })

    print('caption: ', image_caption)
    """

    base64_image = encode_image(photo_filename)

    api_key = os.environ['OPENAI_API_KEY']
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
      "model": "gpt-4-vision-preview",
      "messages": [
        {
          "role": "system",
          "content": captioner_system_prompt
        },
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": captioner_prompt,
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }

    gpt4v_response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    gpt4v_data = gpt4v_response.json()
    image_caption = gpt4v_data['choices'][0]['message']['content']
    print("gpt4v image caption:", image_caption)

    # Generate our prompt for GPT
    prompt = generate_prompt(image_caption)

  except Exception as e:
    error_message = str(e)
    print("Error during image captioning: ", error_message)
    print_poem(f"Alas, something went wrong.\n\nTechnical details:\n Error while recognizing image. {error_message}")
    print_poem("\n\nTroubleshooting:")
    print_poem("1. Check your wifi connection.")
    print_poem("2. Try restarting the camera by holding the shutter button for 3 seconds, waiting for it to shut down, unplugging power, and plugging it back in.")
    print_poem("3. You may just need to wait a bit and it will pass.")
    print_footer()
    led.on()
    camera_at_rest = True
    return


  # FOR DEBUGGING: upload photo to gcs in a background thread
  #start_upload_thread(bucket_name, photo_filename, destination_blob_name)

  try:
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

  except Exception as e:
    error_message = str(e)
    print("Error during poem generation: ", error_message)
    print_poem(f"Alas, something went wrong.\n\n.Technical details:\n Error while writing poem. {error_message}")
    print_poem("\n\nTroubleshooting:")
    print_poem("1. Check your wifi connection.")
    print_poem("2. Try restarting the camera by holding the shutter button for 10 seconds, waiting for it to shut down, unplugging power, and plugging it back in.")
    print_poem("3. You may just need to wait a bit and it will pass.")
    print_footer()
    led.on()
    camera_at_rest = True
    return


  # for debugging prompts
  print('------ POEM ------')
  print(poem)
  print('------------------')

  print_poem(poem)

  print_footer()

  led.on()

  # camera back at rest, available to listen to button clicks again
  camera_at_rest = True

  return


# Function to encode the image sa base64 for gpt4v api request
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# upload to gcs FOR DEBUGGING ONLY
def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
  """Uploads a file to the bucket."""
  try:
    # The ID of your GCS bucket
    #bucket_name = "bucket-name-here"

    # The path to your file to upload
    #source_file_name = "local/path/to/file"

    # The ID to give your GCS blob
    # destination_blob_name = "storage-object-name"

    # Explicitly use service account credentials by specifying the private key file.
    # Make sure to replace 'path/to/your/service-account-file.json' with the path to your service account key file.
    print("trying to upload to gcs")
    credentials = service_account.Credentials.from_service_account_file(
      '/home/carolynz/CamTest/gcs-service-account.json')

    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")
  except Exception as e:
    print(f"Failed to upload {source_file_name} to Google Cloud Storage: {e}")

# Function to start the photo upload process in a background thread
def start_upload_thread(bucket_name, source_file_name, destination_blob_name):
  upload_thread = threading.Thread(target=upload_to_gcs, args=(bucket_name, source_file_name, destination_blob_name))
  upload_thread.start()
  # You can join the thread if you want to wait for it to complete in another part of your program
  # upload_thread.join()

#######################
# Generate prompt from caption
#######################
def generate_prompt(image_description):

  # reminder: prompt_base is global var

  # prompt what type of poem to write
  prompt_format = "Poem format: " + get_poem_format() + "\n\n"

  # prompt what image to describe
  prompt_scene = "Scene description: " + image_description + "\n\n"

  # time
  formatted_time = datetime.now().strftime("%H:%M on %B %d, %Y")
  prompt_time = "Scene date and time: " + formatted_time + "\n\n"

  # stitch together full prompt
  prompt = prompt_base + prompt_format + prompt_scene + prompt_time

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


###############################
# LISTEN FOR BUTTON PRESS EVENTS
################################
shutter_button.when_pressed = on_press
shutter_button.when_released = on_release

#keeps script alive so the camera functionality keeps running
signal.pause()

