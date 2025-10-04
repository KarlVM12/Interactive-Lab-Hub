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
<br> <img width="1221" height="856" alt="verplank_plant_pal" src="https://github.com/user-attachments/assets/f4fbfd39-c17f-4089-a718-d2395e41ca7a" /> <p>**Verplank Diagram: Plant pal**</p>


<br>Write out what you imagine the dialogue to be. Use cards, post-its, or whatever method helps you develop alternatives or group responses. 
<br>\*\***Please describe and document your process.**\*\*
<br> Starting with the goal here, its to kind of create an direct way to receive updates about the health of your plants, but the use cases can extend to just being able to take to and have conversations with your plant. This way you can feel more involved in taking care of your plant. The process i used to create some possible dialogue snippets were just writing down brief ideas about possible user intents and use cases on note cards, and saying the first thing i would think the plant pal would say come to my mind: <br>
1. Greeting
    - User: Hello !
    - Plant Pal: Hi ! Sun is out today and I'm thriving !
2. Small Talk/Fun Facts
    - User: Tell me something interesting
    - Plant Pal: A cool plant fact about Sunflowers are they will always grow with their flower pointing towards the sun !
3. Caring for Plant
    - User: Do you need more water?
    - Plant Pal: I was just watered yesterday, I am doing ok !
4. Emotional Support
    - User: I'm stressed, what should I do?
    - Plant Pal: Take a relaxing walk in the sun and the through the forest, that usually helps you clear your mind !
5. Ending interaction
    - User: Good night plant !
    - Plant Pal: Night ! Can't wait for the morning !

### Acting out the dialogue

Find a partner, and *without sharing the script with your partner* try out the dialogue you've designed, where you (as the device designer) act as the device you are designing.  Please record this interaction (for example, using Zoom's record feature).
<br>\*\***Describe if the dialogue seemed different than what you imagined when it was acted out, and how.**\*\*
<br> The dialogue definitely seemed different when I performed and acted it out versus how i guess I thought it would be. I think the difference though lies in a human vs a device performing the diaglogue. I think we are attuned to allowing devices/AI to take on a different tone. So while for me it felt a little unnatural to respond to someone else with, when it comes to a type of ai buddy like this, i think we typically expect them to act more like this I guess 'unnatural' way because that is how we differentiate it as a species to a difference between pure human interaction. The goal with Plant Pal is also personification which lends itself to a sort of exaggeration as well, which is why the dialogue i planned out felt over the top when I said it human to human, but if you were a human 'talking' to a plant, I assume one would like to think of a plant as being this sort of always upbeat force, making the tone and flow of dialogue fit better under those circumstances. <br>


# Lab 3 Part 2

For Part 2, you will redesign the interaction with the speech-enabled device using the data collected, as well as feedback from part 1.

## Prep for Part 2

1. **\*\*What are concrete things that could use improvement in the design of your device? For example: wording, timing, anticipation of misunderstandings..\*\*** <br>
A couple things that could use improvement that I discovered during the initial acting out of the dialogue:
    - Speech Recognition & timing: The mic often cuts off early or misses part of the user's input, which made the model's responses seem confused. Also trying to play back an immediate sound instead of waiting for the model to generate a response could help a lot in the anxiety of wondering if you were heard or not. Like just immediately responding with "Okay!" or something along those lines
    - Model: phi3 gave weird or contradictory answers. A smarter model like llama3.2 performed a lot better
    - Tone & language: what felt unnatural to say as a human, could still come off as strange to hear from TTS, even if more expected, so improving the personality there is important

2. **\*\*What are other modes of interaction _beyond speech_ that you might also use to clarify how to interact?\*\*** <br>
I was only relying on voice before, so i could make it more interactive a couple of ways:
    - Adding a button thats initiates the conversation
    - Adding an aspect of light to show different states of listening, thinking and responding
    - Using the diplsay to show an emoji or face to convey different states of what the plant pal is expressing

3. **\*\*Make a new storyboard, diagram and/or script based on these reflections.\*\*** <br>
New dialogue script: <br>
&nbsp;&nbsp;&nbsp;&nbsp;**_Asking for water:_**
    - User: _presses button to wake up plant pal_
    - _screen turns blue on wake up to indicate it is listening_
    - Plant: "Hello! What would you like to know?"
    - User: "Do you need water?" 
    - _screen turns pulses from blue to white to indicate it is thinking_
    - _in a perfect world, pi would be attached to a moisture sensor that could tell the water level_
        - if dry, Plant: "I'm actually feeling pretty thirsty, could i get some more water?"
            - User: "Let me grab some water", _user waters plant_
            - Plant: "Thanks, I needed that!"
        - if not dry, Plant: "Nope! I'm doing quite alright!"
            - User: "Awesome!"
            - Plant: "You got it!"
    - _plant pal would go idle and screen turn a soft yellow to indicate its idle_

## Prototype your system

The system should:
* use the Raspberry Pi 
* use one or more sensors
* require participants to speak to it. 

*Document how the system works*

*Include videos or screencaptures of both the system and the controller.*

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











