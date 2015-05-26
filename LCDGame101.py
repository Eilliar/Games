"""
First Program to build a game with Nokia LCD Display

Author: Bruno Godoi Eilliar
Date : May 27, 2015

Dependencies:
- Adafruit Nokia LCD library
- Rasperry Pi GPIO library
- Python Image Library
"""

import time
import numpy as np
import RPi.GPIO as GPIO
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

###############################################
# Global Variables
###############################################
debug = True
w = LCD.LCDWIDTH/2
h = LCD.LCDHEIGHT/2

###############################################
# Classes
###############################################
# Bullet Class
class Bullet:
    def __init__(self, x,y,vx,vy):
        self.x = x
        self.y = y
        self.vx = vx # velocity on x axis
        self.vy = vy # velocity on y axis
    
# Ship Class
class Ship:
    """
    Creates a ship object. 
    Inputs: 
    position -> numpy.array; angle -> float number in radians
    """
    def __init__(self, position, angle):
        assert type(position) is np.ndarray, "Position must be an numpy array."
        assert type(angle) is float, "Angle must be an float point number (radians)."
        self.position = position
        self.angle = angle
        self.vertices = (position[0]-2,position[1]+4, position[0], position[1]-4, position[0]+2, position[1]+4)

    
    def move(self, delta_x, delta_y):
        self.position += np.array([delta_x,delta_y])
        self.vertices = (self.position[0]-2,self.position[1]+4, self.position[0], self.position[1]-4, self.position[0]+2, self.position[1]+4)

# Creates a ship
nave = Ship(np.array([w,h]), 0.)
###############################################
# Functions
###############################################
def left_button_callback(left):
    global nave
    nave.move(1,0)
    return None
    
def right_button_callback(right):
    global nave
    nave.move(-1,0)
    return None
    
###############################################
# Raspberry Pi hardware Configuration
###############################################
# Raspberry Pi hardware SPI config:
DC = 23
RST = 24
SPI_PORT = 0
SPI_DEVICE = 0
# Raspberry Pi GPIO config:
left = 18    # left button port
right = 17  # right button port
GPIO.setmode(GPIO.BCM) # set GPIO numeration label
GPIO.setup(left, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(right, GPIO.IN, pull_up_down = GPIO.PUD_UP)
# Define input channel for the callback, something like an interruption
GPIO.add_event_detect(left, GPIO.FALLING, callback = left_button_callback, bouncetime = 100)
GPIO.add_event_detect(right, GPIO.FALLING, callback = right_button_callback, bouncetime = 100)

###############################################
# Nokia Display Setup
###############################################
# Hardware SPI usage:
disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))
# Initialize library.
disp.begin(contrast=60)

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a white filled box to clear the image.
draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)


###############################################
# Main Loop
###############################################
try:
    while (True):
        # Clear Display before making a new frame
        draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
        draw.polygon(nave.vertices, outline=0, fill = 255)
    
        # Display image.
        disp.image(image)
        disp.display()
        time.sleep(.001)

# Press CTRL+C to stop the main routine
except KeyboardInterrupt:
    pass