import pandas as pd
import pygslib as p
# import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import numpy as np
from histograms import plot_histogram
import math



class VariogramGenerator:

    def __init__(self, data):
        self.data = data
        self.lag = []

    def calculate_gamma_h(self):
        output = []
        for data_lists in self.lag:
            number_of_pairs = len(data_lists)
            squared_difference = []
            for value in data_lists:
                z_difference = data_lists[0]['z_axis'] - value['z_axis']
                z_difference_squared = z_difference ** 2
                squared_difference.append(z_difference_squared)
            sum_of_squared_difference = sum(squared_difference)
            a = sum_of_squared_difference/2
            gamma_h = a * number_of_pairs
            if gamma_h > 0.0:
                output.append(gamma_h)
        # print(output)
        return output

    def plot_graph(self):
        euclidean_distance = self.calculate_euclidean_distance()
        y_h = self.calculate_gamma_h()

        # print(euclidean_distance, y_h)

        # Dataset
        x = np.array(euclidean_distance)
        y = np.array(y_h)

        # Plotting the Graph
        plt.plot(x, y, 'o')
        plt.title("Variogram")
        plt.xlabel("Distance")
        plt.ylabel("gamma(h)")
        plt.grid()
        plt.savefig('./files/variogram')
        plt.show()


    def calculate_euclidean_distance(self):
        output = []
        for x in self.lag:
            # print(x[0])
            number_of_pairs = len(self.lag)
            data = []
            for y in x:
                x_difference = x[0]['x_axis'] - y['x_axis']
                y_difference = x[0]['y_axis'] - y['y_axis']
                x_squared = x_difference ** 2
                y_squared = y_difference ** 2
                total_squared = x_squared + y_squared
                euclidean_distance = math.sqrt(total_squared)
                data.append(euclidean_distance)

            sum_of_euclidean_distance = sum(data)
            average_separation_distance = sum_of_euclidean_distance/number_of_pairs
            if average_separation_distance > 0.0:
                output.append(average_separation_distance)
        
        return output
        

    def run(self):
        """Import data from csv files"""
        self.collar = pd.read_csv(self.data['collar'])
        x_axis = self.collar['XCOLLAR'].to_list()
        y_axis = self.collar['YCOLLAR'].to_list()
        value = self.collar['ZCOLLAR'].to_list()

        start = 0
        while start < len(x_axis):
            x_set = []
            y_set = []
            elevation = []

            grouped_data = []

            for i in range(start,len(x_axis)):
                x_set.append(x_axis[i])
            
            for i in range(start, len(y_axis)):
                y_set.append(y_axis[i])

            for i in range(start, len(value)):
                elevation.append(value[i])


            for x , y, z in zip(x_set,y_set,elevation):
                data = {
                    'x_axis': x,
                    'y_axis': y,
                    'z_axis': z
                }
                # print(data)
                grouped_data.append(data)

          
            self.lag.append(grouped_data)

            start += 1

        self.plot_graph()
       

if __name__ == "__main__":
    data = {
        'collar': 'COLLAR CSV.csv',
        'survey': 'SURVEY CSV.csv',
        'assay': 'ASSAY CSV.csv',
        'geology': 'GEOLOGY.csv'
    }
    bot = VariogramGenerator(data)
    bot.run()