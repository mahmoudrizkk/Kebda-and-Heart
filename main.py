import network
import machine
import time
import urequests
from ssd1306 import SSD1306_I2C
from ota import OTAUpdater
from WIFI_CONFIG import SSID, PASSWORD

from machine import I2C, Pin
from i2c_lcd import I2cLcd

# OLED size
WIDTH = 128
HEIGHT = 64

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# I2C & OLED init
i2c = machine.I2C(0, scl=machine.Pin(5), sda=machine.Pin(4), freq=400000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
# i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
# devices = i2c.scan()
# print("I2C devices found:", devices)
# lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Wi-Fi credentials
SSID = "POCO"
PASSWORD = "qwerty123"

# Keypad 4x4
ROW_PINS = [6, 7, 8, 9]
COL_PINS = [10, 11, 12, 13]
KEYS = [
    ['1', '4', '7', '*'],
    ['2', '5', '8', '0'],
    ['3', '6', '9', '#'],
    ['A', 'B', 'C', 'D']
]
rows = [machine.Pin(pin, machine.Pin.OUT) for pin in ROW_PINS]
cols = [machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP) for pin in COL_PINS]

# Wi-Fi setup
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# UART setup
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))  # Adjust as needed

last_status = None

def connect_wifi():
#     lcd.clear()
#     lcd.putstr("Connecting Wi-Fi")
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        for _ in range(20):
            if wlan.isconnected():
                break
            time.sleep(0.5)
    update_wifi_status(force=True)

def update_wifi_status(force=False):
    global last_status
    status = wlan.isconnected()
    if force or status != last_status:
        oled.fill_rect(0, 50, WIDTH, 14, 0)  # Always clear line before writing
        if status:
            oled.text("WiFi: Connected", 0, 50)
        else:
            oled.text("WiFi: Disconn.", 0, 50)
        oled.show()
        last_status = status


# def update_wifi_status(force=False):
#     global last_status
#     status = wlan.isconnected()
#     if force or status != last_status:
#         if status:
#             oled.fill_rect(0, 10, WIDTH, 54, 0)
#             oled.text("WiFi: Connected ", 0, 50)
#             oled.show()
# #             lcd.move_to(1, 0)  # Column 0, Row 1 (second row)
# #             lcd.putstr("WiFi: Connected ")
#         else:
#             oled.fill_rect(0, 10, WIDTH, 54, 0)
#             oled.text("WiFi: Disconn. ", 0, 50)
#             oled.show()
# #             lcd.move_to(1, 0)  # Column 0, Row 1 (second row)
# #             lcd.putstr("WiFi: Disconn.  ")
#         last_status = status

def scan_keypad():
    for r_idx, row in enumerate(rows):
        for r in rows:
            r.value(1)
        row.value(0)
        for c_idx, col in enumerate(cols):
            if col.value() == 0:
                time.sleep_ms(20)
                if col.value() == 0:
                    return KEYS[r_idx][c_idx]
    return None

# def send_number(number):
#     #http://shatat-ue.runasp.net/api/Devices/Offals?weight=12&type=1&machineid=1
#     url = f"http://shatat-ue.runasp.net/api/Devices/TEST?inputNumber={number}"
#     try:
#         update_wifi_status()
#         #lcd.clear()
#         lcd.move_to(0, 0)
#         lcd.putstr(" " * 16)
#         lcd.move_to(0, 0)
#         lcd.putstr("Sending:" + number)
# 
#         response = urequests.get(url)
#         text = response.text
#         response.close()
# 
#         #lcd.clear()
#         lcd.move_to(0, 0)
#         lcd.putstr(" " * 16)
#         lcd.move_to(0, 0)
#         lcd.putstr("Response:" + text[:16])
#         time.sleep(3)
# 
#     except Exception as e:
#        # lcd.clear()
#         lcd.move_to(0, 0)
#         lcd.putstr(" " * 16)
#         lcd.move_to(0, 0)
#         lcd.putstr("Send failed:" + str(e)[:16])
#         time.sleep(2)


def send_number(weight, type_):
    #http://shatat-ue.runasp.net/api/Devices/VacuumOutput?weight=12&type=1&machineid=1
    #http://shatat-ue.runasp.net/api/Devices/MiscarriageItem?weight=2.5&type=1&machineid=1
    url = f"http://shatat-ue.runasp.net/api/Devices/MiscarriageItem?weight={weight}&type={type_}&machineid=1"
    
    try:
        update_wifi_status()
        
        # Clear LCD first line
#         lcd.move_to(0, 0)
#         lcd.putstr(" " * 16)
        
        # Show sending info
#         lcd.move_to(0, 0)
#         lcd.putstr(f"Sending:{weight}")

        # Send the GET request
        response = urequests.get(url)
        text = response.text
        response.close()

        # Clear LCD and display response
#         lcd.move_to(0, 0)
#         lcd.putstr(" " * 16)
#         lcd.move_to(0, 0)
#         lcd.putstr("Response:" + text[:16])
        oled.text(text[:16],0,30)
        oled.show()
        time.sleep(3)
        oled.fill_rect(0, 10, WIDTH, 54, 0)

    except Exception as e:
        # Display error message
#         lcd.move_to(0, 0)
#         lcd.putstr(" " * 16)
#         lcd.move_to(0, 0)
#         lcd.putstr("Send failed:" + str(e)[:16])
        time.sleep(2)


def flush_uart():
    while uart.any():
        uart.read()  # discard all old bytes

def receive_number():
    flush_uart()
    buffer = b""
    while True:
        if uart.any():
            char = uart.read(1)
            if char == b'\r':
                break
            buffer += char
        time.sleep_ms(10)
    whole_weight = buffer.decode().strip()
    indexplus = whole_weight.find('+')
    indexK = whole_weight.find('k')
    weight = whole_weight[indexplus+1:indexK]
    weight = weight.replace(' ', '')
    return weight

def extract_between_plus_and_k(text = "+ k"):
    try:
        start = text.index('+') + 1
        end = text.index('k', start)
        return text[start:end].strip()
    except ValueError:
        # If '+' or 'K' not found, return empty string or None
        return ''

def trigger_ota_update():
    oled.fill(0)
    oled.text("Starting OTA...", 0, 10)
    update_wifi_status(force=True)
    oled.show()
    try:
        firmware_url = "https://github.com/mahmoudrizkk/Kebda-and-Heart/"
        ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "main.py")
        ota_updater.download_and_install_update_if_available()
    except Exception as e:
        oled.fill_rect(0, 0, WIDTH, 50, 0)
        oled.text("OTA Failed", 0, 10)
        oled.text(str(e)[:16], 0, 20)
        update_wifi_status()
        oled.show()
        time.sleep(3)
        return

    # If successful, reboot is handled by OTA, or restart manually:
    machine.reset()


def main():
    connect_wifi()

    while True:
        number_buffer = ""
        selected_type = None
        last_key = None

        # Step 1: Prompt for type selection
        oled.fill(0)
        oled.text("Select type:", 0, 0)
        oled.text("1: Liverr", 0, 10)
        oled.text("2: Heartt", 0, 20)
        update_wifi_status(force=True)  # Show status at bottom
        oled.show()

        # Wait for type selection

        while selected_type is None:
            update_wifi_status()
            key = scan_keypad()

            if key == '1':
                selected_type = 1
            elif key == '2':
                selected_type = 2
            elif key == '*':
                trigger_ota_update()  # 🚀 Trigger OTA when * is pressed

            if key:
                time.sleep_ms(300)

        oled.fill_rect(0, 0, WIDTH, 50, 0)
        oled.text("Selected:", 0, 0)
        oled.text("Liver" if selected_type == 1 else "Kebda", 0, 10)
        oled.text("Waiting weight...", 0, 30)
        update_wifi_status()
        oled.show()

        # Step 2: Receive weight from UART
#         received_weight = receive_number()
        received_weight = "13254"

        oled.fill_rect(0, 0, WIDTH, 50, 0)
        oled.text("Weight:", 0, 0)
        oled.text(received_weight[:16], 0, 10)
        update_wifi_status()
        oled.show()
        time.sleep(1)

        # Step 3: Send to server and show response
        try:
            url = f"http://shatat-ue.runasp.net/api/Devices/MiscarriageItem?weight={received_weight}&type={selected_type}&machineid=1"
            response = urequests.get(url)
            response_text = response.text[:16]
            response.close()

            oled.fill_rect(0, 0, WIDTH, 50, 0)
            oled.text("Sent!", 0, 0)
            oled.text("Response:", 0, 10)
            oled.text(response_text, 0, 20)

        except Exception as e:
            oled.fill_rect(0, 0, WIDTH, 50, 0)
            oled.text("Error sending", 0, 0)
            oled.text(str(e)[:16], 0, 10)

        update_wifi_status()
        oled.show()
        time.sleep(3)

        # Step 4: Restart
        oled.fill_rect(0, 0, WIDTH, 50, 0)
        oled.text("Restarting...", 0, 0)
        update_wifi_status()
        oled.show()
        time.sleep(2)



# def main():
#     connect_wifi()
#     number_buffer = ""
#     last_key = None
# 
#     #lcd.clear()
# #     lcd.move_to(0, 0)
# #     lcd.putstr(" " * 16)
# #     lcd.move_to(0, 0)
# #     lcd.putstr("Enter number:")
#     oled.text("Enter number:", 0, 10)
#     oled.show()
#     while True:
#         update_wifi_status()
# 
#         key = scan_keypad()
#         if key and key != last_key:
#             if key == 'D':  # ENTER
#                 if number_buffer:
#                     #lcd.clear()
# #                     lcd.move_to(0, 0)
# #                     lcd.putstr(" " * 16)
# #                     lcd.move_to(0, 0)
# #                     lcd.putstr("Waiting weight")
#                     oled.text("Waiting weight", 0, 30)
#                     oled.show()
# #                     received = receive_number()
#                     received = "1234"
#                    # lcd.clear()
# #                     lcd.move_to(0, 0)
# #                     lcd.putstr(" " * 16)
# #                     lcd.move_to(0, 0)
#                     if received:
#                         oled.fill_rect(0, 10, WIDTH, 54, 0)
#                         oled.text("Received:", 0, 10)
#                         oled.text(received, 0, 20)
#                         oled.show()
# #                         lcd.putstr("Received:" + received[:16])
#                     time.sleep(1)
#                     send_number(received,number_buffer)
#                     time.sleep(2)
#                     number_buffer = ""
#                     #lcd.clear()
# #                     lcd.move_to(0, 0)
# #                     lcd.putstr(" " * 16)
# #                     lcd.move_to(0, 0)
# #                     lcd.putstr("Enter number:")
#             elif key in '0123456789ABC#':
#                 number_buffer += key
#                 #lcd.clear()
# #                 lcd.move_to(0, 0)
# #                 lcd.putstr(" " * 16)
# #                 lcd.move_to(0, 0)
# #                 lcd.putstr("Input:" + number_buffer[:16])
#                 oled.text(number_buffer[:16], 0, 20)
#                 oled.show()
#             elif key == '*':  # Backspace
#                 number_buffer = number_buffer[:-1]
#                # lcd.clear()
# #                 lcd.move_to(0, 0)
# #                 lcd.putstr(" " * 16)
# #                 lcd.move_to(0, 0)
# #                 lcd.putstr("Input:" + number_buffer[:16])
#                 oled.text("            ", 0, 20)
#                 oled.show()
#                 oled.text(number_buffer[:16], 0, 20)
#                 oled.show()
#             last_key = key
#         elif not key:
#             last_key = None
# 
#         time.sleep_ms(100)

def main2():
#     connect_wifi()
    while True:
#         update_wifi_status()
        whole_weight = receive_number()
        indexplus = whole_weight.find('+')
        indexK = whole_weight.find('k')
#         weight = extract_between_plus_and_k(whole_weight)
        weight = whole_weight[indexplus+1:indexK+2]
#         lcd.move_to(0, 0)
#         lcd.putstr(weight)
        weight = ""

if __name__ == "__main__":
    
    main()