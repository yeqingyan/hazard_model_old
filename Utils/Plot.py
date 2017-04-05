from matplotlib import pyplot as plt


def plot(data):
    for k,d in data.items():
        plt.plot(d, label=k)
    plt.legend()
    plt.show()
