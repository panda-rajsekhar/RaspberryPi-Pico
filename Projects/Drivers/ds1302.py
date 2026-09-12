from machine import Pin
from micropython import const

# Register addresses (write form)
_REG_SECOND  = const(0x80)
_REG_MINUTE  = const(0x82)
_REG_HOUR    = const(0x84)
_REG_DAY     = const(0x86)
_REG_MONTH   = const(0x88)
_REG_WEEKDAY = const(0x8A)
_REG_YEAR    = const(0x8C)
_REG_WP      = const(0x8E)
_REG_CTRL    = const(0x90)
_REG_RAM     = const(0xC0)

# Burst commands
_BURST_WRITE = const(0xBE)
_BURST_READ  = const(0xBF)

class DS1302:
    def __init__(self, clk, dio, cs):
        self.clk = clk
        self.dio = dio
        self.cs  = cs

        # Initialise pins
        self.clk.init(Pin.OUT, value=0)
        self.cs.init(Pin.OUT, value=0)
        self.dio.init(Pin.OUT, value=0)

        # Cache the .value methods (big speed win on bit-banging)
        self._clk = self.clk.value
        self._dio = self.dio.value
        self._cs  = self.cs.value

    # ---------- low-level helpers ----------
    def _dec2bcd(self, val):
        return (val // 10) << 4 | (val % 10)

    def _bcd2dec(self, val):
        return (val >> 4) * 10 + (val & 0x0F)

    def _write_byte(self, dat):
        self.dio.init(Pin.OUT)
        for i in range(8):
            self._dio((dat >> i) & 1)
            self._clk(1)
            self._clk(0)

    def _read_byte(self):
        self.dio.init(Pin.IN)
        d = 0
        for i in range(8):
            d |= self._dio() << i
            self._clk(1)
            self._clk(0)
        return d

    def _get_reg(self, reg):
        self._cs(1)
        self._write_byte(reg | 1)          # read command
        t = self._read_byte()
        self._cs(0)
        return t

    def _set_reg(self, reg, dat):
        self._cs(1)
        self._write_byte(reg)              # write command
        self._write_byte(dat)
        self._cs(0)

    def _wr(self, reg, dat):
        """Write one register with write-protect handling."""
        self._set_reg(_REG_WP, 0x00)
        self._set_reg(reg, dat)
        self._set_reg(_REG_WP, 0x80)

    # ---------- public API ----------
    def start(self):
        t = self._get_reg(_REG_SECOND)
        self._wr(_REG_SECOND, t & 0x7F)

    def stop(self):
        t = self._get_reg(_REG_SECOND)
        self._wr(_REG_SECOND, t | 0x80)

    def second(self, second=None):
        if second is None:
            return self._bcd2dec(self._get_reg(_REG_SECOND) & 0x7F)
        self._wr(_REG_SECOND, self._dec2bcd(second % 60))

    def minute(self, minute=None):
        if minute is None:
            return self._bcd2dec(self._get_reg(_REG_MINUTE))
        self._wr(_REG_MINUTE, self._dec2bcd(minute % 60))

    def hour(self, hour=None):
        if hour is None:
            return self._bcd2dec(self._get_reg(_REG_HOUR) & 0x3F)
        self._wr(_REG_HOUR, self._dec2bcd(hour % 24))

    def weekday(self, weekday=None):
        if weekday is None:
            return self._bcd2dec(self._get_reg(_REG_WEEKDAY))
        self._wr(_REG_WEEKDAY, self._dec2bcd(weekday % 8))

    def day(self, day=None):
        if day is None:
            return self._bcd2dec(self._get_reg(_REG_DAY))
        self._wr(_REG_DAY, self._dec2bcd(day % 32))

    def month(self, month=None):
        if month is None:
            return self._bcd2dec(self._get_reg(_REG_MONTH))
        self._wr(_REG_MONTH, self._dec2bcd(month % 13))

    def year(self, year=None):
        if year is None:
            return self._bcd2dec(self._get_reg(_REG_YEAR)) + 2000
        self._wr(_REG_YEAR, self._dec2bcd(year % 100))

    def date_time(self, dat=None):
        """
        Get or set the full date/time.
        Format: [year, month, day, weekday, hour, minute, second]
        Uses burst mode for maximum speed.
        """
        if dat is None:
            # Burst read
            self._cs(1)
            self._write_byte(_BURST_READ)
            sec  = self._read_byte()
            minu = self._read_byte()
            hour = self._read_byte()
            day  = self._read_byte()
            mon  = self._read_byte()
            wday = self._read_byte()
            year = self._read_byte()
            self._cs(0)                     # WP byte is ignored

            return [
                self._bcd2dec(year) + 2000,
                self._bcd2dec(mon),
                self._bcd2dec(day),
                self._bcd2dec(wday),
                self._bcd2dec(hour & 0x3F),
                self._bcd2dec(minu),
                self._bcd2dec(sec & 0x7F)
            ]
        else:
            # Burst write – disable WP only once
            self._set_reg(_REG_WP, 0x00)
            self._cs(1)
            self._write_byte(_BURST_WRITE)
            self._write_byte(self._dec2bcd(dat[6] % 60))   # second
            self._write_byte(self._dec2bcd(dat[5] % 60))   # minute
            self._write_byte(self._dec2bcd(dat[4] % 24))   # hour
            self._write_byte(self._dec2bcd(dat[2] % 32))   # day
            self._write_byte(self._dec2bcd(dat[1] % 13))   # month
            self._write_byte(self._dec2bcd(dat[3] % 8))    # weekday
            self._write_byte(self._dec2bcd(dat[0] % 100))  # year
            self._write_byte(0x80)                         # write-protect on
            self._cs(0)

    def ram(self, reg, dat=None):
        addr = _REG_RAM + (reg % 31) * 2
        if dat is None:
            return self._get_reg(addr)
        self._wr(addr, dat)