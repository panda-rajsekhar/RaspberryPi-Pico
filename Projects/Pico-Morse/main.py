from machine import Pin, I2C
from time import ticks_ms, ticks_diff, sleep_ms
from i2c_lcd import I2cLcd

# ---------- Configuration ----------
DOT_PIN   = 14
DASH_PIN  = 15
I2C_SDA   = 0
I2C_SCL   = 1
LCD_ROWS  = 2          # change to 4 if you have 20x4
LCD_COLS  = 16

# Timing (ms) – adjust to your typing speed
LETTER_TIMEOUT = 800   # silence → finish letter
WORD_TIMEOUT   = 1800  # longer silence → add space
DEBOUNCE_MS    = 40

# ---------- Morse dictionary ----------
MORSE = {
    '.-': 'A',   '-...': 'B', '-.-.': 'C', '-..': 'D',  '.': 'E',
    '..-.': 'F', '--.': 'G',  '....': 'H',  '..': 'I',  '.---': 'J',
    '-.-': 'K',  '.-..': 'L', '--': 'M',    '-.': 'N',  '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R',   '...': 'S', '-': 'T',
    '..-': 'U',  '...-': 'V', '.--': 'W',   '-..-': 'X', '-.--': 'Y',
    '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
    '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9',
    '.-.-.-': '.', '--..--': ',', '..--..': '?', '-...-': '=',
    '-.--.': '(', '-.--.-': ')', '.-...': '&', '---...': ':',
    '-.-.--': '!', '-....-': '-', '..--.-': '_', '.-..-.': '"',
    '...-..-': '$', '.--.-.': '@',
}

# ---------- Hardware setup ----------
i2c = I2C(0, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=400_000)
addr = i2c.scan()[0]
lcd = I2cLcd(i2c, addr, LCD_ROWS, LCD_COLS)

dot_btn  = Pin(DOT_PIN,  Pin.IN, Pin.PULL_UP)
dash_btn = Pin(DASH_PIN, Pin.IN, Pin.PULL_UP)

# ---------- State ----------
current_morse = ""
message = ""          # decoded history
last_input_time = 0
last_press_time = 0

def update_display():
    lcd.clear()
    # Line 1: current Morse being typed + preview letter
    preview = MORSE.get(current_morse, "?") if current_morse else " "
    line1 = (current_morse + " → " + preview)[:LCD_COLS]
    lcd.move_to(0, 0)
    lcd.putstr(line1)

    # Line 2: message history (scrolls from the right if long)
    if len(message) <= LCD_COLS:
        lcd.move_to(0, 1)
        lcd.putstr(message)
    else:
        # show the last LCD_COLS characters
        lcd.move_to(0, 1)
        lcd.putstr(message[-LCD_COLS:])

def add_symbol(symbol):
    global current_morse, last_input_time
    current_morse += symbol
    last_input_time = ticks_ms()
    update_display()

def finish_letter():
    global current_morse, message, last_input_time
    if not current_morse:
        return
    letter = MORSE.get(current_morse, "?")
    message += letter
    current_morse = ""
    last_input_time = ticks_ms()
    update_display()

def add_space():
    global message, last_input_time
    if message and not message.endswith(" "):
        message += " "
        last_input_time = ticks_ms()
        update_display()

# ---------- Startup ----------
lcd.clear()
lcd.putstr("Morse Decoder")
lcd.move_to(0, 1)
lcd.putstr("Dot  Dash")
sleep_ms(1500)
update_display()

# ---------- Main loop ----------
while True:
    now = ticks_ms()

    # Debounced button reading
    if ticks_diff(now, last_press_time) > DEBOUNCE_MS:
        if dot_btn.value() == 0:
            add_symbol(".")
            last_press_time = now
            while dot_btn.value() == 0:   # wait for release
                sleep_ms(10)
        elif dash_btn.value() == 0:
            add_symbol("-")
            last_press_time = now
            while dash_btn.value() == 0:
                sleep_ms(10)

    # Timeouts
    silence = ticks_diff(now, last_input_time)

    if current_morse and silence > LETTER_TIMEOUT:
        finish_letter()

    if silence > WORD_TIMEOUT:
        add_space()

    sleep_ms(5)   # light CPU load

