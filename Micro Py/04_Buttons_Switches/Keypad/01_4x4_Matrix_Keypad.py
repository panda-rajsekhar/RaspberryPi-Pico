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

# Turn every column OFF initially
for col in cols:
    col.value(0)

# Key Layout
keys = [
    ['*', '0', '#', 'D'],
    ['7', '8', '9', 'C'],
    ['4', '5', '6', 'B'],
    ['1', '2', '3', 'A']
]

# -----------------------------
# Main Loop
# -----------------------------

last_key = None

while True:

    detected = None

    for c in range(4):

        # Activate one column
        cols[c].value(1)

        for r in range(4):

            if rows[r].value():

                detected = keys[r][c]

        cols[c].value(0)

    if detected != last_key:

        if detected is not None:
            print("Key Pressed:", detected)

        last_key = detected

    sleep_ms(20)

