import vtk
import numpy as np
import pygslib as p

verts = np.genfromtxt ("COLLAR CSV.csv", dtype =None, names =True, delimiter =',', autostrip =True)

faces = [0,1,2, 3, 4, 5, 6,7,8,9,10,11,12,13,14,15,16]


def makePolyData( verts, faces ):
    """Test polydata creation"""
    pd = vtk.vtkPolyData()
    pts = vtk.vtkPoints()
    for pt in verts:
        x = pt[2]
        y = pt[1]
        z = pt[3]
        pts.InsertNextPoint(x, y,z)
    cells = vtk.vtkCellArray()
    cells.InsertNextCell(len(faces))
    for v in faces:
        cells.InsertCellPoint( v )
    pd.SetPoints(pts)
    pd.SetPolys(cells)
    return pd

pd =makePolyData(verts,faces)
p.vtktools.SavePolydata(pd, './files/domain.vtp')