import scipy.io
import csv
import numpy as np


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
