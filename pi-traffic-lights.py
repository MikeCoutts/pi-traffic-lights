# Copyright The Kavinjka Software Company 2021
#
# Authour MikeC@kavinjka.com

import RPi.GPIO as GPIO
import time # for sleep functions

from signal import signal, SIGINT # for Cntrl-C
from sys import exit

# define the GPIO port for the Button
button = 16

# define the GPIO ports for the Traffic Lights
green = 26
amber = 19
red = 13

# define the GPIO ports for the Cross Walk/Pedistrian Signal 
combi_red = 22
combi_green = 27
combi_blue = 17

# define the GPIO port for the Buzzer Activation
buzzer = 23

# Define an exit handler for the program (called on Cntrl-C)
def CntrlCHandler(signal_received, frame):
    # Handle any GPIO cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    GPIO.cleanup()
    exit(0)

# setup  the Cntrl-C handler
signal(SIGINT, CntrlCHandler)

# Initialize the GPIO Infrastructure to BCM (Broadcom SOC channel)
GPIO.setmode(GPIO.BCM)

# Setup all the Input and Output GPIO Pins
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 16 (button) to be an input pin and set initial value to be pulled low (off)

GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT) 
GPIO.setup(amber, GPIO.OUT)
GPIO.setup(combi_red, GPIO.OUT)
GPIO.setup(combi_green, GPIO.OUT)
GPIO.setup(combi_blue, GPIO.OUT) 

GPIO.setup(buzzer, GPIO.OUT)

#initialise previous_input variable to 0 (assume button not pressed on startup) and Pedistrian Crossing as false
previous_input = 0
crossing = False 

# turn on the Green Light and red cross walk light, Assume the cross-Walk is Cars allowed through.
def InitializeCrossWalk():
    GPIO.output(green, GPIO.HIGH)
    GPIO.output(amber, GPIO.LOW)
    GPIO.output(red, GPIO.LOW)
    GPIO.output(combi_red, GPIO.HIGH)
    GPIO.output(combi_blue, GPIO.LOW)
    GPIO.output(combi_green, GPIO.LOW)
    GPIO.output(buzzer, GPIO.LOW)

# Use a function to control the Car to Pedestrian Transition 
def CarToPedestrian(transition_time):
    GPIO.output(green, GPIO.LOW)
    GPIO.output(amber, GPIO.HIGH)

    time.sleep(transition_time) # sleep between Green/Amber/Red

    GPIO.output(amber, GPIO.LOW)
    GPIO.output(red, GPIO.HIGH)

# Use a function to control the Pedestrian to Car transition
def PedestrianToCar(transition_time, locale_usa):
    GPIO.output(combi_red, GPIO.HIGH) # Red Do Not Walk signal to Pedestrians
    
    # As the USA and Scotland return to car sequence is different we need to decide
    if locale_usa:
        time.sleep(transition_time) 
	GPIO.output(red, GPIO.LOW) # Red goes straight to Green in the USA
    else:
	GPIO.output(amber, GPIO.HIGH) # and hold for transition_time
        
        # Scotland Sequence is a little different with Red/Amber on Prior to flip to Green
        GPIO.output(amber, GPIO.HIGH)

        time.sleep(transition_time) # for Scotland Red/Amber ("prepare to proceed")
     
        GPIO.output(red, GPIO.LOW)
        GPIO.output(amber, GPIO.LOW)

    # return the crossing to Cars ("Proceed if safe to do so")
    GPIO.output(green, GPIO.HIGH)

def beep(duration):
    GPIO.output(buzzer, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(buzzer, GPIO.LOW)
	
# use a function to Start and maintain the Walk Signal (White in the USA, Green in Scotland with an intermitent "beep')
def WalkSignal(transition_time, locale_usa):
    if (locale_usa):
	GPIO.output(combi_red, GPIO.HIGH)
    	GPIO.output(combi_blue, GPIO.HIGH)
	GPIO.output(combi_green, GPIO.HIGH)
    else:
	GPIO.output(combi_green, GPIO.HIGH)

    for i in range(1, transition_time):
	beep(0.5)
  	time.sleep(0.5)


def EndWalkSignal(transition_time, locale_usa):
    # Shut of the walk signal
    GPIO.output(combi_red, GPIO.LOW)
    GPIO.output(combi_blue, GPIO.LOW)
    GPIO.output(combi_green, GPIO.LOW)

    if  (locale_usa):
	for i in range(1, transition_time):
	   GPIO.output(combi_red, GPIO.HIGH)
	   beep(0.5)
	   GPIO.output(combi_red, GPIO.LOW)
	   time.sleep(0.5)
    else:
        GPIO.output(combi_green, GPIO.HIGH)
	for i in range(1, transition_time):
	    beep(0.5)
            time.sleep(0.5)

	GPIO.output(combi_red, GPIO.HIGH)
	GPIO.output(combi_green, GPIO.LOW)

# Main Program
InitializeCrossWalk()

# infinate loop for the main thread (Use Cntrl-C to exit)
while True:
  # take a reading from the switch
  input = GPIO.input(button)
 
  # if the last reading was high and this one is low, signal Button Released
  if ((previous_input) and not input):
    print("Button Released")

    CarToPedestrian(5)

    WalkSignal(10, True)

    EndWalkSignal(10, True)

    PedestrianToCar(5, True)
  
  # update prev_input value 
  previous_input = input
 
  #slight pause to debounce
  time.sleep(0.05)