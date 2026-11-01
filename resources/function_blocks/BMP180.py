# BMP180.py - DINASORE function block for the Bosch BMP180 I2C sensor.
#
# Interface comes from BMP180.fbt:
#   inputs : I2C_ID, SCL, SDA, OSS, ADDR
#   outputs: TEMP (degC), PRESS (Pa), ALT (m), STATUS
#   events : REQ -> CNF
#
# Event driven behaviour: every REQ performs one temperature conversion and
# one pressure conversion, applies the Bosch compensation formulas and
# publishes the result together with CNF.
#
# The block only uses the MicroPython core modules (time + machine), so it
# can also be imported on a PC for off-target tests.

import time

try:
    from machine import I2C, Pin
except ImportError:  # CPython - desktop simulation and unit tests
    I2C = None
    Pin = None


def _sleep_ms(duration):
    """Sleep for the given number of milliseconds."""
    try:
        time.sleep_ms(duration)
    except AttributeError:  # CPython
        time.sleep(duration / 1000.0)


def _shr(value, bits):
    """Arithmetic right shift, including for negative intermediate values."""
    return value >> bits


def _div(numerator, denominator):
    """Integer division with C semantics (truncation toward zero)."""
    if denominator == 0:
        raise ZeroDivisionError('division by zero')
    quotient = abs(numerator) // abs(denominator)
    return -quotient if (numerator < 0) != (denominator < 0) else quotient


def _u16(msb, lsb):
    """Big endian unsigned 16 bit value."""
    return (msb << 8) | lsb


def _s16(msb, lsb):
    """Big endian signed 16 bit value (two's complement)."""
    value = (msb << 8) | lsb
    return value - 65536 if value > 32767 else value


class BMP180:

    schedule_args = ['self', 'event_name', 'event_value',
                     'i2c_id', 'scl', 'sda', 'oss', 'addr']

    # --- BMP180 register map and commands -----------------------------
    REG_CALIB = 0xAA        # 11 calibration words, big endian (AC1..MD)
    REG_CHIP_ID = 0xD0
    REG_CTRL_MEAS = 0xF4
    REG_OUT_MSB = 0xF6
    CMD_TEMP = 0x2E         # start temperature conversion
    CMD_PRESS = 0x34        # start pressure conversion (| OSS << 6)
    CHIP_ID = 0x55

    # --- defaults, used when 4DIAC leaves an input unconnected (None) --
    DEFAULT_I2C_ID = 0
    DEFAULT_SCL = 22        # ESP32 default I2C pins
    DEFAULT_SDA = 21
    DEFAULT_OSS = 3         # ultra high resolution
    DEFAULT_ADDR = 0x77
    I2C_FREQ = 100000       # BMP180 supports up to 400 kHz

    # --- physical constants -------------------------------------------
    SEA_LEVEL_PA = 101325.0
    MIN_PRESSURE_PA = 30000.0       # datasheet operating range 300..1100 hPa
    MAX_PRESSURE_PA = 110000.0

    # Conversion times from the datasheet (4.5 ms / 4.5-25.5 ms rounded up).
    TEMP_DELAY_MS = 5
    PRESS_DELAY_MS = (5, 8, 14, 26)     # index = OSS 0..3

    def __init__(self):
        self.i2c = None                 # bus object, replaceable for tests
        self._bus_key = None            # (bus id, scl pin, sda pin)
        self._addr = self.DEFAULT_ADDR
        self._oss = self.DEFAULT_OSS
        self._cal = None                # cached calibration words
        self._temp = 0.0                # last good readings
        self._press = 0.0
        self._alt = 0.0

    # ------------------------------------------------------------------
    # entry point called by the DINASORE runtime
    # ------------------------------------------------------------------
    def schedule(self, event_name, event_value, i2c_id, scl, sda, oss, addr):
        if event_name != 'REQ':
            return None

        try:
            self._configure(i2c_id, scl, sda, oss, addr)
            self._read_calibration()
            raw_temp = self._read_raw_temperature()
            raw_press = self._read_raw_pressure()
            temp, press = self._compensate(raw_temp, raw_press)
            self._check_range(temp, press)
            alt = self._altitude(press)
        except Exception as error:
            # Keep publishing the last valid measurement so that a sensor
            # glitch does not push None into the downstream blocks.
            return [event_value, self._temp, self._press, self._alt,
                    'ERROR: ' + str(error)]

        self._temp = temp
        self._press = press
        self._alt = alt
        return [event_value, temp, press, alt, 'OK']

    def __del__(self):
        try:
            self._close_bus()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # bus handling
    # ------------------------------------------------------------------
    def _configure(self, i2c_id, scl, sda, oss, addr):
        bus_id = self._as_int(i2c_id, self.DEFAULT_I2C_ID)
        scl_pin = self._as_int(scl, self.DEFAULT_SCL)
        sda_pin = self._as_int(sda, self.DEFAULT_SDA)

        for pin in (scl_pin, sda_pin):
            if not 0 <= pin <= 39:
                raise ValueError('invalid pin {0}'.format(pin))
        if scl_pin == sda_pin:
            raise ValueError('SCL and SDA must differ')

        self._oss = self._clamp_oss(oss)
        self._set_addr(addr)

        key = (bus_id, scl_pin, sda_pin)
        if key != self._bus_key:
            self._close_bus()
            self.i2c = self._open_bus(bus_id, scl_pin, sda_pin)
            self._bus_key = key

    def _open_bus(self, bus_id, scl_pin, sda_pin):
        if I2C is None:
            raise OSError('machine.I2C is not available')
        try:
            return I2C(bus_id, scl=Pin(scl_pin), sda=Pin(sda_pin),
                       freq=self.I2C_FREQ)
        except (OSError, ValueError):
            # Hardware I2C peripheral busy or not usable for these pins:
            # fall back to the bit-banged implementation.
            from machine import SoftI2C
            return SoftI2C(scl=Pin(scl_pin), sda=Pin(sda_pin),
                           freq=self.I2C_FREQ)

    def _close_bus(self):
        bus, self.i2c = self.i2c, None
        self._cal = None
        if bus is not None and hasattr(bus, 'deinit'):
            try:
                bus.deinit()
            except Exception:
                pass

    def _read_mem(self, register, length):
        try:
            return self.i2c.readfrom_mem(self._addr, register, length)
        except Exception as error:
            raise OSError('I2C read 0x{0:02x} on 0x{1:02x} failed: {2}'
                          .format(register, self._addr, error))

    def _write_mem(self, register, value):
        try:
            self.i2c.writeto_mem(self._addr, register, bytes((value,)))
        except Exception as error:
            raise OSError('I2C write 0x{0:02x} on 0x{1:02x} failed: {2}'
                          .format(register, self._addr, error))

    # ------------------------------------------------------------------
    # sensor access
    # ------------------------------------------------------------------
    def _read_calibration(self):
        if self._cal is not None:
            return

        chip_id = self._read_mem(self.REG_CHIP_ID, 1)[0]
        if chip_id != self.CHIP_ID:
            raise OSError('no BMP180 at 0x{0:02x} (chip id 0x{1:02x})'
                          .format(self._addr, chip_id))

        data = self._read_mem(self.REG_CALIB, 22)
        calibration = []
        for index in range(0, 22, 2):
            read_word = _u16 if index in (6, 8, 10) else _s16
            calibration.append(read_word(data[index], data[index + 1]))

        empty = 0
        for value in calibration:
            if value == 0:
                empty += 1
        if empty == len(calibration):
            raise OSError('calibration data reads as zero')

        self._cal = calibration

    def _read_raw_temperature(self):
        self._write_mem(self.REG_CTRL_MEAS, self.CMD_TEMP)
        _sleep_ms(self.TEMP_DELAY_MS)
        data = self._read_mem(self.REG_OUT_MSB, 2)
        return _u16(data[0], data[1])

    def _read_raw_pressure(self):
        self._write_mem(self.REG_CTRL_MEAS, self.CMD_PRESS + (self._oss << 6))
        _sleep_ms(self.PRESS_DELAY_MS[self._oss])
        data = self._read_mem(self.REG_OUT_MSB, 3)
        raw = (data[0] << 16) | (data[1] << 8) | data[2]
        return _shr(raw, 8 - self._oss)

    # ------------------------------------------------------------------
    # Bosch compensation formulas (datasheet section "Calculating
    # temperature" / "Calculating pressure"), all integer arithmetic
    # ------------------------------------------------------------------
    def _compensate(self, ut, up):
        ac1, ac2, ac3, ac4, ac5, ac6, b1, b2, mb, mc, md = self._cal

        # Temperature
        x1 = _shr((ut - ac6) * ac5, 15)
        x2 = _div(mc << 11, x1 + md)
        b5 = x1 + x2
        temperature = _shr(b5 + 8, 4) / 10.0

        # Pressure
        b6 = b5 - 4000
        x1 = _shr(b2 * _shr(b6 * b6, 12), 11)
        x2 = _shr(ac2 * b6, 11)
        x3 = x1 + x2
        b3 = _shr(((((ac1 << 2) + x3) << self._oss) + 2), 2)
        x1 = _shr(ac3 * b6, 13)
        x2 = _shr(b1 * _shr(b6 * b6, 12), 16)
        x3 = _shr(x1 + x2 + 2, 2)
        b4 = _shr(ac4 * (x3 + 32768), 15)
        b7 = (up - b3) * _shr(50000, self._oss)

        if b7 < 0x80000000:
            pressure = _div(b7 << 1, b4)
        else:
            pressure = _div(b7, b4) << 1

        x1 = _shr(pressure, 8)
        x1 = _shr(x1 * x1 * 3038, 16)
        x2 = _shr(-7357 * pressure, 16)
        pressure = pressure + _shr(x1 + x2 + 3791, 4)

        return temperature, float(pressure)

    def _check_range(self, temperature, pressure):
        """Reject implausible results, e.g. after a corrupted I2C read."""
        if not -40.0 <= temperature <= 85.0:
            raise ValueError('temperature out of range: ' + str(temperature))
        if not self.MIN_PRESSURE_PA <= pressure <= self.MAX_PRESSURE_PA:
            raise ValueError('pressure out of range: ' + str(pressure))

    def _altitude(self, pressure):
        """International barometric formula, metres above sea level."""
        if pressure <= 0:
            return 0.0
        return 44330.0 * (1.0 - (pressure / self.SEA_LEVEL_PA) ** 0.2425)

    # ------------------------------------------------------------------
    # input normalisation
    # ------------------------------------------------------------------
    @staticmethod
    def _as_int(value, default):
        if value is None:
            return default
        return int(value)

    @staticmethod
    def _clamp_oss(oss):
        if oss is None:
            return BMP180.DEFAULT_OSS
        value = int(oss)
        if value < 0:
            return 0
        if value > 3:
            return 3
        return value

    def _set_addr(self, addr):
        new_addr = self.DEFAULT_ADDR if addr is None else int(addr)
        if new_addr == 0:
            new_addr = self.DEFAULT_ADDR
        new_addr &= 0x7F
        if new_addr != self._addr:
            # A different slave address means a different chip:
            # force the calibration words to be read again.
            self._addr = new_addr
            self._cal = None
