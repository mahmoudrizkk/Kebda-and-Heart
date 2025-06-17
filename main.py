import network
import machine
import time
import urequests
# from ssd1306 import SSD1306_I2C  # Commented out OLED
from ota import OTAUpdater
from WIFI_CONFIG import SSID, PASSWORD

from machine import I2C, Pin
from i2c_lcd import I2cLcd

# LCD configuration
I2C_ADDR = 0x27  # Default I2C address for PCF8574
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# I2C & LCD init
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# Initialize LCD with welcome message
lcd.clear()
lcd.putstr("Kebda & Heart")
lcd.move_to(1, 0)
lcd.putstr("System Ready")
time.sleep(2)
lcd.clear()

# Comment out OLED setup
# WIDTH = 128
# HEIGHT = 64
# oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

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

    if not status:
        wlan.connect(SSID, PASSWORD)
        retries = 10
        while not wlan.isconnected() and retries > 0:
            lcd.clear()
            lcd.putstr("WiFi: Reconnecting")
            time.sleep(0.5)
            retries -= 1

    # Update status on LCD
    status = wlan.isconnected()
    if force or status != last_status:
        if status:
            lcd.clear()
            lcd.putstr("WiFi: Connected")
        else:
            lcd.clear()
            lcd.putstr("WiFi: Disconn.")
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
    url = f"http://shatat-ue.runasp.net/api/Devices/TEST?inputNumber=12"
    
    try:
        update_wifi_status()
        
        # Show sending info
        lcd.clear()
        lcd.putstr("Sending:")
        lcd.move_to(1, 0)
        lcd.putstr(str(weight))

        # Send the GET request
        response = urequests.get(url)
        response_text = response.text
        response.close()

        # Parse JSON and extract number
        import json
        try:
            response_json = json.loads(response_text)
            number = str(response_json.get('numberZ', ''))  # Use consistent field name
            if not number:  # If number is empty
                number = '0'  # Set a default value
            lcd.clear()
            lcd.putstr("Number:")
            lcd.move_to(1, 0)
            lcd.putstr(number)
            # Send only the number via UART with consistent termination
            uart.write(number.encode() + b'=\r\n')
        except json.JSONDecodeError:
            # Handle JSON parsing error
            lcd.clear()
            lcd.putstr("JSON Error")
            uart.write(b'ERROR=\r\n')
        except Exception as e:
            # Handle other errors
            lcd.clear()
            lcd.putstr("Error")
            uart.write(b'ERROR=\r\n')

        # Clear LCD and display response
        lcd.clear()
        lcd.putstr("Response:")
        lcd.move_to(1, 0)
        lcd.putstr(response_text[:16])
        time.sleep(3)
        lcd.clear()

    except Exception as e:
        # Display error message
        lcd.clear()
        lcd.putstr("Send failed:")
        lcd.move_to(1, 0)
        lcd.putstr(str(e)[:16])
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
    lcd.clear()
    lcd.putstr("Enter Password:")
    lcd.move_to(1, 0)
    lcd.putstr("D=confirm #=cancel")
    
    password_buffer = ""
    last_key = None
    
    while True:
        update_wifi_status()
        key = scan_keypad()
        
        if key and key != last_key:
            if key == 'D':  # ENTER
                if password_buffer == "1234":  # You can change this password
                    lcd.clear()
                    lcd.putstr("Starting OTA...")
                    try:
                        firmware_url = "https://github.com/mahmoudrizkk/Kebda-and-Heart/"
                        ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "main.py")
                        ota_updater.download_and_install_update_if_available()
                        lcd.clear()
                        lcd.putstr("OTA Success")
                        time.sleep(3)
                    except Exception as e:
                        lcd.clear()
                        lcd.putstr("OTA Failed")
                        lcd.move_to(1, 0)
                        lcd.putstr(str(e)[:16])
                        time.sleep(3)
                    return
                else:
                    lcd.clear()
                    lcd.putstr("Wrong Password!")
                    lcd.move_to(1, 0)
                    lcd.putstr("Try Again")
                    time.sleep(2)
                    password_buffer = ""
                    lcd.clear()
                    lcd.putstr("Enter Password:")
                    lcd.move_to(1, 0)
                    lcd.putstr("D=confirm #=cancel")
            elif key == '#':  # Cancel
                lcd.clear()
                lcd.putstr("Update Cancelled")
                time.sleep(2)
                lcd.clear()
                lcd.putstr("Select type:")
                lcd.move_to(1, 0)
                lcd.putstr("1:Liver 2:Heart")
                return
            elif key in '0123456789ABC':
                password_buffer += key
                lcd.clear()
                lcd.putstr("Enter Password:")
                lcd.move_to(1, 0)
                lcd.putstr("*" * len(password_buffer))
            elif key == '*':  # Backspace
                password_buffer = password_buffer[:-1]
                lcd.clear()
                lcd.putstr("Enter Password:")
                lcd.move_to(1, 0)
                lcd.putstr("*" * len(password_buffer))
            last_key = key
        elif not key:
            last_key = None
        
        time.sleep_ms(100)


def main():
    connect_wifi()

    while True:
        number_buffer = ""
        selected_type = None
        last_key = None

        # Step 1: Prompt for type selection
        lcd.clear()
        lcd.putstr("Select type:")
        lcd.move_to(1, 0)
        lcd.putstr("1:Liver 2:Heart")
        update_wifi_status(force=True)

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

        lcd.clear()
        lcd.putstr("Selected:")
        lcd.move_to(1, 0)
        lcd.putstr("Liver" if selected_type == 1 else "Heart")
        time.sleep(1)
        
        lcd.clear()
        lcd.putstr("Waiting weight...")
        update_wifi_status()

        # Step 2: Receive weight from UART
        # received_weight = receive_number()
        received_weight = "5078"  # For testing

        lcd.clear()
        lcd.putstr("Weight:")
        lcd.move_to(1, 0)
        lcd.putstr(received_weight[:16])
        update_wifi_status()
        time.sleep(1)

        # Step 3: Send to server and show response
        try:
            url = f"http://shatat-ue.runasp.net/api/Devices/TEST?inputNumber=50"
            response = urequests.get(url)
            response_text = response.text
            response.close()

            # Parse JSON and extract number
            import json
            try:
                response_json = json.loads(response_text)
                number = str(response_json.get("numberZ", ''))
                lcd.clear()
                lcd.putstr("Number:")
                lcd.move_to(1, 0)
                lcd.putstr(number)
                # Send only the number via UART
                uart.write(number.encode() + b'=\r\n')
            except:
                # If JSON parsing fails, send the original response
                lcd.clear()
                lcd.putstr("Response:")
                lcd.move_to(1, 0)
                lcd.putstr(response_text[:16])
                uart.write(response_text.encode() + b'\r\n')

        except Exception as e:
            lcd.clear()
            lcd.putstr("Error sending")
            lcd.move_to(1, 0)
            lcd.putstr(str(e)[:16])

        update_wifi_status()
        time.sleep(3)

        # Step 4: Restart
        lcd.clear()
        lcd.putstr("Success!")
        update_wifi_status()
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