Copy this project into your_ws/src. Make sure you have baxter-related components correctly installed.

==============ROS simulator===============
First terminal:
Use roslaunch chess_bot chess.launch to start a world with baxter and a chess set within.

Second terminal:
Type rosrun baxter_tools enable_robot.py -e for robot status.
Type rosrun baxter_interface joint_trajectory_action_server.py to spin up trajectory server.

Third terminal:
Type roslaunch baxter_moveit_config baxter_launch.grippers to open Moveit!

===============Chess game===============
Run 'python chess_connecter.py' in /src folder to run chess engine and play in Gazebo. Be careful, En passant and pawn promotion is not implemented. 

Usage:
When prompt "Enter move:", type a UCI move (eg. e2e4, b3c2) to issue a move command. Type "exit" to exit the chess game. Type "reset" to start a new game.
To start a new game, you need to shutdown gazebo and chess connecter and restart them all.
