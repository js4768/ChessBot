Copy this project into your_ws/src. Make sure you have baxter-related components correctly installed.

Use roslaunch chess_bot chess.launch to start a world with baxter and a chess set within.

Run 'python chess_connecter.py' in /src folder to run chess engine and play in Gazebo. Be careful, En passant and pawn promotion is not implemented. To start a new game, you need to shutdown gazebo and chess connecter and restart them all.
