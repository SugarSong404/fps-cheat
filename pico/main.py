import board
import busio
import usb_hid
import time
import random
from adafruit_hid.mouse import Mouse

uart = busio.UART(board.GP4, board.GP5, baudrate=115200)
mouse = Mouse(usb_hid.devices)
first_control = False

while True:
    data = uart.readline()
    if data:
        try:
            message = data.decode("utf-8").strip()
            print(f"Received data: {message}")
            if message and "," in message:
                x, y = map(int, message.split(","))                    
                if x==9999 and y==9999:
                    mouse.release(Mouse.LEFT_BUTTON)
                    first_control = False
                elif x==8888 and y==8888:
                    mouse.click(Mouse.LEFT_BUTTON)
                    first_control = False
                else:
                    if not first_control:
                        mouse.press(Mouse.LEFT_BUTTON)
                    first_control = True
                    mouse.move(x,y)
        except Exception as e:
            print(f"Error: Failed to decode or parse the received data. Exception: {e}")
    else:
        time.sleep(0.001)

