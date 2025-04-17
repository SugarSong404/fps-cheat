
## -------------  该版本是鼠标按键触发自瞄版本，调用了鼠标库可能容易导致封号，慎用！-----------

import serial
import numpy as np
import keyboard
import mss
import time
import cv2
import json
import os
import mouse

class AutoTrigger:
    def __init__(self, ser, threshold, region_size, delay):
        self.last_avg_color = None

        self.ser = ser
        self.threshold = threshold
        self.region_size = region_size
        self.delay = delay

    def calculate_avg_color(self):
        with mss.mss() as sct:
            self.center_x = sct.monitors[1]["width"] // 2
            self.center_y = sct.monitors[1]["height"] // 2
            region = {
                "left": self.center_x - self.region_size // 2,
                "top": self.center_y - self.region_size // 2,
                "width": self.region_size,
                "height": self.region_size,
            }
            img = sct.grab(region)
            img_array = np.array(img)
            return np.mean(img_array, axis=(0, 1))

    def check_color_change(self, current_avg):
        if self.last_avg_color is None: return False
        color_diff = np.abs(current_avg - self.last_avg_color)
        return np.any(color_diff > self.threshold)

    def run(self):
        self.last_avg_color = self.calculate_avg_color()
        while True:
            current_avg = self.calculate_avg_color()
            if self.check_color_change(current_avg):
                time.sleep(self.delay / 1000)
                self.ser.write(b"9999,9999\n")
                self.ser.flush()
                self.active = False
                break

class AutoAim:
    def __init__(self, ser, size, lColor, hColor, sens, offsets):
        self.ser = ser
        self.size = size
        self.lColor = lColor
        self.hColor = hColor
        self.sens = sens
        self.offsets = offsets

    def run(self):
        lower_bound = np.clip(self.lColor, 0, 255)
        upper_bound = np.clip(self.hColor, 0, 255)

        with mss.mss() as sct:
            screen_width = sct.monitors[1]['width']
            screen_height = sct.monitors[1]['height']

            region = {
                "top": screen_height // 2 - self.size // 2,
                "left": screen_width // 2 - self.size // 2,
                "width": self.size,
                "height": self.size
            }
            screenshot = sct.grab(region)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)     

            mask = cv2.inRange(frame, lower_bound, upper_bound)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                min_x, min_y = self.size, self.size
                for contour in contours:
                    x, y, _, _ = cv2.boundingRect(contour)
                    if y < min_y or (y == min_y and x < min_x):
                        min_x, min_y = x, y

                rel_x = min_x - self.size // 2
                rel_y = min_y - self.size // 2

                print(f"Find left top key point, sent ({rel_x}, {rel_y})")
                data = f"{int((rel_x + self.offsets[0]) * (0.812 / self.sens))},{int((rel_y + self.offsets[1]) * (0.812 / self.sens))}\n".encode()
                self.ser.write(data)
                self.ser.flush()
            else:
                self.ser.write(b"0,0\n")
                self.ser.flush()
                print("No key point detected, sent (0,0)")

def lets_cheat():
    config_path = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(config_path, 'r') as f:
        config = json.load(f)

    serial_config = config['serial']
    ser = serial.Serial(serial_config['port'], serial_config['baud'])

    trigger_config = config['auto_trigger']
    trigger = AutoTrigger(
        ser,
        threshold=trigger_config['threshold'],
        region_size=trigger_config['region_size'],
        delay=trigger_config['delay']
    )

    aim_config = config['auto_aim']
    bot = AutoAim(
        ser,
        size=aim_config['size'],
        lColor=np.array(aim_config['lower_color']),
        hColor=np.array(aim_config['upper_color']),
        sens=aim_config['sens'],
        offsets=aim_config['offsets']
    )

    trigger_active = False
    aim_active = False

    def on_trigger_press(event):
        nonlocal trigger_active
        if event.name == trigger_config["hotkey"]:
            if not trigger_active:
                trigger_active = True
                print("do auto_trigger")
                trigger.run()

    def on_trigger_release(event):
        nonlocal trigger_active
        if event.name == trigger_config["hotkey"]:
            trigger_active = False

    def on_mouse_click():
        nonlocal aim_active
        if not aim_active:
            aim_active = True
            print("do auto_aim (mouse middle click)")
            bot.run()
            aim_active = False

    # 鼠标中键
    # mouse.on_middle_click(on_mouse_click)

    # 鼠标右键
    mouse.on_right_click(on_mouse_click)
    
    # Set up keyboard handlers for trigger
    keyboard.on_press_key(trigger_config["hotkey"], on_trigger_press)
    keyboard.on_release_key(trigger_config["hotkey"], on_trigger_release)

    print("Program running - press ']' to exit")
    keyboard.wait(']')
    mouse.unhook_all()  # Clean up mouse handlers

lets_cheat()