from machine import Pin
from utime import sleep_ms, sleep_us

scl = Pin(19, Pin.OUT, value=0)
sdo = Pin(18, Pin.IN, Pin.PULL_UP)

KEY_MODE = 32  # 16-key mode; use 16 for 8-key mode


def _key_map(data):
    key = 0
    for bit in data:
        if bit == 0:
            break
        key += 1
    return (key >> 1) + 1


def key_read(mode=KEY_MODE):
    if sdo.value():
        scl.high()
        return 0

    sleep_us(103)

    key = 0
    count = 0

    while count < mode:
        bit = sdo.value()

        if bit == 0:
            key = (count >> 1) + 1
            break

        scl.toggle()
        sleep_ms(1)
        count += 1

    # Preserve the original clock-read cycle when a key is detected.
    if count < mode and key:
        scl.toggle()
        sleep_ms(1)
        count += 1

        while count < mode:
            scl.toggle()
            sleep_ms(1)
            count += 1

    scl.low()
    sleep_ms(2)
    return key


def main():
    print("Press Any Key ...")

    while True:
        key = key_read()
        if key:
            print("key =", key)


if __name__ == "__main__":
    main()
