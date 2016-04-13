#!/usr/bin/env python

import sys
import rospy
from gazebo_msgs.srv import *
from gazebo_msgs.msg import *
from geometry_msgs.msg import *


class PositionUpdater():
    def __init__(self):
        self.chess_table = {'king_w':[0, 0, 0],\
            'king_b':[0, 0, 0],\
            'queen_w':[0, 0, 0],\
            'queen_b':[0, 0, 0],\
            'bishop_w_c':[0, 0, 0],\
            'bishop_w_f':[0, 0, 0],\
            'bishop_b_c':[0, 0, 0],\
            'bishop_b_f':[0, 0, 0],\
            'knight_w_b':[0, 0, 0],\
            'knight_w_g':[0, 0, 0],\
            'knight_b_b':[0, 0, 0],\
            'knight_b_g':[0, 0, 0],\
            'castle_w_a':[0, 0, 0],\
            'castle_w_h':[0, 0, 0],\
            'castle_b_a':[0, 0, 0],\
            'castle_b_h':[0, 0, 0],\
            'pawn_w_a':[0, 0, 0],\
            'pawn_w_b':[0, 0, 0],\
            'pawn_w_c':[0, 0, 0],\
            'pawn_w_d':[0, 0, 0],\
            'pawn_w_e':[0, 0, 0],\
            'pawn_w_f':[0, 0, 0],\
            'pawn_w_g':[0, 0, 0],\
            'pawn_w_h':[0, 0, 0],\
            'pawn_b_a':[0, 0, 0],\
            'pawn_b_b':[0, 0, 0],\
            'pawn_b_c':[0, 0, 0],\
            'pawn_b_d':[0, 0, 0],\
            'pawn_b_e':[0, 0, 0],\
            'pawn_b_f':[0, 0, 0],\
            'pawn_b_g':[0, 0, 0],\
            'pawn_b_h':[0, 0, 0]}
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
            self.chess_table[c][0] = current_position.x
            self.chess_table[c][1] = current_position.y
            self.chess_table[c][2] = current_position.z

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
        print bool(resp.success)


if __name__ == "__main__":
    pu = PositionUpdater()
    pu.update_all_positions()
    pu.set_position("king_w", 0.873528, 0.048277, 1.587601)
