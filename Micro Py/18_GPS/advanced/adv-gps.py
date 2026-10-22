from machine import UART, Pin
import time
import math
import os

# Configuration
UART_ID = 0
BAUDRATE = 9600
TX_PIN = 0              # Pico GP0 -> GPS RX
RX_PIN = 1              # Pico GP1 <- GPS TX

REPORT_INTERVAL_MS = 1000
NO_FIX_INTERVAL_MS = 3000
ALTITUDE_WINDOW = 10

TZ_OFFSET_S = 5 * 3600 + 30 * 60    # IST (UTC+5:30)

MIN_MOVE_M = 5.0                    # ignore jitter below this when summing distance
MOVING_KMH = 3.0                    # below this, treat as stationary (receiver speed noise is ~0-2.5 km/h)
MOVING_CONFIRM = 3                  # consecutive epochs above MOVING_KMH before motion counts
HDOP_JITTER_K = 2.0                 # distance gate is at least HDOP * this many metres

TARGET = None                       # e.g. (31.1048, 77.1734) for bearing/distance
GEOFENCE_RADIUS_M = None            # e.g. 100 -> alert when >100 m from first fix

LOG_TO_FILE = False                 # set True to log to flash
LOG_FILE = "gps_log.csv"
LOG_INTERVAL_MS = 5000

# Large rx buffer so the UART doesn't overflow while printing reports
gps = UART(UART_ID, baudrate=BAUDRATE, tx=Pin(TX_PIN), rx=Pin(RX_PIN),
           timeout=1000, rxbuf=1024)

# Constants (built once, not per call)
SEP = "=" * 52
KN_TO_KMH = 1.852
EARTH_R = 6371000.0
COMPASS = ("N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW")
FIX_NAMES = {1: "No fix", 2: "2D", 3: "3D"}

# State
S = {
    "utc": None, "date": None,
    "fix": 0, "fix_type": 1,            # fix_type: 1 none, 2 2D, 3 3D
    "lat": None, "lon": None,
    "sats_used": 0, "hdop": None, "pdop": None, "vdop": None,
    "alt": None, "geoid": None,
    "speed_kmh": None, "course": None, "rmc_valid": False,
    "used_prns": [], "in_view": 0, "sat_list": [],
}

altitude_samples = []
gsv_tmp = []

start_ms = time.ticks_ms()
ttff_s = None
gga_total = 0
gga_fixed = 0

last_report = last_no_fix = last_log = start_ms
last_fix_state = None

home = None
prev_pos = None
trip_m = 0.0
max_kmh = 0.0
prev_alt = None
prev_alt_ms = None
vspeed = None
filt_alt = None
move_count = 0
geofence_alerted = False
log_header_needed = None


# NMEA helpers
def fnum(s):
    try:
        return float(s) if s else None
    except ValueError:
        return None


def inum(s, default=0):
    try:
        return int(s) if s else default
    except ValueError:
        return default


def nmea_to_decimal(raw, hemi):
    if not raw or not hemi:
        return None
    try:
        v = float(raw)
    except ValueError:
        return None
    deg = int(v // 100)
    minutes = v - deg * 100
    if not 0 <= minutes < 60:
        return None
    res = deg + minutes / 60.0
    if hemi in ("S", "W"):
        res = -res
    elif hemi not in ("N", "E"):
        return None
    limit = 90 if hemi in ("N", "S") else 180
    return res if abs(res) <= limit else None


# Sentence parsers (each updates state S)
def parse_gga(f):
    if len(f) < 13:
        return
    S["utc"] = f[1] or S["utc"]
    S["fix"] = inum(f[6])
    S["sats_used"] = inum(f[7])
    S["lat"] = nmea_to_decimal(f[2], f[3])
    S["lon"] = nmea_to_decimal(f[4], f[5])
    S["hdop"] = fnum(f[8])
    S["alt"] = fnum(f[9]) if f[10] in ("M", "") else None
    S["geoid"] = fnum(f[11]) if f[12] in ("M", "") else None


def parse_rmc(f):
    if len(f) < 10:
        return
    valid = f[2] == "A"
    S["rmc_valid"] = valid
    if not valid:
        return
    S["utc"] = f[1] or S["utc"]
    kn = fnum(f[7])
    S["speed_kmh"] = kn * KN_TO_KMH if kn is not None else None
    S["course"] = fnum(f[8])
    S["date"] = f[9] or S["date"]


def parse_gsa(f):
    if len(f) < 18:
        return
    S["fix_type"] = inum(f[2], 1)
    S["used_prns"] = [p for p in f[3:15] if p]
    S["pdop"] = fnum(f[15])
    S["hdop"] = fnum(f[16]) or S["hdop"]
    S["vdop"] = fnum(f[17])


def parse_gsv(f):
    global gsv_tmp
    if len(f) < 4:
        return
    total = inum(f[1])
    num = inum(f[2])
    S["in_view"] = inum(f[3])
    if num == 1:
        gsv_tmp = []
    for i in range(4, len(f) - 3, 4):
        if f[i]:
            gsv_tmp.append({
                "prn": f[i],
                "elev": inum(f[i + 1]),
                "az": inum(f[i + 2]),
                "snr": inum(f[i + 3], -1),   # -1 = not tracked
            })
    if num == total:
        S["sat_list"] = gsv_tmp
        gsv_tmp = []


PARSERS = {b"GGA": parse_gga, b"RMC": parse_rmc,
           b"GSA": parse_gsa, b"GSV": parse_gsv}


def handle_sentence(line):
    # Returns the sentence type (bytes) if parsed, else None; decodes only wanted sentences
    if len(line) < 10 or line[0] != 36:         # '$'
        return None
    stype = line[3:6]
    parser = PARSERS.get(stype)
    if parser is None:
        return None
    star = line.rfind(b"*")
    if star < 0 or len(line) < star + 3:
        return None
    calc = 0
    for b in line[1:star]:
        calc ^= b
    try:
        if calc != int(line[star + 1:star + 3], 16):
            return None
        fields = line[:star].decode("ascii").split(",")
    except (ValueError, UnicodeError):
        return None
    parser(fields)
    return stype


# Math and derived values
def median(vals):
    o = sorted(vals)
    n = len(o)
    m = n // 2
    return o[m] if n % 2 else (o[m - 1] + o[m]) / 2.0


def smooth_altitude(v):
    if v is None:
        return None
    altitude_samples.append(v)
    if len(altitude_samples) > ALTITUDE_WINDOW:
        altitude_samples.pop(0)
    return median(altitude_samples)


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_R * math.asin(math.sqrt(a))


def bearing_deg(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def compass(deg):
    return COMPASS[int((deg + 11.25) // 22.5) % 16]


def maidenhead(lat, lon):
    lon += 180.0
    lat += 90.0
    a, b = int(lon // 20), int(lat // 10)
    lon -= a * 20
    lat -= b * 10
    c, d = int(lon // 2), int(lat)
    lon -= c * 2
    lat -= d
    e, f = int(lon * 12), int(lat * 24)
    return "{}{}{}{}{}{}".format(chr(65 + a), chr(65 + b), c, d,
                                 chr(97 + e), chr(97 + f))


def local_datetime():
    # UTC time + RMC date -> local (IST) datetime string, handles day rollover
    utc, date = S["utc"], S["date"]
    if not utc or not date or len(utc) < 6 or len(date) < 6:
        return None
    try:
        t = time.mktime((2000 + int(date[4:6]), int(date[2:4]), int(date[0:2]),
                         int(utc[0:2]), int(utc[2:4]), int(utc[4:6]),
                         0, 0)) + TZ_OFFSET_S
        return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*time.localtime(t)[:6])
    except (ValueError, OverflowError):
        return None


def fix_name():
    return FIX_NAMES.get(S["fix_type"], "?")


def dop_quality(h):
    if h is None:
        return "?"
    if h < 1:
        return "ideal"
    if h < 2:
        return "excellent"
    if h < 5:
        return "good"
    if h < 10:
        return "moderate"
    if h < 20:
        return "fair"
    return "poor"


def fmt(v, spec="{:.2f}"):
    return spec.format(v) if v is not None else "-"


# Tracking (trip, max speed, vertical speed, geofence); runs once per fixed epoch
def update_tracking(now_ms):
    global prev_pos, trip_m, max_kmh, home
    global prev_alt, prev_alt_ms, vspeed, geofence_alerted, filt_alt, move_count

    lat, lon = S["lat"], S["lon"]
    speed = S["speed_kmh"]
    filt_alt = smooth_altitude(S["alt"])

    if home is None:
        home = (lat, lon)

    # Motion counts only after several consecutive epochs above the speed threshold
    move_count = move_count + 1 if (speed or 0) >= MOVING_KMH else 0
    moving = move_count >= MOVING_CONFIRM

    if prev_pos is None:
        prev_pos = (lat, lon)
    elif moving:
        d = haversine_m(prev_pos[0], prev_pos[1], lat, lon)
        gate = max(MIN_MOVE_M, HDOP_JITTER_K * (S["hdop"] or 0))
        if d >= gate:
            trip_m += d
            prev_pos = (lat, lon)
    else:
        prev_pos = (lat, lon)       # stationary: follow the drift so it never accumulates

    if moving and speed > max_kmh:
        max_kmh = speed

    # Vertical speed over >= 5 s windows
    if filt_alt is not None:
        if prev_alt is None:
            prev_alt, prev_alt_ms = filt_alt, now_ms
        else:
            dt = time.ticks_diff(now_ms, prev_alt_ms) / 1000.0
            if dt >= 5:
                vspeed = (filt_alt - prev_alt) / dt
                prev_alt, prev_alt_ms = filt_alt, now_ms

    if GEOFENCE_RADIUS_M is not None:
        dist = haversine_m(home[0], home[1], lat, lon)
        if dist > GEOFENCE_RADIUS_M:
            if not geofence_alerted:
                print("\n!!! GEOFENCE BREACH: {:.0f} m from start point".format(dist))
                geofence_alerted = True
        else:
            geofence_alerted = False


# Display
def display():
    lat, lon, alt = S["lat"], S["lon"], S["alt"]
    speed = S["speed_kmh"]

    print("\n" + SEP)
    print("GPS FIX  ({} | Q={})".format(fix_name(), S["fix"]))
    print(SEP)

    ldt = local_datetime()
    print("UTC time      :", S["utc"])
    if ldt:
        print("Local (IST)   :", ldt)

    print("Latitude      : {:.6f}".format(lat))
    print("Longitude     : {:.6f}".format(lon))
    print("Grid locator  :", maidenhead(lat, lon))
    print("Maps          : https://maps.google.com/?q={:.6f},{:.6f}".format(lat, lon))

    if alt is not None:
        print("Altitude MSL  : {:.1f} m raw | {:.1f} m filtered".format(alt, filt_alt))
        if S["geoid"] is not None:
            print("Ellipsoid ht. : {:.1f} m (geoid sep {:.1f} m)".format(
                alt + S["geoid"], S["geoid"]))
    if vspeed is not None:
        print("Vertical speed: {:+.2f} m/s".format(vspeed))

    if speed is not None:
        print("Speed         : {:.1f} km/h ({:.1f} m/s)".format(speed, speed / 3.6))
        if S["course"] is not None and speed >= MOVING_KMH:
            print("Course        : {:.1f} deg {}".format(S["course"], compass(S["course"])))
        else:
            print("Course        : n/a (stationary)")

    print("Satellites    : {} used / {} in view".format(S["sats_used"], S["in_view"]))
    print("DOP           : H={} P={} V={}  [{}]".format(
        fmt(S["hdop"]), fmt(S["pdop"]), fmt(S["vdop"]), dop_quality(S["hdop"])))

    sats = S["sat_list"]
    if sats:
        tracked = [s["snr"] for s in sats if s["snr"] > 0]
        if tracked:
            print("Signal        : {} tracked, avg SNR {:.1f} dB-Hz".format(
                len(tracked), sum(tracked) / len(tracked)))
        print("  PRN  Elev  Azim  SNR  Used")
        used_prns = S["used_prns"]
        for s in sorted(sats, key=lambda x: -x["snr"]):
            print("  {:>3}  {:>3}   {:>3}   {:>3}  {}".format(
                s["prn"], s["elev"], s["az"],
                "--" if s["snr"] < 0 else s["snr"],
                "*" if s["prn"] in used_prns else ""))

    print("Trip distance : {:.1f} m | Max speed {:.1f} km/h".format(trip_m, max_kmh))
    if home is not None:
        print("From start    : {:.1f} m".format(haversine_m(home[0], home[1], lat, lon)))
    if TARGET is not None:
        brg = bearing_deg(lat, lon, TARGET[0], TARGET[1])
        print("Target        : {:.1f} m @ {:.0f} deg {}".format(
            haversine_m(lat, lon, TARGET[0], TARGET[1]), brg, compass(brg)))

    if ttff_s is not None:
        print("TTFF          : {:.0f} s | Fix uptime {:.0f}%".format(
            ttff_s, 100.0 * gga_fixed / max(gga_total, 1)))


# CSV logging
def log_row():
    global log_header_needed
    try:
        # Check for existing file only once
        if log_header_needed is None:
            try:
                os.stat(LOG_FILE)
                log_header_needed = False
            except OSError:
                log_header_needed = True
        with open(LOG_FILE, "a") as fh:
            if log_header_needed:
                fh.write("utc,date,lat,lon,alt_m,speed_kmh,course,sats,hdop,fix_type\n")
                log_header_needed = False
            fh.write("{},{},{:.6f},{:.6f},{},{},{},{},{},{}\n".format(
                S["utc"], S["date"], S["lat"], S["lon"],
                "" if S["alt"] is None else S["alt"],
                fmt(S["speed_kmh"]) if S["speed_kmh"] is not None else "",
                "" if S["course"] is None else S["course"],
                S["sats_used"],
                "" if S["hdop"] is None else S["hdop"],
                S["fix_type"]))
    except OSError as e:
        print("Log error:", e)


# Main loop
print("\n" + SEP)
print("        NEO-6M GPS DIAGNOSTIC (GGA/RMC/GSA/GSV)")
print(SEP)
print("UART{}: GP{} TX / GP{} RX @ {} baud".format(UART_ID, TX_PIN, RX_PIN, BAUDRATE))
print("Waiting for data...\n")

try:
    while True:
        line = gps.readline()
        if not line:
            continue

        # GGA marks the end of each epoch's core data
        if handle_sentence(line.strip()) != b"GGA":
            continue

        gga_total += 1
        has_fix = S["fix"] > 0 and S["lat"] is not None and S["lon"] is not None
        now = time.ticks_ms()

        if has_fix:
            gga_fixed += 1
            if last_fix_state is not True:
                print("\nGPS fix acquired!")
                if ttff_s is None:
                    ttff_s = time.ticks_diff(now, start_ms) / 1000.0
                last_report = time.ticks_add(now, -REPORT_INTERVAL_MS)
            last_fix_state = True

            update_tracking(now)

            if time.ticks_diff(now, last_report) >= REPORT_INTERVAL_MS:
                display()
                last_report = now

            if LOG_TO_FILE and time.ticks_diff(now, last_log) >= LOG_INTERVAL_MS:
                log_row()
                last_log = now
        else:
            if last_fix_state is not False:
                print("\nGPS FIX LOST / SEARCHING")
                altitude_samples.clear()
            last_fix_state = False

            if time.ticks_diff(now, last_no_fix) >= NO_FIX_INTERVAL_MS:
                print("Searching | Sats used: {} | In view: {} | Fix type: {}".format(
                    S["sats_used"], S["in_view"], fix_name()))
                last_no_fix = now

except KeyboardInterrupt:
    print("\nGPS monitor stopped by user.")

finally:
    gps.deinit()
    print("GPS UART closed.")