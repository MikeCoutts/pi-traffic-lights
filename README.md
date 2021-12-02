# pi-traffic-lights
A simple Raspberry PI Python example of the Traffic Lights project with added Buzzer and Analytics as STEM for Kids

Read the status of a momentary switch on GPIO Pin 16 (note the use of a Blue LED in place of a 10k Ohm Pull down resistor)

On detection of the trailing edge (as the switch is released) change the state of a variable and various LED's tied to GPIO PINs

Change the state of a GPIO Output pin that drives a Buzzer via direct input from a GPIO pin to Ground.

![Alt text](https://github.com/MikeCoutts/pi-simple-switch/blob/main/images/IMG_20211103_225959778.jpg?raw=true "Traffic Lights")

# Simple Raspberry Pi Bread Board wiring for this project
[Buzzer](https://www.amazon.com/dp/B07S85WRSZ?psc=1&ref=ppx_yo2_dt_b_product_details) ground on 5V GND line with +ve into GPIO 23

Blue LED (GPIO 17), Green LED (GPIO 23) and Red LED (GPIO 22) connected to the White LED BGR Anodes via 10K Ohm Resitors with Cathode to Ground.

Individual Red LED (GPIO 13), Amber/Yellow LED (GPIO 19), Green LED (GPIO 26) connected to Red/Amber/Green LED's via 10K Ohm resitors.

10K Ohm resiter supplying power to momentary switch with a Blue line (connected to GPIO Input 16) being drawn down by a Blue LED.

# Operation of the Program
On Initialization Green LED is on for traffic progression and "Combination White" LED is Red to stop People crossing.

Upon Button depression the Blue LED get's a simple direct power supply (via a 10K Ohm resister) with the side effect of bringing the "Button" Line Low.

Upon release the pi-traffic-lights program (Cross Walk in the USA, Pedestrian Crossing in Scotland) detects the rising edge and flips from car mode to pedistrain mode:

Initiates the following sequence: Green Off, RED/Amber On and all of the combi LED ON giving a White light to pedestrians plus a screatching Buzzer for ADA. Halfway through the CrossWalk sequence the White "Walk" Signal changes to a flashing Red "Hurry Up" Signal - need to see if the Buzzer frequency changes for ADA.

Ultimately the Crossing is closed and the Traffic Lights return from Red to Green (USA) or RED/Red/Amber/Green (Scotland)

Introduced some very simple argv processing up fron --usa put the code into the USA locale while any other parameter such as --scotland put it into the UK/Scottish locale where the CrossWalk / Pedistrian Crossing light work slightly differently.
