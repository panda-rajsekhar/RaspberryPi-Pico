# ST7735 TFT LCD Graphics Framework for Raspberry Pi Pico

A lightweight graphics and embedded Human Machine Interface (HMI) framework developed entirely in **MicroPython** for the **Raspberry Pi Pico (RP2040)** using a **1.8" ST7735 TFT LCD**.

Unlike many examples that rely on third-party graphics libraries, every core component of this project has been written from scratch as part of the learning journey.

The `lcd/` directory contains the complete graphics framework:

- **ST7735 Display Driver**
- **RGB565 Color Library**
- **Bitmap Font Generator**
- **Font Rendering Engine**
- **Reusable UI Widget Library**

Every drawing primitive, rendering routine, font, and widget was developed, tested, optimized, and verified directly on real Raspberry Pi Pico hardware.

The objective of this repository is not only to drive a TFT display but to understand how modern embedded graphics libraries are built from the ground up while keeping the implementation lightweight, modular, and easy to understand.

# Circuit Connections

The project uses the Raspberry Pi Pico hardware SPI interface to communicate with the ST7735 TFT LCD.

| Raspberry Pi Pico | ST7735 TFT LCD | Description |
|:-----------------:|:--------------:|-------------|
| 3V3              | VCC            | Power Supply |
| GND              | GND            | Ground |
| GP18             | SCK / CLK      | SPI Clock |
| GP19             | SDA / MOSI     | SPI Data |
| GP20             | DC             | Data / Command |
| GP21             | RST            | Display Reset |
| GP22             | CS             | Chip Select |
| 3V3              | BL / LED       | Backlight |

> **Note**
>
> This project uses the Raspberry Pi Pico hardware SPI peripheral for maximum performance. The backlight (BL) pin is connected directly to **3.3 V**, keeping the display permanently illuminated. If brightness control is required, the BL pin can instead be connected to a PWM-capable GPIO.

---

## Hardware

- Raspberry Pi Pico (RP2040)
- ST7735 1.8" TFT LCD (128 × 160)
- SPI Communication Interface
- MicroPython

# Serial Peripheral Interface (SPI)

The **Serial Peripheral Interface (SPI)** is a synchronous serial communication protocol developed by Motorola for high-speed communication between a **master device** and one or more **slave devices**.

In this project, the **Raspberry Pi Pico (RP2040)** operates as the **SPI Master**, while the **ST7735 TFT LCD** functions as the **SPI Slave**.

Unlike parallel communication, SPI transfers data one bit at a time over dedicated communication lines, resulting in fewer GPIO requirements while maintaining high transfer speeds.

---

## SPI Communication Lines

The TFT LCD communicates with the Raspberry Pi Pico using the following signals.

| Signal | Full Form | Direction | Purpose |
|---------|-----------|-----------|---------|
| SCK | Serial Clock | Master → Slave | Synchronizes data transmission |
| MOSI | Master Out Slave In | Master → Slave | Transfers commands and pixel data |
| MISO | Master In Slave Out | Slave → Master | Returns data from the slave (not used by ST7735) |
| CS | Chip Select | Master → Slave | Selects the active SPI device |

Since the ST7735 display only receives information from the Pico, the **MISO line is not required** in this project.

---

## Additional Control Pins

Besides the SPI bus, the display requires a few dedicated control pins.

| Pin | Purpose |
|------|---------|
| DC | Selects whether the transmitted byte is a command or display data |
| RST | Hardware reset of the display controller |
| BL | Controls the display backlight |

These pins are standard GPIO signals rather than part of the SPI protocol itself.

---

## Communication Sequence

Every operation performed on the display follows the same basic sequence.

1. The Pico pulls **CS LOW** to select the display.
2. The **DC** pin is configured.
   - LOW → Command
   - HIGH → Display Data
3. The Pico generates clock pulses on **SCK**.
4. Data bytes are transmitted through **MOSI**.
5. Once the transmission is complete, **CS** returns HIGH.

```
Raspberry Pi Pico                     ST7735 TFT

CS   ───────────────┐___________________________┐────

DC   ──────CMD──────┐────────DATA───────────────┐────

SCK  ──┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐┌─┐─────────

MOSI ──<------ Command ------><------ Data ----->
```

---

## Why SPI?

SPI is one of the most widely used communication protocols in embedded systems because it offers several advantages.

- High communication speed
- Full-duplex capability
- Low protocol overhead
- Simple hardware implementation
- Widely supported by microcontrollers
- Suitable for graphics displays, sensors, SD cards and flash memory

For display applications such as the ST7735, SPI provides enough bandwidth to update graphics efficiently while using only a small number of GPIO pins.

---

## Hardware SPI

The Raspberry Pi Pico contains dedicated SPI peripherals implemented in hardware.

Using the hardware SPI controller provides significant advantages over manually toggling GPIO pins (bit-banging):

- Higher transfer speeds
- Lower CPU usage
- More reliable timing
- Efficient block data transfers
- Better overall display performance

For these reasons, this project exclusively uses the RP2040's **hardware SPI interface**.

---

## SPI in This Project

```
Raspberry Pi Pico                ST7735 TFT

GP18 (SCK)   ───────────────► CLK

GP19 (MOSI)  ───────────────► SDA

GP22 (CS)    ───────────────► CS

GP20 (DC)    ───────────────► DC

GP21 (RST)   ───────────────► RESET

3V3          ───────────────► VCC

GND          ───────────────► GND

3V3          ───────────────► BL
```

Every graphics primitive implemented in this repository—whether drawing a single pixel, rendering text, or displaying complex UI widgets—is ultimately converted into SPI data packets and transmitted over this interface to the ST7735 display controller.


---

# Repository Contents

The project contains **33 progressively developed experiments**, beginning with the first SPI communication test and gradually evolving into a reusable embedded graphics framework.

| Experiment | Description |
|------------|-------------|
| 01 | SPI Test |
| 02 | Display Initialization |
| 03 | Screen Fill Test |
| 04 | Draw Pixel |
| 05 | Corner Test |
| 06 | Crosshair Test |
| 07 | Lines Test |
| 08 | Filled Rectangle Test |
| 09 | Rectangle Test |
| 10 | Filled Rectangle Animation |
| 11 | Multiple Filled Rectangles |
| 12 | Circle Test |
| 13 | Olympic Rings |
| 14 | Multiple Filled Circles |
| 15 | Traffic Signal |
| 16 | Triangles Test |
| 17 | Sierpinski Style Pattern |
| 18 | Filled Triangle Tessellation |
| 19 | Christmas Tree |
| 20 | Rounded Rectangle |
| 21 | Filled Rounded Rectangle |
| 22 | Text Rendering |
| 23 | Font Demonstration |
| 24 | Text Scaling |
| 25 | RP2040 Information Display |
| 26 | RP2040 System Monitor *(continued as a standalone project)* |
| 27 | Draw Panel Widget |
| 28 | Draw Status LED Widget |
| 29 | Draw History Graph Widget |
| 30 | Diamond Widget |
| 31 | Segmented Meter Widget |
| 32 | Button Widget |
| 33 | Battery Widget |

---

> **Note**
>
> Although every experiment has its own screenshot, I have intentionally avoided embedding all of them throughout this README.
>
> Many of these demonstrations include smooth animations and visual effects that static images simply cannot capture. I encourage you to clone the repository, run the examples on real hardware, and experience the animations as they were designed.
>
> The gallery below provides a quick visual overview of the project's progression without taking away the enjoyment of exploring each experiment yourself.

---

# Project Gallery

The following gallery showcases the complete development journey of the ST7735 TFT LCD Graphics Framework, beginning with hardware setup and progressing through graphics primitives, drawing algorithms, and reusable UI widgets.

---

## Hardware

<p align="center">
  <img src="assets/00_circuit.jpg" width="700">
</p>

---

## Display Initialization

<p align="center">
  <img src="assets/01_01_SPI_Test.jpg" width="260">
</p>

---

## Graphics Primitives

<p align="center">
  <img src="assets/04_Draw_Pixel.jpg" width="180">
  <img src="assets/05_Corner_Test.jpg" width="180">
  <img src="assets/06_Crosshair_Test.jpg" width="180">
  <img src="assets/07_Lines_Test.jpg" width="180">
</p>

<p align="center">
  <img src="assets/09_Rectangles_Test.jpg" width="180">
  <img src="assets/11_Multiple_Filled_Rectangles.jpg" width="180">
  <img src="assets/12_Circle_Test.jpg" width="180">
  <img src="assets/13_Olympic_Rings.jpg" width="180">
</p>

<p align="center">
  <img src="assets/14_Multiple_Filled_Circles.jpg" width="180">
  <img src="assets/15_Traffic_Signal.jpg" width="180">
  <img src="assets/16_Triangles_Test.jpg" width="180">
  <img src="assets/17_Sierpinski_Style_Pattern.jpg" width="180">
</p>

<p align="center">
  <img src="assets/18_Filled_Triangles_Tessellation.jpg" width="180">
  <img src="assets/19_Christmas_Tree.jpg" width="180">
  <img src="assets/24_Text_Scaling.jpg" width="180">
</p>

---

## Embedded UI Widgets

<p align="center">
  <img src="assets/27_Draw_Panel.jpg" width="180">
  <img src="assets/28_Draw_Status_LED.jpg" width="180">
  <img src="assets/29_Draw_Graph.jpg" width="180">
  <img src="assets/30_Diamonds_Test.jpg" width="180">
</p>

<p align="center">
  <img src="assets/31_Meter_Test.jpg" width="180">
  <img src="assets/32_Button_Test.jpg" width="180">
  <img src="assets/33_Battery_Test.jpg" width="180">
</p>

---

# Future Projects

This repository is one milestone in a much larger Raspberry Pi Pico journey.

The graphics framework developed here serves as the foundation for future embedded applications, each building upon the previous project while introducing new concepts and capabilities.

## Development Roadmap

- ✅ ST7735 TFT LCD Graphics Framework
- ✅ RP2040 Resource Monitor UI
- ⏳ Image Rendering Engine
- ⏳ Bitmap Image Converter
- ⏳ Icon Library
- ⏳ Embedded Window Manager
- ⏳ Menu Navigation System
- ⏳ Dashboard Framework
- ⏳ Embedded Applications
- ⏳ Advanced Human Machine Interface (HMI)

---

### RP2040 Resource Monitor UI

The first application built using this graphics framework is the **RP2040 Resource Monitor UI**.

It demonstrates how the graphics primitives and reusable widgets developed in this repository can be combined to create a complete embedded dashboard featuring:

- Live system information
- Optimized partial screen updates
- Modular UI architecture
- Reusable dashboard components
- Real-time visualization

This project is available as a separate repository within the Raspberry Pi Pico series.

---

### Next Step — Image Rendering

The next stage of development focuses on bringing images to the ST7735 TFT LCD.

Upcoming work includes:

- Bitmap image rendering
- Image conversion utilities
- Memory-efficient image storage
- RGB565 image generation
- Icons and splash screens
- Logo rendering
- Animation techniques

These additions will further expand the framework and make it suitable for creating polished embedded graphical interfaces.

---

This repository will continue to grow as new graphics capabilities, widgets, and embedded UI techniques are explored.

---

## Author's Note

I am not an industry expert, nor do I claim to know everything about embedded systems.

This project is simply the result of countless hours of curiosity, experimentation, learning from mistakes, and a genuine desire to understand how things work by building them from the ground up.

As a person of faith, I believe the inspiration and strength to pursue these ideas come from God. My role is simply to stay curious, keep learning, and do my best to bring those ideas to life through code and hardware.

If this repository helps even one person learn something new or inspires them to start building their own projects, then every hour spent on it has been worthwhile.

**Jai Jagannath 🙏**
