# Distributed Interaction

\*\***NAMES OF COLLABORATORS HERE**\*\*
<br> **Karl Muller (km2262)**
<br> **Om Kamath (ok97)**

---

## Part A: MQTT Messaging

**Testing Listener**
<img width="1226" height="94" alt="Pasted Graphic" src="https://github.com/user-attachments/assets/744c965e-ccaa-4dc1-a3df-b303d2b2ef94" />

**Testing Publisher**
<img width="1425" height="19" alt="Pasted Graphic 1" src="https://github.com/user-attachments/assets/c5eea771-2870-4fb5-b5a8-cbf98b7a42d6" />

<img width="1788" height="708" alt="Pasted Graphic 2" src="https://github.com/user-attachments/assets/bc9068a7-25b0-4844-89f4-e255c4460ddc" />


**Idea**
- Morse Code communicator with multiple pi to one server

---

## Part B: Collaborative Pixel Grid

**📸 Include: Screenshot of grid + photo of your Pi setup** <br>

<img height="400" alt="image" src="https://github.com/user-attachments/assets/c2293121-8532-407a-8040-fa152fa8a92e" />


---

**1. Project Description** <br>
**What does it do? Why interesting? User experience?** <br>
We built a distributed system using MQTT where multiple Raspberry Pi devices with Qwiic buttons transmit Morse code (dots and dashes) to a shared MQTT broker. A central Flask server with a web dashboard listens to the topic and displays decoded letters, full messages, and transmission history for each Pi in real time.

This project is interesting because it transforms simple tactile inputs (button presses) into distributed, real time communication using networked microcontrollers. The user presses the button for short (dot) or long (dash) durations. After a pause, the system automatically decodes the Morse sequence and displays the letter. Each Pi has its own message stream, making the experience collaborative and transparent.

**2. Architecture Diagram**
- Hardware, connections, data flow
- Label input/computation/output

**3. Build Documentation**

**Devices:**<br>
	•	2 or 3 (as many can connect as they want) rpi5 with qwiic button  connected to GPIO header
	•	Laptop running Flask + MQTT Subscriber Dashboard

**MQTT Topic:**<br>
- IDD/lab6/morse/coolguys/symbol
- Payload: `{ "symbol": ".", "device_id": "karl" }` or `{ "symbol": "-", "device_id": "om" }`

**Code Snippets:**<br>
Publisher function [src/pi/qwiic_button_publisher.py](src/pi/qwiic_button_publisher.py): <br>
```python
def publish_message(client, morse_symbols):
    """Publish morse symbols to the MQTT broker"""
    global message_count
    message_count += 1
    
    payload = json.dumps({
        'symbol': morse_symbols,
        'device_id': 'om',
        'timestamp': time.time(),
        'count': message_count
    })
    
    result = client.publish(MQTT_TOPIC, payload)
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"Published symbols: {morse_symbols}")
    else:
        print(f"Publish failed with code {result.rc}")
    
    return result
```
<br>Where `morse_symbols` were either a dot or dash of current symbol sent from qwiic button. Dot determine by button holding threshold [src/pi/qwiic_button_publisher.py](src/pi/qwiic_button_publisher.py): <br>
```python
...
    if press_duration < DOT_THRESHOLD:
        current_morse += '.'
        print('.', end='', flush=True)
    else:
        current_morse += '-'
        print('-', end='', flush=True)
...
```
<br> Server would listen for the topic, extract the symbol [src/server/app.py](src/server/app.py):
```python
    def ingest_symbol(self, payload: Dict[str, object]) -> None:
        symbol = payload.get("symbol")
        if symbol not in VALID_SYMBOLS:
            logger.debug("Ignoring payload without symbol: %s", payload)
            return
        ...

```
<br> Server would then try to string together symbols based on timing intervals, message would then be decoded and displayed [src/server/app.py](src/server/app.py): 
```python
    def finalize_letter(self, event_time: datetime):
        pattern = "".join(item["symbol"] for item in self.current_symbols)
        if not pattern:
            return None
        letter = decode_morse(pattern)
        entry = {
            "type": "letter",
            "letter": letter,
            "pattern": pattern,
            "timestamp": event_time.isoformat(),
        }
        self.decoded_message += letter
        ...
```
<br> Morse code decoder function [src/server/morse.py](src/server/morse.py):
```python
MORSE_CODE: Dict[str, str] = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    ".-.-.-": ".",
    "--..--": ",",
    "..--..": "?",
    ".----.": "'",
    "-.-.--": "!",
    "-..-.": "/",
    "-.--.": "(",
    "-.--.-": ")",
    ".-...": "&",
    "---...": ":",
    "-.-.-.": ";",
    "-...-": "=",
    ".-.-.": "+",
    "-....-": "-",
    "..--.-": "_",
    ".-..-.": '"',
    "...-..-": "$",
    ".--.-.": "@",
}

VALID_SYMBOLS = {".", "-"}


def decode_morse(pattern: str) -> str:
    """Return the decoded character for a dot/dash pattern (or '?' if unknown)."""
    cleaned = (pattern or "").strip()
    if not cleaned:
        return ""
    return MORSE_CODE.get(cleaned, "?")
```

**4. User Testing**
- **Test with 2+ people NOT on your team**
- Photos/video of use
- What did they think before trying?
- What surprised them?
- What would they change?

**5. Reflection**
- What worked well?
- Challenges with distributed interaction?
- How did sensor events work?
- What would you improve?

---

