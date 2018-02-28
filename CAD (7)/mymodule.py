import random
from OCC.Display.WebGl.x3dom_renderer import *
from IPython.display import display, HTML
import numpy
import os
from OCC.StlAPI import StlAPI_Writer
from OCC.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.BRepMesh import BRepMesh_IncrementalMesh
from OCC.gp import gp_Pnt, gp_Ax2, gp_Dir, gp_Circ
from OCC.GeomAPI import GeomAPI_PointsToBSpline
from OCC.TColgp import TColgp_Array1OfPnt
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCC.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.BRepPrimAPI import BRepPrimAPI_MakeSphere
from OCC.BRepAlgoAPI import BRepAlgoAPI_Cut


def DisplayShapeFunc(shape):
    
    print("Not HW")
    caller_id = 0
    def DisplayShape(shape,
                         vertex_shader=None,
                         fragment_shader=None,
                         export_edges=False,
                         color=(random.random(), random.random(), random.random()),
                         specular_color=(1, 1, 1),
                         shininess=0.9,
                         transparency=0.,
                         line_color=(0, 0., 0.),
                         line_width=2.,
                         mesh_quality=1.):
            def Show(src="<shape><appearance><material diffuseColor='0.603 0.894 0.909'></material></appearance> <box></box></shape>   ", height=400,  width=400):
                width=str(width)
                height=str(height)
                result = ""
                if(caller_id <2):
                    result += " <script type='text/javascript' src='http://www.x3dom.org/download/x3dom.js'> </script>  <link rel='stylesheet' type='text/css' href='http://www.x3dom.org/download/x3dom.css'></link>"

                result +="<div style='height: "+height+"px;width: 100%;' id='x3dholder_"+str(caller_id)+"'  width='100%' height='"+height+"px'><x3d style='height: "+height+"px;width: 100%;' id='x3d"+str(caller_id)+"' width='100%' height='"+height+"px'><scene>"+src+"   </scene></x3d> </div>"
                return result
            x3d_exporter = X3DExporter(shape, vertex_shader, fragment_shader,
                                       export_edges, color,
                                       specular_color, shininess, transparency,
                                       line_color, line_width, mesh_quality)
            x3d_exporter.compute()
            tmp = x3d_exporter.to_x3dfile_string()
            temp_file_name = "tmp_"+str(++caller_id)+".x3d"
            if os.path.exists(temp_file_name): os.remove(temp_file_name)
            text_file = open(temp_file_name, "w")
            text_file.write(tmp)
            text_file.close()
            return HTML(Show("<inline url='./"+temp_file_name+"'> </inline> "))
   
    return DisplayShape(shape)

def pipe(point1, point2, radius):
    makeWire = BRepBuilderAPI_MakeWire()
    edge = BRepBuilderAPI_MakeEdge(point1, point2).Edge()
    makeWire.Add(edge)
    makeWire.Build()
    wire = makeWire.Wire()

    dir = gp_Dir(point2.X() - point1.X(), point2.Y() - point1.Y(), point2.Z() - point1.Z())
    circle = gp_Circ(gp_Ax2(point1,dir), radius)
    profile_edge = BRepBuilderAPI_MakeEdge(circle).Edge()
    profile_wire = BRepBuilderAPI_MakeWire(profile_edge).Wire()
    profile_face = BRepBuilderAPI_MakeFace(profile_wire).Face()
    pipe = BRepOffsetAPI_MakePipe(wire, profile_face).Shape()
    return(pipe)

def sphere(centre, radius):
    sphere = BRepPrimAPI_MakeSphere (centre, radius).Shape()
    return(sphere)

def pipe_3(radius_pipe, radius_sphere):
    pipe1=pipe(gp_Pnt(0,0,0), gp_Pnt(0,0,1), radius_pipe)
    sphere1=sphere(gp_Pnt(0,0,1), radius_sphere)
    pipe2=pipe(gp_Pnt(0,0,1), gp_Pnt(0,1,2), radius_pipe)  
    sphere2=sphere(gp_Pnt(0,1,2), radius_sphere)
    pipe3=pipe(gp_Pnt(0,1,2), gp_Pnt(0,2,2), radius_pipe)
    glued1 = BRepAlgoAPI_Fuse(pipe1, sphere1).Shape()
    glued2= BRepAlgoAPI_Fuse(glued1, pipe2).Shape()
    glued3 = BRepAlgoAPI_Fuse(glued2, sphere2).Shape()
    glued4 = BRepAlgoAPI_Fuse(glued3, pipe3).Shape()
    return glued4
    

def fib(n):
    a = b = 1
    for i in range(n - 2):
        a, b = b, a + b
    return b
