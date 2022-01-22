import matplotlib.pyplot as plt
import numpy as np
import Clustering
import datalogging
import preprocesing
import plotgraph


def akuisisi(x, abd):
    x_long = np.array(x)
    abd_long = np.array(abd)
    # print(len(x))
    x = x_long[0:2000]
    abd = abd_long[0:2000]
    print(x)

    # pre processing
    abd_den = preprocesing.pp(x, abd, show=False)
    plotgraph.plotgraph(x, abd)

    # peak and amplitude detection
    abd_amp, abd_peak, ns = preprocesing.peakvalley(abd_den, show=False)

    # Clustering
    abd_peak1i, abd_peak2i = Clustering.case1(abd_amp, abd_peak, abd_den, ns, show=False)
    plotgraph.plotresult(x, abd_den, abd_peak1i, abd_peak2i)

    datalogging.saveresultcsv(x, abd_den, abd_peak1i, abd_peak2i, 'result.csv')

    plt.show()


if __name__ == "__main__":
    # Load Data
    X, Abd = datalogging.matfile('fekgShort.mat', 'abd1')
    # x, abd = datalogging.loadcsv('sensordata.csv')

    akuisisi(X, Abd)
# load sensor
# x, abd = sensor.serialsensor(10)
# x, abd = datalogging.readsensor('sensordata.csv', 10)

# save data
# datalogging.savecsv(x, abd_den, 'data1.csv')

# initiate before clusterung
# Clustering.case0(abd_amp)
