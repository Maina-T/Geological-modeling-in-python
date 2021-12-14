# Calculating length of sample intervals
mydholedb.table['assay']['Length']= mydholedb.table['assay']['TO']- mydholedb.table['assay']['FROM']
# printing length mode
print ('The Length Mode is:', mydholedb.table['assay']['Length'].mode()[0])
The Length Mode is: 10.0