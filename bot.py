import pandas as pd
import pygslib as p
# import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import numpy as np
from histograms import plot_histogram


class TestEstimation:

    def __init__(self, data):
        self.data = data
        

    def load_data(self):
        """Import data from csv files"""
        self.collar = pd.read_csv(self.data['collar'])
        self.survey = pd.read_csv(self.data['survey'])
        self.assay = pd.read_csv(self.data['assay'])
        # print(self.assay.head(60))

    def create_database(self):
        """create a drillhole object(database)"""
        self.dhole_db= p.drillhole.Drillhole(collar=self.collar, survey=self.survey)

    def add_interval_tables(self):
        """now you can add as many interval tables as you want, for example, assays, lithology and RQD."""
        self.dhole_db.addtable(self.assay, 'assay', overwrite = False)


    def validate_dhole_db(self):
        """validating a drillhole object and """
        self.dhole_db.validate()

    
    def validate_intervals_tables(self):
        """validating interval tables"""
        self.dhole_db.validate_table('assay')

    def clean_survey_table(self):
        """fixing the issue of single interval at survey table"""
        self.dhole_db.fix_survey_one_interval_err(90000.)


    def clean_none_sampled_intervals(self):
        """making non-sampled intervals equal to zero"""
        self.assay.loc[~np.isfinite(self.assay['CU']), 'CU']=0



    def composite(self):
        """Compositing"""
        ##Calculating length of sample intervals
        self.dhole_db.table['assay']['Length'] = self.dhole_db.table['assay']['TO']- self.dhole_db.table['assay']['FROM']
        # print(self.dhole_db.table['assay'].head(10))

        length_mode = self.dhole_db.table['assay']['Length'].mode()[0]  #Find the length mode
        # print ('The Length Mode is:',length_mode)

        # plotting the interval lengths
        # plot_histogram(data =self.dhole_db.table['assay']['Length'], bin_edges=[0,2,4,6,8,10,12,14])

        ## Compositing
        self.dhole_db.downh_composite(
            'assay',
            variable_name= "CU",
            new_table_name= "CMP",
            cint = length_mode,
            minlen=-1,
            overwrite = True
        )
      
        self.dhole_db.desurvey('CMP',warns=False, endpoints=True) # Desurveying and create a table with desurveyed points
    
        self.dhole_db.txt2intID('CMP') # creating BHID of type integer of the desurveyed table
        # print (mydholedb.table["CMP"][['BHID', 'BHIDint', 'FROM', 'TO']].head(70))

        #exporting results to VTK
        self.dhole_db.intervals2vtk('CMP', './files/cmp.vtk')

        self.dhole_db.table["CMP"].to_csv('./files/cmp.csv', index=False)


    def inspect_interval_tables(self):
        print ("Table names ", self.dhole_db.table_mames)


    def create_mineralized_domain(self):
        """Tag samples inside the wireframe as mineralized domain"""
        # importing the wireframe
        self.domain= p.vtktools.loadSTL('domain.stl')
        
        ## creating array to tag samples in domain1
        inside1= p.vtktools.pointinsolid(
            self.domain,
            x= self.dhole_db.table['CMP']['xm'].values,
            y= self.dhole_db.table['CMP']['ym'].values,
            z= self.dhole_db.table['CMP']['zm'].values
        )

        ## creating a new domain field
        self.dhole_db.table['CMP']['Domain']= inside1.astype(int)

        # exporting results to VTK
        self.dhole_db.intervals2vtk('CMP', './files/cmp_tagged_samples.vtk')

        # exporting to csv
        self.dhole_db.table["CMP"].to_csv('./files/cmp_tagged_samples.csv', index=False)

    def create_block_models(self):
        """Block modeling"""
        ## creating a block model parameter
        xorg = 2288230
        yorg = 415200
        zorg = -1000
        dx = 100
        dy = 100
        dz = 30
        nx = 160
        ny = 100
        nz = 90

        # Creating an empty block model
        mymodel=p.blockmodel.Blockmodel(nx,ny,nz,xorg,yorg,zorg,dx,dy,dz)

        # filling wireframe with blocks
        mymodel.fillwireframe(self.domain)
        
        # the fillwireframe function generates a field named  __in,
        # this is the proportion inside the wireframe. Here we rename __in to D1
        mymodel.bmtable.rename(columns={'__in': 'D1'},inplace=True)

        # creating a partial model by filtering out blocks with zero proportion (percentage) inside the solid (wireframe)
        mymodel.set_blocks(mymodel.bmtable[mymodel.bmtable['D1']> 60])
        
        # export partial model to a VTK unstructured grid (*.vtu)
        mymodel.blocks2vtkUnstructuredGrid(path='./files/model.vtu')

    
    
    def run(self):
        self.load_data()
        self.create_database()
        self.add_interval_tables()
        self.clean_none_sampled_intervals()
        self.clean_survey_table()
        # self.validate_intervals_tables()
        # self.validate_dhole_db()
        self.composite()
        self.create_mineralized_domain()
        self.create_block_models()
        self.inspect_interval_tables()

if __name__ == '__main__':
    data = {
        'collar': 'collar_BABBITT.csv',
        'survey': 'survey_BABBITT.csv',
        'assay': 'assay_BABBITT.csv',
    }
    bot = TestEstimation(data)
    bot.run()