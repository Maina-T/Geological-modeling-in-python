import matplotlib.pyplot as plt

# def plot_histogram():
#     data =self.dhole_db.table['assay']['Length'], bin_edges=[0,2,4,6,8,10,12,14]
#     plt.hist(data, bins=bin_edges)
#     plt.xlabel('Class')
#     plt.ylabel('Number of samples')
#     plt.grid()
#     plt.savefig('./files/histo')
#     # plt.show()

def plot_histogram(plot):
    plt.xlabel('Class')
    plt.ylabel('Number of samples')
    plt.savefig('./files/histo')
    # plt.show()
    