import pandas as pd
import pygslib as p
# import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import numpy as np
from histograms import plot_histogram


class Estimate:

    def __init__(self, data):
        self.data = data
        

    def load_data(self):
        """Import data from csv files"""
        self.collar = pd.read_csv(self.data['collar'])
        self.survey = pd.read_csv(self.data['survey'])
        self.assay = pd.read_csv(self.data['assay'])
        self.geology = pd.read_csv(self.data['geology'])
        self.survey['DIP'] = - self.survey['DIP']
        # print(self.survey.head(60))

    def create_database(self):
        """create a drillhole object(database)"""
        self.dhole_db= p.drillhole.Drillhole(collar=self.collar, survey=self.survey)

    def add_interval_tables(self):
        """now you can add as many interval tables as you want, for example, assays, lithology and RQD."""
        self.dhole_db.addtable(self.assay, 'assay', overwrite = False)
        self.dhole_db.addtable(self.geology, 'geology', overwrite = False)


    def validate_dhole_db(self):
        """validating a drillhole object and """
        self.dhole_db.validate()

    def block_model_size(self):
        xmin = self.collar['XCOLLAR'].max()
        ymin = self.collar['YCOLLAR'].max()
        print(xmin,ymin)



    # def generate_surface(self):
    #     # example generating a surface
    #     xmin = self.collar['XCOLLAR'].min()
    #     ymin = self.collar['YCOLLAR'].min()
    #     xmax = self.collar['XCOLLAR'].max()
    #     ymax = self.collar['YCOLLAR'].max()
    #     zmin = self.collar['ZCOLLAR'].min()
    #     zmax = self.collar['ZCOLLAR'].max()

    #     # define working region 
    #     xorg = -10.
    #     yorg = -10.
    #     zorg = -10.
    #     dx = 5.
    #     dy = 5.
    #     dz = 5.
    #     nx = 40
    #     ny = 44
    #     nz = 36

    #     topo = p.vtktools.rbfinterpolate(x=self.collar['XCOLLAR'].values.astype('float'),
    #                                    y=self.collar['YCOLLAR'].values.astype('float'),
    #                                    z=self.collar['ZCOLLAR'].values.astype('float'),
    #                                    xorg=xmin, yorg=ymin,dx=10,dy=10,nx=int((-xmin+xmax)/10),ny=int((-ymin+ymax)/10),
    #                                    snap = False)
    #     impl_topo = p.vtktools.implicit_surface(topo[0])

    #     region = p.vtktools.define_region_grid(xorg, yorg, zorg, dx/2, dy/2,  dz/4, nx*2, ny*2, nz*4) #, snapping_points = [topo,hw,fw])
    #     p.vtktools.SaveUnstructuredGrid(region, "region")
    #     region, topo_d = p.vtktools.evaluate_region(region, implicit_func = impl_topo, func_name='topo_d', invert=False, capt = -10000)

    #     dom_topo= np.minimum(topo_d)
    #     region = p.vtktools.set_region_field(region, dom_topo, 'dom_topo')

    #     # extract surface
    #     dom_topo_poly = p.vtktools.extract_surface(region,'dom_topo')
    #     # Save surface
    #     p.vtktools.SavePolydata(dom_topo_poly, 'dom_topo')

        # # the putput are points of the grid and vtk surface, use topo[0] to get vtk
        # topo = p.vtktools.rbfinterpolate(
        #                 x = self.collar['XCOLLAR'].values,
        #                 y = self.collar['YCOLLAR'].values,
        #                 z = self.collar['ZCOLLAR'].values,
        #                 xorg = xmin,
        #                 yorg = ymin,
        #                 dx = 10,
        #                 dy = 10,
        #                 nx = int((-xmin+xmax)/10),
        #                 ny = int((-ymin+ymax)/10),
        #                 epsilon=10,
        #                 method = 'linear')

        # save topo
        # p.vtktools.SavePolydata(topo[0], 'Topo')
        # p.vtktools.implicit_surface(topo[0],'Topo')
        # p.vtktools.SavePolydata(y, 'Topo')

    
    def validate_intervals_tables(self):
        """validating interval tables"""
        self.dhole_db.validate_table('geology')
        self.dhole_db.validate_table('assay')

    def composite(self):
        """Compositing"""

        ##Calculating length of sample intervals
        self.dhole_db.table['assay']['Length'] = self.dhole_db.table['assay']['TO']- self.dhole_db.table['assay']['FROM']
        # print(self.dhole_db.table['assay'].head(10))

        length_mode = self.dhole_db.table['assay']['Length'].mode()[0]  #Find the length mode
        # print ('The Length Mode is:',length_mode)

        # Composite
        self.dhole_db.downh_composite('assay', "caco3", 'assay_cmp',cint = 3)
        self.dhole_db.desurvey('assay_cmp',warns=False, endpoints=True) # Desurveying and create a table with desurveyed points

        dom1= p.vtktools.loadSTL('domain1.stl')
        
        # creating array to tag samples in domain1
        dm1=p.vtktools.pointinsolid(dom1,
                            x=self.dhole_db.table['assay_cmp']['xm'].values,
                            y=self.dhole_db.table['assay_cmp']['ym'].values,
                            z=self.dhole_db.table['assay_cmp']['zm'].values)

        # creating a new domain field
        self.dhole_db.table['assay_cmp']['Domain']= dm1

        # Save and verify
        self.dhole_db.intervals2vtk('assay_cmp','assay_array')

        # composite only in domain 1
        self.dhole_db.addtable(self.dhole_db.table['assay_cmp'].loc[self.dhole_db.table['assay_cmp']['Domain']==1], 'tmp', overwrite = True)
        self.dhole_db.downh_composite('tmp', "caco3", 'CMP_caco3',cint = 3, overwrite = True)
        self.dhole_db.desurvey('CMP_caco3')
        self.dhole_db.txt2intID('CMP_caco3')
        self.dhole_db.intervals2vtk('CMP_caco3', 'CMP_caco3')


    # def composite(self):
    #     """Compositing"""
    #     ##Calculating length of sample intervals
    #     self.dhole_db.table['assay']['Length'] = self.dhole_db.table['assay']['TO']- self.dhole_db.table['assay']['FROM']
    #     # print(self.dhole_db.table['assay'].head(10))

    #     length_mode = self.dhole_db.table['assay']['Length'].mode()[0]  #Find the length mode
    #     # print ('The Length Mode is:',length_mode)

    #     # plotting the interval lengths
    #     # plot_histogram(data =self.dhole_db.table['assay']['Length'], bin_edges=[0,2,4,6,8,10,12,14])

    #     ## Compositing
    #     self.dhole_db.downh_composite(
    #         'assay',
    #         variable_name= "caco3",
    #         new_table_name= "CMP",
    #         cint = length_mode,
    #         minlen=-1,
    #         overwrite = True
    #     )
      
    #     self.dhole_db.desurvey('CMP',warns=False, endpoints=True) # Desurveying and create a table with desurveyed points
    
    #     self.dhole_db.txt2intID('CMP') # creating BHID of type integer of the desurveyed table
    #     # print (mydholedb.table["CMP"][['BHID', 'BHIDint', 'FROM', 'TO']].head(70))

    #     #exporting results to VTK
    #     self.dhole_db.intervals2vtk('CMP', 'kabini.vtk')

    #     self.dhole_db.table["CMP"].to_csv('KabiniCMPdb.csv', index=False)


    def inspect_interval_tables(self):
        print ("Table names ", self.dhole_db.table_mames)
    
    
    
    def run(self):
        self.load_data()
        self.block_model_size()
        # self.generate_surface()
        # self.create_database()
        # self.add_interval_tables()
        # # self.validate_intervals_tables()
        # # self.validate_dhole_db()
        # self.composite()
        # self.inspect_interval_tables()
    
    
if __name__ == '__main__':
    data = {
        'collar': 'COLLAR CSV.csv',
        'survey': 'SURVEY CSV.csv',
        'assay': 'ASSAY CSV.csv',
        'geology': 'GEOLOGY.csv',
    }
    bot = Estimate(data)
    bot.run()