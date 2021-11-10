import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

def Case1(abd_amp, abd_peak, x, abd_den):
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(abd_amp.reshape(-1, 1))
    abd_clus = kmeans.labels_
    abd_ampI = np.arange(0, len(abd_amp))
    cent = kmeans.cluster_centers_
    centI = np.argsort(cent.T)
    centI = centI[0]
    abd_clus1I = abd_ampI[abd_clus == centI[2]]
    abd_clus2I = abd_ampI[abd_clus == centI[1]]
    abd_clus3I = abd_ampI[abd_clus == centI[0]]
    plt.plot(abd_ampI[abd_clus1I], abd_amp[abd_clus1I], "b*")
    plt.plot(abd_ampI[abd_clus2I], abd_amp[abd_clus2I], "r*")
    plt.plot(abd_ampI[abd_clus3I], abd_amp[abd_clus3I], "y*")
    abd_clus1 = abd_amp[abd_clus == centI[2]]
    abd_clus2 = abd_amp[abd_clus == centI[1]]
    abd_peak1I = np.zeros(len(abd_clus1), int)
    abd_peak1 = np.zeros(len(abd_clus1))
    for n in range(0, len(abd_clus1)):
        abd_peak1I[n] = np.argwhere(abd_amp == abd_clus1[n])
        abd_peak1[n] = abd_peak[abd_peak1I[n]]
        abd_peak1I[n] = np.argwhere(abd_den == abd_peak1[n])
    abd_peak2I = np.zeros(len(abd_clus2), int)
    abd_peak2 = np.zeros(len(abd_clus2))
    for n in range(0, len(abd_clus2)):
        abd_peak2I[n] = np.argwhere(abd_amp == abd_clus2[n])
        abd_peak2[n] = abd_peak[abd_peak2I[n]]
        abd_peak2I[n] = np.argwhere(abd_den == abd_peak2[n])
    plt.figure()
    plt.plot(x, abd_den, "k")
    plt.plot(x[abd_peak1I], abd_den[abd_peak1I], "b*")
    plt.plot(x[abd_peak2I], abd_den[abd_peak2I], "r*")


def Case2(abd_amp, abd_peak, x, abd_den, ns):
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(abd_amp.reshape(-1, 1))
    abd_clus = kmeans.labels_
    abd_ampI = np.arange(0, len(abd_amp))
    cent = kmeans.cluster_centers_
    centI = np.argsort(cent.T)
    centI = centI[0]
    abd_clus1I = abd_ampI[abd_clus == centI[2]]
    abd_clus2I = abd_ampI[abd_clus == centI[1]]
    abd_clus3I = abd_ampI[abd_clus == centI[0]]
    abd_clus23I = np.concatenate((abd_clus2I, abd_clus3I))
    abd_clus23I = np.sort(abd_clus23I)
    plt.plot(abd_ampI[abd_clus1I], abd_amp[abd_clus1I], "b*")
    plt.plot(abd_ampI[abd_clus23I], abd_amp[abd_clus23I], "r*")
    abd_clus23 = abd_amp[abd_clus23I]
    abd_clus23 = abd_clus23 / (ns[abd_clus23I])
    kmeans2 = KMeans(n_clusters=2)
    kmeans2.fit(abd_clus23.reshape(-1, 1))
    abd_2clus23 = kmeans2.labels_
    abd_2clus23I = np.arange(0, len(abd_clus23))
    cent2 = kmeans2.cluster_centers_
    cent2I = np.argsort(cent2.T)
    cent2I = cent2I[0]
    abd_clus2I = abd_2clus23I[abd_2clus23 == cent2I[1]]
    abd_clus3I = abd_2clus23I[abd_2clus23 == cent2I[0]]
    plt.figure()
    plt.plot(abd_2clus23I[abd_clus2I], abd_clus23[abd_clus2I], "b*")
    plt.plot(abd_2clus23I[abd_clus3I], abd_clus23[abd_clus3I], "r*")
    abd_clus1 = abd_amp[abd_clus == centI[2]]
    abd_peak1I = np.zeros(len(abd_clus1), int)
    abd_peak1 = np.zeros(len(abd_clus1))
    for n in range(0, len(abd_clus1)):
        abd_peak1I[n] = np.argwhere(abd_amp == abd_clus1[n])
        abd_peak1[n] = abd_peak[abd_peak1I[n]]
        abd_peak1I[n] = np.argwhere(abd_den == abd_peak1[n])
    abd_clus23n = abd_clus23*ns[abd_clus23I]
    abd_clus2 = abd_clus23n[abd_2clus23 == cent2I[1]]
    abd_amp = np.round(abd_amp, decimals=8)
    abd_clus2 = np.round(abd_clus2, decimals=8)
    abd_peak2I = np.zeros(len(abd_clus2), int)
    abd_peak2 = np.zeros(len(abd_clus2))
    for n in range(0, len(abd_clus2)):
        abd_peak2I[n] = np.argwhere(abd_amp == abd_clus2[n])
        abd_peak2[n] = abd_peak[abd_peak2I[n]]
        abd_peak2I[n] = np.argwhere(abd_den == abd_peak2[n])
    plt.figure()
    plt.plot(x, abd_den, "k")
    plt.plot(x[abd_peak1I], abd_den[abd_peak1I], "b*")
    plt.plot(x[abd_peak2I], abd_den[abd_peak2I], "r*")

def Case3(abd_amp, abd_peak, x, abd_den, ns):
    abd_amp=abd_amp*ns
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(abd_amp.reshape(-1, 1))
    abd_clus = kmeans.labels_
    abd_ampI = np.arange(0, len(abd_amp))
    cent = kmeans.cluster_centers_
    centI = np.argsort(cent.T)
    centI = centI[0]
    abd_clus1I = abd_ampI[abd_clus == centI[2]]
    abd_clus2I = abd_ampI[abd_clus == centI[1]]
    abd_clus3I = abd_ampI[abd_clus == centI[0]]
    plt.plot(abd_ampI[abd_clus1I], abd_amp[abd_clus1I], "b*")
    plt.plot(abd_ampI[abd_clus2I], abd_amp[abd_clus2I], "r*")
    plt.plot(abd_ampI[abd_clus3I], abd_amp[abd_clus3I], "y*")
    abd_clus1 = abd_amp[abd_clus == centI[2]]
    abd_clus2 = abd_amp[abd_clus == centI[1]]
    abd_peak1I = np.zeros(len(abd_clus1), int)
    abd_peak1 = np.zeros(len(abd_clus1))
    for n in range(0, len(abd_clus1)):
        abd_peak1I[n] = np.argwhere(abd_amp == abd_clus1[n])
        abd_peak1[n] = abd_peak[abd_peak1I[n]]
        abd_peak1I[n] = np.argwhere(abd_den == abd_peak1[n])
    abd_peak2I = np.zeros(len(abd_clus2), int)
    abd_peak2 = np.zeros(len(abd_clus2))
    for n in range(0, len(abd_clus2)):
        abd_peak2I[n] = np.argwhere(abd_amp == abd_clus2[n])
        abd_peak2[n] = abd_peak[abd_peak2I[n]]
        abd_peak2I[n] = np.argwhere(abd_den == abd_peak2[n])
    plt.figure()
    plt.plot(x, abd_den, "k")
    plt.plot(x[abd_peak1I], abd_den[abd_peak1I], "b*")
    plt.plot(x[abd_peak2I], abd_den[abd_peak2I], "r*")

def Case4(abd_amp, abd_peak, x, abd_den, ns):
    abd_amp=abd_amp*ns
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(abd_amp.reshape(-1, 1))
    abd_clus = kmeans.labels_
    abd_ampI = np.arange(0, len(abd_amp))
    cent = kmeans.cluster_centers_
    centI = np.argsort(cent.T)
    centI = centI[0]
    abd_clus1I = abd_ampI[abd_clus == centI[2]]
    abd_clus2I = abd_ampI[abd_clus == centI[1]]
    abd_clus3I = abd_ampI[abd_clus == centI[0]]
    abd_clus23I = np.concatenate((abd_clus2I, abd_clus3I))
    abd_clus23I = np.sort(abd_clus23I)
    plt.plot(abd_ampI[abd_clus1I], abd_amp[abd_clus1I], "b*")
    plt.plot(abd_ampI[abd_clus23I], abd_amp[abd_clus23I], "r*")
    abd_clus23 = abd_amp[abd_clus23I]
    abd_clus23 = abd_clus23 / (ns[abd_clus23I])
    kmeans2 = KMeans(n_clusters=2)
    kmeans2.fit(abd_clus23.reshape(-1, 1))
    abd_2clus23 = kmeans2.labels_
    abd_2clus23I = np.arange(0, len(abd_clus23))
    cent2 = kmeans2.cluster_centers_
    cent2I = np.argsort(cent2.T)
    cent2I = cent2I[0]
    abd_clus2I = abd_2clus23I[abd_2clus23 == cent2I[1]]
    abd_clus3I = abd_2clus23I[abd_2clus23 == cent2I[0]]
    plt.figure()
    plt.plot(abd_2clus23I[abd_clus2I], abd_clus23[abd_clus2I], "b*")
    plt.plot(abd_2clus23I[abd_clus3I], abd_clus23[abd_clus3I], "r*")
    abd_clus1 = abd_amp[abd_clus == centI[2]]
    abd_peak1I = np.zeros(len(abd_clus1), int)
    abd_peak1 = np.zeros(len(abd_clus1))
    for n in range(0, len(abd_clus1)):
        abd_peak1I[n] = np.argwhere(abd_amp == abd_clus1[n])
        abd_peak1[n] = abd_peak[abd_peak1I[n]]
        abd_peak1I[n] = np.argwhere(abd_den == abd_peak1[n])
    abd_clus23n = abd_clus23 * ns[abd_clus23I]
    abd_clus2 = abd_clus23n[abd_2clus23 == cent2I[1]]
    abd_amp = np.round(abd_amp, decimals=8)
    abd_clus2 = np.round(abd_clus2, decimals=8)
    abd_peak2I = np.zeros(len(abd_clus2), int)
    abd_peak2 = np.zeros(len(abd_clus2))
    for n in range(0, len(abd_clus2)):
        abd_peak2I[n] = np.argwhere(abd_amp == abd_clus2[n])
        abd_peak2[n] = abd_peak[abd_peak2I[n]]
        abd_peak2I[n] = np.argwhere(abd_den == abd_peak2[n])
    plt.figure()
    plt.plot(x, abd_den, "k")
    plt.plot(x[abd_peak1I], abd_den[abd_peak1I], "b*")
    plt.plot(x[abd_peak2I], abd_den[abd_peak2I], "r*")