# Multiple LED Control using Raspberry Pi Pico (MicroPython)

## Overview

This project demonstrates how to control multiple external LEDs using the Raspberry Pi Pico programmed with **MicroPython**. Four LEDs are connected to individual GPIO pins and different lighting patterns are implemented to introduce fundamental embedded programming concepts such as GPIO output, loops, lists, and timing.

---

## Objectives

* Learn how to interface multiple LEDs with the Raspberry Pi Pico.
* Understand digital GPIO output in MicroPython.
* Create different LED patterns using loops and timing.
* Practice writing clean and reusable embedded code.

---

## Components Required

| Component                      |    Quantity |
| ------------------------------ | ----------: |
| Raspberry Pi Pico              |           1 |
| LEDs (Red, Green, Blue, White) |           4 |
| 330 Ω Resistors                |           4 |
| Breadboard                     |           1 |
| Jumper Wires                   | As required |
| USB Cable                      |           1 |

---

## GPIO Connections

| GPIO Pin | LED Color |
| -------- | --------- |
| GP12     | Red       |
| GP13     | Green     |
| GP14     | Blue      |
| GP15     | White     |

Each LED is connected through its own **330 Ω current-limiting resistor**, while all cathodes are connected to a common GND rail (Common Cathode configuration).


---

# Pattern 1 — All LEDs Blink

## Description

All four LEDs turn ON simultaneously and then turn OFF together at regular intervals.

### Concepts Covered

* GPIO Output
* Digital HIGH and LOW
* Basic Timing

### Demonstration



---

# Pattern 2 — Running LED

## Description

One LED lights up at a time from left to right before repeating continuously.

### Sequence

```
🔴
🟢
🔵
⚪
```

### Concepts Covered

* Lists
* For Loops
* Sequential GPIO Control

### Demonstration



---

# Pattern 3 — Ping Pong

## Description

The LEDs move from left to right and then reverse direction, creating a bouncing animation.

### Sequence

```
🔴 → 🟢 → 🔵 → ⚪
               ↓
🔴 ← 🟢 ← 🔵 ← ⚪
```

### Concepts Covered

* Forward Iteration
* Reverse Iteration
* Indexing

### Demonstration



---

# Pattern 4 — Fill and Empty

## Description

The LEDs gradually turn ON one by one until all are illuminated. They then turn OFF one by one in reverse order.

### Sequence

```
🔴

🔴 🟢

🔴 🟢 🔵

🔴 🟢 🔵 ⚪

↓

🔴 🟢 🔵

↓

🔴 🟢

↓

🔴
```

### Concepts Covered

* Progressive GPIO Control
* Reverse Traversal
* Animation Logic

### Demonstration



---

## Expected Output

* Four LEDs connected to the Raspberry Pi Pico display different lighting patterns.
* Each pattern demonstrates a different programming technique using MicroPython.

---

## Applications

* Learning GPIO programming
* Embedded Systems Fundamentals
* LED Pattern Generation
* Robotics Indicators
* Educational Demonstrations

---

## What You'll Learn

* Configuring GPIO pins in MicroPython
* Controlling multiple outputs simultaneously
* Using loops efficiently
* Organizing code for scalability
* Creating basic LED animations

---

## Future Improvements

* PWM Brightness Control
* Push Button Pattern Selection
* RGB LED Control
* Binary Counter
* Traffic Light Simulation
* Random LED Animations
* Knight Rider (Larson Scanner)
* Morse Code Transmitter

---

## Author

**Rajsekhar Panda**

Bachelor of Technology (Electronics & Communication Engineering)

Jawaharlal Nehru Government Engineering College, Sundernagar
