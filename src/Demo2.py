#!/usr/bin/env python
import argparse
import struct
import sys
import copy

import rospy
import rospkg

from gazebo_msgs.srv import (
SpawnModel,
DeleteModel,
)
from geometry_msgs.msg import (
PoseStamped,
Pose,
Point,
Quaternion,
)
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from std_msgs.msg import (
Header,
Empty,
)

from baxter_core_msgs.srv import (
SolvePositionIK,
SolvePositionIKRequest,
)

import baxter_interface


class PickAndPlace():
	def __init__(self, limb, verbose=True):
		self._limb_name = limb # string
		self._verbose = verbose # bool
		self._limb = baxter_interface.Limb(limb)
		self._gripper = baxter_interface.Gripper(limb)
		ns = "ExternalTools/" + limb + "/PositionKinematicsNode/IKService"
		self._iksvc = rospy.ServiceProxy(ns, SolvePositionIK)
		rospy.wait_for_service(ns, 5.0)
		# verify robot is enabled
		print "Getting robot state... "
		self._rs = baxter_interface.RobotEnable(baxter_interface.CHECK_VERSION)
		self._init_state = self._rs.state().enabled
		print "Enabling robot... "
		self._rs.enable()

	"""def move_to_start(self, start_angles=None):
		print "Moving the {0} arm to start pose...".format(self._limb_name)
		if not start_angles:
			start_angles = dict(zip(self._joint_names, [0]*7))
		self._guarded_move_to_joint_position(start_angles)
		self.gripper_open()
		rospy.sleep(1.0)
		print "Running. Ctrl-c to quit"""


	def ik_request(self, pose):
		hdr = Header(stamp=rospy.Time.now(), frame_id='base')
		ikreq = SolvePositionIKRequest()
		ikreq.pose_stamp.append(PoseStamped(header=hdr, pose=pose))
		try:
			resp = self._iksvc(ikreq)
		except (rospy.ServiceException, rospy.ROSException), e:
			rospy.logerr("Service call failed: %s" % (e,))
			return False
		# Check if result valid, and type of seed ultimately used to get solution
		# convert rospy's string representation of uint8[]'s to int's
		resp_seeds = struct.unpack('<%dB' % len(resp.result_type), resp.result_type)
		limb_joints = {}
		if (resp_seeds[0] != resp.RESULT_INVALID):
			seed_str = {
						ikreq.SEED_USER: 'User Provided Seed',
						ikreq.SEED_CURRENT: 'Current Joint Angles',
						ikreq.SEED_NS_MAP: 'Nullspace Setpoints',
					   }.get(resp_seeds[0], 'None')
			if self._verbose:
				print "IK Solution SUCCESS - Valid Joint Solution Found from Seed Type: {0}".format(
						 (seed_str))
			# Format solution into Limb API-compatible dictionary
			limb_joints = dict(zip(resp.joints[0].name, resp.joints[0].position))
			if self._verbose:
				print "IK Joint Solution:\n{0}".format(limb_joints)
				print "------------------"
		else:
			rospy.logerr("INVALID POSE - No Valid Joint Solution Found.")
			return False
		return limb_joints



	def _guarded_move_to_joint_position(self, joint_angles):
		if joint_angles:
			self._limb.move_to_joint_positions(joint_angles)
		else:
			rospy.logerr("No Joint Angles provided for move_to_joint_positions. Staying put.")

	def gripper_open(self):
		self._gripper.open()
		rospy.sleep(1.0)

	def gripper_close(self):
		self._gripper.close()
		rospy.sleep(1.0)

	"""def _approach(self, pose):
		approach = copy.deepcopy(pose)
		# approach with a pose the hover-distance above the requested pose
		approach.position.z = approach.position.z + self._hover_distance
		joint_angles = self.ik_request(approach)
		self._guarded_move_to_joint_position(joint_angles)"""

	
	def _servo_to_pose(self, pose):
		
		# servo down to release
		joint_angles = self.ik_request(pose)
		self._guarded_move_to_joint_position(joint_angles)
		rospy.sleep(1.0)

	def _retract(self, x, y, z):
		# retrieve current pose from endpoint
		current_pose = self._limb.endpoint_pose()
		ik_pose = Pose()
		ik_pose.position.x = current_pose['position'].x
		ik_pose.position.y = current_pose['position'].y
		ik_pose.position.z = current_pose['position'].z 
		ik_pose.orientation.x = current_pose['orientation'].x
		ik_pose.orientation.y = current_pose['orientation'].y
		ik_pose.orientation.z = current_pose['orientation'].z
		ik_pose.orientation.w = current_pose['orientation'].w
		joint_angles = self.ik_request(ik_pose)
		# servo up from current pose
		self._guarded_move_to_joint_position(joint_angles)
		rospy.sleep(1.0)

	

	def pick(self, pose):
		# open the gripper
		self.gripper_open()
		# servo above pose
		#self._approach(pose)
		# servo to pose
		self._servo_to_pose(pose)
		# close gripper
		self.gripper_close()
		# retract to clear object
		self._retract()

	def place(self, pose):
		# servo above pose
		#self._approach(pose)
		# servo to pose
		self._servo_to_pose(pose)
		# open the gripper
		self.gripper_open()
		# retract to clear object
		self._retract()



"""def main():
	RSDK Inverse Kinematics Pick and Place Example
	A Pick and Place example using the Rethink Inverse Kinematics
	Service which returns the joint angles a requested Cartesian Pose.
	This ROS Service client is used to request both pick and place
	poses in the /base frame of the robot.
	Note: This is a highly scripted and tuned demo. The object location
	is "known" and movement is done completely open loop. It is expected
	behavior that Baxter will eventually mis-pick or drop the block. You
	can improve on this demo by adding perception and feedback to close
	the loop.
	
	rospy.init_node("ik_pick_and_place_demo")
	# Load Gazebo Models via Spawning Services
	# Note that the models reference is the /world frame
	# and the IK operates with respect to the /base frame


	# Wait for the All Clear from emulator startup
	rospy.wait_for_message("/robot/sim/started", Empty)

	limb = 'left'
	hover_distance = 0.15 # meters
	# Starting Joint angles for left arm
	starting_joint_angles = {'left_w0': 0.6699952259595108,
							 'left_w1': 1.030009435085784,
							 'left_w2': -0.4999997247485215,
							 'left_e0': -1.189968899785275,
							 'left_e1': 1.9400238130755056,
							 'left_s0': -0.08000397926829805,
							 'left_s1': -0.9999781166910306}
	pnp = PickAndPlace(limb, hover_distance)
	# An orientation for gripper fingers to be overhead and parallel to the obj
	overhead_orientation = Quaternion(
							 x=-0.0249590815779,
							 y=0.999649402929,
							 z=0.00737916180073,
							 w=0.00486450832011)
	block_poses = list()
	# The Pose of the block in its initial location.
	# You may wish to replace these poses with estimates
	# from a perception node.
	block_poses.append(Pose(
		position=Point(x=0.510416, y=0.105672, z=-0.313),
		orientation=overhead_orientation))
	# Feel free to add additional desired poses for the object.
	# Each additional pose will get its own pick and place.
	block_poses.append(Pose(
		position=Point(x=0.569889, y=0.105672, z=-0.343),
		orientation=overhead_orientation))
	# Move to the desired starting angles
	pnp.move_to_start(starting_joint_angles)
	idx = 0
	# while not rospy.is_shutdown():
	print pose
	
	pnp.pick(block_poses[idx])
	
	idx = (idx+1) % len(block_poses)
	pnp.place(block_poses[idx])

	return 0


if __name__ == '__main__':
	sys.exit(main())"""
