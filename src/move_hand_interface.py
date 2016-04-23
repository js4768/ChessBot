import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from geometry_msgs.msg import (
PoseStamped,
Pose,
Point,
Quaternion,
)
import tf
from std_msgs.msg import String


class HandMover():
	def __init__(self):
		## First initialize moveit_commander and rospy.
		moveit_commander.roscpp_initialize(sys.argv)
		rospy.init_node('move_piece_interface',
				anonymous=True)

		## Instantiate a RobotCommander object.  This object is an interface to
		## the robot as a whole.
		self.robot = moveit_commander.RobotCommander()

		## Instantiate a PlanningSceneInterface object.  This object is an interface
		## to the world surrounding the robot.
		self.scene = moveit_commander.PlanningSceneInterface()

		## Instantiate a MoveGroupCommander object.  This object is an interface
		## to one group of joints.  In this case the group is the joints in the left
		## arm.  This interface can be used to plan and execute motions on the left
		## arm.
		self.group = moveit_commander.MoveGroupCommander("left_arm")
		self.listener = tf.TransformListener()
		self.listener.waitForTransform("/base", 'left_gripper', rospy.Time(0), rospy.Duration(3.0));

	def move_hand_interface(self, x, y, z):
		(trans, rot) = self.listener.lookupTransform('/base', 'left_gripper', rospy.Time(0))
		rotation = geometry_msgs.msg.Quaternion()
		rotation.x = rot[0]
		rotation.y = rot[1]
		rotation.z = rot[2]
		rotation.w = rot[3]
		#quaternion = (rot[0], rot[1],rot[2],rot[3])
		#print tf.transformations.euler_from_quaternion(quaternion)
		pose_target = geometry_msgs.msg.Pose()
		pose_target.orientation.x = rotation.x
		pose_target.orientation.y = rotation.y
		pose_target.orientation.z = rotation.z
		pose_target.orientation.w = rotation.w
		pose_target.position.x = x
		pose_target.position.y = y
		pose_target.position.z = z

		self.group.set_pose_target(pose_target)
		print '============Waiting for execution...'
		print 'Target position: %s, %s, %s' % (x, y, z)
		self.group.plan()
		self.group.go(wait=True)

		self.group.clear_pose_targets()

	def shutdown(self):
		moveit_commander.roscpp_shutdown()

