import pandas as pd
import pygslib as p
import matplotlib.pyplot as plt
import numpy as np
from histograms import plot_histogram


class Estimate:

    def __init__(self, data, block_parameters):
        self.data = data
        self.block = block_parameters

        

    def load_data(self):
        """Import data from csv files"""
        self.collar = pd.read_csv(self.data['collar'])
        self.survey = pd.read_csv(self.data['survey'])
        self.assay = pd.read_csv(self.data['assay'])
        self.geology = pd.read_csv(self.data['geology'])
        self.survey['DIP'] = - self.survey['DIP']
        self.wireframe = p.vtktools.loadSTL('domain1.stl') #domain1 wireframe
        # print(self.survey.head(60))

    def create_database(self):
        """create a drillhole object(database)"""
        self.dhole_db= p.drillhole.Drillhole(collar=self.collar, survey=self.survey)

    def add_interval_tables(self):
        """now you can add as many interval tables as you want, for example, assays, lithology and RQD."""
        self.dhole_db.addtable(self.assay, 'assay', overwrite = False)
        self.dhole_db.addtable(self.geology, 'geology', overwrite = False)

    def validate_intervals_tables(self):
        """validating interval tables"""
        self.dhole_db.validate_table('geology')
        self.dhole_db.validate_table('assay')


    def validate_db(self):
        """validating a drillhole object and """
        self.dhole_db.validate()

    

    def block_model_size(self):
        xmin = self.collar['XCOLLAR'].max()
        ymin = self.collar['YCOLLAR'].max()
        print(xmin,ymin)


    def composite(self):
        """ This python function perform Compositing (weighted-length) using caco3 column in the  assay.csv"""

        ##Calculating length of sample intervals
        self.dhole_db.table['assay']['Length'] = self.dhole_db.table['assay']['TO']- self.dhole_db.table['assay']['FROM']
        # print(self.dhole_db.table['assay'].head(10))

        
        length_mode = self.dhole_db.table['assay']['Length'].mode()[0]  #Find the length mode
        # print ('The Length Mode is:',length_mode)

        #plotting the interval lengths
        plot_histogram(self.dhole_db.table['assay']['Length'].hist(bins = np.arange(0.25,10, 0.5)))

        # Composite
        self.dhole_db.downh_composite('assay', "caco3", 'CMP_assay',cint = 3)
        self.dhole_db.desurvey('CMP_assay',warns=False, endpoints=True) # Desurveying and create a table with desurveyed points
        self.dhole_db.txt2intID('CMP_assay')
        
        
        # creating array to tag samples in domain1
        dm1=p.vtktools.pointinsolid(self.dom1,
                            x=self.dhole_db.table['CMP_assay']['xm'].values,
                            y=self.dhole_db.table['CMP_assay']['ym'].values,
                            z=self.dhole_db.table['CMP_assay']['zm'].values)

        # creating a new domain field
        self.dhole_db.table['CMP_assay']['Domain']= dm1

        # Save and verify
        self.dhole_db.intervals2vtk('CMP_assay', './files/CMP_assay')
        self.dhole_db.table["CMP_assay"].to_csv('./files/CMP_assay.csv', index=False)


        # composite only in domain 1
        self.dhole_db.addtable(
            self.dhole_db.table['CMP_assay'].loc[self.dhole_db.table['CMP_assay']['Domain']==1], 'domain_table',
            overwrite = True
        )
        self.dhole_db.downh_composite('domain_table', "caco3", 'CMP_caco3',cint = 3, overwrite = True)
        self.dhole_db.desurvey('CMP_caco3')
        self.dhole_db.txt2intID('CMP_caco3')
        self.dhole_db.intervals2vtk('CMP_caco3', './files/CMP_caco3')
        self.dhole_db.table["CMP_caco3"].to_csv('./files/CMP_caco3.csv', index=False)
        # print(self.dhole_db.table["CMP_caco3"][['BHID', 'BHIDint', 'FROM', 'TO']].head(70))

    
    def block_model(self):
        # create a block model object
        self.model = p.blockmodel.Blockmodel(
            xorg = self.block['xorg'],
            yorg = self.block['yorg'],
            zorg = self.block['zorg'],
            dx = self.block['dx'],
            dy = self.block['dy'],
            dz = self.block['dz'],
            nx = self.block['nx'],
            ny = self.block['ny'],
            nz = self.block['nz']
        )

        # fill the wireframe with blocks
        self.model.fillwireframe(self.wireframe)

        # remove blocks with 0% outside the wireframe (mineralized Zone) 
        self.model.set_blocks(self.model.bmtable.loc[self.model.bmtable['__in']>0])
        
        # Save to vtk and csv file for visualization in paraview
        self.model.blocks2vtkUnstructuredGrid('./files/model_grid')
        self.model.bmtable.to_csv('./files/model_grid.csv', index=False)


    def estimate(self):
        # interpolate
        kt3d_parameters = {
             # Input Data
            # ----------
            'x' : self.dhole_db.table['CMP_caco3']['xm'].values,   # 1D array('f'), x coordinates of input data
            'y' : self.dhole_db.table['CMP_caco3']['ym'].values,   # 1D array('f'), y coordinates of input data
            'z' : self.dhole_db.table['CMP_caco3']['zm'].values,   # 1D array('f'), z coordinates of input data
            'vr' : self.dhole_db.table['CMP_caco3']['caco3'].values,   # 1D array('f'), primary variable
            've' : None,   # (optional) 1D array('f'), extra variable, external drift
            'bhid': self.dhole_db.table['CMP_caco3']['BHIDint'].values, #  (optional) 1D array('i'), drillhole ID, or fault zone ID
            
            # Output grid definition (only used for superblock search, can use dummy values)
            # ---------- not used, can ignore this, is supper block in gslib
            'nx' : 1,   # int, size of the grid
            'ny' : 1,   # int,
            'nz' : 1,   # int,
            'xmn' : 0,   # float, origing of coordinate
            'ymn' : 0,   # float,
            'zmn' : 0,   # float,
            # Output data
            # ----------
            'xsiz' : self.block['dx'],   # float, block size in x
            'ysiz' : self.block['dy'],   # float, block size in x
            'zsiz' : self.block['dz'],   # float, block size in x
            'nxdis' : 3,   # int, number of discretization points in x
            'nydis' : 3,   # int, number of discretization points in y
            'nzdis' : 3,   # int, number of discretization points in z
            'outx' : self.model.bmtable.iloc[[120]][['XC']].values,   # 1D array('f'), x coordinates of output data
            'outy' : self.model.bmtable.iloc[[120]][['YC']].values,   # 1D array('f'), y coordinates of output data
            'outz' : self.model.bmtable.iloc[[120]][['ZC']].values,   # 1D array('f'), z coordinates of output data
            'outextve' : None,   # 1D array('f') external drift in output data
            # Search parameters
            # ----------
            'radius'     : 120,   # float, search distance in direction 1 ###120
            'radius1'    : 120,   # float, search distance in direction 2  ##120
            'radius2'    : 120,   # float, search distance in direction 3
            'ndmax'      : 12,   # int, maximum number of points
            'ndmin'      : 5,   # int, minimum number of points
            'noct'       : 0,   # (optional) int, maximum number of samples per octant, if zero octans not used, default == 0
            'nbhid'      : 3,   # (optional) int, maximum number of samples from each drillhole, default not used == 0
            'sang1'      : 0,   # (optional) float, rotation angle 1
            'sang2'      : 0,   # (optional) float, rotation angle 1
            'sang3'      : 0,   # (optional) float, rotation angle 1
            # Kriging parameters and options
            # ----------
            'idrif'      : None,   # (optional) array('i'), array of 9 indicators to use drift models
            'itrend'     : None,   # (optional) int, if == 1 the trend will be estimated
            'ktype'      : 1,   # (optional) int, kriging type: 0 skmean, 1 ordinary kriging, 2 simple kriging with local means, 3 kriging with an external drift
            'skmean'     : 0,   # (optional) float, simple kriging mean for ktype = 0
            'koption'    : 0,   # (optional) int, set to 0 for kriging a grid of points or blocks, to 1 for cross validation with the data in datafl and to 2 for jackknifing
            'iktype'     : 0,   # (optional) int, median indicator kriging, default False = 0
            'cut'        : None,   # (optional) 1D array('f'), thresholds for median indicator kriging, default = []
            'idbg'       : 1,   # (optional) int, debug ?, defaul False == 0
            # Inverse of the power of the distance parameter
            'id2power'   : 2,   # (optional) float, inverse of the distance powe, defaul 2
            # Variogram parameters
            # ----------
            'c0'         : 0.25,   # float, nugget value
            'it'         : [2],   # array('i'), structures type, on for each structure: 1 Spherical, 2 Exponential, 3 Gaussian, 4 Power, 5 Cosine hole effect
            'cc'         : [0.75],   # array('f'), structures variance, one for each structure
            'aa'         : [100],   # array('f'), structures range/practical range in direction 1, one for each structure
            'aa1'        : [100],   # array('f'), structures range/practical range in direction 2, one for each structure
            'aa2'        : [100],   # array('f'), structures range/practical range in direction 3, one for each structure
            'ang1'       : [0.],   # (optional) array('f'), rotation angle 1, one for each structure, defaul array of zeros
            'ang2'       : [0.],   # (optional) array('f'), rotation angle 2, one for each structure, defaul array of zeros
            'ang3'       : [0.]   # (optional) array('f'), rotation angle 3, one for each structure, defaul array of zeros

        }

        # estimating in one block
        estimate, debug, summary = p.gslib.kt3d(kt3d_parameters)
        # print(estimate, debug, summary)

        # saving debug to a csv file using Pandas
        pd.DataFrame({'x':debug['dbgxdat'],
                    'y':debug['dbgydat'],
                    'z':debug['dbgzdat'],
                    'wt':debug['dbgwt']}).to_csv('dbg_data.csv', index=False)
        # save block centroid
        self.model.bmtable.iloc[[120]][['XC','YC','ZC']].to_csv('dbg_blk.csv', index = False)

        # save the search ellipse to a VTK file
        p.vtktools.SavePolydata(debug['ellipsoid'], 'search_ellipsoid')


        # estimate in all blocks
        kt3d_parameters['outx'] = self.model.bmtable['XC']
        kt3d_parameters['outy'] = self.model.bmtable['YC']
        kt3d_parameters['outz'] = self.model.bmtable['ZC']
        kt3d_parameters['idbg'] = 0

        estimate, debug, summary = p.gslib.kt3d(kt3d_parameters)
        # print(estimate)


        # adding the estimate into the model
        self.model.bmtable['caco3_OK'] = estimate['outest']
        self.model.bmtable['caco3_ID2'] = estimate['outidpower']
        self.model.bmtable['caco3_NN'] = estimate['outnn']
        self.model.bmtable['caco3_Lagrange'] = estimate['outlagrange']
        self.model.bmtable['caco3_KVar']= estimate['outkvar']

        # Validations
        print ("Mean in model OK   :", self.model.bmtable['caco3_OK'].mean())
        print ("Mean in model ID2   :", self.model.bmtable['caco3_ID2'].mean())
        print ("Mean in model NN   :", self.model.bmtable['caco3_NN'].mean())
        print ("Mean in data    :", self.dhole_db.table['CMP_caco3']['caco3'].mean())


        self.model.bmtable.groupby('XC')[['caco3_OK','caco3_ID2','caco3_NN']].mean().plot()
        self.model.bmtable.groupby('YC')[['caco3_OK','caco3_ID2','caco3_NN']].mean().plot()
        self.model.bmtable.groupby('ZC')[['caco3_OK','caco3_ID2','caco3_NN']].mean().plot()

        # plt.show()

        # save model for visual inspection
        self.model.blocks2vtkUnstructuredGrid('model')
        self.model.bmtable.to_csv('model.csv', index=False)
           
    
    


    def inspect_interval_tables(self):
        print ("Table names ", self.dhole_db.table_mames)
    
    
    
    def run(self):
        self.load_data()
        self.create_database()
        self.add_interval_tables()
        # # # self.validate_intervals_tables()
        # # # # self.validate_db()
        self.composite()
        # self.block_model()
        # self.estimate()
        # self.inspect_interval_tables()
    
    
if __name__ == '__main__':
    data = {
        'collar': 'COLLAR CSV.csv',
        'survey': 'SURVEY CSV.csv',
        'assay': 'ASSAY CSV.csv',
        'geology': 'GEOLOGY.csv',
    }
    block_parameters = {
        'xorg':309360, #key block x coordinate
        'yorg': 9762420, #key block y coordinate
        'zorg': 1160, #key block z coordinate
        'dx': 10, #block size in X direction
        'dy': 10, #block size in y direction
        'dz': 10, #block size in z direction
        'nx': 28, #The number of blocks in X direction
        'ny': 50, #The number of blocks in y direction
        'nz': 140, #The number of blocks in z direction
    }
    block_parameters = {
        'xorg':309360,
        'yorg': 9762420,
        'zorg': 1160,
        'dx': 10,
        'dy': 10,
        'dz': 10,
        'nx': 28,
        'ny': 50,
        'nz': 290,
    }
    bot = Estimate(data,block_parameters)
    bot.run()