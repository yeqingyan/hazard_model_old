import pickle
from Utils.Plot import *

dist = pickle.load(open("prob.pickle", 'rb'))
plot_distrubtion(dist, len(dist), show=False)