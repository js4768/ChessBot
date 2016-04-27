#!/usr/bin/env python

import sys
import rospy
from gazebo_msgs.srv import *
from gazebo_msgs.msg import *
from geometry_msgs.msg import *
import move_hand_interface as MH
import random

class PositionUpdater():
    def __init__(self):
        self.offset = 0.15 - 0.93
        self.hand_planner = MH.HandMover()
        self.step = 0.0596
        self.left_trash = (0.6, 0.3, 0.05)
        self.right_trash = (0.6, -0.3, 0.05)
        self.left_arm_region = ['h1', 'g1', 'f1', 'h2', 'g2', 'f2', 'h3', 'g3', 'f3']
        self.right_arm_region = ['a1', 'b1', 'c1', 'a2', 'b2', 'c2', 'a3', 'b3', 'c3']
        self.chess_table = {'king_w_':(0, 0, 0),\
            'king_b_':(0, 0, 0),\
            'queen_w_':(0, 0, 0),\
            'queen_b_':(0, 0, 0),\
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
        self.initial_positions = {'king_w_':(0, 0, 0),\
            'king_b_':(0, 0, 0),\
            'queen_w_':(0, 0, 0),\
            'queen_b_':(0, 0, 0),\
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

    def record_initial_state(self):
        for c in self.initial_positions:
            current_position = self.read_position(c)
            self.initial_positions[c] = (current_position.x, current_position.y, current_position.z)

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

    def advance(self, name, move):
        if len(move) != 4:
            print 'Invalid move format!'
        else:
            print 'target grid: %s' % move
            start_y = move[0]
            start_x = move[1]
            end_y = move[2]
            end_x = move[3]
            s = 'abcdefgh'
            delta_x = -self.step * (int(end_x) - int(start_x))
            delta_y = self.step * (s.find(end_y) - s.find(start_y))
            prev_pos = self.read_position(name)
            if '_b_' in name:
                arm = 'left'
		# If chess is unreachable by left arm
                if move[0:2] in self.right_arm_region:
                    print 'Using right arm'
                    arm = 'right'
                    # Impossible reaches by robot. Put the piece to destination directly
                    if move[2:4] in self.left_arm_region:
                        print 'Cannot reach. Teleporting piece instead'
                        self.set_position(name, prev_pos.x + delta_x, prev_pos.y + delta_y, prev_pos.z)
                        return
		if move[2:4] in self.right_arm_region:
                    print 'Using right arm'
                    arm = 'right'
                    if move[0:2] in self.left_arm_region:
                        print 'Cannot reach. Teleporting piece instead'
                        self.set_position(name, prev_pos.x + delta_x, prev_pos.y + delta_y, prev_pos.z)
                        return
                self.hand_planner.move_hand_interface(prev_pos.x, prev_pos.y, prev_pos.z + self.offset, arm)
                print "approach"
                # TODO Pick up chess
                
                self.hand_planner.gripper_open()
                print "open"
                self.hand_planner.move_hand_interface(prev_pos.x, prev_pos.y, prev_pos.z + 0.014 - 0.93, arm)
                print "down"
                self.hand_planner.gripper_close()
                print "close"
                self.hand_planner.move_hand_interface(prev_pos.x, prev_pos.y, prev_pos.z + self.offset, arm)
                print "up"
                # TODO Drop chess
                self.hand_planner.move_hand_interface(prev_pos.x + delta_x, prev_pos.y + delta_y, prev_pos.z + self.offset, arm)
                print "approach"
                self.hand_planner.move_hand_interface(prev_pos.x + delta_x, prev_pos.y + delta_y, prev_pos.z + 0.015 - 0.93, arm)
                print "down"
                self.hand_planner.gripper_open()
                print "open"
                self.hand_planner.move_hand_interface(prev_pos.x + delta_x, prev_pos.y + delta_y, prev_pos.z + self.offset, arm)
                print "up"
                # TODO Return to safe place
                if arm == 'left':
                    self.hand_planner.move_hand_interface(0.3, 0.3, 0.1, arm)
                if arm == 'right':
                    self.hand_planner.move_hand_interface(0.3, -0.3, 0.1, arm)
                print "Return to safe pose"
            self.set_position(name, prev_pos.x + delta_x, prev_pos.y + delta_y, prev_pos.z)

    def takeout(self, name):
        if '_b_' in name:
            self.set_position(name, self.left_trash[0], self.left_trash[1], self.left_trash[2])
        else:
            prev_pos = self.read_position(name)
            arm = 'left'
            # If the chess is in right hand side, use right arm
            if prev_pos.y < 0:
                arm = 'right'
            self.hand_planner.move_hand_interface(prev_pos.x, prev_pos.y, prev_pos.z + self.offset, arm)
            # TODO Pick up chess
            self.hand_planner.gripper_open()
            print "open"
            self.hand_planner.move_hand_interface(prev_pos.x, prev_pos.y, prev_pos.z + 0.014 - 0.93, arm)
            print "down"
            self.hand_planner.gripper_close()
            print "close"
            self.hand_planner.move_hand_interface(prev_pos.x, prev_pos.y, prev_pos.z + self.offset, arm)
            print "up"
            if arm == 'left':
                self.hand_planner.move_hand_interface(self.left_trash[0], self.left_trash[1], self.left_trash[2])
                self.hand_planner.move_hand_interface(0.3, 0.3, 0.05, arm)
            if arm == 'right':
                self.hand_planner.move_hand_interface(self.right_trash[0], self.right_trash[1], self.right_trash[2])
                self.hand_planner.move_hand_interface(0.3, -0.3, 0.05, arm)
            # TODO Drop chess
            self.hand_planner.gripper_open()
            print "open"

    def reset_board(self):
        # First move every piece to somewhere else
        for c in self.chess_table:
            self.set_position(c, random.random()+3, random.random()+3, random.random())
        # Put every piece back
        for c in self.initial_positions:
            initial_pos = self.initial_positions[c]
            self.set_position(c, initial_pos[0], initial_pos[1], initial_pos[2])

    def shutdown(self):
        self.hand_planner.shutdown()




