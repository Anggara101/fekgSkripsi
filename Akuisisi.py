import pickle
import matplotlib.pyplot as plt
import pywt
import numpy as np
from skimage.restoration import denoise_wavelet
import scipy.signal as sci
import Clustering
# Load Data
file = open('fekgShort.txt', 'rb')
mat = pickle.load(file)
file.close()
# Load Abdomen
abd = mat['abd4']
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
    abd_peakI = np.delete(abd_peakI, -1)
if len(abd_valleyI) > len(abd_peakI):
    abd_valleyI = np.delete(abd_valleyI, -1)
abd_peak = abd_den[abd_peakI]
abd_valley = abd_den[abd_valleyI]
# Amplitude
abd_amp = abd_peak - abd_valley
ns = abd_valleyI - abd_peakI
# plt.figure()
# plt.plot(abd_amp,"*")

Clustering.Case4(abd_amp, abd_peak, x, abd_den, ns)
plt.show()
