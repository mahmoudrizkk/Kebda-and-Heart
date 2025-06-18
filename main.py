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
lcd.move_to(0, 0)
lcd.putstr("Kebda & Heart")

# Read version from JSON file
try:
    import json
    with open('version.json', 'r') as f:
        version_data = json.load(f)
        version = str(version_data.get('version', 'Unknown'))
    lcd.move_to(1, 0)
    lcd.putstr(f"Version: {version}")
except Exception as e:
    lcd.move_to(1, 0)
    lcd.putstr("Version: Unknown")

time.sleep(2)
lcd.move_to(0, 0)
lcd.putstr("                ")  # Clear first row
lcd.move_to(1, 0)
lcd.putstr("                ")  # Clear second row for WiFi status

# Comment out OLED setup
# WIDTH = 128
# HEIGHT = 64
# oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Wi-Fi credentials
SSID = "SYS-Horizon"
PASSWORD = "9078@horiz"

# Keypad 4x4
COL_PINS = [6, 7, 8, 9]
ROW_PINS = [10, 11, 12, 13]
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
            lcd.move_to(1, 0)
            lcd.putstr("WiFi: Reconnecting")
            time.sleep(0.5)
            retries -= 1

    # Update status on LCD
    status = wlan.isconnected()
    if force or status != last_status:
        lcd.move_to(1, 0)
        lcd.putstr("                ")  # Clear second row
        if status:
            lcd.move_to(1, 0)
            lcd.putstr("WiFi: Connected")
        else:
            lcd.move_to(1, 0)
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


# def send_number(weight, type_):
#     #http://shatat-ue.runasp.net/api/Devices/VacuumOutput?weight=12&type=1&machineid=1
#     #http://shatat-ue.runasp.net/api/Devices/MiscarriageItem?weight=2.5&type=1&machineid=1
#     url = f"http://shatat-ue.runasp.net/api/Devices/TEST?inputNumber=12"
    
#     try:
#         update_wifi_status()
        
#         # Show sending info
#         lcd.move_to(0, 0)
#         lcd.putstr("                ")  # Clear first row
#         lcd.move_to(0, 0)
#         lcd.putstr("Sending:")
#         lcd.move_to(0, 8)
#         lcd.putstr(str(weight)[:8])

#         # Send the GET request
#         response = urequests.get(url)
#         response_text = response.text
#         response.close()

#         # Parse JSON and extract number
#         import json
#         try:
#             response_json = json.loads(response_text)
#             number = str(response_json.get('numberZ', ''))  # Use consistent field name
#             if not number:  # If number is empty
#                 number = '0'  # Set a default value
#             lcd.move_to(0, 0)
#             lcd.putstr("                ")  # Clear first row
#             lcd.move_to(0, 0)
#             lcd.putstr("Number:")
#             lcd.move_to(0, 7)
#             lcd.putstr(number[:9])
#             # Send only the number via UART with consistent termination
#             uart.write(number.encode() + b'=\r\n')
#         except json.JSONDecodeError:
#             # Handle JSON parsing error
#             lcd.move_to(0, 0)
#             lcd.putstr("                ")  # Clear first row
#             lcd.move_to(0, 0)
#             lcd.putstr("JSON Error")
#             uart.write(b'ERROR=\r\n')
#         except Exception as e:
#             # Handle other errors
#             lcd.move_to(0, 0)
#             lcd.putstr("                ")  # Clear first row
#             lcd.move_to(0, 0)
#             lcd.putstr("Error")
#             uart.write(b'ERROR=\r\n')

#         # Clear LCD and display response
#         lcd.move_to(0, 0)
#         lcd.putstr("                ")  # Clear first row
#         lcd.move_to(0, 0)
#         lcd.putstr("Response:")
#         lcd.move_to(0, 9)
#         lcd.putstr(response_text[:7])
#         time.sleep(3)
#         lcd.move_to(0, 0)
#         lcd.putstr("                ")  # Clear first row

#     except Exception as e:
#         # Display error message
#         lcd.move_to(0, 0)
#         lcd.putstr("                ")  # Clear first row
#         lcd.move_to(0, 0)
#         lcd.putstr("Send failed:")
#         lcd.move_to(0, 11)
#         lcd.putstr(str(e)[:5])
#         time.sleep(2)


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
    lcd.move_to(0, 0)
    lcd.putstr("                ")  # Clear first row
    lcd.move_to(0, 0)
    lcd.putstr("Enter Password:")
    lcd.move_to(0, 15)
    lcd.putstr("*")
    
    password_buffer = ""
    last_key = None
    
    while True:
        update_wifi_status()
        key = scan_keypad()
        
        if key and key != last_key:
            if key == 'D':  # ENTER
                if password_buffer == "1234":  # You can change this password
                    lcd.move_to(0, 0)
                    lcd.putstr("                ")  # Clear first row
                    lcd.move_to(0, 0)
                    lcd.putstr("Starting OTA...")
                    try:
                        firmware_url = "https://github.com/mahmoudrizkk/Kebda-and-Heart/"
                        ota_updater = OTAUpdater(SSID, PASSWORD, firmware_url, "main.py")
                        ota_updater.download_and_install_update_if_available()
                        lcd.move_to(0, 0)
                        lcd.putstr("                ")  # Clear first row
                        lcd.move_to(0, 0)
                        lcd.putstr("OTA Success")
                        time.sleep(3)
                    except Exception as e:
                        lcd.move_to(0, 0)
                        lcd.putstr("                ")  # Clear first row
                        lcd.move_to(0, 0)
                        lcd.putstr("OTA Failed")
                        lcd.move_to(0, 10)
                        lcd.putstr(str(e)[:6])
                        time.sleep(3)
                    return
                else:
                    lcd.move_to(0, 0)
                    lcd.putstr("                ")  # Clear first row
                    lcd.move_to(0, 0)
                    lcd.putstr("Wrong Password!")
                    time.sleep(2)
                    password_buffer = ""
                    lcd.move_to(0, 0)
                    lcd.putstr("                ")  # Clear first row
                    lcd.move_to(0, 0)
                    lcd.putstr("Enter Password:")
                    lcd.move_to(0, 15)
                    lcd.putstr("*")
            elif key == '#':  # Cancel
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(0, 0)
                lcd.putstr("Update Cancelled")
                time.sleep(2)
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(0, 0)
                lcd.putstr("Select type:")
                lcd.move_to(0, 8)
                lcd.putstr("1:L 2:H")
                return
            elif key in '0123456789ABC':
                password_buffer += key
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(0, 0)
                lcd.putstr("Enter Password:")
                lcd.move_to(0, 15)
                lcd.putstr("*" * min(len(password_buffer), 1))
            elif key == '*':  # Backspace
                password_buffer = password_buffer[:-1]
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(0, 0)
                lcd.putstr("Enter Password:")
                lcd.move_to(0, 15)
                lcd.putstr("*" * min(len(password_buffer), 1))
            last_key = key
        elif not key:
            last_key = None
        
        time.sleep_ms(100)


def get_last_barcode(selected_type):
    """
    Call the LastBarcodeForLiverAndHeart API to get the last barcode for the selected type
    """
    url = f"http://shatat-ue.runasp.net/api/Devices/LastBarcodeForLiverAndHeart?type={selected_type}"
    
    try:
        update_wifi_status()
        
        # Show sending info
        lcd.move_to(0, 0)
        lcd.putstr("                ")  # Clear first row
        lcd.move_to(0, 0)
        lcd.putstr("Getting barcode...")

        # Send the GET request
        response = urequests.get(url)
        response_text = response.text
        response.close()

        # Parse JSON and extract barcode
        import json
        try:
            response_json = json.loads(response_text)
            barcode = str(response_json.get('message', ''))
            
            if barcode:
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(0, 0)
                lcd.putstr("Barcode:")
                lcd.move_to(0, 8)
                lcd.putstr(barcode[:8])
                
                # Send the barcode via UART
                uart.write(barcode.encode() + b'=\r\n')
                
                time.sleep(3)
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(0, 0)
                lcd.putstr("Barcode sent!")
            else:
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(0, 0)
                lcd.putstr("No barcode found")
                uart.write(b'NO_BARCODE=\r\n')
                
        except json.JSONDecodeError:
            # Handle JSON parsing error
            lcd.move_to(0, 0)
            lcd.putstr("                ")  # Clear first row
            lcd.move_to(0, 0)
            lcd.putstr("JSON Error")
            uart.write(b'ERROR=\r\n')
        except Exception as e:
            # Handle other errors
            lcd.move_to(0, 0)
            lcd.putstr("                ")  # Clear first row
            lcd.move_to(0, 0)
            lcd.putstr("Error")
            uart.write(b'ERROR=\r\n')

        time.sleep(2)
        lcd.move_to(0, 0)
        lcd.putstr("                ")  # Clear first row

    except Exception as e:
        # Display error message
        lcd.move_to(0, 0)
        lcd.putstr("                ")  # Clear first row
        lcd.move_to(0, 0)
        lcd.putstr("Get failed:")
        lcd.move_to(0, 11)
        lcd.putstr(str(e)[:5])
        time.sleep(2)


def trigger_barcode_request():
    """
    Handle B button press - ask for type and get last barcode
    """
    lcd.move_to(0, 0)
    lcd.putstr("                ")  # Clear first row
    lcd.move_to(0, 0)
    lcd.putstr("Get Last Barcode")
    lcd.move_to(1, 0)
    lcd.putstr("Select: 1:L 2:H")
    
    selected_type = None
    last_key = None
    
    while selected_type is None:
        update_wifi_status()
        key = scan_keypad()
        
        if key and key != last_key:
            if key == '1':
                selected_type = 1
            elif key == '2':
                selected_type = 2
            elif key == '#':  # Cancel
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(1, 0)
                lcd.putstr("                ")  # Clear second row
                lcd.move_to(0, 0)
                lcd.putstr("Cancelled")
                time.sleep(2)
                return
            last_key = key
        elif not key:
            last_key = None
        
        time.sleep_ms(100)
    
    if selected_type:
        lcd.move_to(0, 0)
        lcd.putstr("                ")  # Clear first row
        lcd.move_to(1, 0)
        lcd.putstr("                ")  # Clear second row
        lcd.move_to(0, 0)
        lcd.putstr("Type:")
        lcd.move_to(0, 5)
        lcd.putstr("Liver" if selected_type == 1 else "Heart")
        time.sleep(1)
        
        get_last_barcode(selected_type)


def main():
    connect_wifi()

    while True:
        number_buffer = ""
        selected_type = None
        last_key = None

        # Step 1: Prompt for type selection
        update_wifi_status(force=True)
        lcd.move_to(0, 0)
        lcd.putstr("                ")  # Clear first row
        lcd.move_to(0, 0)
        lcd.putstr("Select:")
        lcd.move_to(0, 8)
        lcd.putstr("1:L 2:H")

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
            elif key == 'B':
                trigger_barcode_request()  # 🔍 Get last barcode when B is pressed
                # After barcode request, return to type selection
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(1, 0)
                lcd.putstr("                ")  # Clear second row
                lcd.move_to(0, 0)
                lcd.putstr("Select:")
                lcd.move_to(0, 8)
                lcd.putstr("1:L 2:H")

            if key:
                time.sleep_ms(300)

        lcd.move_to(0, 0)
        lcd.putstr("                ")  # Clear first row
        lcd.move_to(0, 0)
        lcd.putstr("Selected:")
        lcd.move_to(0, 9)
        lcd.putstr("Liver" if selected_type == 1 else "Heart")
        time.sleep(1)
        
        lcd.move_to(0, 0)
        lcd.putstr("                ")  # Clear first row
        lcd.move_to(0, 0)
        lcd.putstr("Waiting weight...")
        update_wifi_status()

        # Step 2: Receive weight from UART
        received_weight = receive_number()
        # received_weight = "5078"  # For testing

        lcd.move_to(0, 0)
        lcd.putstr("                ")  # Clear first row
        lcd.move_to(0, 0)
        lcd.putstr("Weight:")
        lcd.move_to(0, 7)
        lcd.putstr(received_weight[:9])
        update_wifi_status()
        time.sleep(1)

        # Step 3: Send to server and show response
        try:
            url = "http://shatat-ue.runasp.net/api/Devices/LiverAndHeart"
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "type": selected_type,
                "weight": received_weight,
                "machineId": 1
            }

            response = urequests.post(url, headers=headers, data=json.dumps(payload))
            response_text = response.text
            response.close()
      # Parse JSON and extract number
            import json
            try:
                response_json = json.loads(response_text)
                number = str(response_json.get("message", ''))
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(0, 0)
                lcd.putstr("Number:")
                lcd.move_to(0, 7)
                lcd.putstr(number[:9])
                # Send only the number via UART
                uart.write(number.encode() + b'=')
            except:
                # If JSON parsing fails, send the original response
                lcd.move_to(0, 0)
                lcd.putstr("                ")  # Clear first row
                lcd.move_to(0, 0)
                lcd.putstr("Response:")
                lcd.move_to(0, 9)
                lcd.putstr(response_text[:7])
                uart.write(response_text.encode() + b'\r\n')

        except Exception as e:
            lcd.move_to(0, 0)
            lcd.putstr("                ")  # Clear first row
            lcd.move_to(0, 0)
            lcd.putstr("Error:")
            lcd.move_to(0, 6)
            lcd.putstr(str(e)[:10])

        update_wifi_status()
        time.sleep(3)

        # Step 4: Restart
        lcd.move_to(0, 0)
        lcd.putstr("                ")  # Clear first row
        lcd.move_to(0, 0)
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