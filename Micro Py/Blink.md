# Raspberry Pi Pico Onboard LED Blink with Micro Python 

A simple MicroPython project that blinks the onboard LED of the Raspberry Pi Pico using GPIO 25.

## 📖 Overview

This project demonstrates the fundamentals of GPIO programming on the Raspberry Pi Pico using MicroPython. The onboard LED connected to GPIO 25 toggles its state every 0.5 seconds, producing a continuous blinking effect.

This is often considered the embedded systems equivalent of the classic **"Hello, World!"** program.

---

## 🛠 Requirements

- Raspberry Pi Pico
- MicroPython firmware
- Thonny IDE (or any MicroPython-compatible IDE)
- USB cable

---

## 💻 Code

```python
from machine import Pin
from time import sleep

led = Pin(25, Pin.OUT)

while True:
    led.toggle()
    sleep(0.5)
```


---

## ▶️ Running the Program

1. Flash MicroPython onto the Raspberry Pi Pico.
2. Open Thonny IDE.
![[thonny 1.png]]
3. Connect the Pico via USB.
4. Select the MicroPython interpreter.
5. Copy the code into a new file or you can write own code .
6. Save the file as `blink.py` on the Pico (or run it directly).
7. The onboard LED will blink every 0.5 seconds.

![[blink.jpg]]


---

## 📚 Concepts Covered

- GPIO Output
- Digital Logic
- Infinite Loops
- Timing with `sleep()`
- MicroPython Basics
- Embedded Systems Programming

---


Made with ❤️ using **MicroPython** on the **Raspberry Pi Pico**.