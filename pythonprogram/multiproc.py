import time
import csv
import matplotlib as plt
from drawnow import *
from multiprocessing import Process
import numpy as np


def readsensor(filename):
    adc = Adafruit_ADS1x15.ADS1115()
    GAIN = 1
    start = time.time()
    x, y = [], []
    while True:
        f = open(filename, 'w', newline='')
        writer = csv.writer(f)
        value = adc.read_adc(0, gain=GAIN)
        t = np.round((time.time() - start), decimals=3)
#         print(t, value)
        x.append(t)
        y.append(value)
        for i in range(len(x)):
            writer.writerow([x[i], y[i]])
        f.close()
        time.sleep(0.1)
        if (time.time() - start) >= 30.0:
            break


def plotsensor(filename):
    start = time.time()

    def makegraph():
        plt.plot(x, y)

    while True:
        time.sleep(1)
        x = []
        y = []
        f = open(filename, 'r')
        plots = csv.reader(f)
        for row in plots:
            x.append(float(row[0]))
            y.append(float(row[1]))
        #         print(x)
        drawnow(makegraph)
        if (time.time() - start) >= 30.0:
            drawnow(makegraph, show_once=True)
            break
        f.close()


Filename = 'multi.csv'
# readsensor(Filename)
p1 = Process(target=readsensor, args=(Filename,))
p2 = Process(target=plotsensor, args=(Filename,))

p1.start()
p2.start()

p1.join()
p2.join()
