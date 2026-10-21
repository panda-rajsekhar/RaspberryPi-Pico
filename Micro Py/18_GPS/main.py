from machine import UART, Pin
import time

gps = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

print("GPS satellite diagnostic")
print("Waiting for GGA messages...\n")

while True:
    line = gps.readline()

    if line:
        try:
            s = line.decode("ascii").strip()

            if s.startswith(("$GPGGA", "$GNGGA")):
                f = s.split(",")

                if len(f) >= 10:
                    fix = f[6] or "0"
                    sats = f[7] or "0"

                    if fix != "0":
                        print("|------------------------------------------|")
                        print("FIX ACQUIRED!")
                        print("Satellites used:", sats)
                        print("Latitude:", f[2], f[3])
                        print("Longitude:", f[4], f[5])
                        print("Altitude:", f[9], "m")
                    else:
                        print("No fix | Satellites used:", sats)

        except (ValueError, IndexError):
            pass

    time.sleep_ms(100)
    

