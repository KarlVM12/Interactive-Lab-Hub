import time
import board
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import qwiic_joystick
import qwiic_button
import qwiic_proximity
import digitalio
import adafruit_rgb_display.st7789 as st7789

i2c = busio.I2C(board.SCL, board.SDA)
spi = busio.SPI(board.SCK, board.MOSI)

oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
oled.fill(0)
oled.show()
oled_font = ImageFont.load_default()

cs_pin = digitalio.DigitalInOut(board.D5)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    x_offset=50,
    y_offset=40,
    rotation=90,
)

joystick = qwiic_joystick.QwiicJoystick()
button = qwiic_button.QwiicButton()
prox = qwiic_proximity.QwiicProximity()

joystick.begin()
button.begin()
prox.begin()

happiness = 5
pet_awake = True
selected = 0
menu_options = ['Feed', 'Play', 'Clean']
last_input_time = time.time()



# ==== Image Assets ====
def clear_display():
    """Fill the MiniPiTFT display with black."""
    blank = Image.new("RGB", (135, 240), (0, 0, 0))
    disp.image(blank)

def show_face(name, selected_option=None):
    """Safely display a pet face image with optional text on MiniPiTFT."""
    img = faces[name].convert("RGB")

    if img.size != (240, 135):
        img = img.resize((240, 135), Image.BICUBIC)

    base = Image.new("RGB", (240, 135), (0, 0, 0))
    base.paste(img, (0, 0))

    if selected_option is not None:
        draw = ImageDraw.Draw(base)
        font = ImageFont.load_default()
        text = f"> {selected_option} <"
        
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = (240 - text_width) // 2
        text_y = 135 - text_height - 5

        draw.rectangle([0, text_y - 2, 240, 135], fill=(0, 0, 0))
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255))

    disp.image(base)

faces = {
    'happy': Image.open("assets/happy.png"),
    'meh': Image.open("assets/meh.png"),
    'sad': Image.open("assets/sad.png"),
    'sleeping': Image.open("assets/sleeping.png"),
}

def draw_happiness_bar():
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Draw bar based on happiness level
    bar_width = int((happiness / 10) * oled.width)
    draw.rectangle((0, 0, bar_width, oled.height), outline=255, fill=255)

    oled.image(image)
    oled.show()

while True:
    try:
        prev_debug_msg = ""

        # even with nothing in front of it, seems to default to giving a value of 3, 4, or 5, so made threshold 7
        distance = prox.get_proximity()
        if distance <= 7:
            pet_awake = False
        else:
            pet_awake = True

        # only worried about up and down input
        joy_x = joystick.horizontal
        if joy_x < 100:
            selected = (selected - 1) % len(menu_options)
            last_input_time = time.time()
            time.sleep(0.3)
        elif joy_x > 900:
            selected = (selected + 1) % len(menu_options)
            last_input_time = time.time()
            time.sleep(0.3)

        if button.is_button_pressed():
            if menu_options[selected] == 'Feed':
                happiness = min(10, happiness + 1)
            elif menu_options[selected] == 'Play':
                happiness = min(10, happiness + 2)
            elif menu_options[selected] == 'Clean':
                happiness = max(0, happiness - 1)
            time.sleep(0.5)

        if not pet_awake:
            show_face('sleeping', menu_options[selected])
        elif happiness >= 8:
            show_face('happy', menu_options[selected])
        elif happiness >= 4:
            show_face('meh', menu_options[selected])
        else:
            show_face('sad', menu_options[selected])

        draw_happiness_bar()

        debug_msg = f"Distance: {distance}mm | Selected: {menu_options[selected]} | Happiness: {happiness}/10"
        if debug_msg != prev_debug_msg:
            print(debug_msg)
            prev_debug_msg = debug_msg

        time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting program.")
        break
