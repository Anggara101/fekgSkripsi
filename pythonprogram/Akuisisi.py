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
Clustering.Case1(abd_amp, abd_peak, x, abd_den, ns)

plt.show()
