from machine import Pin, SPI
from time import sleep_ms


# ============================================================
# MFRC522 REGISTERS (MFRC522 datasheet, section 9.3) 
# ============================================================

CommandReg      = 0x01
ComIEnReg       = 0x02
ComIrqReg       = 0x04
ErrorReg        = 0x06
FIFODataReg     = 0x09
FIFOLevelReg    = 0x0A
ControlReg      = 0x0C
BitFramingReg   = 0x0D
CollReg         = 0x0E

ModeReg         = 0x11
TxModeReg       = 0x12
RxModeReg       = 0x13
TxControlReg    = 0x14
TxASKReg        = 0x15

TModeReg        = 0x2A
TPrescalerReg   = 0x2B
TReloadHReg     = 0x2C
TReloadLReg     = 0x2D

VersionReg      = 0x37


# ============================================================
# MFRC522 COMMANDS
# ============================================================

PCD_IDLE        = 0x00
PCD_TRANSCEIVE  = 0x0C
PCD_RESETPHASE  = 0x0F

PICC_REQA       = 0x26
PICC_ANTICOLL   = 0x93


# ============================================================
# SPI SETUP
# ============================================================

spi = SPI(
    0,
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19),
    miso=Pin(16)
)

cs = Pin(17, Pin.OUT, value=1)
rst = Pin(20, Pin.OUT, value=1)


# ============================================================
# LOW LEVEL SPI
# ============================================================

def write_reg(reg, value):
    cs.value(0)
    spi.write(bytes([(reg << 1) & 0x7E, value]))
    cs.value(1)


def read_reg(reg):
    cs.value(0)
    spi.write(bytes([((reg << 1) & 0x7E) | 0x80]))
    value = spi.read(1)[0]
    cs.value(1)
    return value


def set_bit_mask(reg, mask):
    write_reg(reg, read_reg(reg) | mask)


def clear_bit_mask(reg, mask):
    write_reg(reg, read_reg(reg) & (~mask))


# ============================================================
# RESET
# ============================================================

def reset():
    rst.value(0)
    sleep_ms(2)
    rst.value(1)
    sleep_ms(50)

    write_reg(CommandReg, PCD_RESETPHASE)
    sleep_ms(50)


# ============================================================
# MFRC522 INITIALIZATION
# ============================================================

def init_rc522():

    reset()

    write_reg(TModeReg, 0x8D)
    write_reg(TPrescalerReg, 0x3E)

    write_reg(TReloadLReg, 30)
    write_reg(TReloadHReg, 0)

    write_reg(TxASKReg, 0x40)
    write_reg(ModeReg, 0x3D)

    write_reg(TxModeReg, 0x00)
    write_reg(RxModeReg, 0x00)

    # Turn antenna ON
    if (read_reg(TxControlReg) & 0x03) != 0x03:
        set_bit_mask(TxControlReg, 0x03)


# ============================================================
# SEND DATA TO RFID TAG
# ============================================================

def transceive(data, valid_bits=0):

    write_reg(CommandReg, PCD_IDLE)
    write_reg(ComIrqReg, 0x7F)

    write_reg(FIFOLevelReg, 0x80)

    for byte in data:
        write_reg(FIFODataReg, byte)

    write_reg(BitFramingReg, valid_bits)
    write_reg(CommandReg, PCD_TRANSCEIVE)

    set_bit_mask(BitFramingReg, 0x80)

    # Wait for response
    for _ in range(100):
        irq = read_reg(ComIrqReg)

        if irq & 0x30:
            break

        if irq & 0x01:
            break

        sleep_ms(1)

    clear_bit_mask(BitFramingReg, 0x80)

    if read_reg(ErrorReg) & 0x1B:
        return None

    length = read_reg(FIFOLevelReg)

    if length == 0:
        return None

    response = []

    for _ in range(length):
        response.append(read_reg(FIFODataReg))

    return response


# ============================================================
# CHECK FOR RFID CARD
# ============================================================

def request():

    # REQA is 7 bits
    response = transceive([PICC_REQA], 0x07)

    return response


# ============================================================
# READ UID
# ============================================================

def read_uid():

    response = transceive([PICC_ANTICOLL, 0x20])

    if response is None:
        return None

    if len(response) != 5:
        return None

    # Last byte = checksum
    checksum = 0

    for i in range(4):
        checksum ^= response[i]

    if checksum != response[4]:
        return None

    return response[:4]


# ============================================================
# MAIN
# ============================================================

print("MFRC522 test")
print("----------------")

init_rc522()

version = read_reg(VersionReg)

print("Version register:", hex(version))

if version not in (0x00, 0xFF):
    print("RC522 detected! (version 0x%02X)" % version)
else:
    print("RC522 NOT detected — check wiring/power.")

print("----------------")
print("Bring an RFID card/tag near the antenna...")
print()


while True:

    card = request()

    if card is not None:

        uid = read_uid()

        if uid is not None:

            uid_string = ":".join(
                "{:02X}".format(x) for x in uid
            )

            print("RFID TAG DETECTED!")
            print("UID:", uid_string)
            print()

            sleep_ms(1000)

    sleep_ms(100)