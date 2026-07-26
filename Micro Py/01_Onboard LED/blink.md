# Raspberry Pi Pico Onboard LED Blink (MicroPython)

A beginner-friendly MicroPython project that demonstrates how to blink the onboard LED of the Raspberry Pi Pico.

---

## 📖 Overview

This project introduces the basics of GPIO programming on the **Raspberry Pi Pico** using **MicroPython**. The onboard LED connected to **GPIO 25** is toggled every **0.5 seconds**, creating a continuous blinking effect.

Blinking an LED is traditionally the first program written for a new microcontroller and is widely regarded as the embedded systems equivalent of **"Hello, World!"**. It provides a simple introduction to GPIO control, digital outputs, loops, and timing.

---

## 🛠 Requirements

- Raspberry Pi Pico (RP2040)
- MicroPython firmware installed
- USB Type-A to Micro-USB data cable
- Thonny IDE (or any MicroPython-compatible IDE)

---

## 💻 Source Code

```python
from machine import Pin
from time import sleep

led = Pin(25, Pin.OUT)

while True:
    led.toggle()
    sleep(0.5)
```

---

## ▶️ How to Run

1. Install **MicroPython** on the Raspberry Pi Pico.
2. Connect the Pico to your computer using a USB cable.
3. Open **Thonny IDE**.

![Thonny IDE](https://github.com/panda-rajsekhar/RaspberryPi-Pico/blob/1ae2b83a19d2a15359522303caca3c0f33ac6c13/Assets/thonny%201.png?raw=true)

4. Select the **MicroPython (Raspberry Pi Pico)** interpreter.
5. Create a new file and copy the program above.
6. Save the file as `blink.py` or `main.py` on the Pico.
7. Click **Run** (or save it as `main.py` to execute automatically on boot).

The onboard LED will begin blinking every **0.5 seconds**.

![Blinking LED Demo](https://github.com/panda-rajsekhar/RaspberryPi-Pico/blob/1ae2b83a19d2a15359522303caca3c0f33ac6c13/Assets/blink.jpg)

---

## 📚 Concepts Covered

- MicroPython Basics
- GPIO Output
- Digital Logic
- Infinite Loops
- Timing using `sleep()`
- Embedded Systems Programming

---

## 🔍 Code Explanation

### Importing Modules

```python
from machine import Pin
from time import sleep
```

- `machine.Pin` provides access to the Pico's GPIO pins.
- `sleep()` pauses program execution for a specified duration.

---

### Configuring the LED

```python
led = Pin(25, Pin.OUT)
```

This configures **GPIO 25** as a digital output connected to the onboard LED.

---

### Infinite Loop

```python
while True:
```

The program continuously repeats the instructions inside the loop until power is removed or another program is loaded.

---

### Toggling the LED

```python
led.toggle()
```

The `toggle()` function automatically changes the LED state:

- ON → OFF
- OFF → ON

This removes the need to manually write HIGH and LOW values.

---

### Delay

```python
sleep(0.5)
```

Pauses the program for **0.5 seconds (500 milliseconds)** before toggling the LED again.

---

--

## 🎯 Expected Output

After running the program:

- The onboard LED turns ON.
- After **0.5 seconds**, it turns OFF.
- After another **0.5 seconds**, it turns ON again.
- This sequence repeats indefinitely.

A successful blinking LED confirms that:

- MicroPython has been installed correctly.
- The Raspberry Pi Pico is functioning properly.
- GPIO output is working as expected.

---

## 📜 License

This project is intended for educational purposes and is part of the Raspberry Pi Pico learning repository.

---

Made with ❤️ using **MicroPython** on the **Raspberry Pi Pico**.
