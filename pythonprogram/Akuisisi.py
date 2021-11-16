import matplotlib.pyplot as plt
import Clustering
import datalogging
import preprocesing
# Load Data
x, abd = datalogging.matfile('fekgShort.mat', 'abd1')
# x, abd = datalogging.loadcsv('rawdata.csv')
# pre processing
abd_den = preprocesing.pp(abd)

# save data
datalogging.savecsv(x, abd_den, 'data1.csv')
# peak and amplitude detection
abd_amp, abd_peak, ns = preprocesing.peakvalley(abd_den)

# Clustering
abd_peak1i, abd_peak2i = Clustering.Case4(abd_amp, abd_peak, x, abd_den, ns)
datalogging.plotresult(x, abd_den, abd_peak1i, abd_peak2i)

plt.show()
