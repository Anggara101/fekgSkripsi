import pickle
import matplotlib.pyplot as plt
import pywt
import numpy as np
from skimage.restoration import denoise_wavelet
import scipy.signal as sci
from sklearn.cluster import KMeans
# Load Data
file = open('fekgShort.txt', 'rb')
mat = pickle.load(file)
file.close()
# Load Abdomen 4
abd = mat['abd1']
abd = abd[0]
# X axis
x = mat['x']
x = x[0]
# wavelet decomposition
coeffs = pywt.wavedec(abd, 'sym4', level=8)
# cA8,cD8,cD7,cD6,cD5,cD4,cD3,cD2,cD1=coeffs
# remove baseline wander
for i in range(1, 9):  # Remove detail coefficient
    coeffs[i] = np.zeros_like(coeffs[i])
a = pywt.waverec(coeffs, 'sym4')
abd_noBW = abd - a
# remove noise
abd_den = denoise_wavelet(abd_noBW, wavelet='sym4', mode='hard', wavelet_levels=4, rescale_sigma='True')
# detect peak and valley
abd_peakI, _ = sci.find_peaks(abd_den)
abd_valleyI, _ = sci.find_peaks(-abd_den)
# plt.plot(abd_den)
# plt.plot(abd_peakI, abd_den[abd_peakI], "r*")
# plt.plot(abd_valleyI, abd_den[abd_valleyI], "y*")

# amplitude of peak followed by the next valley
# if the first signal is valley, delete the first valley
if abd_peakI[0] > abd_valleyI[0]:
    for i in range(len(abd_valleyI)-1):
        abd_valleyI[i] = abd_valleyI[i+1]
# check length of peak and valley
if len(abd_peakI) > len(abd_valleyI):
    np.delete(abd_peakI, -1)
if len(abd_valleyI) > len(abd_peakI):
    np.delete(abd_valleyI, -1)
abd_peak = abd_den[abd_peakI]
abd_valley = abd_den[abd_valleyI]
# Amplitude
abd_amp = abd_peak - abd_valley
# plt.figure()
# plt.plot(abd_amp,"*")
# Clustering
kmeans = KMeans(n_clusters=3)
kmeans.fit(abd_amp.reshape(-1, 1))
cent = kmeans.cluster_centers_
abd_clus = kmeans.labels_
abd_ampI = np.arange(0, len(abd_amp))
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
abd_clus3 = abd_amp[abd_clus == centI[0]]
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
plt.show()