import serial
import time
# import csv
# import numpy as np
# import Adafruit_ADS1x15


def serialsensor():
    ser = serial.Serial(port="COM5", baudrate=115200, timeout=1)
    ser.reset_input_buffer()
    start = time.time()
    # x , ekg = [], []
    buf = []
    while True:
        if ser.in_waiting > 0:
            line = ser.read()
            buf.append(line.decode())
            if line == b'\n':
                data = buf
                print(data)
                buf = []
            # line = line.decode().rstrip()
            # line = list(line.split(","))
            # print(string)
            # value = int(line[1])
            # x.append(t)
            # ekg.append(value)
            # if len(ekg) >= 5000:
            #     t = 0
            #     x, ekg = [], []
            # print(t)
            if time.time() - start >= 3:
                ser.close()
                break


if __name__ == '__main__':
    #     x, y = serialsensor(10)
    serialsensor()
