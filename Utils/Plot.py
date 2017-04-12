from matplotlib import pyplot as plt

def plot(data, show=True):
    for k,d in data.items():
        plt.plot(d, label=k)
    plt.legend()
    if show:
        plt.show()
    else:
        plt.savefig("plot.png")
    plt.clf()

def plot_distrubtion(data, show=True):
    for k,d in data.items():
        plt.hist(d, label=k, bins=100)
    plt.legend()
    if show:
        plt.show()
    else:
        plt.savefig("plot_dist.png")
    plt.clf()