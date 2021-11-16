import scipy.io
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


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
