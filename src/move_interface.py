## To use the python interface to move_group, import the moveit_commander
## module.  We also import rospy and some messages that we will use.
import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
## END_SUB_TUTORIAL

from std_msgs.msg import String

def move_group_python_interface():
	## BEGIN_TUTORIAL
	##
	## Setup
	## ^^^^^
	## CALL_SUB_TUTORIAL imports
	##
	## First initialize moveit_commander and rospy.
	
	print "============ Starting setup"
	moveit_commander.roscpp_initialize(sys.argv)
	rospy.init_node('move_group_python_interface', anonymous=True)
	
	## Instantiate a RobotCommander object.  This object is an interface to
	## the robot as a whole.
	robot = moveit_commander.RobotCommander()

	## Instantiate a PlanningSceneInterface object.  This object is an interface
	## to the world surrounding the robot.
	scene = moveit_commander.PlanningSceneInterface()

	## Instantiate a MoveGroupCommander object.  This object is an interface
	## to one group of joints.  In this case the group is the joints in the left
	## arm.  This interface can be used to plan and execute motions on the left
	## arm.
	group = moveit_commander.MoveGroupCommander("left_arm")
	
	## We create this DisplayTrajectory publisher which is used below to publish
  ## trajectories for RVIZ to visualize.
	display_trajectory_publisher = rospy.Publisher(
                                      '/move_group/display_planned_path',
                                      moveit_msgs.msg.DisplayTrajectory)
	
	## Planning to a Pose goal
	chess_x = ()
	chess_y = ()
	chess_z = ()

	print "============ Generating plan 1"
  pose_target = geometry_msgs.msg.Pose()
  pose_target.position.x = 0.461448
  pose_target.position.y = 0.050919
  pose_target.position.z = 0.687600
  group.set_pose_target(pose_target)
	
	plan1 = group.plan()
	
	print "============ Waiting while RVIZ displays plan1..."
  rospy.sleep(5)

	## Moving to a pose goal
	
	## Let's set a joint space goal and move towards it. 
  ## First, we will clear the pose target we had just set.
	group.clear_pose_targets()

  ## Then, we will get the current set of joint values for the group
  group_variable_values = group.get_current_joint_values()
  print "============ Joint values: ", group_variable_values
	
	## Now, let's modify one of the joints, plan to the new joint
  ## space goal and visualize the plan
	group_variable_values[0] = 1.0
	group.set_joint_value_target(group_variable_values)
	
	plan2 = group.plan()

	print "============ Waiting while RVIZ displays plan2..."
  rospy.sleep(5)


	## Cartesian Paths
	waypoints = []

  # start with the current pose
  waypoints.append(group.get_current_pose().pose)
	
  # first orient gripper and move forward (+x)
  wpose = geometry_msgs.msg.Pose()
  wpose.orientation.w = 1.0
  wpose.position.x = waypoints[0].position.x + 0.1
  wpose.position.y = waypoints[0].position.y
  wpose.position.z = waypoints[0].position.z
  waypoints.append(copy.deepcopy(wpose))

  # second move down
  wpose.position.z -= 0.10
  waypoints.append(copy.deepcopy(wpose))

  # third move to the side
  wpose.position.y += 0.05
  waypoints.append(copy.deepcopy(wpose))

  ## We want the cartesian path to be interpolated at a resolution of 1 cm
  ## which is why we will specify 0.01 as the eef_step in cartesian
  ## translation.  We will specify the jump threshold as 0.0, effectively
  ## disabling it.
  (plan3, fraction) = group.compute_cartesian_path(
                               waypoints,   # waypoints to follow
                               0.01,        # eef_step
                               0.0)         # jump_threshold
                               
  print "============ Waiting while RVIZ displays plan3..."
  rospy.sleep(5)
	
	## Adding/Removing Objects and Attaching/Detaching Objects
	collision_object = moveit_msgs.msg.CollisionObject()



  ## When finished shut down moveit_commander.
  moveit_commander.roscpp_shutdown()

  ## END_TUTORIAL

  print "============ STOPPING"


	if __name__=='__main__':
  try:
    move_group_python_interface()
  except rospy.ROSInterruptException:
    pass




















