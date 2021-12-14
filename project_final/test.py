import pandas as pd
import pygslib as p
# import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import numpy as np
from histograms import plot_histogram


class Estimate:

    def __init__(self, data):
        self.data = data
        # self.block = block_parameters

        

    def load_data(self):
        """Import data from csv files"""
        self.collar = pd.read_csv(self.data['collar'])
        plt.plot(self.collar.XCOLLAR, self.collar.YCOLLAR, 'o')
        plt.grid()
        plt.show()
        # print(self.collar)

if __name__ == "__main__":
    data = {
        'collar': 'COLLAR CSV.csv',
        'survey': 'SURVEY CSV.csv',
        'assay': 'ASSAY CSV.csv',
        'geology': 'GEOLOGY.csv',
    }
    bot = Estimate(data)
    bot.load_data()