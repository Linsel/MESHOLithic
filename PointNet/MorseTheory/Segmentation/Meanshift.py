import numpy as np

from sklearn.cluster import MeanShift
import numpy as np

def MeanShiftClusteringLabels(values=None,bandwidth=None):

    return  MeanShift(bandwidth=bandwidth).fit(values).labels_

