# Interactive Prototyping: The Clock of Pi
**NAMES OF COLLABORATORS HERE:**
<br> Karl Muller

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
[screen_clock.py](screen_clock.py)

## Part E. Now moved to Lab2 Part 2.

## Part F. Now moved to Lab2 Part 2.

## Part G. 
## Sketch and brainstorm further interactions and features you would like for your clock for Part 2.


# Prep for Part 2

1. Pick up remaining parts for kit on Thursday lab class. Check the updated [parts list inventory](partslist.md) and let the TA know if there is any part missing.
  

2. Look at and give feedback on the Part G. for at least 2 other people in the class (and get 2 people to comment on your Part G!)

# Lab 2 Part 2

## Assignment that was formerly Lab 2 Part E.
### Modify the barebones clock to make it your own

Does time have to be linear?  How do you measure a year? [In daylights? In midnights? In cups of coffee?](https://www.youtube.com/watch?v=wsj15wPpjLY)

Can you make time interactive? You can look in `screen_test.py` for examples for how to use the buttons.

Please sketch/diagram your clock idea. (Try using a [Verplank digram](http://www.billverplank.com/IxDSketchBook.pdf)!

**We strongly discourage and will reject the results of literal digital or analog clock display.**


\*\*\***A copy of your code should be in your Lab 2 Github repo.**\*\*\*


## Assignment that was formerly Part F. 
## Make a short video of your modified barebones PiClock

\*\*\***Take a video of your PiClock.**\*\*\*

After you edit and work on the scripts for Lab 2, the files should be upload back to your own GitHub repo! You can push to your personal github repo by adding the files here, commiting and pushing.

```
(venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 2 $ git add .
(venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 2 $ git commit -m 'your commit message here'
(venv) pi@raspberrypi:~/Interactive-Lab-Hub/Lab 2 $ git push
```

After that, Git will ask you to login to your GitHub account to push the updates online, you will be asked to provide your GitHub user name and password. Remember to use the "Personal Access Tokens" you set up in Part A as the password instead of your account one! Go on your GitHub repo with your laptop, you should be able to see the updated files from your Pi!


[Update your Lab Hub](pull_updates/README.md) to get the latest content and requirements for Part 2.

Modify the code from last week's lab to make a new visual interface for your new clock. You may [extend the Pi](Extending%20the%20Pi.md) by adding sensors or buttons, but this is not required.

As always, make sure you document contributions and ideas from others explicitly in your writeup.

You are permitted (but not required) to work in groups and share a turn in; you are expected to make equal contribution on any group work you do, and N people's group project should look like N times the work of a single person's lab. What each person did should be explicitly documented. Make sure the page for the group turn in is linked to your Interactive Lab Hub page. 


