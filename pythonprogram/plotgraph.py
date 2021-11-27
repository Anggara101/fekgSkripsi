import time
import csv
import numpy as np
from drawnow import *


def plotsensor(filename, endtime):
    start = time.time()

    def makegraph():
        plt.plot(x, y)

    while True:
        time.sleep(2)
        x = []
        y = []
        with open(filename, 'r') as f:
            plots = csv.reader(f)
            for row in plots:
                x.append(float(row[0]))
                y.append(float(row[1]))
        print(x)
        if x:
            drawnow(makegraph)
        f.close()
        if (time.time() - start) >= endtime:
            drawnow(makegraph, show_once=True)
            break


def plotgraph(x, y):
    plt.plot(x, y)


def plotgraphanimate(x, y):
    # lists to store x and y axis points
    xdata, ydata = [], []
    plt.figure()

    def makegraph():
        plt.plot(xarray.T, yarray.T, 'b')

    m = (len(x) + 1) / 100
    # animation function
    for i in range(1, int(m)):
        n1 = i * 100 - 1
        n2 = (i + 1) * 100
        xdata.append(x[n1:n2])
        ydata.append(y[n1:n2])
        # appending new points to x, y axes points list
        xarray = np.array(xdata)
        yarray = np.array(ydata)
        drawnow(makegraph)
        time.sleep(0.1)


def plotresult(x, y, peak1, peak2):
    plt.figure()
    plt.plot(x, y, "k")
    plt.plot(x[peak1], y[peak1], "b*")
    plt.plot(x[peak2], y[peak2], "r*")


def plotresultanimate(x, y, peak1, peak2):
    # lists to store x and y axis points
    xdata, ydata, peak1data, peak2data = [], [], [], []
    plt.figure()

    def makegraph():
        plt.plot(xarray.T, yarray.T, 'k')
        plt.plot(x[peak1i], y[peak1i], 'b*')
        plt.plot(x[peak2i], y[peak2i], 'r*')

    # animation function
    m = (len(x) + 1) / 100
    for i in range(1, int(m)):
        n1 = i * 100 - 1
        n2 = (i + 1) * 100
        xdata.append(x[n1:n2])
        ydata.append(y[n1:n2])
        xarray = np.array(xdata)
        yarray = np.array(ydata)
        for l1 in range(len(peak1)):
            if n2 >= peak1[l1]:
                peak1data.append(peak1[l1])
        for l2 in range(len(peak2)):
            if n2 >= peak2[l2]:
                peak2data.append(peak2[l2])
        peak1i = list(dict.fromkeys(peak1data))
        peak2i = list(dict.fromkeys(peak2data))
        drawnow(makegraph)
        time.sleep(0.1)
