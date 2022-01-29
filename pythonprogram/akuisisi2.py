import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

import datalogging


def filtering(ecg, fs):
    #bandpass filter
    f1 = 9
    f2 = 27
    wn = np.array([f1, f2]) * 2/fs
    [b, a] = signal.butter(2, wn, 'bandpass', output='ba')
    # Filter the signal
    ecg_f = np.zeros(len(ecg))
    for m in range(len(b), len(ecg)):
        ecg_f[m] = b[0] * ecg[m]
        for i in range(1, len(b)):
            ecg_f[m] += b[i] * ecg[m - i] - a[i] * ecg_f[m - i]

    # Derivative Filter
    b = np.array([1, 2, 0, -2, -1])*(1/8)*fs
    ecg_d = np.zeros(len(ecg_f))
    for m in range(len(b), len(ecg_f)):
        ecg_d[m] = b[0] * ecg_f[m]
        for i in range(1, len(b)):
            ecg_d[m] += b[i] * ecg_f[m - i]
    ecg_d = ecg_d/max(ecg_d)

    ecg_s = ecg_d**2

    window_width = 80
    kernel = np.ones((window_width, 1))/window_width
    b = kernel[:, 0]
    a = window_width
    ecg_m = np.zeros(len(ecg_s))
    for m in range(len(b), len(ecg_s)):
        ecg_m[m] = b[0] * ecg_s[m]
        for i in range(1, len(b)):
            ecg_m[m] += b[i] * ecg_s[m - i]
    return ecg_f, ecg_m


def detection(peaks, peaks_i, thrs, siglev, noislev, type):
    refrac_p = 150          # Refraction period for mQRS 150 ms
    if type ==1:
        refrac_p = 80       # Refraction period for fQRS 80 ms
    thrs_buf = []
    thrs_buf_i = []
    qrs_i = np.array([], dtype=int)
    n = 0
    for i in range(len(peaks)):
        try:
            last_qrs_i = qrs_i[-1]
        except IndexError:
            last_qrs_i = 0
        if peaks_i[i] - last_qrs_i > refrac_p or not qrs_i.size:
            if peaks[i] > thrs:
                n += 1
                qrs_i = np.append(qrs_i, peaks_i[i])
                siglev = 0.125 * peaks[i] + 0.875 * siglev
                if n > 2:
                    RR = [qrs_i[-2] - qrs_i[-3], qrs_i[-1] - qrs_i[-2]]
                    RRavr = np.mean(RR)
                    HR = 60/RR[-1] * 1/fs * 1000000
                    if type == 1:
                        print(RR[-1], RRavr)
                    if 0.92 * RRavr <= RR[-1] < 1.16 * RRavr:
                        print(HR)
                    elif 1.16 * RRavr <= RR[-1] < 1.66 * RRavr or 360 <= RR[-1] < 0.92 * RRavr:
                        print('Heart rate is irregular')
                    elif RR[-1] >= 1.66 * RRavr:
                        thrs = 0.5 * thrs
                        print('need search back')
            else:
                noislev = 0.125 * peaks[i] + 0.875 * noislev
            thrs_buf.append(thrs)
            thrs_buf_i.append(peaks_i[i])
            thrs = noislev + 0.25 * (siglev - noislev)
    return qrs_i, thrs_buf, thrs_buf_i

if __name__ == "__main__":
    # Training
    x, ecg = datalogging.matfile('data4.mat', 'abd1')
    x = np.array(x)
    fs = 1000

    ecg_f, ecg_m = filtering(ecg, fs)

    # Learning phase 1 (initialize threshold based on first 2 s of signal)
    siglev = max(ecg_m[0:int(2000000/fs)])/2
    noislev = np.mean(ecg_m[0:int(2000000/fs)])/2
    thrs = noislev + 0.25 * (siglev - noislev)

    # find all peaks
    peaks_i, _ = signal.find_peaks(ecg_m, distance=np.round(0.09 * fs))
    peaks = ecg_m[peaks_i]

    # R-peak mother detection
    mqrs_i, mthrs_buf, mthrs_buf_i = detection(peaks, peaks_i, thrs, siglev, noislev, type=0)
    # R-peak fetus detection
    f_peaks_i = peaks_i
    for i in range(len(mqrs_i)):
        f_peaks_i = f_peaks_i[f_peaks_i != mqrs_i[i]]
    f_peaks = ecg_m[f_peaks_i]
    # Learning phase 1 (initialize threshold based on first 2 s of signal)
    siglev = max(f_peaks[0:int(2000000/fs)])/2
    noislev = np.mean(f_peaks[0:int(2000000/fs)])/2
    fthrs = noislev + 0.25 * (siglev - noislev)
    fqrs_i, fthrs_buf, fthrs_buf_i = detection(f_peaks, f_peaks_i, fthrs, siglev, noislev, type=1)

    plt.figure()
    plt.plot(x, ecg)
    plt.figure()
    plt.plot(x, ecg_f)
    # plt.figure()
    # plt.plot(x, ecg_m)
    plt.figure()
    plt.plot(x, ecg_m)
    plt.plot(x[peaks_i], ecg_m[peaks_i], '*r')
    plt.figure()
    plt.plot(x, ecg_m, 'k')
    plt.plot(x[mthrs_buf_i], mthrs_buf, 'b')
    plt.plot(x[mqrs_i], ecg_m[mqrs_i], '*b')
    plt.plot(x[fthrs_buf_i], fthrs_buf, 'r')
    plt.plot(x[fqrs_i], ecg_m[fqrs_i], '*r')
    plt.show()
