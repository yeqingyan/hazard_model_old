from matplotlib import pyplot as plt


def plot(data):
    for d in data:
        plt.plot(d)
    plt.show()
