import pandas as pd
import pygslib as p
# import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import numpy as np
from histograms import plot_histogram


# Importing data from file
collar = pd.read_csv('COLLAR CSV.csv')
survey = pd.read_csv('SURVEY CSV.csv')
assay = pd.read_csv('ASSAY CSV.csv')
geology = pd.read_csv('GEOLOGY.csv')
# print(assay.head(60))

# assay.drop(index=[0,1],axis=1, inplace=True)
# print(assay.head(60))

# ## making non-sampled intervals equal to zero
# assay.loc[~np.isfinite(assay['CU']), 'CU']=0
# print('\n',assay.head(20))

##creating a drillhole object
mydholedb= p.drillhole.Drillhole(collar=collar, survey=survey)

## now you can add as many interval tables as you want, for example, assays, lithology and RQD.
mydholedb.addtable(assay, 'assay', overwrite = False)
mydholedb.addtable(geology, 'geology', overwrite = False)

## validating a drillhole object
# mydholedb.validate()


## validating interval tables
# mydholedb.validate_table('geology')
# print(mydholedb.table['assay'].head(10))


##compositing
##Calculating length of sample intervals
mydholedb.table['assay']['Length'] = mydholedb.table['assay']['TO']- mydholedb.table['assay']['FROM']
print(mydholedb.table['assay'].head(10))


length_mode = mydholedb.table['assay']['Length'].mode()[0]
print ('The Length Mode is:',length_mode)


## plotting the interval lengths
# plot_histogram(data =mydholedb.table['assay']['Length'], bin_edges=[0,2,4,6,8,10,12,14])


## Compositing
mydholedb.downh_composite(
    'assay',
    variable_name= "caco3",
    new_table_name= "CMP",
    cint = length_mode,
    minlen=-1,
    overwrite = True
)
# print (mydholedb.table["CMP"].tail(70))


## desurveying an interval table
mydholedb.desurvey('CMP',warns=False, endpoints=True)
# print (mydholedb.table["CMP"].head(70))


## creating BHID of type integer
mydholedb.txt2intID('CMP')
print (mydholedb.table["CMP"][['BHID', 'BHIDint', 'FROM', 'TO']].head(70))


## exporting results to VTK
mydholedb.intervals2vtk('CMP', 'cmp.vtk')
