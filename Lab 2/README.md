# Interactive Prototyping: The Clock of Pi
**NAMES OF COLLABORATORS HERE:**
<br> Karl Muller (ChatGPT assisted with some of the math code to get my clock to display and rotate properly)

## Lab Description
Does it feel like time is moving strangely during this semester? <br>
For our first Pi project, we will pay homage to the [timekeeping devices of old](https://en.wikipedia.org/wiki/History_of_timekeeping_devices) by making simple clocks. <br>
It is worth spending a little time thinking about how you mark time, and what would be useful in a clock of your own design. <br>

## Prep
Lab Prep is extra long this week. Make sure to start this early for lab on Thursday. ✅
<br>
### 1. Set up your Lab 2 Github ✅
Before the start of lab Thursday, ensure you have the latest lab content by updating your forked repository. <br>
**📖 [Follow the step-by-step guide for safely updating your fork](pull_updates/README.md)** <br>
This guide covers how to pull updates without overwriting your completed work, handle merge conflicts, and recover if something goes wrong. <br>
<br>
### 2. Get Kit and Inventory Parts ✅
Prior to the lab session on Thursday, taken inventory of the kit parts that you have, and note anything that is missing: <br>
***Update your [parts list inventory](partslist.md)*** <br>
<br>
### 3. Prepare your Pi for lab this week ✅
[Follow these instructions](prep.md) to download and burn the image for your Raspberry Pi before lab Thursday.

## Overview
For this assignment, you are going to <br>
A) [Connect to your Pi](#part-a)  ✅ <br>
B) [Try out cli_clock.py](#part-b) ✅ <br>
C) [Set up your RGB display](#part-c) ✅ <br>
D) [Try out clock_display_demo](#part-d) ✅ <br>
E) [Modify the code to make the display your own](#part-e) <br>
F) [Make a short video of your modified barebones PiClock](#part-f) <br>
G) [Sketch and brainstorm further interactions and features you would like for your clock for Part 2.](#part-g) <br>

## The Report
This readme.md page in your own repository should be edited to include the work you have done. You can delete everything but the headers and the sections between the \*\*\***stars**\*\*\*. Write the answers to the questions under the starred sentences. Include any material that explains what you did in this lab hub folder, and link it in the readme. <br>
Labs are due on Mondays. Make sure this page is linked to on your main class hub page. <br>

## Part A. ✅
### Connect to your Pi
Just like you did in the lab prep, ssh on to your pi. Once you get there, create a Python environment (named venv) by typing the following commands.

## Part B. ✅
### Try out the Command Line Clock ✅
Clone your own lab-hub repo for this assignment to your Pi and change the directory to Lab 2 folder (remember to replace the following command line with your own GitHub ID):

## Part C. ✅
### Set up your RGB Display ✅
We have asked you to equip the [Adafruit MiniPiTFT](https://www.adafruit.com/product/4393) on your Pi in the Lab 2 prep already. Here, we will introduce you to the MiniPiTFT and Python scripts on the Pi with more details.

### Hardware (you have already done this in the prep)

From your kit take out the display and the [Raspberry Pi 5](https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.raspberrypi.com%2Fproducts%2Fraspberry-pi-5%2F&psig=AOvVaw330s4wIQWfHou2Vk3-0jUN&ust=1757611779758000&source=images&cd=vfe&opi=89978449&ved=0CBMQjRxqFwoTCPi1-5_czo8DFQAAAAAdAAAAABAE) <br>
Line up the screen and press it on the headers. The hole in the screen should match up with the hole on the raspberry pi.

### Testing your Screen ✅

The display uses a communication protocol called [SPI](https://www.circuitbasics.com/basics-of-the-spi-communication-protocol/) to speak with the raspberry pi. We won't go in depth in this course over how SPI works. The port on the bottom of the display connects to the SDA and SCL pins used for the I2C communication protocol which we will cover later. GPIO (General Purpose Input/Output) pins 23 and 24 are connected to the two buttons on the left. GPIO 22 controls the display backlight. <br>
To show you the IP and Mac address of the Pi to allow connecting remotely we created a service that launches a python script that runs on boot. For the following steps stop the service by typing ``` sudo systemctl stop piscreen.service --now```. Othwerise two scripts will try to use the screen at once. You may start it again by typing ``` sudo systemctl start piscreen.service --now```

#### Displaying Info with Texts ✅
You can look in `screen_boot_script.py` for how to display text on the screen!

#### Displaying an image ✅
You can look in `image.py` for an example of how to display an image on the screen. Can you make it switch to another image when you push one of the buttons?


## Part D. ✅
### Set up the Display Clock Demo ✅
Work on `screen_clock.py`, try to show the time by filling in the while loop (at the bottom of the script where we noted "TODO" for you). You can use the code in `cli_clock.py` and `stats.py` to figure this out. <br>
\*\*\***Testing working basic analog clock**\*\*\* <br>
Code: [screen_clock.py](screen_clock.py) <br>
<img width="611" height="412" alt="image" src="https://github.com/user-attachments/assets/c7b2af33-1039-45d8-8e96-873ae8c13fdf" /> <br>

## Sketch and brainstorm further interactions and features you would like for your clock for Part 2.
\*\*\***Initial Sketch Idea: Flower Time!**\*\*\*<br>
<img width="515" height="573" alt="image" src="https://github.com/user-attachments/assets/528dd747-d1d0-4644-9062-a7a8fee2a240" />

# Lab 2 Part 2

## Assignment that was formerly Lab 2 Part E.
### Modify the barebones clock to make it your own
#### Sketch & Verplank Diagram
\*\*\***A copy of your code should be in your Lab 2 Github repo.**\*\*\* <br>
Sketch: <br><img width="447" height="351" alt="image" src="https://github.com/user-attachments/assets/452735d3-8d33-44a9-875d-78d714e7080f" /> <br>
Verplank Diagram: <img width="1230" height="886" alt="image" src="https://github.com/user-attachments/assets/618ba9a9-14ea-475e-a6a3-8bb0cd22c182" /> <br>
<b>The purpose of this 'Flower Time' version of a clock is it growing over time to represent the passing of time by gaining leaves, petals, and the bee constantly flying around. Time passes as the flower grows. With the interaction added, we can add petals to the flower to accelerate its growth (completing the day faster) or we can make the flower lose its petals and leaves (turning time back).</b>
<br><br>All Code available here: [clock_code folder](clock_code) <br>
- Final version of code: [Custom clock w/ buttons](clock_code/custom_clock_buttons.py) 

## Assignment that was formerly Part F. 
## Make a short video of your modified barebones PiClock

\*\*\***Take a video of your PiClock.**\*\*\* <br>
### Photos:
<figcaption><b>Initial working code of Flower Time (contrast of screen made pictures hard):</b></figcaption><br><img width="532" height="468" alt="image" src="https://github.com/user-attachments/assets/29c14477-6999-459c-a950-edf6e61446c5" />  <br>

<br><figcaption><b>Final design of Flower Time showing 6:42pm (6 leaves have grown, 8.5 petals grown, small bee flying around!): </b></figcaption> <br> <img width="587" height="600" alt="image" src="https://github.com/user-attachments/assets/409499b0-054c-4c09-8e7d-603ffabf9969" /> <br> 


### Videos:
<b>[Basic Flower Time Functionality (6:41pm -> 6:42pm)](Videos/basic_functionality.mov)</b> <br>
<b>[Bees Adds Petal (6:44pm -> 6:45pm)](Videos/bee_adds_petal.mov)</b> <br>
<b>[Bee Adds New Leaf (6:59pm -> 7:00pm)](Videos/new_leaf.mov)</b> <br>
<b>[User Interaction causes flower to grow faster and gain petals/leaves (+5 minutes a button press) or causes flower to lose petals/leaves (-5 minutes a button press)](Videos/add_remove_petals.mov)</b> <br>


