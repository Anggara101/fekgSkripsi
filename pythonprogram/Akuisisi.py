import numpy as np
from scipy import signal
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import datalogging


def filtering(y, sf):
    # bandpass filter
    f1 = 9
    f2 = 27
    wn = np.array([f1, f2]) * 2 / sf
    [b, a] = signal.butter(2, wn, 'bandpass', output='ba')
    # Filter the signal
    y_f = np.zeros(len(y))
    for m in range(len(b), len(y)):
        y_f[m] = b[0] * y[m]
        for i in range(1, len(b)):
            y_f[m] += b[i] * y[m - i] - a[i] * y_f[m - i]

    # Derivative Filter
    b = np.array([1, 2, 0, -2, -1]) * (1 / 8) * sf
    y_d = np.zeros(len(y_f))
    for m in range(len(b), len(y_f)):
        y_d[m] = b[0] * y_f[m]
        for i in range(1, len(b)):
            y_d[m] += b[i] * y_f[m - i]
    y_d = y_d / 4000

    y_s = y_d ** 2

    window_width = 75
    kernel = np.ones((window_width, 1)) / window_width
    b = kernel[:, 0]
    y_m = np.zeros(len(y_s))
    for m in range(len(b), len(y_s)):
        y_m[m] = b[0] * y_s[m]
        for i in range(1, len(b)):
            y_m[m] += b[i] * y_s[m - i]
    return y_f, y_m


def training(ecg, fs):
    ecg_f, ecg_m = filtering(ecg, fs)

    # find all peaks
    peaks_i, _ = signal.find_peaks(ecg_m, distance=np.round(0.09 * fs))
    peaks = ecg_m[peaks_i]

    kmeans = KMeans(n_clusters=2)
    kmeans.fit(peaks.reshape(-1, 1))
    peaks_clus = kmeans.labels_
    cent = kmeans.cluster_centers_
    cent_i = np.argsort(cent.T)
    cent_i = cent_i[0]
    peaks_m = peaks[peaks_clus == cent_i[1]]
    peaks0 = peaks[peaks_clus == cent_i[0]]
    mqrs_i = np.array([], dtype=int)
    for i in range(len(peaks_m)):
        mqrs_i = np.append(mqrs_i, np.argwhere(ecg_m == peaks_m[i]))
        if i >= 2:
            mRR = np.diff(mqrs_i)
            mRRavr = np.mean(mRR)
            if 360 <= mRR[i - 2] < 1.4 * mRRavr:
                mHR = 60 / mRR[i-2] * 1 / fs * 1000000
                # print(f'{mqrs_i[-1]} mHR normal : {mHR}')
            elif mRR[i - 2] >= 1.4 * mRRavr:
                mHR = 60 / mRR[i-2] * 1 / fs * 1000000
                # print(f'{mqrs_i[-1]} mHR need search back: {mHR}')
            else:
                # print(f'{mqrs_i[-1]} mHR: {mHR}')
                mqrs_i = np.delete(mqrs_i, -1)


    kmeans2 = KMeans(n_clusters=2)
    kmeans2.fit(peaks0.reshape(-1, 1))
    peaks0_clus = kmeans2.labels_
    fcent = kmeans2.cluster_centers_
    fcent_i = np.argsort(fcent.T)
    fcent_i = fcent_i[0]
    peaks_f = peaks0[peaks0_clus == fcent_i[1]]
    fqrs_i = np.array([], dtype=int)
    for i in range(len(peaks_f)):
        fqrs_i = np.append(fqrs_i, np.argwhere(ecg_m == peaks_f[i]))
        if i >= 2:
            fRR = np.diff(fqrs_i)
            fRRavr = np.mean(fRR)
            if 200 <= fRR[i - 2] < 1.4 * fRRavr:
                fHR = 60 / fRR[i-2] * 1 / fs * 1000000
                # print(f'{fqrs_i[-1]} fHR normal : {fHR}')
            elif fRR[i - 2] >= 1.4 * fRRavr:
                fHR = 60 / fRR[i-2] * 1 / fs * 1000000
                # print(f'{fqrs_i[-1]} fHR need search back: {fHR}')
            else:
                # print(f'{fqrs_i[-1]} fHR skip: {fHR}')
                fqrs_i = np.delete(fqrs_i, -1)

    return ecg_m, mqrs_i, fqrs_i, kmeans, kmeans2, cent, fcent


if __name__ == '__main__':
    x, ecg_raw = datalogging.matfile('data4.mat', 'abd2')
    x = np.array(x)
    ecg = np.array(ecg_raw)
    fs = 1000

    len_training = 10000
    ecg_m, mqrs_i, fqrs_i, kmeans, kmeans2, cent, fcent = training(ecg[:len_training], fs)

    x_training = x[:len_training]
    plt.figure()
    plt.plot(x_training, ecg_m)
    plt.plot(x_training[mqrs_i], ecg_m[mqrs_i], 'r*')
    plt.plot(x_training[fqrs_i], ecg_m[fqrs_i], 'y*')

    # Bandpass filter parameter
    f1 = 9
    f2 = 27
    wn = np.array([f1, f2]) * 2 / fs
    [b_b, a_b] = signal.butter(2, wn, 'bandpass', output='ba')
    # Derivative filter parameter
    b_d = np.array([1, 2, 0, -2, -1]) * (1 / 8) * fs
    # Moving window integration parameter
    window_width = 75
    kernel = np.ones((window_width, 1)) / window_width
    b_m = kernel[:, 0]

    # init
    distance = int(0.09 * fs)
    len_buf = distance
    ecg_buf = np.zeros(len_buf)
    ecg_f_buf = np.zeros(len_buf)
    ecg_d_buf = np.zeros(len_buf)
    ecg_s_buf = np.zeros(len_buf)
    ecg_m_buf = np.zeros(len_buf)
    peaks_i = np.array([], dtype=int)
    peaks = np.array([], dtype=float)
    peak_i_buf2 = np.zeros(2, dtype=int)
    peak_len = distance
    if cent[0] > cent[1]:
        clus1 = 0
    else:
        clus1 = 1
    if fcent[0] > fcent[1]:
        clus2 = 0
    else:
        clus2 = 1

    for i in range(len_training, len(ecg)):
        # Bandpass filtering
        ecg_buf[0] = ecg[i]
        ecg_f_buf[0] = b_b[0] * ecg_buf[0]
        for m in range(1, len(b_b)):
            ecg_f_buf[0] += b_b[m] * ecg_buf[m] - a_b[m] * ecg_f_buf[m]
        # ecg_f = np.append(ecg_f, ecg_f_buf[0])

        # Derivative filtering
        ecg_d_buf[0] = b_d[0] * ecg_f_buf[0]
        for m in range(1, len(b_d)):
            ecg_d_buf[0] += b_d[m] * ecg_f_buf[m]
        ecg_d_buf[0] = ecg_d_buf[0] / 4000

        # Squaring
        ecg_s_buf[0] = ecg_d_buf[0] ** 2

        # Moving window integration
        ecg_m_buf[0] = b_m[0] * ecg_s_buf[0]
        for m in range(1, len(b_m)):
            ecg_m_buf[0] += b_m[m] * ecg_s_buf[m]
        ecg_m = np.append(ecg_m, ecg_m_buf[0])

        # Find peaks
        if i >= 10000 + peak_len:
            peak_buf = np.max(ecg_m_buf)
            peak_i_buf = np.argwhere(ecg_m == peak_buf)
            peak_i_buf = peak_i_buf[0]
            peak_i_buf2[0] = peak_i_buf
            peak_len += int(distance/2)
            if peak_i_buf2[0] != peak_i_buf2[1]:
                try:
                    if ecg_m[peak_i_buf] > ecg_m[peak_i_buf + 1] and ecg_m[peak_i_buf] > ecg_m[peak_i_buf - 1]:
                        peaks_i = np.append(peaks_i, peak_i_buf)
                        peaks = np.append(peaks, peak_buf)

                        # Clustering
                        peaks_clus = kmeans.predict(peaks[-1].reshape(-1, 1))
                        if peaks_clus[0] == clus1:
                            mqrs_i = np.append(mqrs_i, peak_i_buf)
                            mRR = np.diff(mqrs_i)
                            mRRavr = np.mean(mRR[:-1])
                            if 360 <= mRR[-1] < 1.66 * mRRavr:
                                mHR = 60 / mRR[-1] * 1 / fs * 1000000
                                print(f'{mqrs_i[-1]} mHR normal : {mHR}')
                            elif mRR[-1] >= 1.66 * mRRavr:
                                mHR = 60 / mRR[-1] * 1 / fs * 1000000
                                print(f'{mqrs_i[-1]} mHR need search back: {mHR}')
                            else:
                                print(f'{mqrs_i[-1]} mHR skip')
                                fqrs_i = np.delete(fqrs_i, -1)
                        else:
                            peaks_clus2 = kmeans2.predict(peaks[-1].reshape(-1, 1))
                            if peaks_clus2[0] == clus2:
                                fqrs_i = np.append(fqrs_i, peak_i_buf)
                                fRR = np.diff(fqrs_i[-8:])
                                fRRavr = np.mean(fRR[:-1])
                                if 200 <= fRR[-1] < 1.66 * fRRavr:
                                    fHR = 60 / fRR[-1] * 1 / fs * 1000000
                                    # print(f'{fqrs_i[-1]} fHR normal : {fHR}')
                                elif fRR[-1] >= 1.66 * fRRavr:
                                    fHR = 60 / fRR[-1] * 1 / fs * 1000000
                                    # print(f'{fqrs_i[-1]} fHR need search back: {fHR}')
                                else:
                                    # print(f'{fqrs_i[-1]} fHR skip')
                                    fqrs_i = np.delete(fqrs_i, -1)

                except IndexError:
                    # print(peak_i_buf)
                    pass
            peak_i_buf2[1] = peak_i_buf2[0]

        # reset filtering
        for m in reversed(range(len_buf - 1)):
            ecg_buf[m + 1] = ecg_buf[m]
            ecg_f_buf[m + 1] = ecg_f_buf[m]
            ecg_d_buf[m + 1] = ecg_d_buf[m]
            ecg_s_buf[m + 1] = ecg_s_buf[m]
            ecg_m_buf[m + 1] = ecg_m_buf[m]

    plt.figure()
    plt.plot(x, ecg_m)
    plt.plot(x[peaks_i], ecg_m[peaks_i], '*')
    plt.figure()
    plt.plot(x, ecg_m)
    plt.plot(x[mqrs_i], ecg_m[mqrs_i], 'r*')
    plt.plot(x[fqrs_i], ecg_m[fqrs_i], 'y*')
    plt.show()
