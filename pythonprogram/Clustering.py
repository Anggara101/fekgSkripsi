import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans


# clustering the amplitude, return clustered amplitude and center of cluster
def kmeans_clustering(abd_amp, no_of_cluster):
    kmeans = KMeans(n_clusters=no_of_cluster)
    kmeans.fit(abd_amp.reshape(-1, 1))
    abd_clus = kmeans.labels_
    cent = kmeans.cluster_centers_
    cent_i = np.argsort(cent.T)
    cent_i = cent_i[0]
    return abd_clus, cent_i


def case0(abd_amp):
    plt.figure()
    plt.plot(abd_amp, "*")


def case1(abd_amp, abd_peak, abd_den, _, show):
    abd_clus, cent_i = kmeans_clustering(abd_amp, 3)
    #
    abd_ampi = np.arange(0, len(abd_amp))
    abd_clus1i = abd_ampi[abd_clus == cent_i[2]]
    abd_clus2i = abd_ampi[abd_clus == cent_i[1]]
    abd_clus3i = abd_ampi[abd_clus == cent_i[0]]
    if show:
        plt.figure()
        plt.plot(abd_ampi[abd_clus1i], abd_amp[abd_clus1i], "b*")
        plt.plot(abd_ampi[abd_clus2i], abd_amp[abd_clus2i], "r*")
        plt.plot(abd_ampi[abd_clus3i], abd_amp[abd_clus3i], "y*")
    abd_clus1 = abd_amp[abd_clus == cent_i[2]]
    abd_clus2 = abd_amp[abd_clus == cent_i[1]]
    abd_peak1i = np.zeros(len(abd_clus1), int)
    abd_peak1 = np.zeros(len(abd_clus1))
    for n in range(0, len(abd_clus1)):
        abd_peak1i[n] = np.argwhere(abd_amp == abd_clus1[n])
        abd_peak1[n] = abd_peak[abd_peak1i[n]]
        abd_peak1i[n] = np.argwhere(abd_den == abd_peak1[n])
    abd_peak2i = np.zeros(len(abd_clus2), int)
    abd_peak2 = np.zeros(len(abd_clus2))
    for n in range(0, len(abd_clus2)):
        abd_peak2i[n] = np.argwhere(abd_amp == abd_clus2[n])
        abd_peak2[n] = abd_peak[abd_peak2i[n]]
        abd_peak2i[n] = np.argwhere(abd_den == abd_peak2[n])
    return abd_peak1i, abd_peak2i


def case2(abd_amp, abd_peak, abd_den, ns, show):
    abd_clus, cent_i = kmeans_clustering(abd_amp, 3)
    abd_ampi = np.arange(0, len(abd_amp))
    abd_clus1i = abd_ampi[abd_clus == cent_i[2]]
    abd_clus2i = abd_ampi[abd_clus == cent_i[1]]
    abd_clus3i = abd_ampi[abd_clus == cent_i[0]]
    abd_clus23i = np.concatenate((abd_clus2i, abd_clus3i))
    abd_clus23i = np.sort(abd_clus23i)
    if show:
        plt.figure()
        plt.plot(abd_ampi[abd_clus1i], abd_amp[abd_clus1i], "b*")
        plt.plot(abd_ampi[abd_clus23i], abd_amp[abd_clus23i], "r*")
    abd_clus23 = abd_amp[abd_clus23i]
    abd_clus23 = abd_clus23 / (ns[abd_clus23i])
    abd_2clus23, cent2i = kmeans_clustering(abd_clus23, 2)
    abd_2clus23i = np.arange(0, len(abd_clus23))
    abd_clus2i = abd_2clus23i[abd_2clus23 == cent2i[1]]
    abd_clus3i = abd_2clus23i[abd_2clus23 == cent2i[0]]
    if show:
        plt.figure()
        plt.plot(abd_2clus23i[abd_clus2i], abd_clus23[abd_clus2i], "b*")
        plt.plot(abd_2clus23i[abd_clus3i], abd_clus23[abd_clus3i], "r*")
    abd_clus1 = abd_amp[abd_clus == cent_i[2]]
    abd_peak1i = np.zeros(len(abd_clus1), int)
    abd_peak1 = np.zeros(len(abd_clus1))
    for n in range(0, len(abd_clus1)):
        abd_peak1i[n] = np.argwhere(abd_amp == abd_clus1[n])
        abd_peak1[n] = abd_peak[abd_peak1i[n]]
        abd_peak1i[n] = np.argwhere(abd_den == abd_peak1[n])
    abd_clus23n = abd_clus23 * ns[abd_clus23i]
    abd_clus2 = abd_clus23n[abd_2clus23 == cent2i[1]]
    abd_amp = np.round(abd_amp, decimals=8)
    abd_clus2 = np.round(abd_clus2, decimals=8)
    abd_peak2i = np.zeros(len(abd_clus2), int)
    abd_peak2 = np.zeros(len(abd_clus2))
    for n in range(0, len(abd_clus2)):
        abd_peak2i[n] = np.argwhere(abd_amp == abd_clus2[n])
        abd_peak2[n] = abd_peak[abd_peak2i[n]]
        abd_peak2i[n] = np.argwhere(abd_den == abd_peak2[n])
    # plt.figure()
    # plt.plot(x, abd_den, "k")
    # plt.plot(x[abd_peak1i], abd_den[abd_peak1i], "b*")
    # plt.plot(x[abd_peak2i], abd_den[abd_peak2i], "r*")
    return abd_peak1i, abd_peak2i


def case3(abd_amp, abd_peak, abd_den, ns, show):
    abd_amp = abd_amp * ns
    abd_clus, cent_i, = kmeans_clustering(abd_amp, 3)
    abd_ampi = np.arange(0, len(abd_amp))
    abd_clus1i = abd_ampi[abd_clus == cent_i[2]]
    abd_clus2i = abd_ampi[abd_clus == cent_i[1]]
    abd_clus3i = abd_ampi[abd_clus == cent_i[0]]
    if show:
        plt.figure()
        plt.plot(abd_ampi[abd_clus1i], abd_amp[abd_clus1i], "b*")
        plt.plot(abd_ampi[abd_clus2i], abd_amp[abd_clus2i], "r*")
        plt.plot(abd_ampi[abd_clus3i], abd_amp[abd_clus3i], "y*")
    abd_clus1 = abd_amp[abd_clus == cent_i[2]]
    abd_clus2 = abd_amp[abd_clus == cent_i[1]]
    abd_peak1i = np.zeros(len(abd_clus1), int)
    abd_peak1 = np.zeros(len(abd_clus1))
    for n in range(0, len(abd_clus1)):
        abd_peak1i[n] = np.argwhere(abd_amp == abd_clus1[n])
        abd_peak1[n] = abd_peak[abd_peak1i[n]]
        abd_peak1i[n] = np.argwhere(abd_den == abd_peak1[n])
    abd_peak2i = np.zeros(len(abd_clus2), int)
    abd_peak2 = np.zeros(len(abd_clus2))
    for n in range(0, len(abd_clus2)):
        abd_peak2i[n] = np.argwhere(abd_amp == abd_clus2[n])
        abd_peak2[n] = abd_peak[abd_peak2i[n]]
        abd_peak2i[n] = np.argwhere(abd_den == abd_peak2[n])
    # plt.figure()
    # plt.plot(x, abd_den, "k")
    # plt.plot(x[abd_peak1i], abd_den[abd_peak1i], "b*")
    # plt.plot(x[abd_peak2i], abd_den[abd_peak2i], "r*")
    return abd_peak1i, abd_peak2i


def case4(abd_amp, abd_peak, abd_den, ns, show):
    abd_amp = abd_amp * ns
    abd_clus, cent_i = kmeans_clustering(abd_amp, 3)
    abd_ampi = np.arange(0, len(abd_amp))
    abd_clus1i = abd_ampi[abd_clus == cent_i[2]]
    abd_clus2i = abd_ampi[abd_clus == cent_i[1]]
    abd_clus3i = abd_ampi[abd_clus == cent_i[0]]
    abd_clus23i = np.concatenate((abd_clus2i, abd_clus3i))
    abd_clus23i = np.sort(abd_clus23i)
    if show:
        plt.figure()
        plt.plot(abd_ampi[abd_clus1i], abd_amp[abd_clus1i], "b*")
        plt.plot(abd_ampi[abd_clus23i], abd_amp[abd_clus23i], "r*")
    abd_clus23 = abd_amp[abd_clus23i]
    abd_clus23 = abd_clus23 / (ns[abd_clus23i])
    abd_2clus23, cent2i = kmeans_clustering(abd_clus23, 2)
    abd_2clus23i = np.arange(0, len(abd_clus23))
    abd_clus2i = abd_2clus23i[abd_2clus23 == cent2i[1]]
    abd_clus3i = abd_2clus23i[abd_2clus23 == cent2i[0]]
    if show:
        plt.figure()
        plt.plot(abd_2clus23i[abd_clus2i], abd_clus23[abd_clus2i], "b*")
        plt.plot(abd_2clus23i[abd_clus3i], abd_clus23[abd_clus3i], "r*")
    abd_clus1 = abd_amp[abd_clus == cent_i[2]]
    abd_peak1i = np.zeros(len(abd_clus1), int)
    abd_peak1 = np.zeros(len(abd_clus1))
    for n in range(0, len(abd_clus1)):
        abd_peak1i[n] = np.argwhere(abd_amp == abd_clus1[n])
        abd_peak1[n] = abd_peak[abd_peak1i[n]]
        abd_peak1i[n] = np.argwhere(abd_den == abd_peak1[n])
    abd_clus23n = abd_clus23 * ns[abd_clus23i]
    abd_clus2 = abd_clus23n[abd_2clus23 == cent2i[1]]
    abd_amp = np.round(abd_amp, decimals=8)
    abd_clus2 = np.round(abd_clus2, decimals=8)
    abd_peak2i = np.zeros(len(abd_clus2), int)
    abd_peak2 = np.zeros(len(abd_clus2))
    for n in range(0, len(abd_clus2)):
        abd_peak2i[n] = np.argwhere(abd_amp == abd_clus2[n])
        abd_peak2[n] = abd_peak[abd_peak2i[n]]
        abd_peak2i[n] = np.argwhere(abd_den == abd_peak2[n])
    # plt.figure()
    # plt.plot(x, abd_den, "k")
    # plt.plot(x[abd_peak1i], abd_den[abd_peak1i], "b*")
    # plt.plot(x[abd_peak2i], abd_den[abd_peak2i], "r*")
    return abd_peak1i, abd_peak2i
