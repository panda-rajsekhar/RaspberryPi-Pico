# Raspberry Pi Pico LED State Machine (Non-Blocking)

A simple and efficient LED control system for the Raspberry Pi Pico using a non-blocking state machine approach with`millis()` timing.

This project demonstrates how to control multiple LEDs without using `delay()`, making it suitable for scalable embedded systems.

## 🚀 Features

- ⏱️ Non-blocking timing using `millis()`
- 🔄 State machine-based LED control
- 💡 Clean and readable logic
- 🧠 Easily extendable for complex applications
- 🐼 Fun variable naming (`Panda`, `previousPanda`)

---

## 🔌 Hardware Requirements

- Raspberry Pi Pico
- 3 LEDs (Green, Orange, Blue)
- 3 Current-limiting resistors (220Ω recommended)
- Breadboard & jumper wires


## 📍 Pin Configuration

| LED Color | GPIO Pin |
|-----------|----------|
| GREEN     | 9        |
| ORANGE    | 1        |
| BLUE      | 5        |

---

## 📈 Why Non-Blocking?

Using `delay()` halts the CPU, preventing multitasking.  
With `millis()`:

- 🧠 You can run multiple tasks simultaneously  
- ⚡ System stays responsive  
- 🎯 Perfect for real-time embedded systems  

---

## 🔧 Future Improvements

- 🚦 Convert into a traffic light controller  
- 🎚️ Add PWM fading effects  
- 🔘 Button-controlled state switching  
- 📡 Integrate UART / Bluetooth control  
- ⏲️ Variable timing per state  



