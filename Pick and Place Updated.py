from robodk.robolink import *
from robodk.robomath import *
RDK = Robolink()
from random import uniform
R_Frame = RDK.Item("UR10e Base")#Pick Place base frame

robot1 = RDK.Item('UR10e')#pick place robot
tool = RDK.Item('Zimmer GEP2016IO-12-B-01 Gripper')# gripping tool
object = RDK.Item('Part')
table = RDK.Item('Table')
TT = RDK.Item('TurnTable')#turntable
TTf = RDK.Item('TurnTable Base')#turntable base
staticRef = RDK.Item('staticRef')#ref frame attached to TT base
home = robot1.JointsHome()# define home

camref = RDK.Item('Camera Ref Frame',ITEM_TYPE_FRAME)
cam_id = RDK.Cam2D_Add(camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=400 SIZE=640x480 BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=black LIGHT_SPECULAR=white')

robot1.setSpeed(200)
robot1.MoveL(home)
joints = robot1.Joints().list()          # retrieve the current robot joints as a list
joints[0] = 0  
joints[2] = 0 
joints[1] = 0  
joints[3] = 0 

home1 = TT.JointsHome() #Turntable home
TT.MoveJ(home1)   
#Generate pick target W.r.t to robot frame
Pi_targets = []

for i in range(16) :
    Pi_target_name = 'Pi_{}'.format(i) 
    Pi = RDK.AddTarget(Pi_target_name, R_Frame)
    external_axes1 = [10, 1000, 30, 0, 0, 0]
    Pi.setJoints([100,100,i*500,0,0,0] + external_axes1)#joints angles to be specified
    Pi.setPose(transl(400,50*i,500))
    Pi_targets.append(Pi)

#Approach Pick
App_target_name = 'ApproachPick'
ApPi = RDK.AddTarget(App_target_name, R_Frame)
ApPi.setAsCartesianTarget()
external_axes = [10, 20, 30, 0,0,0]
ApPi.setJoints([100,100,100,0,0,0] + external_axes)
ApPi.setPose(transl(660, 300, 800)*rotz(0.25))


# Generate place target W.r.t to robot frame
Pl_target_name = 'Place'
Pl = RDK.AddTarget(Pl_target_name, R_Frame)
Pl.setAsCartesianTarget()
external_axes = [10, 20, 30, 0,0,0]
Pl.setJoints([100,100,100,0,0,0] + external_axes)
Pl.setPose(transl(60, 560, 800)*rotz(0.3))
joints = robot1.Joints().list()          # retrieve the current robot joints as a list
joints[0] = 0  
joints[2] = 0 

#Create a new frame and get parts
A = RDK.AddFrame('Parts_Ref')
A.setPose(transl(1030,1000,500))
parts = []
##generate parts and add them to A
for i in range(16):
    part_name = 'part_{}'.format(i)
    part_name = RDK.AddFile('C:\\Users\\prajw\\Documents\\RoboDK\\Tutorial\\RoboDK_inetrn1_R_Code\\hairpin1_v0.stl', A)
    #part = RDK.AddFile('C:\\Users\\prajw\\Documents\\RoboDK\\Tutorial\\RoboDK_inetrn1_R_Code\\hairpin1_v0.stl', A)
    part_name.setPose(Pi_targets[i].Pose()*transl(-370,0,-500))
    #part_name.setPoseAbs(Pi_targets[i].Pose())
    parts.append(part_name)

#gripper
Open_Grip = tool.JointsHome()
#pick place movement
for i in range(16) :
    pick = Pi_targets[i]
    joints = robot1.Joints().list()          # retrieve the current robot joints as a list
    joints[0] = 0  
    joints[2] = 0 
    joints[1] = 0  
    joints[3] = 0 
    robot1.MoveJ(pick)
    tool.MoveL(transl(85,0,0))
    parts[i].setParentStatic(tool)
    #robot.MoveJ(home)# move robot to home

    #randomising the orientation of prts at the target
    TX = uniform(-5, 5)
    RZ = uniform(-10*pi/180, +10*pi/180)
    robot1.MoveL(Pl.Pose()*transl(TX,0,0)*rotz(RZ))

    #robot1.MoveL(Pl)
    tool.MoveJ(Open_Grip)
    #parts[i].setParentStatic(A)  
    
    parts[i].setParentStatic(TT)#rotating frame
    robot1.MoveL(ApPi)
    TT.MoveJ(rotz(i * 0.393))
    parts[i].setParentStatic(staticRef)#static frame
    
robot1.MoveL(home)
TT.MoveJ(home1)   

#Welding

weldframe = RDK.Item("Welding")
robot2 = RDK.Item("UR10e-Welding", ITEM_TYPE_ROBOT)
#robot2.setFrame(reference)
axis = RDK.Item("HMDTech_SpotWeld_Gun", ITEM_TYPE_ROBOT)
OPEN_VALUE = axis.JointsHome().list()#open position
home2 = robot2.JointsHome()# define home
robot2.MoveJ(home2)
Wl_target_name = 'Wled'
Wl = RDK.AddTarget(Wl_target_name, weldframe)
Wl.setAsCartesianTarget()
external_axes = [10, 20, 30]
Wl.setJoints([100,100,100,0,0,0] + external_axes)
Wl.setPose(transl(660, -700, 800)*rotz((pi/2)))

#approach
Ap_target_name = 'Approach'
Ap = RDK.AddTarget(Ap_target_name, weldframe)
Ap.setAsCartesianTarget()
external_axes = [10, 20, 30]
Ap.setJoints([100,100,100,0,0,0] + external_axes)
Ap.setPose(transl(660, -600, 1200)*rotz(0.25))
#Pl.setParentStatic(weldframe)

for i in range(16) :
    parts[i].setParentStatic(TT)

for i in range(16) :
    
    robot2.MoveJ(Wl)
    axis.MoveJ((transl(10,0,0)))
    import time
    time.sleep(1 / RDK.SimulationSpeed())
    axis.MoveJ(OPEN_VALUE)
    axis.MoveJ((transl(10,0,0)))
    robot2.MoveJ(Ap)    
    TT.MoveJ(rotz(i * 0.393))
    
robot2.MoveJ(home2)
TT.MoveJ(home1) 

#pause(5)
RDK.Delete(Pi_targets)
RDK.Delete(parts)
#RDK.Delete(Wl_targets)
RDK.Delete(A)
#RDK.Delete(Pi_targets)
#RDK.Delete(parts)
#RDK.Delete(Ap_target_name)
#RDK.Delete(Pl_target_name)
#RDK.Delete(Wl_target_name)
#RDK.Delete(A)
RDK.Delete(App_target_name)
#RDK.CollisionPairs()





