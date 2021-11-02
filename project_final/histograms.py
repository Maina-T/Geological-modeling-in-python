import matplotlib.pyplot as plt

def plot_histogram(data, bin_edges):
    # sns.set()
    plt.hist(data, bins=bin_edges)
    plt.xlabel('drill holes length')
    plt.ylabel('Drillhole numbers ')
    plt.show()