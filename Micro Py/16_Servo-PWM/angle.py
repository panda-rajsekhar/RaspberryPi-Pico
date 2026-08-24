from machine import Pin, PWM

servo = PWM(Pin(15))
servo.freq(50)


def set_angle(angle):
    # 90° servo
    # Adjust these two values during calibration if necessary.
    MIN_PULSE = 1000   # µs
    MAX_PULSE = 2000   # µs

    pulse_us = MIN_PULSE + (
        (MAX_PULSE - MIN_PULSE) * angle / 90
    )

    # 50 Hz = 20,000 µs period
    duty = int(pulse_us * 65535 / 20000)

    servo.duty_u16(duty)


print("=== Pico Servo Calibration ===")
print("Enter an angle from 0 to 90.")
print("Type 'q' to quit.\n")

while True:
    value = input("angle> ")

    if value.lower() == "q":
        break

    try:
        angle = float(value)

        if 0 <= angle <= 90:
            set_angle(angle)
            print("Servo ->", angle, "degrees")
        else:
            print("Enter a value between 0 and 90.")

    except ValueError:
        print("Invalid input. Enter a number.")

servo.deinit()
print("Servo PWM stopped.")