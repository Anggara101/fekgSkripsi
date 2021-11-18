import scipy.io
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import Adafruit_ADS1x15
from drawnow import *
    
def readsensor(filename):
    adc = Adafruit_ADS1x15.ADS1115()
    GAIN = 1
    start = time.time()
    f = open(filename, 'w', newline='')
    writer = csv.writer(f)
    x,y = [],[]
    plt.figure()
    def makegraph():
        plt.plot(x, y)
        
    while True:
        value = adc.read_adc(0, gain=GAIN)
        t = np.round((time.time() - start), decimals=4)
        print(t, value)
        xy = [t, value]
        writer.writerow(xy)
        x.append(t)
        y.append(value)
        drawnow(makegraph)
        time.sleep(0.01)
        if (time.time() - start) >= 20.0:
            break
    f.close()
    # return x, y
    
    
def plotsensor():
    fig = plt.figure()
    x, y = [], []
    def animate(i):
        f = open('sensordata.csv', 'r')
        plots = csv.reader(f)
        for row in plots:
            x.append(float(row[0]))
            y.append(float(row[1]))
        f.close()
        plt.plot(np.array(x), np.array(y))
    anim = animation.FuncAnimation(fig, animate, interval=500)
    plt.show()
        
    
def matfile(filename, abdname):
    mat = scipy.io.loadmat(filename)
    # Load Abdomen
    abd = mat[abdname]
    abd = abd[0]
    # X axis
    x = mat['x']
    x = x[0]
    return x, abd


def loadcsv(filename):
    x = []
    y = []
    f = open(filename, 'r')
    plots = csv.reader(f)
    for row in plots:
        x.append(float(row[0]))
        y.append(float(row[1]))
    f.close()
    x = np.array(x)
    y = np.array(y)
    # plt.figure()
    # plt.plot(x, y)
    return x, y


def savecsv(x, y, filename):
    f = open(filename, 'w', newline='')
    writer = csv.writer(f)
    for i in range(len(x)):
        writer.writerow([x[i], y[i]])
    f.close()


def plotgraph(x, y):
    # lists to store x and y axis points
    xdata, ydata = [], []
    fig = plt.figure()

    # animation function
    def animate(i):
        # appending new points to x, y axes points list
        n1 = i * 100
        n2 = (i + 1) * 100 + 1
        xdata.append(x[n1:n2])
        ydata.append(y[n1:n2])
        xarray = np.array(xdata)
        yarray = np.array(ydata)
        plt.cla()
        plt.plot(xarray.T, yarray.T, 'b')

    m = (len(x)-1)/100-1
    frame = np.arange(int(m))
    # call the animator
    anim = animation.FuncAnimation(fig, animate, interval=1, frames=frame, repeat=False)
    plt.show()

def plotresult(x, y, peak1, peak2):
    # lists to store x and y axis points
    xdata, ydata, peak1data, peak2data = [], [], [], []
    fig = plt.figure()

    # animation function
    def animate(i):
        # appending new points to x, y axes points list
        n1 = i * 100
        n2 = (i + 1) * 100 + 1
        xdata.append(x[n1:n2])
        ydata.append(y[n1:n2])
        xarray = np.array(xdata)
        yarray = np.array(ydata)
        plt.cla()
        plt.plot(xarray.T, yarray.T, 'k')

        for l1 in range(len(peak1)):
            if n2 >= peak1[l1]:
                peak1data.append(peak1[l1])
        for l2 in range(len(peak2)):
            if n2 >= peak2[l2]:
                peak2data.append(peak2[l2])
        peak1i = list(dict.fromkeys(peak1data))
        peak2i = list(dict.fromkeys(peak2data))
        plt.plot(x[peak1i], y[peak1i], 'b*')
        plt.plot(x[peak2i], y[peak2i], 'r*')


    m = (len(x)-1)/100-1
    frame = np.arange(int(m))
    # call the animator
    anim = animation.FuncAnimation(fig, animate, interval=1, frames=frame, repeat=False)
    plt.show()

