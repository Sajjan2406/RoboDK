# Robodk
This is my first project both in terms of simulation software and robotics.

The project is on developing a Robotic cell for Pick_Place and Welding applicaitons using 'RoboDk' robot simulation software.

Scene setup:  
3 UR10 robots, U shaped pins, a Camera and a Turntable  

Sequence:  
1. Robot1 picks the U pins and place them on to the 'Turntable'.
2. Turntable rotates 0.393 rad every time a new U pin is plced on it.
3. Once all the Pins are placed, the Turntable rotates back to the home position.
4. Robot2 starts welding each pin pair. For each welding movement, the Turntable rotates again by 0.393 rad
5. The pins overlap can be visualised through the camera mounted on the Robot3

Code Explaination:
1. Robot1, base frame, tool, pins and the Turntable(TT) are defined
2. Robot1 joints_home, speed are defined
3. Targets Pick, approach and Place are defined
4. The Pins are spawned in the scence and are placed at the each Pick target corodinates, w.r.t 'Part_Ref' reference frame
5. To make the robot1 pick the pins, the parent of the pins is changed to 'tool'
6. During the place action, the pins' parent is again changed to 'TT' frame.
7. The TT rotates for every place action.
8. Once all the pins are placed on the TT, Robot1 moves to home poisition and TT rotates back to home too
9. next, weld frame, robot2  and welding tool are defined
10. Similar to 'robot1', Weld target and approach positon are set
11. 'Robot2' does the welding operations and moves back to home position.
12. All the pick targets, pins, pins ref frame, Targets are then deleted.

Before running the code, the scene should be setup inside the RoboDk software.