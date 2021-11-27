import serial
import time
import csv
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
import Adafruit_ADS1x15


def readsensorsql(endtime):
    conn = sqlite3.connect('fekgdata.db')
    c = conn.cursor()

    ser = serial.Serial('/dev/ttyUSB0', 19200, timeout=1)
    ser.reset_input_buffer()
    start = time.time()
    n0 = 7
    n=n0
    x, y = [], []
    while True:
        if ser.in_waiting > 0:    
            n=n-1
            line = ser.readline()
#             print(line)
            if n < 0:
                string = line.decode('utf-8').rstrip()
                string = list(string.split(","))
                t = int(string[0])
                value = int(string[1])
                x.append(t)
                y.append(value)
                c.execute("INSERT INTO fekg VALUES (:id, :time, :raw_abdomen)",{'id': int(start), 'time': t, 'raw_abdomen': value})
                conn.commit()
                print(t, value)
            if time.time()-start >= endtime + n0:
                break
    conn.close()
    return x, y
    

def serialsensor(endtime):
    ser = serial.Serial('/dev/ttyUSB0', 19200, timeout=1)
    ser.reset_input_buffer()
    start = time.time()
    n0 = 7
    n=n0
    x, y = [], []
    while True:
        if ser.in_waiting > 0:    
            n=n-1
            line = ser.readline()
#             print(line)
            if n < 0:
                string = line.decode('utf-8').rstrip()
                string = list(string.split(","))
                t = int(string[0])
                value = int(string[1])
                x.append(t)
                y.append(value)
                print(t, value)
            if time.time()-start >= endtime + n0:
                break
    return x, y


def readsensor(filename, endtime):
    adc = Adafruit_ADS1x15.ADS1115()
    gain = 1
    start = time.time()
    x, y = [], []
    adc.start_adc(0, gain=gain)
    while True:
        value = adc.get_last_result()
        t = np.round((time.time() - start), decimals=3)
        print(t, value)
        x.append(t)
        y.append(value)
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for i in range(len(x)):
                writer.writerow([x[i], y[i]])
        time.sleep(0.01)
        if (time.time() - start) >= endtime:
            adc.stop_adc()
            break
    return x, y


if __name__ == '__main__':
#     x, y = serialsensor(10)
    x, y = readsensorsql(10)
    plt.figure()
    plt.plot(x, y)
    plt.show()
