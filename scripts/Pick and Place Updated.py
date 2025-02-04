"""
RoboDK Pick and Place & Welding Automation Script
-------------------------------------------------
- Controls a UR10e robot for a pick-and-place operation using RoboDK.
- Implements a welding sequence with a secondary robot.
- Uses a turntable for part positioning.
"""

# Import required RoboDK modules
from robodk.robolink import *
from robodk.robomath import *
from random import uniform
import time

# Initialize RoboDK connection
RDK = Robolink()

# ------------------------ #
# Initialization           #
# ------------------------ #

def initialize_environment():
    """Initialize robots, tools, objects, and reference frames."""
    global robot1, tool, TT, staticRef, home_robot1, home_turntable
    global R_Frame, camref, cam_id
    global robot2, axis, home_robot2, OPEN_VALUE, weldframe

    # Define robot base frame
    R_Frame = RDK.Item("UR10e Base")

    # Pick-and-place robot
    robot1 = RDK.Item('UR10e')
    tool = RDK.Item('Zimmer GEP2016IO-12-B-01 Gripper')
    TT = RDK.Item('TurnTable')
    staticRef = RDK.Item('staticRef')

    # Define home positions
    home_robot1 = robot1.JointsHome()
    home_turntable = TT.JointsHome()

    # Set camera
    camref = RDK.Item('Camera Ref Frame', ITEM_TYPE_FRAME)
    cam_id = RDK.Cam2D_Add(
        camref, 'FOCAL_LENGHT=6 FOV=32 FAR_LENGHT=400 SIZE=640x480 '
                'BG_COLOR=black LIGHT_AMBIENT=red LIGHT_DIFFUSE=black LIGHT_SPECULAR=white'
    )

    # Set Speed
    robot1.setSpeed(200)

    # Move to home positions
    robot1.MoveL(home_robot1)
    TT.MoveJ(home_turntable)

    # Welding system initialization
    weldframe = RDK.Item("Welding")
    robot2 = RDK.Item("UR10e-Welding", ITEM_TYPE_ROBOT)
    axis = RDK.Item("HMDTech_SpotWeld_Gun", ITEM_TYPE_ROBOT)

    OPEN_VALUE = axis.JointsHome().list()
    home_robot2 = robot2.JointsHome()
    robot2.MoveJ(home_robot2)


# ------------------------ #
# Target Generation        #
# ------------------------ #

def generate_pick_targets():
    """Generate pick targets for the robot."""
    pick_targets = []

    for i in range(16):
        target = RDK.AddTarget(f'Pi_{i}', R_Frame)
        external_axes = [10, 1000, 30, 0, 0, 0]
        target.setJoints([100, 100, i * 500, 0, 0, 0] + external_axes)
        target.setPose(transl(400, 50 * i, 500))
        pick_targets.append(target)

    return pick_targets


def define_positions():
    """Define approach pick and place positions."""
    approach_pick = RDK.AddTarget('ApproachPick', R_Frame)
    approach_pick.setAsCartesianTarget()
    approach_pick.setPose(transl(660, 300, 800) * rotz(0.25))

    place_position = RDK.AddTarget('Place', R_Frame)
    place_position.setAsCartesianTarget()
    place_position.setPose(transl(60, 560, 800) * rotz(0.3))

    return approach_pick, place_position


# ------------------------ #
# Part Generation          #
# ------------------------ #

def generate_parts(pick_targets):
    """Create parts and associate them with reference frame."""
    parts_frame = RDK.AddFrame('Parts_Ref')
    parts_frame.setPose(transl(1030, 1000, 500))

    parts = []
    for i in range(16):
        part = RDK.AddFile(
            'C:\\Users\\prajw\\Documents\\RoboDK\\Tutorial\\RoboDK_inetrn1_R_Code\\hairpin1_v0.stl',
            parts_frame
        )
        part.setPose(pick_targets[i].Pose() * transl(-370, 0, -500))
        parts.append(part)

    return parts, parts_frame


# ------------------------ #
# Pick & Place Execution  #
# ------------------------ #

def execute_pick_and_place(pick_targets, approach_pick, place_position, parts):
    """Perform the pick-and-place operation."""
    open_grip = tool.JointsHome()

    for i in range(16):
        robot1.MoveJ(pick_targets[i])
        tool.MoveL(transl(85, 0, 0))
        parts[i].setParentStatic(tool)

        # Randomizing orientation
        TX = uniform(-5, 5)
        RZ = uniform(-10 * pi / 180, +10 * pi / 180)
        robot1.MoveL(place_position.Pose() * transl(TX, 0, 0) * rotz(RZ))

        tool.MoveJ(open_grip)
        parts[i].setParentStatic(TT)

        # Move robot to approach position
        robot1.MoveL(approach_pick)
        TT.MoveJ(rotz(i * 0.393))
        parts[i].setParentStatic(staticRef)

    robot1.MoveL(home_robot1)
    TT.MoveJ(home_turntable)


# ------------------------ #
# Welding Process          #
# ------------------------ #

def execute_welding(parts):
    """Perform the welding operation."""
    weld_target = RDK.AddTarget('Weld', weldframe)
    weld_target.setAsCartesianTarget()
    weld_target.setPose(transl(660, -700, 800) * rotz(pi / 2))

    approach_target = RDK.AddTarget('Approach', weldframe)
    approach_target.setAsCartesianTarget()
    approach_target.setPose(transl(660, -600, 1200) * rotz(0.25))

    # Assign parts back to turntable
    for part in parts:
        part.setParentStatic(TT)

    for i in range(16):
        robot2.MoveJ(weld_target)
        axis.MoveJ(transl(10, 0, 0))
        time.sleep(1 / RDK.SimulationSpeed())
        axis.MoveJ(OPEN_VALUE)
        axis.MoveJ(transl(10, 0, 0))
        robot2.MoveJ(approach_target)
        TT.MoveJ(rotz(i * 0.393))

    robot2.MoveJ(home_robot2)
    TT.MoveJ(home_turntable)


# ------------------------ #
# Cleanup                 #
# ------------------------ #

def cleanup(pick_targets, parts, parts_frame):
    """Delete all targets and clean up RoboDK environment."""
    RDK.Delete(pick_targets)
    RDK.Delete(parts)
    RDK.Delete(parts_frame)


# ------------------------ #
# Main Execution           #
# ------------------------ #

def main():
    """Main execution function."""
    try:
        initialize_environment()
        pick_targets = generate_pick_targets()
        approach_pick, place_position = define_positions()
        parts, parts_frame = generate_parts(pick_targets)

        execute_pick_and_place(pick_targets, approach_pick, place_position, parts)
        execute_welding(parts)

        cleanup(pick_targets, parts, parts_frame)

    except Exception as e:
        print(f"An error occurred: {e}")


# Run script
if __name__ == "__main__":
    main()
