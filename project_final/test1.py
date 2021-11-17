# Code for ’Script’

# We will use NumPy to read the csv file.
 # Refer to NumPy documentation for genfromtxt() for details on
# customizing the CSV file parsing.
import vtk
import numpy as np
import pygslib as p
from vtk.numpy_interface import algorithms as algs
# assuming data.csv is a CSV file with the 1st row being the names names for
# the columns
verts = np.genfromtxt ("COLLAR CSV.csv", dtype =None, names =True, delimiter =',', autostrip =True)
# print(type(data['YCOLLAR']))
# print(data['XCOLLAR'])
# print(data['ZCOLLAR'])

faces = [0,1,2, 3, 4, 5, 6,7,8,9,10,11,12,13,14,15,16]
# faces = np.hstack([[4, 0, 1, 2, 3]])



def makePolyData( verts, faces ):
    pd = vtk.vtkPolyData()
    pts = vtk.vtkPoints()
    for pt in verts:
        print(pt)
        x = pt[2]
        y = pt[1]
        z = pt[3]
        # print('\n',x,y,z)
        pts.InsertNextPoint(x, y,z)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(len(faces))
    for v in faces:
        cells.InsertCellPoint( v )
    pd.SetPoints(pts)
    pd.SetPolys(cells)
    return pd

pd =makePolyData(verts,faces)
# print(pd)
p.vtktools.SavePolydata(pd, './files/domain.vtp')
# points = p.vtktools.GetPointsInPolydata(pd)

# for pt in verts:
#     # print(pt)
#     x = pt[2]
#     y = pt[1]
#     z = pt[3]
# points = p.vtktools.delaunay2D(verts)
# print(points)




# output.intervals2vtk('CMP', 'kabini3.vtk')
# p.vtktools.dmtable2wireframe(data['XCOLLAR'],data['YCOLLAR'],data['ZCOLLAR'],indexone = False, filename = './project_final')
# output = 'esxmple.vtk'
# for name in data . dtype . names :
#     array = data [ name ]
#     print(array)
#     # You can directly pass a NumPy array to the pipeline.
#     # Since ParaView expects all arrays to be named, you
#     # need to assign it a name in the ’append’ call.
#     output.RowData.append ( array , 'k.vtk' )
#     # ,pid1=0.0,pid2=0.0,pid3=0.0,
