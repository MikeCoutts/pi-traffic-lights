# Copyright The Kavinjka Software Company 2021-2022
#
# Author MikeC@kavinjka.com

import RPi.GPIO as GPIO
import time # for sleep functions
import sqlite3 # for storing Button Pushes

from signal import signal, SIGINT # for Cntrl-C
from sys import exit, argv
from datetime import datetime
import requests # for REST external access

# process argv according to https://realpython.com/python-command-line-arguments/
print(argv[0]) # file name

# assume we are in the USA Locale - Cross Walk not Pedistrian Crossing
locale_usa = True

# assume we want the beep On (as it's really loud when you are developing we can turn it off with the --no_beep argument)
beep = True

# use a database_file variable in case we ever want to change it
database_file = 'pi-traffic-lights.db'

# define a transition time variable so we can run the code very quickly
transition_time = 1 # 1 second

# check for any Command Line Arguments (this is a little better)
for i in range(1, len(argv)): # ignore argv[0] as it is the file name
    print(argv[i])
    if (argv[i] == "--scotland"):
        locale_usa = False
    if (argv[i] == "--no_beep"):
        beep = False
    if (argv[i] == "--zero_transition"):
        transition_time = 0
    if (argv[i] == '--database'): # technically has to be last pair of argv elements
        database_file = argv[i+1]

# define the GPIO port for the Button
BUTTON = 16

# define the GPIO ports for the Traffic Lights
GREEN = 26
AMBER = 19
RED = 13

# define the GPIO ports for the Cross Walk/Pedistrian Signal 
COMBI_RED = 22
COMBI_GREEN = 27
COMBI_BLUE = 17

# define the GPIO port for the Buzzer Activation
BUZZER = 23

#initialise previous_input variable to 0 (assume button not pressed on startup) and Pedistrian Crossing as false
previous_input = 0
crossing = False

# Define an exit handler for the program (called on Cntrl-C)
def ctrl_c_handler(signal_received, frame):
    # Handle any GPIO cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    GPIO.cleanup()
    connection.close() # to close out Sqlite3
    exit(0)

def initialize_GPIO():
    # Initialize the GPIO Infrastructure to BCM (Broadcom SOC channel)
    GPIO.setmode(GPIO.BCM)

    # Setup all the Input and Output GPIO Pins
    GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 16 (button) to be an input pin and set initial value to be pulled low (off)
    GPIO.setup(RED, GPIO.OUT)
    GPIO.setup(GREEN, GPIO.OUT)
    GPIO.setup(AMBER, GPIO.OUT)
    GPIO.setup(COMBI_RED, GPIO.OUT)
    GPIO.setup(COMBI_GREEN, GPIO.OUT)
    GPIO.setup(COMBI_BLUE, GPIO.OUT)
    GPIO.setup(BUZZER, GPIO.OUT)

# turn on the Green Light and red cross walk light, Assume the Cross-Walk is Cars allowed through.
def initialize_cross_walk():
    GPIO.output(GREEN, GPIO.HIGH)
    GPIO.output(AMBER, GPIO.LOW)
    GPIO.output(RED, GPIO.LOW)
    GPIO.output(COMBI_RED, GPIO.HIGH)
    GPIO.output(COMBI_BLUE, GPIO.LOW)
    GPIO.output(COMBI_GREEN, GPIO.LOW)
    GPIO.output(BUZZER, GPIO.LOW)

# Get the Unique MAC address of this Raspberry Pi for a given Network Interface
def get_MAC(interface='eth0'):
  # Return the MAC address of the specified interface
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]

# Setup the Sqlite3 connection and curosr to pi-traffic-lights.db
connection = sqlite3.connect(database_file)
cursor = connection.cursor()

# Use a function to control the Car to Pedestrian Transition
def car_to_pedestrian(transition_time):
    # Add a short sleep so there is time from the button release to the start of the transition
    time.sleep(transition_time)

    # Transition from Green to Amber
    GPIO.output(GREEN, GPIO.LOW)
    GPIO.output(AMBER, GPIO.HIGH)

    # sleep between Amber/Red
    time.sleep(transition_time)

    # Transition from Amber to Red
    GPIO.output(AMBER, GPIO.LOW)
    GPIO.output(RED, GPIO.HIGH)

    # Add a short sleep to let the Red to Car drivers be in place
    time.sleep(transition_time)

# Use a function to control the Pedestrian to Car transition
def pedestrian_to_car(transition_time, locale_usa):
    GPIO.output(COMBI_RED, GPIO.HIGH) # Red Do Not Walk signal to Pedestrians
    # Add a short sleep  after Pedistian signal goes Red before moving on
    time.sleep(transition_time)

    # As the USA and Scotland return to car sequence is different we need to decide
    if locale_usa:
        time.sleep(transition_time)
        GPIO.output(RED, GPIO.LOW) # Red goes straight to Green in the USA
    else:
        # Add a small sleep before tranitioning to Red/Amber
        time.sleep(transition_time)

        GPIO.output(AMBER, GPIO.HIGH) # and hold for transition_time

        # Scotland Sequence is a little different with Red/Amber on Prior to flip to Green
        GPIO.output(AMBER, GPIO.HIGH)

        time.sleep(transition_time) # for Scotland Red/Amber ("prepare to proceed")

        GPIO.output(RED, GPIO.LOW)
        GPIO.output(AMBER, GPIO.LOW)

    # return the crossing to Cars ("Proceed if safe to do so")
    GPIO.output(GREEN, GPIO.HIGH)

def beep_function(duration):
    if (beep == True):
        GPIO.output(BUZZER, GPIO.HIGH)

    # sleep whether or not the buzzer is on or not
    time.sleep(duration)
    GPIO.output(BUZZER, GPIO.LOW)

# use a function to Start and maintain the Walk Signal (White in the USA, Green in Scotland with an intermitent "beep')
def walk_signal(transition_time, locale_usa):
    if (locale_usa): # USA Walk signal is solid white (R+B+G)
        GPIO.output(COMBI_RED, GPIO.HIGH)
        GPIO.output(COMBI_BLUE, GPIO.HIGH)
        GPIO.output(COMBI_GREEN, GPIO.HIGH)
    else: # Scotland Pedestrian Crossing signal is Green
        GPIO.output(COMBI_GREEN, GPIO.HIGH)

    for i in range(1, transition_time):
        beep_function(0.1)
        time.sleep(0.5)

def end_walk_signal(transition_time, locale_usa):
    # Shut of the walk signal
    GPIO.output(COMBI_RED, GPIO.LOW)
    GPIO.output(COMBI_BLUE, GPIO.LOW)
    GPIO.output(COMBI_GREEN, GPIO.LOW)

    if  (locale_usa):
        for i in range(1, transition_time):
           GPIO.output(COMBI_RED, GPIO.HIGH)
           beep_function(0.2)
           GPIO.output(COMBI_RED, GPIO.LOW)
           time.sleep(0.5)
    else: # Scotland leaves the Green Light on throughout but good to change the Beep Frequency
        GPIO.output(COMBI_GREEN, GPIO.HIGH)
        for i in range(1, transition_time):
            beep_function(0.2)
            time.sleep(0.5)

        # When done Turn off Green and Trun on Red
        GPIO.output(COMBI_GREEN, GPIO.LOW)
        GPIO.output(COMBI_RED, GPIO.HIGH)

# Main Program
signal(SIGINT, ctrl_c_handler)
initialize_GPIO()
initialize_cross_walk()
pi_id = get_MAC('wlan0')

# infinite loop for the main thread (Use Cntrl-C to exit)
while True:
  # take a reading from the switch
  input = GPIO.input(BUTTON)

  # if the last reading was high and this one is low, signal Button Released
  if ((previous_input) and not input):
    current_date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ") # Proper ISO8601 Timestamp
    print("Button Released at", current_date_time)

    # Update the database
    cursor.execute('INSERT INTO button_pressed VALUES(?,?,?,?)', (pi_id, current_date_time, locale_usa, beep))
    connection.commit()

    # send out ButtonPressed data to AWS API Gateway / Server Proxy to DynamoDB
    remote_api_url = "https://wbf4yrz1ui.execute-api.us-east-2.amazonaws.com/v1/button_presses"
    data = {"dateTime": current_date_time, "piId": pi_id, "usa": locale_usa, "beep": beep}
 
    # Send the json=data to the remote_api_url 
    response = requests.post(remote_api_url, json=data)
    print("Status code = ", response.status_code)
    print(response.json())
    
    # Run the Traffic Lights Sequence
    car_to_pedestrian(5 * transition_time)

    walk_signal(10 * transition_time, locale_usa)

    end_walk_signal(10 * transition_time, locale_usa)

    pedestrian_to_car(5 * transition_time, locale_usa)

  # update prev_input value
  previous_input = input

  #slight pause to debounce
  time.sleep(0.05)
