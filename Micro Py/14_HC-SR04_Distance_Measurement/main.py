from machine import Pin, I2C, time_pulse_us
from i2c_lcd import I2cLcd
from time import sleep, sleep_us

# ---------------- LCD ----------------
i2c = I2C(
    0,
    sda=Pin(0),
    scl=Pin(1),
    freq=400000
)

lcd = I2cLcd(i2c, 0x27, 2, 16)

# ---------------- HC-SR04 ----------------
trig = Pin(15, Pin.OUT)
echo = Pin(14, Pin.IN)

# ---------------- Main Program ----------------
lcd.clear()
lcd.putstr("Ultrasonic")
lcd.move_to(0, 1)
lcd.putstr("Sensor")
sleep(2)

while True:

    # Make sure trigger is LOW
    trig.low()
    sleep_us(2)

    # Send 10 us trigger pulse
    trig.high()
    sleep_us(10)
    trig.low()

    # Measure ECHO pulse duration
    duration = time_pulse_us(echo, 1, 30000)

    lcd.clear()

    if duration < 0:
        lcd.putstr("NO ECHO")
        lcd.move_to(0, 1)
        lcd.putstr("Check Sensor")

    else:
        # Calculate distance in cm
        distance = (duration * 0.0343) / 2

        lcd.putstr("Distance:")
        lcd.move_to(0, 1)
        lcd.putstr("{:.2f} cm".format(distance))

    sleep(0.2)