from matplotlib import pyplot as plt
import pickle
from scipy import stats
import scipy

def plot(data):
    for k,d in data.items():
        plt.plot(d, label=k)
    plt.legend()
    plt.show()

def plot_distrubtion(data):
    for k,d in data.items():
        plt.hist(d, label=k)
    plt.legend()
    plt.show()

x = scipy.arange(0, 1, 0.05)
data = pickle.load(open("prob.pickle", 'rb'))[:50]
stats.powerlaw.pdf(x, )
# data = [d for d in data if d <= 0.4]
print(stats.powerlaw.fit(data))
stats.powerlaw.pdf()
plt.hist(data, bins = 100)
plt.show()
# print(len(data))