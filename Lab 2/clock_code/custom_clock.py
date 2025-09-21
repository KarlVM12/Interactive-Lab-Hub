import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
import math

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

# -------- Flower Clock helpers --------
COLORS = {
    "bg": (10, 12, 14),
    "stem": (28, 110, 62),
    "leaf_on": (46, 171, 97),
    "leaf_off": (24, 60, 38),
    "petal_on": (255, 160, 190),   # pink
    "petal_off": (70, 70, 90),     # muted ticks
    "disc": (230, 195, 60),        # flower center
    "disc_ring": (120, 90, 20),
    "bee": (250, 210, 50),
    "bee_stripe": (40, 35, 30),
    "time": (255, 255, 255),
    "date": (160, 160, 160),
}

def draw_stem(draw, x, y_bottom, y_top, thickness=6):
    draw.line((x, y_bottom, x, y_top), fill=COLORS["stem"], width=thickness)

def draw_leaf(draw, x, y, side="left", length=26, width_leaf=14, filled=True):
    # Simple elliptical leaf to left/right of stem
    if side == "left":
        bbox = (x - length, y - width_leaf//2, x, y + width_leaf//2)
    else:
        bbox = (x, y - width_leaf//2, x + length, y + width_leaf//2)
    fill = COLORS["leaf_on"] if filled else COLORS["leaf_off"]
    draw.ellipse(bbox, fill=fill, outline=None)

def draw_flower_head(draw, cx, cy, r, minute, second):
    """
    - 60 petals around ring; petals [0..minute-1] are 'on'
    - small center disc
    - bee orbits once per minute based on 'second'
    """
    # Petal ring
    r_in = int(r * 0.62)
    r_out = int(r * 0.92)
    for i in range(60):
        theta = (2 * math.pi * i) / 60.0 - math.pi/2  # start at top
        x0 = cx + int(r_in  * math.cos(theta))
        y0 = cy + int(r_in  * math.sin(theta))
        x1 = cx + int(r_out * math.cos(theta))
        y1 = cy + int(r_out * math.sin(theta))
        col = COLORS["petal_on"] if i < minute else COLORS["petal_off"]
        draw.line((x0, y0, x1, y1), fill=col, width=3)

    # Center disc
    draw.ellipse(
        (cx - int(r*0.38), cy - int(r*0.38), cx + int(r*0.38), cy + int(r*0.38)),
        fill=COLORS["disc"], outline=COLORS["disc_ring"], width=2
    )

    # Bee (seconds)
    theta_bee = (2 * math.pi * (second % 60)) / 60.0 - math.pi/2
    r_bee = int(r * 1.1)
    bx = cx + int(r_bee * math.cos(theta_bee))
    by = cy + int(r_bee * math.sin(theta_bee))

    # Bee body
    bee_r = 5
    draw.ellipse((bx - bee_r, by - bee_r, bx + bee_r, by + bee_r), fill=COLORS["bee"], outline=None)
    # Stripes
    draw.line((bx - bee_r, by, bx + bee_r, by), fill=COLORS["bee_stripe"], width=2)
    # Tiny wing
    draw.ellipse((bx - 2, by - bee_r - 3, bx + 4, by - bee_r + 2), fill=(240,240,255))

def hour_to_leaves(h24):
    # 12-hour style: 1..12 leaves; 0→12
    h = h24 % 12
    return 12 if h == 0 else h

while True:
    # Clear frame
    draw.rectangle((0, 0, width, height), outline=0, fill=COLORS["bg"])

    now = time.localtime()
    h, m, s = now.tm_hour, now.tm_min, now.tm_sec

    # --- Layout (works with 240x135 landscape) ---
    # Stem on the left third, head on the right
    stem_x = int(width * 0.22)              # ~53 px when width=240
    stem_y_bottom = height - 8              # ~127
    stem_y_top    = int(height * 0.52)      # ~70

    head_cx = int(width * 0.72)             # ~172
    head_cy = int(height * 0.52)            # ~70
    head_r  = 48

    # --- Draw stem & leaves (hour) ---
    draw_stem(draw, stem_x, stem_y_bottom, stem_y_top, thickness=6)
    leaves_on = hour_to_leaves(h)           # 1..12
    total_leaves = 12
    # Distribute leaves along the stem
    span = stem_y_bottom - stem_y_top
    step = span / (total_leaves + 1)
    for i in range(total_leaves):
        y = int(stem_y_bottom - (i + 1) * step)
        side = "left" if (i % 2 == 0) else "right"
        filled = (i < leaves_on)            # fill first N leaves
        draw_leaf(draw, stem_x, y, side=side, length=26, width_leaf=14, filled=filled)

    # --- Draw flower head (minutes + bee/seconds) ---
    draw_flower_head(draw, head_cx, head_cy, head_r, minute=m, second=s)

    # --- Optional: small time/date label at bottom ---
    time_str = time.strftime("%I:%M:%S %p", now).lstrip("0")
    date_str = time.strftime("%a %b %d, %Y", now)
    # pick smaller fonts you already defined
    t_bbox = draw.textbbox((0, 0), time_str, font=date_font)
    d_bbox = draw.textbbox((0, 0), date_str, font=date_font)
    t_w = t_bbox[2] - t_bbox[0]
    d_w = d_bbox[2] - d_bbox[0]
    # Draw at bottom, centered
    # ty = height - 24
    # draw.text(((width - t_w)//2, ty), time_str, font=date_font, fill=COLORS["time"])
    # draw.text(((width - d_w)//2, ty + 14), date_str, font=date_font, fill=COLORS["date"])

    # Push frame
    disp.image(image, rotation)
    time.sleep(1)

