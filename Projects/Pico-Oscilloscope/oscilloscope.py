"""
------------------------------------------------
JAI JAGANNATH
Pico Makeshift Oscilloscope 
------------------------------------------------

Author : Rajsekhar Panda

Captures a 0-3.3 V signal and renders the
waveform on a 1.8" ST7735 TFT.

Measurements:
    - Frequency
    - Period
    - Duty Cycle
    - Vpp

Hardware:
    SIGNAL ──── GP26 / ADC0  (also used as digital for frequency)
    
IMPORTANT:
    Input signal must remain between 0 V and 3.3 V.

Requires:
    st7735.py
    widgets.py
    colors.py
    fonts.py
"""

import time
import machine
from machine import ADC, Pin
from array import array

from st7735 import ST7735
from widgets import draw_panel
from colors import BLACK, WHITE, GREEN, RED, GRAY, CYAN, YELLOW

#---------------Config------------------------------------

ADC_PIN         = 26
DIGITAL_PIN     = 26

ADC_MAX         = 65535
ADC_VREF        = 3.3

NUM_SAMPLES     = 120
WAVEFORM_OFFSET_Y = 9

TRIG_LEVEL      = ADC_MAX // 2
TRIG_HYST       = int(ADC_MAX * 0.05)
TRIG_TIMEOUT_MS = 200

MIN_SAMPLE_DELAY_US = 0
MAX_SAMPLE_DELAY_US = 4000
TARGET_CYCLES       = 3

LOOP_PERIOD_MS  = 35          # slightly faster refresh

MIN_EDGE_SPACING_US = 5

#------------- Display Layout -----------------------------

display = ST7735()
display.fill_screen(BLACK)

PANEL_X, PANEL_Y = 2, 12
PANEL_W, PANEL_H = 124, 75

GRAPH_X = PANEL_X + 2
GRAPH_Y = PANEL_Y + 4
GRAPH_W = PANEL_W - 4
GRAPH_H = PANEL_H - 8

MEAS_X, MEAS_Y = 2, PANEL_Y + PANEL_H + 4
MEAS_W, MEAS_H = 124, 62

LED_X, LED_Y, LED_R = 122, 6, 3

ROW_FREQ_Y   = MEAS_Y + 10
ROW_PERIOD_Y = MEAS_Y + 22
ROW_DUTY_Y   = MEAS_Y + 34
ROW_VPP_Y    = MEAS_Y + 46

LABEL_X = MEAS_X + 6
VALUE_X = MEAS_X + 54


#--------------------Static UI-----------------------------------

def draw_static_ui():
    draw_panel(display, PANEL_X, PANEL_Y, PANEL_W, PANEL_H,
               border_color=GREEN, title="CH1", title_color=GREEN)

    draw_panel(display, MEAS_X, MEAS_Y, MEAS_W, MEAS_H,
               border_color=CYAN, title="MEASURE", title_color=CYAN)

    display.draw_text_fast(LABEL_X, ROW_FREQ_Y,   "FREQ", GRAY, BLACK)
    display.draw_text_fast(LABEL_X, ROW_PERIOD_Y, "PER ", GRAY, BLACK)
    display.draw_text_fast(LABEL_X, ROW_DUTY_Y,   "DUTY", GRAY, BLACK)
    display.draw_text_fast(LABEL_X, ROW_VPP_Y,    "VPP ", GRAY, BLACK)


#--------------------Status-----------------------------------------

def draw_status_indicator(triggered):
    display.fill_rectangle(LED_X - LED_R - 1, LED_Y - LED_R - 1,
                           LED_R * 2 + 3, LED_R * 2 + 3, BLACK)
    if triggered:
        display.fill_rectangle(LED_X - LED_R, LED_Y - LED_R,
                               LED_R * 2 + 1, LED_R * 2 + 1, GREEN)
    else:
        display.draw_circle(LED_X, LED_Y, LED_R, RED)

#---------------------Hardware Timner /Meter -------------------------

class SignalMeter:
    def __init__(self, pin_num):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
        self.prev_rise_us = None
        self.last_rise_us = 0
        self.period_sum_us = 0
        self.high_sum_us = 0
        self.edges = 0
        self.last_edge_us = 0

        self.pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                     handler=self._on_edge)

    def _on_edge(self, pin):
        now = time.ticks_us()

        # Glitch filter
        if self.last_edge_us:
            if time.ticks_diff(now, self.last_edge_us) < MIN_EDGE_SPACING_US:
                return
        self.last_edge_us = now

        if pin.value():                       # Rising
            if self.prev_rise_us is not None:
                period = time.ticks_diff(now, self.prev_rise_us)
                if period > MIN_EDGE_SPACING_US:
                    self.period_sum_us += period
                    self.edges += 1
            self.prev_rise_us = now
            self.last_rise_us = now
        else:                                 # Falling
            if self.last_rise_us:
                high = time.ticks_diff(now, self.last_rise_us)
                if high > 0:
                    self.high_sum_us += high

    def read(self):
        state = machine.disable_irq()
        edges = self.edges
        period_sum = self.period_sum_us
        high_sum = self.high_sum_us
        self.edges = 0
        self.period_sum_us = 0
        self.high_sum_us = 0
        machine.enable_irq(state)

        if edges == 0 or period_sum <= 0:
            return 0.0, 0.0, 0.0, 0

        avg_period = period_sum / edges
        freq = 1_000_000.0 / avg_period
        duty = (high_sum / (edges * avg_period)) * 100.0
        duty = max(0.0, min(100.0, duty))

        return freq, avg_period, duty, edges


#----------------Capturing Waves-------------------------

# Pre-allocated buffer 
samples = array('H', (0 for _ in range(NUM_SAMPLES)))

def capture_waveform(adc, sample_delay_us):
    start = time.ticks_ms()
    armed = False

    # Trigger wait
    while time.ticks_diff(time.ticks_ms(), start) < TRIG_TIMEOUT_MS:
        v = adc.read_u16()
        if not armed:
            if v < (TRIG_LEVEL - TRIG_HYST):
                armed = True
        else:
            if v >= TRIG_LEVEL:
                break
    else:
        return False          # timeout

    # Tight capture loop
    if sample_delay_us <= 0:
        for i in range(NUM_SAMPLES):
            samples[i] = adc.read_u16()
    else:
        for i in range(NUM_SAMPLES):
            samples[i] = adc.read_u16()
            time.sleep_us(sample_delay_us)

    return True


#------------------------Auto Time Base ---------------------
def choose_sample_delay(freq_hz):
    if freq_hz <= 0:
        return 1500
    period_us = 1_000_000.0 / freq_hz
    delay = int((period_us * TARGET_CYCLES) / NUM_SAMPLES)
    return max(MIN_SAMPLE_DELAY_US, min(MAX_SAMPLE_DELAY_US, delay))

#-------------------Rendering WaveForm --------------------------------

def draw_waveform():
    # Clear only the graph
    display.fill_rectangle(GRAPH_X, GRAPH_Y, GRAPH_W, GRAPH_H, BLACK)

    mid_y = GRAPH_Y + GRAPH_H // 2
    display.draw_hline(GRAPH_X, mid_y, GRAPH_W, GRAY)

    scale = (GRAPH_H - 2) / ADC_MAX
    step = GRAPH_W / (NUM_SAMPLES - 1)

    prev_x = GRAPH_X
    prev_y = GRAPH_Y + GRAPH_H - 1 - int(samples[0] * scale) - WAVEFORM_OFFSET_Y

    for i in range(1, NUM_SAMPLES):
        x = GRAPH_X + int(i * step)
        y = GRAPH_Y + GRAPH_H - 1 - int(samples[i] * scale) - WAVEFORM_OFFSET_Y
        display.draw_line(prev_x, prev_y, x, y, YELLOW)
        prev_x, prev_y = x, y


#-------------------Formatting Help---------------------------------------------

def fmt_freq(hz):
    if hz >= 1000:
        return "{:.2f}kHz".format(hz / 1000)
    return "{:.1f}Hz".format(hz)

def fmt_period(us):
    if us >= 1000:
        return "{:.2f}ms".format(us / 1000)
    return "{:.0f}us".format(us)

#------------------------------ Measurement Rendering ------------------------------

_last_freq_str = ""
_last_period_str = ""
_last_duty_str = ""
_last_vpp_str = ""

def draw_readouts(freq, period, duty, vpp):
    global _last_freq_str, _last_period_str, _last_duty_str, _last_vpp_str

    f_str = fmt_freq(freq)
    p_str = fmt_period(period)
    d_str = "{:.1f}%".format(duty)
    v_str = "{:.2f}V".format(vpp)

    if f_str != _last_freq_str:
        display.fill_rectangle(VALUE_X, ROW_FREQ_Y, 70, 8, BLACK)
        display.draw_text_fast(VALUE_X, ROW_FREQ_Y, f_str, WHITE, BLACK)
        _last_freq_str = f_str

    if p_str != _last_period_str:
        display.fill_rectangle(VALUE_X, ROW_PERIOD_Y, 70, 8, BLACK)
        display.draw_text_fast(VALUE_X, ROW_PERIOD_Y, p_str, WHITE, BLACK)
        _last_period_str = p_str

    if d_str != _last_duty_str:
        display.fill_rectangle(VALUE_X, ROW_DUTY_Y, 70, 8, BLACK)
        display.draw_text_fast(VALUE_X, ROW_DUTY_Y, d_str, WHITE, BLACK)
        _last_duty_str = d_str

    if v_str != _last_vpp_str:
        display.fill_rectangle(VALUE_X, ROW_VPP_Y, 70, 8, BLACK)
        display.draw_text_fast(VALUE_X, ROW_VPP_Y, v_str, WHITE, BLACK)
        _last_vpp_str = v_str

#------------------Main Loop----------------------------------------

def main():
    adc = ADC(Pin(ADC_PIN))
    meter = SignalMeter(DIGITAL_PIN)

    draw_static_ui()

    last_freq = 0.0
    last_period = 0.0
    last_duty = 0.0
    last_loop = time.ticks_ms()

    while True:
        # Frequency / duty
        freq, period, duty, edges = meter.read()
        if edges > 0:
            last_freq = freq
            last_period = period
            last_duty = duty

        # Auto timebase
        delay_us = choose_sample_delay(last_freq)

        # Capture
        triggered = capture_waveform(adc, delay_us)

        # Status LED
        draw_status_indicator(triggered)

        # Waveform (only if we got a trigger)
        if triggered:
            draw_waveform()
        else:
            # Optional: clear graph on timeout
            display.fill_rectangle(GRAPH_X, GRAPH_Y, GRAPH_W, GRAPH_H, BLACK)

        # Vpp
        vpp = 0.0
        if triggered:
            mn = samples[0]
            mx = samples[0]
            for i in range(1, NUM_SAMPLES):
                v = samples[i]
                if v < mn: mn = v
                if v > mx: mx = v
            vpp = (mx - mn) / ADC_MAX * ADC_VREF

        # Measurements (smart update)
        draw_readouts(last_freq, last_period, last_duty, vpp)

        # Maintain roughly constant frame rate
        elapsed = time.ticks_diff(time.ticks_ms(), last_loop)
        if elapsed < LOOP_PERIOD_MS:
            time.sleep_ms(LOOP_PERIOD_MS - elapsed)
        last_loop = time.ticks_ms()


if __name__ == "__main__":
    main()
