#!/usr/bin/env python

import sys
import rospy
from gazebo_msgs.srv import *
from gazebo_msgs.msg import *
from geometry_msgs.msg import *


class PositionUpdater():
    def __init__(self):
        self.step = 0.0596
        self.trash = (0.6, -0.3, 0.6)
        self.chess_table = {'king_w':(0, 0, 0),\
            'king_b':(0, 0, 0),\
            'queen_w':(0, 0, 0),\
            'queen_b':(0, 0, 0),\
            'bishop_w_c':(0, 0, 0),\
            'bishop_w_f':(0, 0, 0),\
            'bishop_b_c':(0, 0, 0),\
            'bishop_b_f':(0, 0, 0),\
            'knight_w_b':(0, 0, 0),\
            'knight_w_g':(0, 0, 0),\
            'knight_b_b':(0, 0, 0),\
            'knight_b_g':(0, 0, 0),\
            'castle_w_a':(0, 0, 0),\
            'castle_w_h':(0, 0, 0),\
            'castle_b_a':(0, 0, 0),\
            'castle_b_h':(0, 0, 0),\
            'pawn_w_a':(0, 0, 0),\
            'pawn_w_b':(0, 0, 0),\
            'pawn_w_c':(0, 0, 0),\
            'pawn_w_d':(0, 0, 0),\
            'pawn_w_e':(0, 0, 0),\
            'pawn_w_f':(0, 0, 0),\
            'pawn_w_g':(0, 0, 0),\
            'pawn_w_h':(0, 0, 0),\
            'pawn_b_a':(0, 0, 0),\
            'pawn_b_b':(0, 0, 0),\
            'pawn_b_c':(0, 0, 0),\
            'pawn_b_d':(0, 0, 0),\
            'pawn_b_e':(0, 0, 0),\
            'pawn_b_f':(0, 0, 0),\
            'pawn_b_g':(0, 0, 0),\
            'pawn_b_h':(0, 0, 0)}
        rospy.wait_for_service('gazebo/get_model_state')
        rospy.wait_for_service('gazebo/set_model_state')
        try:
            self.get_model_state = rospy.ServiceProxy('gazebo/get_model_state', GetModelState)
            self.set_model_state = rospy.ServiceProxy('gazebo/set_model_state', SetModelState)
        except rospy.ServiceException, e:
            print "Service call failed: %s"%e

    def read_position(self, name):
        resp = self.get_model_state(name, None)
        return resp.pose.position

    def get_all_positions(self):
        for c in self.chess_table:
            print "%s x:%f y:%f z:%f"%(c, self.chess_table[c][0], \
            self.chess_table[c][1], \
            self.chess_table[c][2])

    def update_all_positions(self):
        for c in self.chess_table:
            current_position = self.read_position(c)
            self.chess_table[c] = (current_position.x, current_position.y, current_position.z)

	def update_position(self, name):
		new_pos = self.get_model_state(name, None).pose.position
		self.chess_table[name][0] = (new_pos.x, new_pos.y, new_pos.z)

    def set_position(self, name, x, y, z):
        new_model_state = ModelState()
        new_pose = Pose()
        new_pose.position = Point(x, y, z)
        new_pose.orientation = Quaternion(0, 0, 0, 0)
        new_twist = Twist()
        new_twist.linear = Vector3(0, 0, 0)
        new_twist.angular = Vector3(0, 0, 0)
        new_model_state.model_name = name
        new_model_state.pose = new_pose
        new_model_state.twist = new_twist
        new_model_state.reference_frame = ""
        resp = self.set_model_state(new_model_state)
        self.chess_table[name] = (x, y, z)
        print bool(resp.success)

    def advance(self, name, move):
		if len(move) != 4:
			print 'Invalid move format!'
		else:
			start_y = move[0]
			start_x = move[1]
			end_y = move[2]
			end_x = move[3]
			s = 'abcdefgh'
			delta_x = -self.step * (int(end_x) - int(start_x))
			delta_y = self.step * (s.find(end_y) - s.find(start_y))
			prev_pos = self.read_position(name)
			self.set_position(name, prev_pos.x + delta_x, prev_pos.y + delta_y, prev_pos.z)

    def takeout(self, name):
        if '_w_' in name:
            self.set_position(name, self.trash[0] + 0.3, self.trash[1], self.trash[2])
        else:
            self.set_position(name, self.trash[0] - 0.3, self.trash[1], self.trash[2])


















