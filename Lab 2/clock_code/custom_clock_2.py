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
    "petal_on": (255, 160, 190),
    "petal_off": (70, 70, 90),
    "disc": (230, 195, 60),
    "disc_ring": (120, 90, 20),
    "bee": (250, 210, 50),
    "bee_stripe": (40, 35, 30),
    "time": (255, 255, 255),
    "date": (160, 160, 160),
}

def draw_stem(draw, x, y_bottom, y_top, thickness=6):
    draw.line((x, y_bottom, x, y_top), fill=COLORS["stem"], width=thickness)

def draw_leaf(draw, x, y, side="left", length=28, width_leaf=8, filled=True, tilt_deg=22):
    """
    Diamond/teardrop-ish leaf that points LEFT/RIGHT correctly.
    - side="right"  => base angle = 0°, then tilt slightly upward  (−tilt)
    - side="left"   => base angle = 180°, then tilt slightly upward (π − tilt)
    """
    import math
    tilt = math.radians(tilt_deg)
    if side == "right":
        theta = -tilt                     # a little above the horizontal
    else:
        theta = math.pi - tilt            # to the left + a little above

    # unit vectors: u = along the leaf axis, v = perpendicular (for thickness)
    ux, uy = math.cos(theta), math.sin(theta)
    vx, vy = -uy, ux

    # geometry: tip -> base (stem) with rounded-ish diamond
    w = width_leaf / 2.0
    tip = (x + ux * length, y + uy * length)
    base = (x, y)
    p2 = (base[0] + vx * w, base[1] + vy * w)
    p4 = (base[0] - vx * w, base[1] - vy * w)

    color = COLORS["leaf_on"] if filled else COLORS["leaf_off"]
    draw.polygon([tip, p2, base, p4], fill=color)


def draw_flower_head(draw, cx, cy, r, minute, second):
    """
    12 big petals (5-minute chunks).
    - Completed chunks are fully filled.
    - The current chunk fills proportionally within the petal itself (smooth with seconds).
    - No dots or external arc.
    """
    import math

    r_in  = int(r * 0.62)
    r_out = int(r * 0.92)
    width = 9                     # petal thickness
    cap_r = width // 2

    group  = minute // 5          # 0..11
    within = minute % 5           # 0..4
    # Smooth fill: within 0..1 over the 5-minute window (uses seconds)
    fill_frac = ((within + min(second, 59) / 60.0) / 5.0)
    fill_frac = max(0.0, min(1.0, fill_frac))

    # --- Base: draw all 12 petals OFF (as capsules) ---
    for i in range(12):
        theta = (2 * math.pi * i) / 12.0 - math.pi/2
        x0 = cx + int(r_in  * math.cos(theta))
        y0 = cy + int(r_in  * math.sin(theta))
        x1 = cx + int(r_out * math.cos(theta))
        y1 = cy + int(r_out * math.sin(theta))
        col = COLORS["petal_off"]
        draw.line((x0, y0, x1, y1), fill=col, width=width)
        draw.ellipse((x0-cap_r, y0-cap_r, x0+cap_r, y0+cap_r), fill=col)
        draw.ellipse((x1-cap_r, y1-cap_r, x1+cap_r, y1+cap_r), fill=col)

    # --- Fill all COMPLETED petals fully ON ---
    for i in range(group):
        theta = (2 * math.pi * i) / 12.0 - math.pi/2
        x0 = cx + int(r_in  * math.cos(theta))
        y0 = cy + int(r_in  * math.sin(theta))
        x1 = cx + int(r_out * math.cos(theta))
        y1 = cy + int(r_out * math.sin(theta))
        col = COLORS["petal_on"]
        draw.line((x0, y0, x1, y1), fill=col, width=width)
        draw.ellipse((x0-cap_r, y0-cap_r, x0+cap_r, y0+cap_r), fill=col)
        draw.ellipse((x1-cap_r, y1-cap_r, x1+cap_r, y1+cap_r), fill=col)

    # --- Partially fill the CURRENT petal (rounded tip) ---
    theta = (2 * math.pi * group) / 12.0 - math.pi/2
    x0 = cx + int(r_in * math.cos(theta))
    y0 = cy + int(r_in * math.sin(theta))
    # length from inner to outer scaled by fill_frac
    partial_r = r_in + int((r_out - r_in) * fill_frac)
    xm = cx + int(partial_r * math.cos(theta))
    ym = cy + int(partial_r * math.sin(theta))
    col = COLORS["petal_on"]
    draw.line((x0, y0, xm, ym), fill=col, width=width)
    draw.ellipse((x0-cap_r, y0-cap_r, x0+cap_r, y0+cap_r), fill=col)  # inner round
    draw.ellipse((xm-cap_r, ym-cap_r, xm+cap_r, ym+cap_r), fill=col)  # rounded tip

    # --- Center disc ---
    draw.ellipse(
        (cx - int(r*0.38), cy - int(r*0.38), cx + int(r*0.38), cy + int(r*0.38)),
        fill=COLORS["disc"], outline=COLORS["disc_ring"], width=2
    )

    # --- Bee orbit (seconds) ---
    theta_bee = (2 * math.pi * (second % 60)) / 60.0 - math.pi/2
    r_bee = int(r * 1.15)
    bx = cx + int(r_bee * math.cos(theta_bee))
    by = cy + int(r_bee * math.sin(theta_bee))
    bee_r = 5
    draw.ellipse((bx - bee_r, by - bee_r, bx + bee_r, by + bee_r), fill=COLORS["bee"])
    draw.line((bx - bee_r, by, bx + bee_r, by), fill=COLORS["bee_stripe"], width=2)
    draw.ellipse((bx - 2, by - bee_r - 3, bx + 4, by - bee_r + 2), fill=(240, 240, 255))


def hour_to_leaves(h24):
    h = h24 % 12
    return 12 if h == 0 else h

while True:
    # Clear frame
    draw.rectangle((0, 0, width, height), outline=0, fill=COLORS["bg"])

    now = time.localtime()
    h, m, s = now.tm_hour, now.tm_min, now.tm_sec

    # --- Stem ---
    stem_x = int(width * 0.22)
    stem_y_bottom = height - 6
    stem_y_top    = int(height * 0.08)
    draw_stem(draw, stem_x, stem_y_bottom, stem_y_top, thickness=6)

    # --- Leaves (alternating L/R, non-overlapping) ---
    total_leaves = 12
    leaves_on = hour_to_leaves(h)               # 1..12
    span = stem_y_bottom - stem_y_top
    step = max(10.0, span / (total_leaves + 1)) # >=10 px spacing
    for i in range(total_leaves):
        y = int(stem_y_bottom - (i + 1) * step)
        y += (-1 if (i % 2 == 0) else 1) * 1    # tiny ±1 px stagger
        side = "left" if (i % 2 == 0) else "right"
        filled = (i < leaves_on)
        draw_leaf(draw, stem_x, y, side=side, length=28, width_leaf=8, filled=filled, tilt_deg=22)

    # --- Flower head (12 petals; current petal fills smoothly; bee = seconds) ---
    head_cx = int(width * 0.72)
    head_cy = int(height * 0.50)
    head_r  = 50
    draw_flower_head(draw, head_cx, head_cy, head_r, minute=m, second=s)

    # --- Optional small labels ---
    time_str = time.strftime("%I:%M %p", now).lstrip("0")
    date_str = time.strftime("%a %b %d", now)
    ty = height - 22
    # draw.text((8, ty), time_str, font=date_font, fill=COLORS["time"])
    # dw = draw.textbbox((0, 0), date_str, font=date_font)[2]
    # draw.text((width - 8 - dw, ty), date_str, font=date_font, fill=COLORS["date"])  # right-align
    
    # Push frame
    disp.image(image, rotation)
    time.sleep(0.2)  # smoother bee/petal fill; use 1.0 for once-per-second updates

