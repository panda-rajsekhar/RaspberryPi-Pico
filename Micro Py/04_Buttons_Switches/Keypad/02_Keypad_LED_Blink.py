from machine import Pin
from time import sleep_ms

# -----------------------------
# GPIO Configuration
# -----------------------------

rows = [
    Pin(6, Pin.IN, Pin.PULL_DOWN),   # R1
    Pin(7, Pin.IN, Pin.PULL_DOWN),   # R2
    Pin(8, Pin.IN, Pin.PULL_DOWN),   # R3
    Pin(9, Pin.IN, Pin.PULL_DOWN)    # R4
]

cols = [
    Pin(5, Pin.OUT),    # C4
    Pin(4, Pin.OUT),    # C3
    Pin(3, Pin.OUT),    # C2
    Pin(2, Pin.OUT)     # C1
]

for col in cols:
    col.value(0)

keys = [
    ['*', '0', '#', 'D'],
    ['7', '8', '9', 'C'],
    ['4', '5', '6', 'B'],
    ['1', '2', '3', 'A']
]

# Onboard LED
led = Pin("LED", Pin.OUT)

last_key = None

while True:

    detected = None

    # Scan keypad
    for c in range(4):
        cols[c].value(1)

        for r in range(4):
            if rows[r].value():
                detected = keys[r][c]

        cols[c].value(0)

    # Process only new key press
    if detected != last_key:

        if detected is not None:

            print("Key Pressed:", detected)

            # Blink only for numeric keys
            if detected.isdigit():

                count = int(detected)

                if count == 0:
                    count = 10      # Optional: make 0 blink 10 times

                for _ in range(count):
                    led.on()
                    sleep_ms(200)
                    led.off()
                    sleep_ms(200)

        last_key = detected

    sleep_ms(20)
