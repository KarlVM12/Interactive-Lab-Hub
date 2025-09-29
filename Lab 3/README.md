# Chatterboxes
**Karl Muller (km2262)**

## Prep for Part 1: Get the Latest Content and Pick up Additional Parts ✅

\*\***Write your own shell file to use your favorite of these TTS engines to have your Pi greet you by name.**\*\*
<br>Script here: [Google TTS Personal Greeting](./src/GoogleTTS_personal_greeting.sh)


\*\***Write your own shell file that verbally asks for a numerical based input (such as a phone number, zipcode, number of pets, etc) and records the answer the respondent provides.**\*\*
<br>Script here: [Ask & Store User's Zip Code](./src/ask_number.sh)


\*\***Try creating a simple voice interaction that combines speech recognition, Ollama processing, and text-to-speech output. Document what you built and how users responded to it.**\*\*
<br>Script here: [Simple Ollama Back & Forth](./src/ollama_simple_interaction/ollama_voice_pipeline.py)
<br> This is a back and forth between phi3 mini and the user. Ollama starts off with a spoken unique greeting and then the user can talk back, have it filtered through STT with vosk, then sent through to phi3 to form a response, phi3 streams back over its response which is spoken back to the user using piper TTS. I opted to have the model be hosted on my laptop to have much faster response times when communicating with phi3. But given this method, i could also then use a multitude of smarter smaller models as well like llama3.2:3b or qwen3:1.7b/4b.
<br> Users responded way better when ha ving the model hosted on my laptop over just being on the raspberry as it was much faster. Some did express some concern about the answers Phi3 would give. Oftentimes it would contradict it self in the next sentence or just not really be too sure what it was talking about, but for SLMs this tends to be standard. Using a smarter smaller model like llama3.2:3b produced much more positive feedback in terms of knowledge and ability to hold conversation. The microphone capture was clunky at first which led to user responses being cut off and making the model more confused. When i relaxed the constraints on the mic capture, user acceptance to their prompt being answer in a satisfactory way was more positive as well. Even though Siri has existed and is much more advanced than this, people i used this with felt that this was something new or even 'creepy', although this could have been perpetuated by the fact that the TTS is also a little uncanny.

### Storyboard

Storyboard and/or use a Verplank diagram to design a speech-enabled device. (Stuck? Make a device that talks for dogs. If that is too stupid, find an application that is better than that.) 
<br>\*\***Post your storyboard and diagram here.**\*\*
<br> <img width="450" height="604" alt="storyboard_1_care_refrusal" src="https://github.com/user-attachments/assets/c8bcec3c-e9a9-49ca-ad10-5d510888a5a2" /> <p>**Storyboard 1: Plant refuses care; informs user of current care**</p>
<br> <img width="436" height="517" alt="storyboard_2_request_care" src="https://github.com/user-attachments/assets/8786be13-024c-401e-864f-df57d5cf2195" /> <p>**Storyboard 2: Plant requests care; informs first user of current need**</p>
<br> <img width="1221" height="856" alt="verplank_plant_pal" src="https://github.com/user-attachments/assets/f4fbfd39-c17f-4089-a718-d2395e41ca7a" /> <p>**Verplankl Diagram: Plant pal**</p>


Write out what you imagine the dialogue to be. Use cards, post-its, or whatever method helps you develop alternatives or group responses. 
<br>\*\***Please describe and document your process.**\*\*
<br>

### Acting out the dialogue

Find a partner, and *without sharing the script with your partner* try out the dialogue you've designed, where you (as the device designer) act as the device you are designing.  Please record this interaction (for example, using Zoom's record feature).
<br>\*\***Describe if the dialogue seemed different than what you imagined when it was acted out, and how.**\*\*
<br>


### Wizarding with the Pi (OPTIONAL)
In the [demo directory](./demo), you will find an example Wizard of Oz project. In that project, you can see how audio and sensor data is streamed from the Pi to a wizard controller that runs in the browser.  You may use this demo code as a template. By running the `app.py` script, you can see how audio and sensor data (Adafruit MPU-6050 6-DoF Accel and Gyro Sensor) is streamed from the Pi to a wizard controller that runs in the browser `http://<YouPiIPAddress>:5000`. You can control what the system says from the controller as well!
\*\*** [OPTIONAL] Describe if the dialogue seemed different than what you imagined, or when acted out, when it was wizarded, and how.**\*\*

# Lab 3 Part 2

For Part 2, you will redesign the interaction with the speech-enabled device using the data collected, as well as feedback from part 1.

## Prep for Part 2

1. What are concrete things that could use improvement in the design of your device? For example: wording, timing, anticipation of misunderstandings...
2. What are other modes of interaction _beyond speech_ that you might also use to clarify how to interact?
3. Make a new storyboard, diagram and/or script based on these reflections.

## Prototype your system

The system should:
* use the Raspberry Pi 
* use one or more sensors
* require participants to speak to it. 

*Document how the system works*

*Include videos or screencaptures of both the system and the controller.*

<details>
  <summary><strong>Submission Cleanup Reminder (Click to Expand)</strong></summary>
  
  **Before submitting your README.md:**
  - This readme.md file has a lot of extra text for guidance.
  - Remove all instructional text and example prompts from this file.
  - You may either delete these sections or use the toggle/hide feature in VS Code to collapse them for a cleaner look.
  - Your final submission should be neat, focused on your own work, and easy to read for grading.
  
  This helps ensure your README.md is clear professional and uniquely yours!
</details>

## Test the system
Try to get at least two people to interact with your system. (Ideally, you would inform them that there is a wizard _after_ the interaction, but we recognize that can be hard.)

Answer the following:

### What worked well about the system and what didn't?
\*\**your answer here*\*\*

### What worked well about the controller and what didn't?

\*\**your answer here*\*\*

### What lessons can you take away from the WoZ interactions for designing a more autonomous version of the system?

\*\**your answer here*\*\*


### How could you use your system to create a dataset of interaction? What other sensing modalities would make sense to capture?

\*\**your answer here*\*\*







