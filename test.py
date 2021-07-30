import pandas as pd
import pygslib as p
# import matplotlib.pylab as plt
import matplotlib.pyplot as plt
import numpy as np
from histograms import plot_histogram

# Importing data from file
collar = pd.read_csv('collar_BABBITT.csv')
survey = pd.read_csv('survey_BABBITT.csv')
assay = pd.read_csv('assay_BABBITT.csv')
# print(assay.head(60))
# print (assay.dtypes) # See columns types
# print(collar.head(30))
# print(survey.head(30))

## Droping some indexes
# collar.drop(index=[0,1],axis=1, inplace=True)
# assay.drop(index=[n for n in range(97)],axis=1, inplace=True)
# survey.drop(index=[0,1],axis=1, inplace=True)
# print(assay.head(60))

## droping some columns
assay.drop(['NI','S','FE'], axis=1, inplace=True)
# print('\n',assay.head(20))


## droping some columns and row indexes at the same time
# assay.drop(index=[0,10], columns=['NI','S','FE'], axis=1, inplace=True)
# print('\n',assay.head(20))


## making non-sampled intervals equal to zero
assay.loc[~np.isfinite(assay['CU']), 'CU']=0
# print('\n',assay.head(20))



##creating a drillhole object
mydholedb= p.drillhole.Drillhole(collar=collar, survey=survey)

## now you can add as many interval tables as you want, for example, assays, lithology and RQD.
mydholedb.addtable(assay, 'assay', overwrite = False)


## validating a drillhole object
# mydholedb.validate()

## fixing the issue of single interval at survey table
mydholedb.fix_survey_one_interval_err(90000.)
# mydholedb.validate()

# validating interval tables
# mydholedb.validate_table('assay')
# print(mydholedb.table['assay'].head(10))


### compositing
# Calculating length of sample intervals        ``
mydholedb.table['assay']['Length'] = mydholedb.table['assay']['TO']- mydholedb.table['assay']['FROM']
# print(mydholedb.table['assay'].head(10))

## plotting the interval lengths
# plot_histogram(data =mydholedb.table['assay']['Length'], bin_edges=[0,2,4,6,8,10,12,14])



# printing length mode
# print ('The Length Mode is:', mydholedb.table['assay']['Length'].mode()[0])


## Compositing
mydholedb.downh_composite(
    'assay',
    variable_name= "CU",
    new_table_name= "CMP",
    cint = 10,
    minlen=-1,
    overwrite = True
)
# first 5 rows of a table
# print (mydholedb.table["CMP"].tail(70))


## desurveying an interval table
mydholedb.desurvey('CMP',warns=False, endpoints=True)
# first 3 rows of a table
# print (mydholedb.table["CMP"].head(70))


# creating BHID of type integer
mydholedb.txt2intID('CMP')
# first 3 rows of a subtable
# print (mydholedb.table["CMP"][['BHID', 'BHIDint', 'FROM', 'TO']].head(70))

## Droping table columns in mydholedb
# mydholedb.table["CMP"].drop(['BHID'],axis=1, inplace=True)
# print (mydholedb.table["CMP"][['BHIDint', 'FROM', 'TO']].head(70))



## exporting results to VTK
# mydholedb.intervals2vtk('CMP', 'cmp3.vtk')


# # inspecting interval tables in drillhole object
# print ("Table names ", mydholedb.table_mames)
# print ("Tables names", mydholedb.table.keys())
# print ("Table is    ", type(mydholedb.table))


## exporting db pandas.Dataframe object to csv
# mydholedb.table["CMP"].to_csv('CMPdb.csv', index=False)

## importing the wireframe
domain= p.vtktools.loadSTL('domain.stl')


## creating array to tag samples in domain1
inside1= p.vtktools.pointinsolid(
    domain,
    x=mydholedb.table['CMP']['xm'].values,
    y=mydholedb.table['CMP']['ym'].values,
    z=mydholedb.table['CMP']['zm'].values
)
## creating a new domain field
mydholedb.table['CMP']['Domain']= inside1.astype(int)
## first 3 rows of a subtable
print (mydholedb.table['CMP'][['BHID', 'FROM', 'TO', 'Domain']].head(3))

# print(type(collar))
# print (collar.dtypes) # to see the column types and plot the tables
# print (survey.head(10))
# print('After cleaniing:',assay.head(20))

# 34873,0,0,90
# B1-001,0,327,60