import random
from OCC.Display.WebGl.x3dom_renderer import *
from IPython.display import display, HTML
import numpy
import os
from OCC.StlAPI import StlAPI_Writer
from OCC.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.BRepMesh import BRepMesh_IncrementalMesh
from OCC.gp import gp_Pnt, gp_Pln, gp_Ax2, gp_Dir, gp_Circ
from OCC.GeomAPI import GeomAPI_PointsToBSpline
from OCC.TColgp import TColgp_Array1OfPnt
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCC.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.BRepPrimAPI import BRepPrimAPI_MakeSphere
from OCC.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Display.SimpleGui import init_display
from OCC.TopoDS import TopoDS_Shape
from OCC.StlAPI import StlAPI_Reader
import subprocess
from subprocess import PIPE, STDOUT
from OCC.ChFi2d import ChFi2d_AnaFilletAlgo


# function preparing given shape to be displayed using X3D in interactive way; returns geometry intance to display;
# to display the shape use : " display(geometry) ", where geometry is the variable returned from def DisplayShapeFunc(shape)
# for instance you can use it as:
# geometry = DisplayShapeFunc(shape)
# display(geometry)

def DisplayShapeFunc(shape):
    
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

# returns (TopoDS)shape of the whole pipe based on the parameters
# point1 and point2 defines the wire(line) across which the pipe would go
# radius defines the radius of the pipe

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


def filletEdges(ed1, ed2):
    radius = 0.3
    f = ChFi2d_AnaFilletAlgo()
    f.Init(ed1,ed2,gp_Pln())
    f.Perform(radius)
    return f.Result(ed1, ed2)

def pipe_fillet(radius):
    # the points
    p1 = gp_Pnt(0,0,0)
    p2 = gp_Pnt(0,1,0)
    p3 = gp_Pnt(1,2,0)
    p4 = gp_Pnt(2,2,0)
    # the edges
    ed1 = BRepBuilderAPI_MakeEdge(p1,p2).Edge()
    ed2 = BRepBuilderAPI_MakeEdge(p2,p3).Edge()
    ed3 = BRepBuilderAPI_MakeEdge(p3,p4).Edge()
    # inbetween
    fillet12 = filletEdges(ed1, ed2)
    fillet23 = filletEdges(ed2, ed3) 
    # the wire
    makeWire = BRepBuilderAPI_MakeWire()
    makeWire.Add(ed1)
    makeWire.Add(fillet12)
    makeWire.Add(ed2)
    makeWire.Add(fillet23)
    makeWire.Add(ed3)
    makeWire.Build()
    wire = makeWire.Wire()
    # the pipe
    dir = gp_Dir(0,1,0)
    circle = gp_Circ(gp_Ax2(p1,dir), radius)
    profile_edge = BRepBuilderAPI_MakeEdge(circle).Edge()
    profile_wire = BRepBuilderAPI_MakeWire(profile_edge).Wire()
    profile_face = BRepBuilderAPI_MakeFace(profile_wire).Face()
    pipe = BRepOffsetAPI_MakePipe(wire, profile_face).Shape()
    #display.DisplayShape(pipe, update=True)
    return(pipe)

# returns (TopoDS)shape of the sphere based on the parameters
# centre/radius - the center/radius of the sphere

def sphere(centre, radius):
    sphere = BRepPrimAPI_MakeSphere (centre, radius).Shape()
    return(sphere)


# returns (TopoDS)shape of the 3 staged pipe based on the parameters
# example of constructing the bent pipe
# the parts of pipe are joined with spheres in order to smooth irregularities or build different pipe joints
# the optimal way to create bent pipe would be to put radius_pipe=radius_sphere
# radius_pipe - radius of the all parts of the pipe
# radius_sphere - radius of the joint spheres

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

def Mesh(shape):
    mesh = BRepMesh_IncrementalMesh(shape, 0.6)
    mesh.Perform()

def stl_file(name, shape):
    stl_filename = "./" + name + "_low_resolution.stl"
    stl_exporter = StlAPI_Writer()
    stl_exporter.SetASCIIMode(True)  # change to False if you need binary export
    stl_exporter.Write(shape, stl_filename)
    # then we change the mesh resolution
    #mesh.SetDeflection(0.05)
    stl_reader = StlAPI_Reader()
    fan_shp = TopoDS_Shape()
    stl_reader.Read(fan_shp, stl_filename)
    exproted = DisplayShapeFunc(fan_shp)
    display(exproted)
    return stl_filename

def getGeo(stl_filename):
    geoCounter = 0
    geoFile = "Merge \""+stl_filename+"\";\nSurface Loop(1) = {1};\nVolume(1) = {1};\nPhysical Volume(1) = {1};\n"
    temp_file_name = "tmp_"+str(++geoCounter)+".geo"
    if os.path.exists(temp_file_name): os.remove(temp_file_name)
    text_file = open(temp_file_name, "w")
    text_file.write(geoFile)
    text_file.close()
    return temp_file_name;

def Geo_file(stl_file_name):
    out = ""
    try:
        out = subprocess.check_output(
                ["gmsh", "gmsh -3 -algo meshadapt tmp_0.geo -o SFM.msh"],
                stderr=subprocess.STDOUT
                ).strip().decode('utf8')
    except subprocess.CalledProcessError as e:
        out = e.output
    getGeo(stl_file_name)
    print(out)


def clean(stl_filename):  
    directory="./tmp"
    if not os.path.exists(directory):
        os.makedirs(directory)

    files= ["sfm.xml", "SFM.msh", stl_filename, "sfm_physical_region.xml", "tmp_0.geo", "tmp_0.x3d"]
    for i in files:
        os.rename(i, "tmp/"+i)
    
def gmsh_algo(stl_filename):
    cmds = "gmsh -3 -algo meshadapt tmp_0.geo -o SFM.msh \n dolfin-convert SFM.msh sfm.xml \n ls -la"
    def process(cmd):
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        for stdout_line in iter(popen.stdout.readline, ""): # how to add popen.stderr.readline check?
             yield stdout_line
    for n in process(cmds):
        print(n)
    clean(stl_filename)

