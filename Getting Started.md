# Introduction

The **Raspberry Pi Pico** is a low-cost microcontroller development board introduced by the Raspberry Pi Foundation in **January 2021**. It is built around the **RP2040** microcontroller, the first microcontroller chip designed in-house by Raspberry Pi. The Pico was created to provide an affordable yet powerful platform for learning embedded systems, electronics, and hardware programming.

Unlike a single-board computer such as the Raspberry Pi 4, the Raspberry Pi Pico is a **microcontroller board**. It does not run a full operating system like Linux. Instead, it executes a single program stored in its onboard flash memory, making it ideal for real-time applications, robotics, automation, sensor interfacing, and Internet of Things (IoT) projects.

This repository focuses on the **original Raspberry Pi Pico (2021)**, which features the **RP2040** microcontroller and **does not include built-in Wi-Fi or Bluetooth connectivity**. All networking capabilities, if required, must be added using external modules.

![[IMG_20260726_131444.jpg]]


## Key Features

- Dual-core ARM Cortex-M0+ processor running at up to **133 MHz**
    
- **264 KB** of on-chip SRAM
    
- **2 MB** of onboard QSPI flash memory
    
- **26** multifunction GPIO pins
    
- Support for **I²C, SPI, UART, PWM, ADC, and PIO (Programmable I/O)**
    
- USB 1.1 device and host support
    
- Low-power operation suitable for battery-powered applications
    
- Programmable using **CircuitPython, MicroPython, C/C++, Arduino**, and other supported SDKs
    


## Repository Goal

The objective of this repository is to document the process of learning embedded systems using the Raspberry Pi Pico through a series of practical experiments and projects. Each project is organized with source code, circuit diagrams, explanations, and demonstrations to provide a structured learning path from basic GPIO control to advanced peripheral interfacing.


# Getting Started

Before programming the Raspberry Pi Pico, you need to flash a compatible firmware onto the board. The Pico supports multiple programming environments, with **MicroPython** and **CircuitPython** being the most popular choices.

---

# Installing MicroPython

MicroPython is a lightweight implementation of Python designed specifically for microcontrollers. It is officially supported by the Raspberry Pi Foundation and is an excellent choice for embedded systems development.

## Requirements

- Raspberry Pi Pico
    
- USB Type-A to Micro-USB cable (data cable)
    
- A computer running Windows, Linux, or macOS
    
- Latest MicroPython UF2 firmware
    

## Step 1: Download the Firmware

Download the latest MicroPython UF2 firmware for the Raspberry Pi Pico from the official MicroPython website.
![[download.png]]

> [https://micropython.org/download/rp2-pico/](https://micropython.org/download/rp2-pico/)

## Step 2: Enter BOOTSEL Mode
   
1. Press and hold the **BOOTSEL** button.
    
2. While holding the button, connect the Pico to your computer using the USB cable.
    
3. Release the button after the board is detected.
    
![[rp1-rp2.png]]
The Pico will appear as a USB mass storage device named **RPI-RP2**.

## Step 3: Flash the Firmware

1. Copy the downloaded `.uf2` firmware file onto the **RPI-RP2** drive.
![[pico-drive.png]]
    
2. Wait a few seconds.
    

![[Transfer.png]]

The board will automatically reboot and the **RPI-RP2** drive will disappear.

MicroPython is now installed.

## Step 4: Verify the Installation

Open **Thonny IDE**.

Navigate to:

```
Run → Select Interpreter
```

Choose:

```
MicroPython (Raspberry Pi Pico)
```

Click **OK**.

![[Thonny.png]]
Open the Shell. If the installation was successful, you should see the MicroPython REPL:

```python
MicroPython v1.xx.x on 202x-xx-xx
Type "help()" for more information.
>>>
```

Congratulations! Your Raspberry Pi Pico is now ready to run MicroPython programs.

![[verification.png]]

---

# Installing CircuitPython

CircuitPython is a beginner-friendly fork of MicroPython developed by Adafruit. It emphasizes ease of use by allowing users to edit files directly on the board's USB storage without requiring a separate upload process.

## Requirements

- Raspberry Pi Pico
    
- USB Type-A to Micro-USB data cable
    
- A computer running Windows, Linux, or macOS
    
- Latest CircuitPython UF2 firmware
    

## Step 1: Download the Firmware
![[download.png]]
Download the latest CircuitPython firmware for the Raspberry Pi Pico from Adafruit.

> [https://circuitpython.org/board/raspberry_pi_pico/](https://circuitpython.org/board/raspberry_pi_pico/)

## Step 2: Enter BOOTSEL Mode

1. Disconnect the Pico.
    
2. Hold the **BOOTSEL** button.
    
3. Connect the Pico to your computer.
    
4. Release the button.
    

The board will appear as **RPI-RP2**.

## Step 3: Flash the Firmware

Copy the downloaded CircuitPython `.uf2` file onto the **RPI-RP2** drive.
![[cktpy-firmwhere.png]]


The Pico will automatically reboot after the file transfer is complete.

## Step 4: Verify the Installation

After rebooting, a new USB drive named:

```
CIRCUITPY
```

will appear.

This confirms that CircuitPython has been installed successfully.
![[cktpy-frmwhere.png]]

![[cktpy-ssfl.png]]

Inside the drive you will find files similar to:

```
boot_out.txt
code.py
lib/
```

The file `code.py` is executed automatically every time the board starts. Simply edit and save this file to run your program.

## Using Thonny with CircuitPython

1. Open **Thonny IDE**.
    
2. Navigate to:
    

```
Run → Select Interpreter
```

3. Select:
    

```
CircuitPython (generic)
```

or the appropriate CircuitPython interpreter available in your version of Thonny.

4. Open the Shell to access the CircuitPython REPL.
    

You should see:

```python
Adafruit CircuitPython x.x.x on 202x-xx-xx
>>>
```

Your Raspberry Pi Pico is now ready for CircuitPython development.



----
# How to View Files Inside Pico 

## Using Thonny (Easiest)

1. Connect your Pico to your computer.
2. Open **Thonny**.
3. Go to **View → Files**.
![[File1.png]]
4. In the **Files** pane, select **MicroPython device** or **CircuitPython Device**
![[File2.png]]
5. You'll see the files stored on the Pico (e.g., `main.py`, `boot.py`, other `.py` files).
6. Right-click the file you want to delete and choose **Delete**.