"""
Second Program to build a game with Nokia LCD Display
Add Welcome screen and some rocks

Author: Bruno Godoi Eilliar
Date : May 28, 2015

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
w = LCD.LCDWIDTH
h = LCD.LCDHEIGHT
bullet_list = []
bullet_vx = 0
bullet_vy = -1
font = ImageFont.load_default()# Load default font.
Welcome = True  #Show welcome screen

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
    def move(self):
        self.x += self.vx
        self.y += self.vy
    
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
nave = Ship(np.array([w/2,h-8]), 0.)
###############################################
# Functions
###############################################
def left_button_callback(left):
    global nave
    nave.move(-1,0)
    return None
    
def right_button_callback(right):
    global nave
    nave.move(1,0)
    return None
    
def fire_button_callback(fire):
    global bullet_list, nave, bullet_vx, bullet_vy
    #time.sleep(.5)    
    bullet_list.append(Bullet(nave.position[0], nave.position[1]-4, bullet_vx, bullet_vy))
    if debug: print "BAWG!"
    return None
    
def welcome_draw(draw):
    """
    Function to draw welcome screen.
    Inputs: draw object
    """
    # Draw a white filled box to clear the image.
    draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
    # Write some text.
    draw.text((6,3), '-=Invaders=-', font=font)
    draw.text((1,37), 'By Bruno G. E.', font=font)
    return None
    
def show_image(nokia, image):
    """
    Function to show image on the display
    Inputs: nokia-> display in use; image -> image to show
    """
    # Display image.
    nokia.image(image)
    nokia.display()
    time.sleep(.001)
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
fire = 22   # shooting button (A Button)
b_button = 27   #B Button

GPIO.setmode(GPIO.BCM) # set GPIO numeration label
GPIO.setup(left, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(right, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(fire, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(b_button, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Define input channel for the callback, something like an interruption
GPIO.add_event_detect(left, GPIO.FALLING, callback = left_button_callback, bouncetime = 100)
GPIO.add_event_detect(right, GPIO.FALLING, callback = right_button_callback, bouncetime = 100)
GPIO.add_event_detect(fire, GPIO.FALLING, callback = fire_button_callback, bouncetime = 200)

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
        # Welcome Screen
        while (Welcome):
            # Draw welcome screen
            welcome_draw(draw)
            # Display image.
            show_image(disp, image)
            if (GPIO.input(b_button) == False):
                if debug: print "B pressed"
                Welcome = False
                
        bullets_index = []
        # Clear Display before making a new frame
        draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill=255)
        # Draw the ship
        draw.polygon(nave.vertices, outline=0, fill = 255)
        #Draw the bulets
        for bullet in bullet_list:
            bullet.move()
            if bullet.y >=0: # bullet still on the screen
                draw.line((bullet.x, bullet.y, bullet.x, bullet.y-1), fill = 0)
            else: # bullet out of display range
                bullets_index.append(bullet_list.index(bullet))
        # Remove bullets that are out of display's range
        for i in bullets_index:
            bullet_list.pop(i)
        
        #if debug: print bullet_list
        
        # Display image.
        show_image(disp, image)

# Press CTRL+C to stop the main routine
except KeyboardInterrupt:
    # Draw welcome screen
    welcome_draw(draw)
    # Display image.
    show_image(disp, image)
    pass