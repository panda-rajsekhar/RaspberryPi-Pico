from machine import Pin, I2C
import time
import ds1302
from i2c_lcd import I2cLcd

# =========================
# Hardware
# =========================
rtc = ds1302.DS1302(Pin(10), Pin(11), Pin(12))   # CLK, DAT, RST

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)  
lcd = I2cLcd(i2c, 0x27, 2, 16)

DAYS = ("SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT")

lcd.clear()

last_date = None
last_time = None

while True:
    # Unpack once, ignore seconds (not displayed)
    year, month, day, weekday, hour, minute, _ = rtc.date_time()

    # Build display strings (centered)
    date_str = f"{DAYS[weekday-1]} {day:02d}/{month:02d}/{year:04d}".center(16)
    time_str = f"{hour:02d}:{minute:02d}".center(16)

    # Update LCD only when content actually changes
    if date_str != last_date:
        lcd.move_to(0, 0)
        lcd.putstr(date_str)
        last_date = date_str

    if time_str != last_time:
        lcd.move_to(0, 1)
        lcd.putstr(time_str)
        last_time = time_str

    time.sleep(1)          # 1 s is enough – we only show minutes