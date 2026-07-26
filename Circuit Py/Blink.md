# Raspberry Pi Pico Onboard LED Blink (CircuitPython)

A beginner-friendly CircuitPython project that blinks the onboard LED of the Raspberry Pi Pico.

## 📖 Overview

This project demonstrates how to control the onboard LED of the Raspberry Pi Pico using **CircuitPython**. The LED is turned on and off every 100 milliseconds using the `digitalio` module.

This is one of the first programs beginners write when learning embedded systems and is often referred to as the embedded equivalent of **"Hello, World!"**.

---

## 🛠 Requirements

- Raspberry Pi Pico (RP2040)
- CircuitPython firmware
- Thonny IDE, Mu Editor, or any text editor
- USB cable

---

## 💻 Code

```python
import time
import board
import digitalio

led_onb = digitalio.DigitalInOut(board.LED)
led_onb.direction = digitalio.Direction.OUTPUT

while True:
    led_onb.value = True
    time.sleep(0.1)

    led_onb.value = False
    time.sleep(0.1)
```

---

## ▶️ How to Run

1. Flash CircuitPython onto the Raspberry Pi Pico.
2. Connect the Pico to your computer.
3. Open the `CIRCUITPY` drive.
4. Create or replace the `code.py` file with the program above.
5. Save the file.
6. The Pico will automatically reload the code and the onboard LED will begin blinking.

![[ckp1.png]]

---

## 📚 Concepts Covered

- CircuitPython Basics
- GPIO Output
- `digitalio` Module
- `board.LED`
- Infinite Loops
- Timing with `time.sleep()`

---

## 🔍 Code Explanation

- `board.LED` refers to the onboard LED, making the code portable across many CircuitPython-supported boards.
- `DigitalInOut()` creates a digital output object.
- `Direction.OUTPUT` configures the LED pin as an output.
- `led_onb.value = True` turns the LED on.
- `led_onb.value = False` turns the LED off.
- `time.sleep(0.1)` creates a 100 ms delay between state changes.

---

Made with ❤️ using **CircuitPython** on the **Raspberry Pi Pico**.