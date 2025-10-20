
# Ph-UI!!!

---

<details>
<summary><strong>Lab 4 Deliverables</strong></summary>

### Part 1 (Week 1)
**Submit the following for Part 1:**  
*️⃣ **A. Capacitive Sensing**
	- Photos/videos of your Twizzler (or other object) capacitive sensor setup
	- Code and terminal output showing touch detection

*️⃣ **B. More Sensors**
	- Photos/videos of each sensor tested (light/proximity, rotary encoder, joystick, distance sensor)
	- Code and terminal output for each sensor

*️⃣ **C. Physical Sensing Design**
	- 5 sketches of different ways to use your chosen sensor
	- Written reflection: questions raised, what to prototype
	- Pick one design to prototype and explain why

*️⃣ **D. Display & Housing**
	- 5 sketches for display/button/knob positioning
	- Written reflection: questions raised, what to prototype
	- Pick one display design to integrate
	- Rationale for design
	- Photos/videos of your cardboard prototype

---

### Part 2 (Week 2)
**Submit the following for Part 2:**  
*️⃣ **E. Multi-Device Demo**
	- Code and video for your multi-input multi-output demo (e.g., chaining Qwiic buttons, servo, GPIO expander, etc.)
	- Reflection on interaction effects and chaining

*️⃣ **F. Final Documentation**
	- Photos/videos of your final prototype
	- Written summary: what it looks like, works like, acts like
	- Reflection on what you learned and next steps

</details>

---

## Lab Overview
**NAMES OF COLLABORATORS HERE** <br>
\*\***Karl Muller**\*\*

<details>
<summary><strong>Readings</strong></summary>

* [What do prototypes prototype?](https://www.semanticscholar.org/paper/What-do-Prototypes-Prototype-Houde-Hill/30bc6125fab9d9b2d5854223aeea7900a218f149)
* [Paper prototyping](https://www.uxpin.com/studio/blog/paper-prototyping-the-practical-beginners-guide/) is used by UX designers to quickly develop interface ideas and run them by people before any programming occurs. 
* [Cardboard prototypes](https://www.youtube.com/watch?v=k_9Q-KDSb9o) help interactive product designers to work through additional issues, like how big something should be, how it could be carried, where it would sit. 
* [Tips to Cut, Fold, Mold and Papier-Mache Cardboard](https://makezine.com/2016/04/21/working-with-cardboard-tips-cut-fold-mold-papier-mache/) from Make Magazine.
* [Surprisingly complicated forms](https://www.pinterest.com/pin/50032245843343100/) can be built with paper, cardstock or cardboard.  The most advanced and challenging prototypes to prototype with paper are [cardboard mechanisms](https://www.pinterest.com/helgangchin/paper-mechanisms/) which move and change. 
* [Dyson Vacuum Cardboard Prototypes](http://media.dyson.com/downloads/JDF/JDF_Prim_poster05.pdf)
<p align="center"><img src="https://dysonthedesigner.weebly.com/uploads/2/6/3/9/26392736/427342_orig.jpg"  width="200" > </p>
</details>

## Lab Overview

A) [Capacitive Sensing](#part-a)

B) [OLED screen](#part-b) 

C) [Paper Display](#part-c)

D) [Materiality](#part-d)

E) [Servo Control](#part-e)

F) [Record the interaction](#part-f)


## The Report (Part 1: A-D, Part 2: E-F)


### Part A
### Capacitive Sensing, a.k.a. Human-Twizzler Interaction 

<img height="443" alt="image" src="https://github.com/user-attachments/assets/9062b469-856f-4bbc-87b6-da0093f6e7e9" />


### Part B
### More sensors

#### Light/Proximity/Gesture sensor (APDS-9960)

Testing Video: [APDS-9960 Testing](https://drive.google.com/file/d/19ji18uo4OrQfEDOP8SNH0KE-qHcD3yUQ/view?usp=sharing)

#### Rotary Encoder 

Testing video: [Rotary Encoder Testing](https://drive.google.com/file/d/1xP1qEUrOX9xLYzTWMjOcdiMAup0OWAHB/view?usp=sharing)

#### Joystick 

Testing video: [Joystick Testing](https://drive.google.com/file/d/1fbiWQDocInuRhKuCqUAxVy4dsgXrwWOP/view?usp=sharing)

#### Distance Sensor

Testing video: [Distance Sensor Testing](https://drive.google.com/file/d/1Fa5bztd5yWVVMMViA1SEq6rev27EYS9M/view?usp=sharing)

### Part C
### Physical considerations for sensing

**\*\*\*Draw 5 sketches of different ways you might use your sensor, and how the larger device needs to be shaped in order to make the sensor useful.\*\*\***
The sensor I went with was the <strong>Joystick</strong>. Here are five different use case sketches:
<img width="524" height="437" alt="image" src="https://github.com/user-attachments/assets/ab203121-f73e-45af-b4d6-f79f464aaf67" /><br>
<img width="380" height="541" alt="image" src="https://github.com/user-attachments/assets/b1346041-d74b-477e-a000-00d2c9bcb453" /><br>
<img width="386" height="471" alt="image" src="https://github.com/user-attachments/assets/e6eec587-90f8-40b1-97e5-06f51d0717bb" /><br>
<img width="389" height="394" alt="image" src="https://github.com/user-attachments/assets/a21bbd38-3679-4b66-95b2-3203e72d32f6" /><br>
<img width="340" height="418" alt="image" src="https://github.com/user-attachments/assets/8ce19308-0003-48ac-9ec9-8090fa45d476" /><br>


**\*\*\*What are some things these sketches raise as questions? What do you need to physically prototype to understand how to anwer those questions?\*\*\***
<br>Some questions raised:
- How will feedback be provided to the user?
- Will diagonal input be supported or blocked?
- Will the click button serve a unique role or just be an 'enter'?
- How will the size and placement affect ease of use?
- Is the center push button sensitive enough?

Some of these like the sensitivity of the joystick can't really be determined till a proper prototype is created.
<br><br>

**\*\*\*Pick one of these designs to prototype.\*\*\***
<br>Chosen design to prototype: **Tamagotchi Pet Arcade**. The interaction will be determined through the joystick as it will be able to choose different actions for the pet to do (like pet, feed, play, rest, etc).

### Part D
### Physical considerations for displaying information and housing parts

**\*\*\*Sketch 5 designs for how you would physically position your display and any buttons or knobs needed to interact with it.\*\*\***
<br>Based off the Tamagotchi Pet Caretaker idea, some possible physical sketches for it could be:
<img height="444" alt="image" src="https://github.com/user-attachments/assets/fafb5b78-1662-458b-afaf-29ad599fbd8d" /><br>
<img height="402" alt="image" src="https://github.com/user-attachments/assets/de00e422-fdd6-4ded-9e2f-1d47b573b591" /><br>
<img height="407" alt="image" src="https://github.com/user-attachments/assets/4ca683fe-a311-4384-9c6f-9bd6058f290e" /><br>
<img height="401" alt="image" src="https://github.com/user-attachments/assets/9d7a58ee-dc30-4141-8154-8421b51025f2" /><br>
<img height="487" alt="image" src="https://github.com/user-attachments/assets/4b12d8be-fb70-49ef-946d-935059d261b3" /><br>


**\*\*\*What are some things these sketches raise as questions? What do you need to physically prototype to understand how to answer those questions?\*\*\***
<br>Questions that came up during sketching:
- Should it be hand held or larger or not able to take with you?
- What angle should the screen be tilted for optimal viewing?
- Should there be space inside the box for speaker or future sensors?
- Any other sensors that could complement a certain form factor to expand its capabilities?

Physically prototyping the size would help determine if its a mobile device or not. It would also help in determining space for any complement sensors.
<br>

**\*\*\*Pick one of these display designs to integrate into your prototype. Explain the rationale for the design.\*\*\*** (e.g. Does it need to be a certain size or form or need to be able to be seen from a certain distance?)
<br>Went with the **Arcade Box** style physical design to prototype. This will be a compact cardboard box resembling a mini arcade where the screen will be angled for good viewing with the joystick centered below. Size is meant to be small. Angling the screen will help reduce the contrast. This design is very retro and familiar and would mimic the feeling of classic games. Hope to also have this design be modular given the size of the box to maybe add more sensors into.

<br>

**\*\*\*Document your rough prototype.\*\*\***
<br>Rough prototype: <br>
<img height="614" alt="image" src="https://github.com/user-attachments/assets/0336f515-f223-4a80-843a-daae6f9b76a6" /><br>
<img height="639" alt="image" src="https://github.com/user-attachments/assets/2c7f992b-a27e-4554-8ade-7c7a4a9509b8" /><br>
<img height="606" alt="image" src="https://github.com/user-attachments/assets/7e2a3d93-4dd3-435b-9b1a-2cd4e0c236b1" /><br>

<br>Just went for a very rough prototype here, but ideally, if fully implemented, would make the casing a lot deeper and much more sturdy. That would leave a good amount of room for the pi in back as well as anything under the base where the joystick is. 

<br><br><br>

# LAB PART 2

### Part 2

Following exploration and reflection from Part 1, complete the "looks like," "works like" and "acts like" prototypes for your design, reiterated below.



### Part E

#### Chaining Devices and Exploring Interaction Effects

For Part 2, you will design and build a fun interactive prototype using multiple inputs and outputs. This means chaining Qwiic and STEMMA QT devices (e.g., buttons, encoders, sensors, servos, displays) and/or combining with traditional breadboard prototyping (e.g., LEDs, buzzers, etc.).

**Your prototype should:**
- Combine at least two different types of input and output devices, inspired by your physical considerations from Part 1.
- Be playful, creative, and demonstrate multi-input/multi-output interaction.

**Document your system with:**
- Code for your multi-device demo
- Photos and/or video of the working prototype in action
- A simple interaction diagram or sketch showing how inputs and outputs are connected and interact
- Written reflection: What did you learn about multi-input/multi-output interaction? What was fun, surprising, or challenging?

**Questions to consider:**
- What new types of interaction become possible when you combine two or more sensors or actuators?
- How does the physical arrangement of devices (e.g., where the encoder or sensor is placed) change the user experience?
- What happens if you use one device to control or modulate another (e.g., encoder sets a threshold, sensor triggers an action)?
- How does the system feel if you swap which device is "primary" and which is "secondary"?

Try chaining different combinations and document what you discover!

See encoder_accel_servo_dashboard.py in the Lab 4 folder for an example of chaining together three devices.

**`Lab 4/encoder_accel_servo_dashboard.py`**

#### Using Multiple Qwiic Buttons: Changing I2C Address (Physically & Digitally)

If you want to use more than one Qwiic Button in your project, you must give each button a unique I2C address. There are two ways to do this:

##### 1. Physically: Soldering Address Jumpers

On the back of the Qwiic Button, you'll find four solder jumpers labeled A0, A1, A2, and A3. By bridging these with solder, you change the I2C address. Only one button on the chain can use the default address (0x6F).

**Address Table:**

| A3 | A2 | A1 | A0 | Address (hex) |
|----|----|----|----|---------------|
|  0 |  0 |  0 |  0 |    0x6F       |
|  0 |  0 |  0 |  1 |    0x6E       |
|  0 |  0 |  1 |  0 |    0x6D       |
|  0 |  0 |  1 |  1 |    0x6C       |
|  0 |  1 |  0 |  0 |    0x6B       |
|  0 |  1 |  0 |  1 |    0x6A       |
|  0 |  1 |  1 |  0 |    0x69       |
|  0 |  1 |  1 |  1 |    0x68       |
|  1 |  0 |  0 |  0 |    0x67       |
| ...| ...| ...| ... |     ...      |

For example, if you solder A0 closed (leave A1, A2, A3 open), the address becomes 0x6E.

**Soldering Tips:**
- Use a small amount of solder to bridge the pads for the jumper you want to close.
- Only one jumper needs to be closed for each address change (see table above).
- Power cycle the button after changing the jumper.

##### 2. Digitally: Using Software to Change Address

You can also change the address in software (temporarily or permanently) using the example script `qwiic_button_ex6_changeI2CAddress.py` in the Lab 4 folder. This is useful if you want to reassign addresses without soldering.

Run the script and follow the prompts:
```bash
python qwiic_button_ex6_changeI2CAddress.py
```
Enter the new address (e.g., 5B for 0x5B) when prompted. Power cycle the button after changing the address.

**Note:** The software method is less foolproof and you need to make sure to keep track of which button has which address!


##### Using Multiple Buttons in Code

After setting unique addresses, you can use multiple buttons in your script. See these example scripts in the Lab 4 folder:

- **`qwiic_1_button.py`**: Basic example for reading a single Qwiic Button (default address 0x6F). Run with:
	```bash
	python qwiic_1_button.py
	```

- **`qwiic_button_led_demo.py`**: Demonstrates using two Qwiic Buttons at different addresses (e.g., 0x6F and 0x6E) and controlling their LEDs. Button 1 toggles its own LED; Button 2 toggles both LEDs. Run with:
	```bash
	python qwiic_button_led_demo.py
	```

Here is a minimal code example for two buttons:
```python
import qwiic_button

# Default button (0x6F)
button1 = qwiic_button.QwiicButton()
# Button with A0 soldered (0x6E)
button2 = qwiic_button.QwiicButton(0x6E)

button1.begin()
button2.begin()

while True:
		if button1.is_button_pressed():
				print("Button 1 pressed!")
		if button2.is_button_pressed():
				print("Button 2 pressed!")
```

For more details, see the [Qwiic Button Hookup Guide](https://learn.sparkfun.com/tutorials/qwiic-button-hookup-guide/all#i2c-address).

---

### PCF8574 GPIO Expander: Add More Pins Over I²C

Sometimes your Pi’s header GPIO pins are already full (e.g., with a display or HAT). That’s where an I²C GPIO expander comes in handy.

We use the Adafruit PCF8574 I²C GPIO Expander, which gives you 8 extra digital pins over I²C. It’s a great way to prototype with LEDs, buttons, or other components on the breadboard without worrying about pin conflicts—similar to how Arduino users often expand their pinouts when prototyping physical interactions.

**Why is this useful?**
- You only need two wires (I²C: SDA + SCL) to unlock 8 extra GPIOs.
- It integrates smoothly with CircuitPython and Blinka.
- It allows a clean prototyping workflow when the Pi’s 40-pin header is already occupied by displays, HATs, or sensors.
- Makes breadboard setups feel more like an Arduino-style prototyping environment where it’s easy to wire up interaction elements.

**Demo Script:** `Lab 4/gpio_expander.py`

<p align="center">
    <img src="gpio_leds.gif" alt="GPIO Expander LED Demo" width="400"/>
</p>

We connected 8 LEDs (through 220 Ω resistors) to the expander and ran a little light show. The script cycles through three patterns:
- Chase (one LED at a time, left to right)
- Knight Rider (back-and-forth sweep)
- Disco (random blink chaos)

Every few runs, the script swaps to the next pattern automatically:
```bash
python gpio_expander.py
```

This is a playful way to visualize how the expander works, but the same technique applies if you wanted to prototype buttons, switches, or other interaction elements. It’s a lightweight, flexible addition to your prototyping toolkit.

---

### Servo Control with SparkFun Servo pHAT
For this lab, you will use the **SparkFun Servo pHAT** to control a micro servo (such as the Miuzei MS18 or similar 9g servo). The Servo pHAT stacks directly on top of the Adafruit Mini PiTFT (135×240) display without pin conflicts:
- The Mini PiTFT uses SPI (GPIO22, 23, 24, 25) for display and buttons ([SPI pinout](https://pinout.xyz/pinout/spi)).
- The Servo pHAT uses I²C (GPIO2 & 3) for the PCA9685 servo driver ([I2C pinout](https://pinout.xyz/pinout/i2c)).
- Since SPI and I²C are separate buses, you can use both boards together.
**⚡ Power:**
- Plug a USB-C cable into the Servo pHAT to provide enough current for the servos. The Pi itself should still be powered by its own USB-C supply. Do NOT power servos from the Pi’s 5V rail.

<p align="center">
    <img src="Servo_pHAT.gif" alt="Servo pHAT Demo" width="400"/>
</p>

**Basic Python Example:**
We provide a simple example script: `Lab 4/pi_servo_hat_test.py` (requires the `pi_servo_hat` Python package).
Run the example:
```
python pi_servo_hat_test.py
```
For more details and advanced usage, see the [official SparkFun Servo pHAT documentation](https://learn.sparkfun.com/tutorials/pi-servo-phat-v2-hookup-guide/all#resources-and-going-further).
A servo motor is a rotary actuator that allows for precise control of angular position. The position is set by the width of an electrical pulse (PWM). You can read [this Adafruit guide](https://learn.adafruit.com/adafruit-arduino-lesson-14-servo-motors/servo-motors) to learn more about how servos work.

---


### Part F

### Record

Document all the prototypes and iterations you have designed and worked on! Again, deliverables for this lab are writings, sketches, photos, and videos that show what your prototype:
* "Looks like": shows how the device should look, feel, sit, weigh, etc.
* "Works like": shows what the device can do
* "Acts like": shows how a person would interact with the device

