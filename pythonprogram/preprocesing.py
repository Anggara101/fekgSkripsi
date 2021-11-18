import pywt
from skimage.restoration import denoise_wavelet
import numpy as np
import scipy.signal as sci


def pp(abd):
    # wavelet decomposition
    coeffs = pywt.wavedec(abd, 'sym4', level=8)
    # cA8,cD8,cD7,cD6,cD5,cD4,cD3,cD2,cD1=coeffs
    # remove baseline wander
    for i in range(1, 9):  # Remove detail coefficient
        coeffs[i] = np.zeros_like(coeffs[i])
    a = pywt.waverec(coeffs, 'sym4')
    abd_nobw = abd - a
    # remove noise
    abd_den = denoise_wavelet(abd_nobw, wavelet='sym4', mode='hard', wavelet_levels=4, rescale_sigma='True')
    return abd_den


def peakvalley(abd_den):
    # detect peak and valley
    abd_peaki, _ = sci.find_peaks(abd_den)
    abd_valleyi, _ = sci.find_peaks(-abd_den)
    # plt.plot(abd_den)
    # plt.plot(abd_peakI, abd_den[abd_peakI], "r*")
    # plt.plot(abd_valleyI, abd_den[abd_valleyI], "y*")

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
    # plt.figure()
    # plt.plot(abd_amp,"*")
    return abd_amp, abd_peak, ns
