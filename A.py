import cv2
import numpy as np
import mss
import time

with mss.mss() as sct:
    monitor = sct.monitors[1]
    while True:
        screenshot = np.array(sct.grab(monitor))

        lab = cv2.cvtColor(screenshot, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4,4))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        resized = cv2.resize(enhanced, (0,0), fx=0.5, fy=0.5)

        cv2.imshow('Real-time Enhanced Screenshot', resized)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()