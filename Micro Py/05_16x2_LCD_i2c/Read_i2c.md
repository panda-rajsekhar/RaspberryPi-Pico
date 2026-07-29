# The I²C Protocol: History, Design, and Its Role in the Raspberry Pi Pico

## 1. Introduction

Inter-Integrated Circuit, universally written as **I²C** (pronounced "I-squared-C" or "I-two-C"), is a synchronous, half-duplex, multi-master/multi-slave serial communication protocol. It is one of the most widely used buses for connecting low-speed peripheral chips — sensors, EEPROMs, real-time clocks, displays, ADCs/DACs — to a microcontroller, using only two wires.

This document covers:
- Where I²C came from and why it was invented
- How the protocol actually works at the electrical and framing level
- Why it's such a good fit for the original Raspberry Pi Pico (2021, RP2040-based, no Wi-Fi/Bluetooth)
- Practical usage on the Pico with example code

---

## 2. Historical Background

### 2.1 Origins at Philips (1982)

I²C was invented by **Philips Semiconductors** (now NXP Semiconductors) in **1982**. The engineer most credited with the design is often cited alongside the Philips Semiconductors applications lab team working on consumer electronics — specifically television sets.

**The problem they were solving:**

In the late 1970s and early 1980s, a single TV or audio device contained many separate ICs — tuner chips, volume/tone control chips, display drivers, EEPROMs for storing settings, etc. Every one of these chips needed to talk to a central microcontroller. The naive way to do this was to give each chip its own dedicated set of control lines (parallel buses), which meant:

- More PCB wiring and board space
- More pins required on both the microcontroller and each peripheral chip (pins were, and still are, expensive in silicon area and package cost)
- More complex board layouts, especially as consumer electronics got smaller
- Difficulty scaling — adding one more chip meant adding more wires

Philips wanted a way to let **many chips share the same two wires**, with the microcontroller addressing each one individually in software rather than via dedicated physical lines. This is the core insight of I²C: trade a small amount of transfer speed for a massive reduction in pin count and wiring complexity.

### 2.2 Why Two Wires, Specifically

I²C uses exactly two signal lines, shared by all devices on the bus:

- **SDA** (Serial Data)
- **SCL** (Serial Clock)

Both lines are **open-drain** (or open-collector in older parts), meaning any device on the bus can pull the line low, but no device actively drives it high — a shared **pull-up resistor** on each line brings it back to the logic-high voltage when nothing is pulling it down. This is a deliberate design choice: it allows multiple devices to share the same wire without fighting each other (no bus contention that could damage a chip), and it's what enables features like clock stretching and multi-master arbitration (covered below).

### 2.3 Standardization and Evolution

- **1982** — I²C introduced by Philips, initially running at 100 kbit/s (**Standard Mode**).
- **1992** — First official public I²C specification (rev 1) published, adding **Fast Mode** (400 kbit/s).
- **1998** — Rev 2 added **Fast Mode Plus** considerations and **High Speed Mode** (3.4 Mbit/s), aimed at applications like fast EEPROM programming.
- **2000s** — Philips spun off its semiconductor division into **NXP Semiconductors**, which now stewards the I²C specification.
- **2012 (v4)** — **Ultra Fast Mode** (5 Mbit/s, unidirectional) added, along with 10-bit addressing improvements.
- I²C became so ubiquitous that many vendors implemented compatible-but-differently-branded versions to avoid licensing fees historically associated with the "I²C" trademark — e.g., **SMBus** (System Management Bus, a stricter subset used in PCs), and other "two-wire interface" (TWI) implementations, which are electrically and functionally near-identical to I²C.

By the 2000s, I²C had become a de facto standard for **low-speed, short-distance, chip-to-chip communication**, especially in embedded systems, precisely because of the pin economy Philips originally designed it for.

---

## 3. How I²C Works

### 3.1 Bus Topology

- All devices connect to the same two wires: SDA and SCL.
- Each wire has one pull-up resistor (typically 2 kΩ–10 kΩ, depending on bus speed and capacitance) to the logic supply voltage (commonly 3.3V or 5V).
- Devices are either **controllers** (historically called "masters") — which initiate communication and generate the clock — or **targets** (historically called "slaves") — which respond when addressed.
- A single bus can have **multiple controllers** and **multiple targets**, which is one of I²C's defining features compared to something like SPI.

### 3.2 Addressing

Every target device on the bus has a unique address:

- **7-bit addressing** is standard, allowing 128 theoretical addresses (a handful are reserved for special purposes, so effectively ~112 usable addresses).
- **10-bit addressing** exists for larger networks but is far less common in practice.
- Many real-world chips let you select part of their address via hardware pins (e.g., tying an `ADDR` pin high or low), so you can put two identical sensors on one bus without a collision.

### 3.3 Frame Structure

A basic I²C transaction looks like this:

1. **START condition** — the controller pulls SDA low while SCL is high (this is the only time SDA changes while SCL is high; it signals "a transaction is beginning").
2. **Address byte** — 7 bits of target address + 1 bit for Read (1) or Write (0).
3. **ACK/NACK bit** — the addressed target pulls SDA low to acknowledge ("ACK") it saw its address; if no device responds, the line stays high (NACK), telling the controller nothing is there.
4. **Data byte(s)** — 8 bits of data, sent MSB-first, each byte followed by an ACK/NACK bit from the receiver.
5. **Repeated START (optional)** — used when a controller wants to switch from writing to reading (e.g., writing a register address, then reading its value) without releasing the bus.
6. **STOP condition** — the controller releases SDA while SCL is high, ending the transaction and freeing the bus.

Data bits are only considered valid while SCL is high; SDA is only allowed to change while SCL is low (except for START/STOP conditions, which are the deliberate exception).

### 3.4 Clock Stretching

If a target device needs more time to process something (e.g., it's busy preparing data), it can hold SCL low even after the controller releases it. The controller must wait for SCL to actually go high before continuing. This lets slow peripherals participate on a bus driven by a faster controller clock, without special negotiation.

### 3.5 Multi-Master Arbitration

Because I²C is open-drain, if two controllers start transmitting at the same time, they can both monitor the bus while sending. If one controller tries to send a "1" (release the line) but sees the line is actually low (because another controller pulled it low for a "0"), it recognizes it has lost arbitration and backs off, letting the other controller continue. This is a non-destructive process — no data is corrupted and no damage occurs, it just resolves who gets to talk.

### 3.6 Speed Grades

| Mode | Speed | Typical Use |
|---|---|---|
| Standard Mode | 100 kbit/s | Original spec, simple sensors |
| Fast Mode | 400 kbit/s | Most common today |
| Fast Mode Plus | 1 Mbit/s | Higher-throughput sensors/EEPROMs |
| High Speed Mode | 3.4 Mbit/s | Rare, needs special bus config |
| Ultra Fast Mode | 5 Mbit/s | Unidirectional, niche |

---

## 4. I²C and the Raspberry Pi Pico (2021, RP2040, no Wi-Fi/BT)

### 4.1 About This Board

The original Raspberry Pi Pico, released in **January 2021**, is built around the **RP2040** microcontroller — a chip designed in-house by Raspberry Pi Ltd. This original Pico has **no wireless connectivity at all** (that came later with the Pico W in 2022, which added an Infineon wireless chip). The plain 2021 Pico is a low-cost, wired, dual-core Cortex-M0+ board intended for direct GPIO-level embedded projects.

Because it has no built-in networking, the Pico relies heavily on wired peripheral buses — I²C, SPI, and UART — to talk to sensors, displays, and expansion boards. I²C is one of the most commonly used of these for hobbyist and professional projects alike.

### 4.2 RP2040's I²C Hardware

The RP2040 includes **two independent hardware I²C controller blocks**, labeled `i2c0` and `i2c1`, based on a licensed Synopsys DesignWare I²C IP core. Key practical points:

- Each I²C block can be a controller or target.
- The RP2040's flexible GPIO muxing means I²C signals (SDA/SCL) can be routed to **several different physical pin pairs**, not fixed to just one location — you choose in software/firmware which GPIOs carry `i2c0`/`i2c1`.
- Common default pin choices in the Pico's pinout (per the official pinout diagram) include GPIO 0/1, 2/3, 4/5, 6/7, and others, each assignable to either I²C block.
- Standard, Fast, and Fast Mode Plus speeds are all supported in hardware.

### 4.3 Why I²C Specifically Suits the Pico

1. **Pin economy on a small board** — the Pico exposes 26 usable GPIO pins in a small 21mm × 51mm footprint. I²C lets you connect many peripherals using just 2 signal pins total (plus power/ground), leaving the remaining pins free for other purposes.
2. **No wireless means more reliance on physical sensors** — since the plain Pico can't reach the network directly, projects commonly read local sensors (temperature, humidity, pressure, motion, light) via I²C and either log data locally or forward it through a wired connection to a host computer.
3. **Daisy-chaining multiple devices cheaply** — a hobbyist can connect an OLED display, an RTC module, and an environmental sensor all on the same two wires (`i2c0`), each with a distinct address, without running separate wiring for each.
4. **Good ecosystem support** — the RP2040 C/C++ SDK (`pico-sdk`) provides a mature `hardware_i2c` library, and MicroPython/CircuitPython builds for the Pico expose a simple `machine.I2C` class, making I²C the easiest bus to get running quickly for beginners.

### 4.4 Typical Use Cases on the Plain Pico

- **Environmental sensors**: BME280/BMP280 (temperature, humidity, pressure) over I²C for weather stations or data loggers.
- **Displays**: SSD1306-based small OLED screens are near-ubiquitous I²C displays paired with the Pico for status readouts.
- **Real-time clocks**: DS3231 or PCF8523 RTC modules, since the Pico itself has no battery-backed clock and loses track of time on power loss.
- **IMUs/accelerometers**: MPU6050 and similar motion sensors for robotics projects.
- **Port expanders**: PCF8574 I/O expanders, useful when the Pico's own GPIO count runs low, e.g., for large keypad or LED matrix projects.
- **EEPROMs**: 24LCxx-series chips for extra persistent storage beyond the Pico's onboard flash.

### 4.5 Example: Reading a Sensor via I²C (MicroPython)

```python
from machine import Pin, I2C

# Use i2c0 on GPIO 4 (SDA) and GPIO 5 (SCL)
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)

# Scan the bus for connected devices
devices = i2c.scan()
print("I2C devices found:", [hex(d) for d in devices])

# Example: read 6 bytes starting at register 0x00 from a device at address 0x76
addr = 0x76
data = i2c.readfrom_mem(addr, 0x00, 6)
print("Raw sensor bytes:", data)
```

### 4.6 Example: Reading a Sensor via I²C (C, pico-sdk)

```c
#include "pico/stdlib.h"
#include "hardware/i2c.h"

#define I2C_PORT i2c0
#define SDA_PIN 4
#define SCL_PIN 5
#define SENSOR_ADDR 0x76

int main() {
    stdio_init_all();
    i2c_init(I2C_PORT, 400 * 1000); // 400 kHz Fast Mode

    gpio_set_function(SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(SDA_PIN);
    gpio_pull_up(SCL_PIN);

    uint8_t reg = 0x00;
    uint8_t buf[6];

    i2c_write_blocking(I2C_PORT, SENSOR_ADDR, &reg, 1, true);  // send register addr, keep bus
    i2c_read_blocking(I2C_PORT, SENSOR_ADDR, buf, 6, false);   // read 6 bytes, release bus

    while (true) {
        tight_loop_contents();
    }
}
```

Note the external pull-up resistors are still required on real hardware (typically 4.7 kΩ) unless the internal weak pull-ups enabled by `gpio_pull_up()` are sufficient for your bus length and speed — for anything beyond breadboard-scale wiring, external resistors are recommended.

---

## 5. I²C vs. SPI vs. UART (Quick Comparison)

| Feature | I²C | SPI | UART |
|---|---|---|---|
| Wires | 2 (SDA, SCL) | 4+ (MOSI, MISO, SCK, CS per device) | 2 (TX, RX) |
| Multi-device on one bus | Yes, via addressing | Yes, via separate CS lines | No (point-to-point) |
| Typical speed | 100 kHz–1 MHz | Several MHz–tens of MHz | Tens of kbps–a few Mbps |
| Multi-master support | Yes | Not standard | N/A |
| Common Pico uses | Sensors, RTC, displays, EEPROMs | SD cards, fast displays, flash | Debug console, GPS modules |

I²C's main tradeoff versus SPI is speed for pin count: SPI is faster and simpler to implement in hardware (push-pull, no addressing overhead), but needs a dedicated chip-select line per device. I²C wins when you have several low/medium-speed peripherals and want to conserve GPIOs — exactly the situation on a small board like the Pico.

---

## 6. Summary

I²C was invented by Philips in 1982 to solve a very concrete problem: too many wires between too many chips inside consumer electronics. Its two-wire, open-drain, addressable design let a single controller talk to dozens of peripherals cheaply, and that same property is exactly why it remains a first choice for embedded hobbyist and professional boards today. On the original Raspberry Pi Pico — a compact, wireless-free RP2040 board — I²C's pin efficiency and broad sensor/display ecosystem make it the natural bus for adding temperature sensors, real-time clocks, small OLED displays, and similar peripherals without consuming the board's limited GPIO budget.
