from lcd_api import LcdApi
from machine import I2C
from time import sleep_ms

# PCF8574 pin mapping to LCD
MASK_RS = 0x01
MASK_RW = 0x02
MASK_E  = 0x04
MASK_BACKLIGHT = 0x08
SHIFT_DATA = 4

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = MASK_BACKLIGHT
        self.i2c.writeto(self.i2c_addr, bytearray([0]))
        sleep_ms(20)

        self.hal_write_init_nibble(0x03)
        sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        sleep_ms(1)
        self.hal_write_init_nibble(0x03)
        sleep_ms(1)
        self.hal_write_init_nibble(0x02)

        super().__init__(num_lines, num_columns)
        self.backlight_on()

    def hal_write_init_nibble(self, nibble):
        byte = ((nibble << SHIFT_DATA) & 0xF0)
        self.pulse(byte)

    def hal_backlight_on(self):
        self.backlight = MASK_BACKLIGHT
        self.i2c.writeto(self.i2c_addr, bytearray([self.backlight]))

    def hal_backlight_off(self):
        self.backlight = 0
        self.i2c.writeto(self.i2c_addr, bytearray([0]))

    def pulse(self, data):
        self.i2c.writeto(self.i2c_addr, bytearray([data | MASK_E | self.backlight]))
        sleep_ms(1)
        self.i2c.writeto(self.i2c_addr, bytearray([(data & ~MASK_E) | self.backlight]))
        sleep_ms(1)

    def hal_write_command(self, cmd):
        self.hal_write(cmd, 0)

    def hal_write_data(self, data):
        self.hal_write(data, MASK_RS)

    def hal_write(self, data, mode):
        high = mode | (data & 0xF0)
        low = mode | ((data << 4) & 0xF0)
        self.pulse(high)
        self.pulse(low)
        
    def backlight_on(self):
        self.hal_backlight_on()

    def backlight_off(self):
        self.hal_backlight_off()


