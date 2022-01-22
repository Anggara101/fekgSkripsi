import scipy.io
import csv
import sqlite3
import matplotlib.pyplot as plt

# conn = sqlite3.connect('fekgdata.db')
# c = conn.cursor()
# #     c.execute("""CREATE TABLE fekg(
# #                     sqlid INTEGER,
# #                     time REAL,
# #                     raw_abdomen REAL)""")
# #     c.execute("INSERT INTO fekg VALUES (:sqlid, :time, :raw_abdomen)",{'sqlid': int(start),
#               'time': t, 'raw_abdomen': value})
# #     c.execute("SELECT time, raw_abdomen FROM fekg WHERE sqlid=:sqlid", {'sqlid': sqlid})
# print(c.fetchall())
# conn.commit()
# conn.close()


def readdatabase(sqlid):
    conn = sqlite3.connect('fekgdata.db')
    c = conn.cursor()
    c.execute("SELECT time, raw_abdomen FROM fekg WHERE sqlid=:sqlid", {'sqlid': sqlid})
    conn.commit()
    result = c.fetchall()
    conn.close()
    unzipped_result = list(zip(*result))
    x = unzipped_result[0]
    x = list(x)
    y = unzipped_result[1]
    y = list(y)
    print(x, y)
    plt.figure()
    plt.plot(x, y)
    plt.show()


def matfile(filename, abdname):
    mat = scipy.io.loadmat(filename)
    # Load Abdomen
    abd = mat[abdname]
    abd = abd[0]
    abd = abd.tolist()
    # X axis
    x = mat['x']
    x = x[0]
    x = x.tolist()
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
    # plt.figure()
    # plt.plot(x, y)
    return x, y


def savecsv(x, y, filename):
    f = open(filename, 'w', newline='')
    writer = csv.writer(f)
    for i in range(len(x)):
        writer.writerow([x[i], y[i]])
    f.close()


def saveresultcsv(x, y, peak1, peak2, filename):
    f = open(filename, 'w', newline='')
    writer = csv.writer(f)
    p1 = [0] * len(x)
    p2 = [0] * len(x)
    for n in peak1:
        p1[n] = 1
    for n in peak2:
        p2[n] = 1
    for i in range(len(x)):
        writer.writerow([x[i], y[i], p1[i], p2[i]])
    f.close()


if __name__ == '__main__':
    pass
