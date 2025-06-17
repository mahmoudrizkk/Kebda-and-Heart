import time

class LcdApi:
    # LCD Commands
    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_ENTRY_INC = 0x02
    LCD_ENTRY_SHIFT = 0x01
    LCD_ON_CTRL = 0x08
    LCD_ON_DISPLAY = 0x04
    LCD_ON_CURSOR = 0x02
    LCD_ON_BLINK = 0x01
    LCD_MOVE = 0x10
    LCD_MOVE_DISP = 0x08
    LCD_MOVE_RIGHT = 0x04
    LCD_FUNC = 0x20
    LCD_FUNC_2LINE = 0x08
    LCD_FUNC_5x10DOTS = 0x04
    LCD_FUNC_8BIT = 0x10
    LCD_SET_CGRAM = 0x40
    LCD_SET_DDRAM = 0x80

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cur_line = 0
        self.hal_write_command(self.LCD_FUNC | self.LCD_FUNC_2LINE)
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)
        self.hal_write_command(self.LCD_CLR)
        time.sleep_ms(2)
        self.hal_write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)

    def clear(self):
        self.hal_write_command(self.LCD_CLR)
        time.sleep_ms(2)

    def home(self):
        self.hal_write_command(self.LCD_HOME)
        time.sleep_ms(2)

    def move_to(self, line, col):
        addr = col & 0x3F
        if line & 1:
            addr += 0x40
        self.hal_write_command(self.LCD_SET_DDRAM | addr)

    def putstr(self, string):
        for char in string:
            self.hal_write_data(ord(char))

    def hal_write_command(self, cmd): pass
    def hal_write_data(self, data): pass
