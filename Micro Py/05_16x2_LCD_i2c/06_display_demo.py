from machine import Pin, I2C
from i2c_lcd import I2cLcd
import time

# ----------------------------
# Initialize LCD
# ----------------------------
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)

lcd = I2cLcd(i2c, 0x27, 2, 16)

# ----------------------------
# Display Control Demo
# ----------------------------

lcd.clear()
lcd.putstr("Display Demo")
time.sleep(2)

# Cursor ON
lcd.show_cursor()
lcd.move_to(12, 0)
time.sleep(2)

# Cursor OFF
lcd.hide_cursor()
time.sleep(2)

# Cursor Blink ON
lcd.blink_cursor_on()
time.sleep(3)

# Cursor Blink OFF
lcd.blink_cursor_off()
time.sleep(2)

# Display OFF
lcd.display_off()
time.sleep(2)

# Display ON
lcd.display_on()
time.sleep(2)

# Backlight OFF
lcd.backlight_off()
time.sleep(2)

# Backlight ON
lcd.backlight_on()
time.sleep(2)

# Finish
lcd.clear()
lcd.putstr("Demo Complete!")
