from machine import ADC
import machine
import gc
import time

from st7735 import *
from colors import *
from widgets import *

# ==========================================================
# Layout Constants
# ==========================================================

# Resource Labels

LEFT = 8

CPU_Y = 12
MEM_Y = 22
TEMP_Y = 32
RAM_Y = 42
RUN_Y = 52

# Meters

METER_X = 34

# Value text

VALUE_X = 70

# Status LEDs

LED_LEFT = 49
LED_RIGHT = 103
LED_RADIUS = 3

# Core

CORE_TITLE_Y = 65
CORE0_Y = 76
CORE1_Y = 86

# Protocol

PROTO_TITLE_Y = 100

UART_Y = 111
I2C_Y = 121

# Footer

FOOTER_TITLE_Y = 138
FOOTER_VALUE_Y = 148

# Divider Lines

DIV1_Y = 61
DIV2_Y = 96
DIV3_Y = 132


# ==========================================================
# System Monitor
# ==========================================================

class SystemMonitor:

    def __init__(self):

        # --------------------------------------------------
        # Display
        # --------------------------------------------------

        self.display = ST7735()

        # --------------------------------------------------
        # Temperature Sensor
        # --------------------------------------------------

        self.temp_sensor = ADC(4)

        # --------------------------------------------------
        # Boot Time
        # --------------------------------------------------

        self.start_time = time.ticks_ms()

        # --------------------------------------------------
        # Resource Values
        # --------------------------------------------------

        self.cpu_percent = 0

        self.mem_percent = 0

        self.mem_total = 264

        self.mem_free = 0

        self.temperature = 0.0

        self.frequency = 125

        self.uptime = "00:00"

        # --------------------------------------------------
        # Core Status
        # --------------------------------------------------

        self.core0_active = False

        self.core1_active = False

        # --------------------------------------------------
        # Protocol Status
        # --------------------------------------------------

        self.uart_active = False

        self.spi_active = False

        self.i2c_active = False

        self.pwm_active = False

        # --------------------------------------------------
        # RUN LED
        # --------------------------------------------------

        self.run_led = False

        # ==================================================
        # Cached Values
        # (Used to avoid unnecessary redraws)
        # ==================================================

        self.last_cpu = -1

        self.last_mem = -1

        self.last_temp = -1

        self.last_ram = -1

        self.last_freq = -1

        self.last_uptime = ""

        self.last_run = None

        self.last_core0 = None

        self.last_core1 = None

        self.last_uart = None

        self.last_spi = None

        self.last_i2c = None

        self.last_pwm = None
        
    # =====================================================
    # Draw Static Dashboard
    # =====================================================

    def draw_static(self):

        d = self.display

        # --------------------------------------------------
        # Background
        # --------------------------------------------------

        d.fill_screen(BLACK)

        # --------------------------------------------------
        # Main Panel
        # --------------------------------------------------

        draw_panel(
            d,
            4,
            4,
            122,
            154,
            CYAN,
            title="RP2040 MONITOR"
        )

        # ==================================================
        # RESOURCE LABELS
        # ==================================================

        d.draw_text(LEFT, CPU_Y, "CPU", WHITE)
        d.draw_text(LEFT, MEM_Y, "MEM", WHITE)
        d.draw_text(LEFT, TEMP_Y, "TEMP", WHITE)
        d.draw_text(LEFT, RAM_Y, "RAM", WHITE)
        d.draw_text(LEFT, RUN_Y, "RUN", WHITE)

        # ==================================================
        # RESOURCE METERS
        # ==================================================

        draw_meter(
            d,
            METER_X,
            CPU_Y,
            0
        )

        draw_meter(
            d,
            METER_X,
            MEM_Y,
            0
        )

        draw_meter(
            d,
            METER_X,
            TEMP_Y,
            0
        )

        # ==================================================
        # PLACEHOLDER VALUES
        # ==================================================

        d.draw_text(
            VALUE_X,
            CPU_Y,
            "00%",
            WHITE
        )

        d.draw_text(
            VALUE_X,
            MEM_Y,
            "00%",
            WHITE
        )

        d.draw_text(
            VALUE_X,
            TEMP_Y,
            "00C",
            WHITE
        )

        d.draw_text(
            66,
            RAM_Y,
            "",
            WHITE
        )

        draw_status_led(
            d,
            LED_LEFT,
            RUN_Y + 3,
            LED_RADIUS,
            False
        )

        # ==================================================
        # Divider
        # ==================================================

        d.draw_line(
            6,
            DIV1_Y,
            123,
            DIV1_Y,
            CYAN
        )

        # ==================================================
        # CORE STATUS
        # ==================================================

        d.draw_text(
            LEFT,
            CORE_TITLE_Y,
            "CORE STATUS",
            CYAN
        )

        d.draw_text(
            10,
            CORE0_Y,
            "CORE0",
            WHITE
        )

        d.draw_text(
            10,
            CORE1_Y,
            "CORE1",
            WHITE
        )

        draw_status_led(
            d,
            LED_LEFT,
            CORE0_Y + 3,
            LED_RADIUS,
            False
        )

        draw_status_led(
            d,
            LED_LEFT,
            CORE1_Y + 3,
            LED_RADIUS,
            False
        )

        # ==================================================
        # Divider
        # ==================================================

        d.draw_line(
            6,
            DIV2_Y,
            123,
            DIV2_Y,
            CYAN
        )

        # ==================================================
        # PROTOCOL STATUS
        # ==================================================

        d.draw_text(
            LEFT,
            PROTO_TITLE_Y,
            "PROTOCOL STATUS",
            CYAN
        )

        d.draw_text(
            10,
            UART_Y,
            "UART",
            WHITE
        )

        d.draw_text(
            64,
            UART_Y,
            "SPI",
            WHITE
        )

        d.draw_text(
            10,
            I2C_Y,
            "I2C",
            WHITE
        )

        d.draw_text(
            64,
            I2C_Y,
            "PWM",
            WHITE
        )

        draw_status_led(
            d,
            LED_LEFT,
            UART_Y + 3,
            LED_RADIUS,
            False
        )

        draw_status_led(
            d,
            LED_RIGHT,
            UART_Y + 3,
            LED_RADIUS,
            False
        )

        draw_status_led(
            d,
            LED_LEFT,
            I2C_Y + 3,
            LED_RADIUS,
            False
        )

        draw_status_led(
            d,
            LED_RIGHT,
            I2C_Y + 3,
            LED_RADIUS,
            False
        )

        # ==================================================
        # Divider
        # ==================================================

        d.draw_line(
            6,
            DIV3_Y,
            123,
            DIV3_Y,
            CYAN
        )

        # ==================================================
        # FOOTER
        # ==================================================

        d.draw_text(
            8,
            FOOTER_TITLE_Y,
            "FREQ",
            CYAN
        )

        d.draw_text(
            70,
            FOOTER_TITLE_Y,
            "UP",
            CYAN
        )

        d.draw_line(
            60,
            135,
            60,
            154,
            CYAN
        )

        d.draw_text(
            8,
            FOOTER_VALUE_Y,
            "125 MHz",
            WHITE
        )

        d.draw_text(
            66,
            FOOTER_VALUE_Y,
            "00:00",
            WHITE
        )
        
    # =====================================================
    # Read RP2040 Values
    # =====================================================

    def update_values(self):

        # CPU Frequency

        self.frequency = machine.freq() // 1000000

        # Memory

        gc.collect()

        self.mem_free = gc.mem_free() // 1024
        

        if self.mem_free > self.mem_total:
            self.mem_free = self.mem_total

        self.mem_percent = int(
            (self.mem_total - self.mem_free)
            * 100
            / self.mem_total
        )

        # Demo CPU Usage

        t = time.ticks_ms() // 250

        self.cpu_percent = (t * 7) % 101

        # Temperature

        raw = self.temp_sensor.read_u16()

        voltage = raw * 3.3 / 65535

        self.temperature = (
            27 -
            (voltage - 0.706) / 0.001721
        )

        self.temperature = round(self.temperature, 1)

        if self.temperature < 0:
            self.temperature = 0

        if self.temperature > 99:
            self.temperature = 99

        # Uptime

        elapsed = time.ticks_diff(
            time.ticks_ms(),
            self.start_time
        ) // 1000

        minutes = elapsed // 60

        seconds = elapsed % 60

        self.uptime = "{:02d}:{:02d}".format(
            minutes,
            seconds
        )

        # Demo LEDs

        self.run_led = not self.run_led

        self.core0_active = self.run_led

        self.core1_active = not self.run_led

        self.uart_active = self.run_led

        self.spi_active = not self.run_led

        self.i2c_active = self.core0_active

        self.pwm_active = self.core1_active

    # =====================================================
    # Update Dynamic Display
    # =====================================================

    def update_display(self):

        d = self.display

        # ---------------- CPU ----------------

        if self.cpu_percent != self.last_cpu:

            draw_meter(
                d,
                METER_X,
                CPU_Y,
                self.cpu_percent
            )

            d.draw_text(
                VALUE_X,
                CPU_Y,
                "{:02d}%".format(int(self.cpu_percent)),
                WHITE,
                bg_color=BLACK
            )

            self.last_cpu = self.cpu_percent

        # ---------------- Memory ----------------

        if self.mem_percent != self.last_mem:

            draw_meter(
                d,
                METER_X,
                MEM_Y,
                self.mem_percent
            )

            d.draw_text(
                VALUE_X,
                MEM_Y,
                "{:02d}%".format(int(self.mem_percent)),
                WHITE,
                bg_color=BLACK
            )

            self.last_mem = self.mem_percent

        # ---------------- Temperature ----------------

        temp_int = int(self.temperature)

        if temp_int != self.last_temp:

            draw_meter(
                d,
                METER_X,
                TEMP_Y,
                temp_int
            )

            d.draw_text(
                VALUE_X,
                TEMP_Y,
                "{:02d}C".format(temp_int),
                WHITE,
                bg_color=BLACK
            )

            self.last_temp = temp_int
            
        # ---------------- RAM ----------------

        ram_used = self.mem_total - self.mem_free

        if ram_used != self.last_ram:

            d.fill_rectangle(
                VALUE_X,
                RAM_Y,
                48,
                8,
                BLACK
            )

            d.draw_text(
                VALUE_X,
                RAM_Y,
                "{:03d}/264".format(ram_used),
                CYAN
            )

            self.last_ram = ram_used

        # ---------------- Frequency ----------------

        if self.frequency != self.last_freq:

            d.draw_text(
                8,
                FOOTER_VALUE_Y,
                "{} MHz".format(self.frequency),
                WHITE,
                bg_color=BLACK
            )

            self.last_freq = self.frequency

        # ---------------- Uptime ----------------

        if self.uptime != self.last_uptime:

            d.draw_text(
                66,
                FOOTER_VALUE_Y,
                self.uptime,
                WHITE,
                bg_color=BLACK
            )

            self.last_uptime = self.uptime

        # ---------------- RUN LED ----------------

        if self.run_led != self.last_run:

            draw_status_led(
                d,
                LED_LEFT,
                RUN_Y + 3,
                LED_RADIUS,
                self.run_led
            )

            self.last_run = self.run_led

        # ---------------- CORE LEDs ----------------

        if self.core0_active != self.last_core0:

            draw_status_led(
                d,
                LED_LEFT,
                CORE0_Y + 3,
                LED_RADIUS,
                self.core0_active
            )

            self.last_core0 = self.core0_active

        if self.core1_active != self.last_core1:

            draw_status_led(
                d,
                LED_LEFT,
                CORE1_Y + 3,
                LED_RADIUS,
                self.core1_active
            )

            self.last_core1 = self.core1_active

        # ---------------- Protocol LEDs ----------------

        if self.uart_active != self.last_uart:

            draw_status_led(
                d,
                LED_LEFT,
                UART_Y + 3,
                LED_RADIUS,
                self.uart_active
            )

            self.last_uart = self.uart_active

        if self.spi_active != self.last_spi:

            draw_status_led(
                d,
                LED_RIGHT,
                UART_Y + 3,
                LED_RADIUS,
                self.spi_active
            )

            self.last_spi = self.spi_active

        if self.i2c_active != self.last_i2c:

            draw_status_led(
                d,
                LED_LEFT,
                I2C_Y + 3,
                LED_RADIUS,
                self.i2c_active
            )

            self.last_i2c = self.i2c_active

        if self.pwm_active != self.last_pwm:

            draw_status_led(
                d,
                LED_RIGHT,
                I2C_Y + 3,
                LED_RADIUS,
                self.pwm_active
            )

            self.last_pwm = self.pwm_active



    # =====================================================
    # Main Loop
    # =====================================================

    def run(self):

        self.draw_static()

        while True:

            self.update_values()

            self.update_display()

            time.sleep_ms(250)
        
