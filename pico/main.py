import board
import busio
import usb_hid
import time
import random
from adafruit_hid.mouse import Mouse

def smooth_move(mouse, target_x, target_y, duration=0.02, overshoot_range=5):
    start_x, start_y = 0, 0 
    steps = int(duration / 0.01) 

    overshoot_x = target_x + random.randint(-overshoot_range, overshoot_range)
    overshoot_y = target_y + random.randint(-overshoot_range, overshoot_range)
    
    for i in range(steps):
        progress = (i + 1) / steps
        if progress < 0.8:
            cur_x = start_x + progress * (overshoot_x - start_x)
            cur_y = start_y + progress * (overshoot_y - start_y)
        else:
            cur_x = overshoot_x - (progress - 0.8) * (overshoot_x - target_x) / 0.2
            cur_y = overshoot_y - (progress - 0.8) * (overshoot_y - target_y) / 0.2
        
        dx = int(cur_x - start_x)
        dy = int(cur_y - start_y)
        
        mouse.move(dx, dy)
        start_x, start_y = cur_x, cur_y
        time.sleep(0.01)
    
    final_dx = target_x - start_x
    final_dy = target_y - start_y
    mouse.move(final_dx, final_dy)


uart = busio.UART(board.GP4, board.GP5, baudrate=9600)
mouse = Mouse(usb_hid.devices)

while True:
    data = uart.readline()
    if data:
        try:
            message = data.decode("utf-8").strip()
            print(f"Received data: {message}")
            
            if message and "," in message:
                x, y = map(int, message.split(","))
                
                if x == 0 and y == 0:
                    print("No target detected, skipping movement.")
                    continue
                elif x == 9999 and y == 9999:
                    mouse.click(Mouse.LEFT_BUTTON)
                    print("Mouse clicked! Be triggerred success!")
                    continue
                
                mouse.move(x, y)
                
                mouse.click(Mouse.LEFT_BUTTON)
                print(f"Mouse moved smoothly to {x}, {y} and clicked.")
                
            else:
                print("Error: Invalid or empty data received")
                
        except Exception as e:
            print(f"Error: Failed to decode or parse the received data. Exception: {e}")
    else:
        time.sleep(0.001)

