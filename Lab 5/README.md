# Observant Systems

**NAMES OF COLLABORATORS HERE:** <br>
**Karl Muller**

For lab this week, we focus on creating interactive systems that can detect and respond to events or stimuli in the environment of the Pi, like the Boat Detector we mentioned in lecture. 
Your **observant device** could, for example, count items, find objects, recognize an event or continuously monitor a room.

This lab will help you think through the design of observant systems, particularly corner cases that the algorithms need to be aware of.

### Deliverables for this lab are:
1. Show pictures, videos of the "sense-making" algorithms you tried.
1. Show a video of how you embed one of these algorithms into your observant system.
1. Test, characterize your interactive device. Show faults in the detection and how the system handled it.

## Overview
Building upon the paper-airplane metaphor (we're understanding the material of machine learning for design), here are the four sections of the lab activity:

A) [Play](#part-a)

B) [Fold](#part-b)

C) [Flight test](#part-c)

D) [Reflect](#part-d)

---

### Part A: Play with different sense-making algorithms.

#### \*\*Pytorch for object recognition\*\*
Ran and tested `infer.py`

#### \*\*MediaPipe\*\*
Ran and tested `hand_pose.py` with pecentage control and quiet coyote
<br>Testing Vid: [Hand Pose Test](https://drive.google.com/file/d/10it2BaKFEcAhRogGAz5EzPjarISGGZV3/view?usp=sharing)
<br>Could use this for a variety of reason, most importantly recognizing gestures, especially ASL. An interaction with this could involve translating hand positions to the correct letter and displaying that on the mini screen. 

#### \*\*Teachable Machines\*\*

Made a simple model testing between waving Hi with dominant (right) and non-dominant (left) hand <br>
[Labels](testing_teachable_machines/labels.txt) <br>
[Model](testing_teachable_machines/model_unquant.tflite) <br>

<img width="1286" height="685" alt="Screenshot 2025-11-09 at 7 20 56 PM" src="https://github.com/user-attachments/assets/879f03dc-3a84-4489-8111-57aab55b96da" />
<img width="1336" height="720" alt="Screenshot 2025-11-09 at 7 21 12 PM" src="https://github.com/user-attachments/assets/13c0a0ec-1982-4932-a7e4-dc47f0739c7a" />
This method is really useful for when you need something over just gesture recognition and could be a little harder/abstract to recognize over simple gestures.

### Part B: Construct a simple interaction.

**\*\*\*Describe and detail the interaction, as well as your experimentation here.\*\*\*** <br>
Interaction would involve making sure your posture is correct. Using Teachable Machines, you would be able to split between sitting upright, leaning slightly, or slouching. It would display a green check, warning, or red x, respecitvely, on the pi miniTFT screen depending on the posture class. After 10 seconds it can even play a sound telling you to correct posture. <br>
Teachable Machine: <br>
[Posture Teachable Machine Files](posture_teachable_machine/model.json) <br>
<img height="400" alt="image" src="https://github.com/user-attachments/assets/152e2264-0089-434a-b336-dfab2d6029a1" />
<img height="400" alt="image" src="https://github.com/user-attachments/assets/62141135-3f41-46ca-9007-8abd739c1da0" />
<img height="400" alt="image" src="https://github.com/user-attachments/assets/2648d239-f232-4918-b293-6dc63074eca7" />


### Part C: Test the interaction prototype

1. When does it what it is supposed to do?
   - works well in lit up rooms with direct upper body view and correctly identifies upright vs slouched positions when facing the camera
2. When does it fail?
   - if the background is noisy, father from camera, out of the frame of the camera, if seated at a different angle
3. When it fails, why does it fail?
   - Not critical, user just might face posture issues if not classified properly over time.
4. Based on the behavior you have seen, what other scenarios could cause problems?
   - Other scenarios would be obstructions like your arms being crossed or objecs blocking the camera, multiple people in the frame, interference in the background, and shifts in lighting.

**\*\*\*Think about someone using the system. Describe how you think this will work.\*\*\***
1. Are they aware of the uncertainties in the system?
   - In some ways the user would be, the system provides visible feedback so the user should be able to show inconsistences in real time. But if the misclassification is obvious or disruptive, the user might not recognize the false positives or negatives
2. How bad would they be impacted by a miss classification?
   -  The impact would be pretty low, the system might falsely prompt the user to sit up when they are already in good posture, which might be sligthly annoying. It wouldn't cause any harm or block interactions or anything else.
3. How could change your interactive system to address this?
   - A couple ways to fix this: Require posture classification to occur only after classifying it an N number of times (like 5 times classifying slouching during 10 second interval), let the user set their baseline for good posture first, and maybe also display system's confidence in classifying your posture
4. Are there optimizations you can try to do on your sense-making algorithm.
   - The best optimization would be to make each classification of poor posture vs good posture user & their environment specific

### Part D
### Characterize your own Observant system

Now that you have experimented with one or more of these sense-making systems **characterize their behavior**.
During the lecture, we mentioned questions to help characterize a material:
* **What can you use X for?**
   * Encouraging good posture
* **What is a good environment for X?**
   * At a desk with a seated user with consistent lighting
* **What is a bad environment for X?**
   * Dim lighting, standing/out of frame/differnt angled users, cluttered background
* **When will X break?**
   * If user walks away or another person enters frame
* **When it breaks how will X break?**
   * Will misclassify posture or stop detecting a person  
* **What are other properties/behaviors of X?**
   * It could also end up measuring time seating correctly/incorrectly
* **How does X feel?**
   * Like a quiet posture coach sitting by you

**\*\*\*Include a short video demonstrating the answers to these questions.\*\*\***

### Part 2.

Following exploration and reflection from Part 1, finish building your interactive system, and demonstrate it in use with a video.

**\*\*\*Include a short video demonstrating the finished result.\*\*\***
