import pywt
from skimage.restoration import denoise_wavelet
import numpy as np
import scipy.signal as sci
import matplotlib.pyplot as plt


def pp(x, abd, show):
    # wavelet decomposition
    lvl = 8
    coeffs = pywt.wavedec(abd, 'sym4', level=lvl)
    coeffs_nodetails = coeffs

    # remove baseline wander
    for i in range(1, lvl+1):  # detail coefficient
        coeffs_nodetails[i] = np.zeros_like(coeffs[i])
    a = pywt.waverec(coeffs_nodetails, 'sym4')
    while True:
        if len(a) > len(abd):
            a = np.delete(a, -1)
        if len(abd) > len(a):
            abd = np.delete(abd, -1)
        else:
            break
    # remove detail coefficient
    abd_nobw = abd - a

    # remove noise
    abd_den = denoise_wavelet(abd_nobw, sigma=20, wavelet='sym4', mode='hard', wavelet_levels=4)
    if show:
        plt.figure()
        plt.plot(x, abd_nobw, 'b')
        plt.plot(x, abd_den, 'r', lw=0.8)
    return abd_den


def peakvalley(abd_den, show):
    # detect peak and valley
    abd_peaki, _ = sci.find_peaks(abd_den)
    abd_valleyi, _ = sci.find_peaks(-abd_den)
    if show:
        plt.figure()
        plt.plot(abd_den)
        plt.plot(abd_peaki, abd_den[abd_peaki], "r*")
        plt.plot(abd_valleyi, abd_den[abd_valleyi], "y*")

    # amplitude of peak followed by the next valley
    # if the first signal is valley, delete the first valley
    if abd_peaki[0] > abd_valleyi[0]:
        for i in range(len(abd_valleyi) - 1):
            abd_valleyi[i] = abd_valleyi[i + 1]

    # check length of peak and valley
    if len(abd_peaki) > len(abd_valleyi):
        abd_peaki = np.delete(abd_peaki, -1)
    if len(abd_valleyi) > len(abd_peaki):
        abd_valleyi = np.delete(abd_valleyi, -1)
    abd_peak = abd_den[abd_peaki]
    abd_valley = abd_den[abd_valleyi]

    # Amplitude
    abd_amp = abd_peak - abd_valley
    ns = abd_valleyi - abd_peaki
    return abd_amp, abd_peak, ns
