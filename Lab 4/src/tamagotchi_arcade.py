import time
import board
import busio

import qwiic_joystick
import qwiic_button
import qwiic_proximity
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# === Initialize I2C ===
i2c = busio.I2C(board.SCL, board.SDA)

# === OLED ===
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
oled.fill(0)
oled.show()
font = ImageFont.load_default()

# === Devices ===
joystick = qwiic_joystick.QwiicJoystick()
button = qwiic_button.QwiicButton()
prox = qwiic_proximity.QwiicProximity()

# === State ===
happiness = 5
pet_awake = True
selected = 0
menu_options = ['Feed', 'Play', 'Clean']
last_joy_position = 512  # Neutral

# === Setup ===
joystick.begin()
button.begin()
prox.begin()

def draw_oled_status():
    oled.fill(0)
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Happiness + Wake Status
    draw.text((0, 0), f"Happiness: {happiness}/10", font=font, fill=255)
    draw.text((90, 0), "Awake" if pet_awake else "Zzz", font=font, fill=255)

    # Menu bar
    menu_display = " | ".join(
        [f"[{m}]" if i == selected else m for i, m in enumerate(menu_options)]
    )
    draw.text((0, 16), menu_display, font=font, fill=255)

    oled.image(image)
    oled.show()

# === Main Loop ===
while True:
    try:
        # === Distance sensor: Wake/sleep logic ===
        prox_value = prox.get_proximity()
        pet_awake = prox_value > 5  # Empirical threshold; tune if needed

        # === Joystick logic ===
        joy_x = joystick.horizontal

        if joy_x < 100 and last_joy_position >= 100:
            selected = (selected - 1) % len(menu_options)
            time.sleep(0.2)
        elif joy_x > 900 and last_joy_position <= 900:
            selected = (selected + 1) % len(menu_options)
            time.sleep(0.2)

        last_joy_position = joy_x

        # === Button logic ===
        if button.is_button_pressed():
            if menu_options[selected] == 'Feed':
                happiness = min(10, happiness + 1)
            elif menu_options[selected] == 'Play':
                happiness = min(10, happiness + 2)
            elif menu_options[selected] == 'Clean':
                happiness = max(0, happiness - 1)
            time.sleep(0.4)  # debounce

        # === Update OLED ===
        draw_oled_status()

        # === Debug Output ===
        print(f"Prox: {prox_value} | Pet: {'Awake' if pet_awake else 'Sleep'}")
        print(f"Menu: {menu_options[selected]} | Happiness: {happiness}/10")

        time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting program.")
        break
