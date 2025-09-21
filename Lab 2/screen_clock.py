import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
time_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 55)
date_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0) # fill=400
    
    # Lab 2 Part D:
    now = time.localtime()
    colon = ":" if (now.tm_sec % 2) == 0 else " " # fun blinking colon
    time_str = time.strftime(f"%H{colon}%M{colon}%S", now) # currently 24h time, if I use %I gives 12h
    date_str = time.strftime("%a %b %d, %Y", now)

    # attempt to center and position nicely
    t_bbox = draw.textbbox((0, 0), time_str, font=time_font)
    d_bbox = draw.textbbox((0, 0), date_str, font=date_font)
    t_w, t_h = t_bbox[2] - t_bbox[0], t_bbox[3] - t_bbox[1]
    d_w, d_h = d_bbox[2] - d_bbox[0], d_bbox[3] - d_bbox[1]

    t_x = (width  - t_w) // 2
    t_y = ((height - t_h) // 2) - 10
    d_x = (width  - d_w) // 2
    d_y = t_y + t_h + 12

    # sends text into image buffer so it can be displayed
    draw.text((t_x, t_y), time_str, font=time_font, fill="#FFFFFF")
    draw.text((d_x, d_y), date_str, font=date_font, fill="#A0A0A0")

    # Push the buffer to the display
    disp.image(image, rotation)
    time.sleep(1)
