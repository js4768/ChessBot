#!/usr/bin/env python
# This code talks to the Stockfish Chess Engine. Entries are to be made in algebraic
# chess notation (eg. e2e4). Stockfish is set to think for a maximum of 1 sec.

import sys
import detect_position as DP


def move_piece(path):
    move = ''
    taken = ''
    castling = ''
    castling_move = ''
    for c in chess_table:
        # A piece will be taken out
        if chess_table[c] == path[2:4]:
            chess_table[c] = 'taken'
            taken = c
    for c in chess_table:
        # Find the piece to move
        if chess_table[c] == path[0:2]:
            chess_table[c] = path[2:4]
            move = c
            # Check for castling move
            if c == 'king_w_' and path[0:2] == 'e1':
                if path[2:4] == 'g1':
                    chess_table['castle_w_h'] = 'f1'
                    chess_table[c] = 'g1'
                    castling = 'castle_w_h'
                    castling_move = 'h1f1'
                elif path[2:4] == 'c1':
                    chess_table['castle_w_a'] = 'd1'
                    chess_table[c] = 'c1'
                    castling = 'castle_w_a'
                    castling_move = 'a1c1'
            elif c == 'king_b_' and path[0:2] == 'e8':
                if path[2:4] == 'g8':
                    chess_table['castle_b_h'] = 'f8'
                    chess_table[c] = 'g8'
                    castling = 'castle_b_h'
                    castling_move = 'h8f8'
                elif path[2:4] == 'c8':
                    chess_table['castle_b_a'] = 'd8'
                    chess_table[c] = 'c8'
                    castling = 'castle_b_a'
                    castling_move = 'a8d8'
    return move, taken, castling, castling_move

chess_table = {'king_w_':'e1',\
            'king_b_':'e8',\
            'queen_w_':'d1',\
            'queen_b_':'d8',\
            'bishop_w_c':'c1',\
            'bishop_w_f':'f1',\
            'bishop_b_c':'c8',\
            'bishop_b_f':'f8',\
            'knight_w_b':'b1',\
            'knight_w_g':'g1',\
            'knight_b_b':'b8',\
            'knight_b_g':'g8',\
            'castle_w_a':'a1',\
            'castle_w_h':'h1',\
            'castle_b_a':'a8',\
            'castle_b_h':'h8',\
            'pawn_w_a':'a2',\
            'pawn_w_b':'b2',\
            'pawn_w_c':'c2',\
            'pawn_w_d':'d2',\
            'pawn_w_e':'e2',\
            'pawn_w_f':'f2',\
            'pawn_w_g':'g2',\
            'pawn_w_h':'h2',\
            'pawn_b_a':'a7',\
            'pawn_b_b':'b7',\
            'pawn_b_c':'c7',\
            'pawn_b_d':'d7',\
            'pawn_b_e':'e7',\
            'pawn_b_f':'f7',\
            'pawn_b_g':'g7',\
            'pawn_b_h':'h7'}

# Load ROS chess position reader
pu = DP.PositionUpdater()
pu.record_initial_state()
pu.update_all_positions()
pu.get_all_positions()

while true:
    try:
        move = raw_input('Enter move:')
        if move == 'exit':
            print 'Goodbye'
            print 'Exiting program...'
            pu.shutdown()
            break
        if move == 'reset':
            print 'Reset game'
            chess_table = {'king_w_':'e1',\
            'king_b_':'e8',\
            'queen_w_':'d1',\
            'queen_b_':'d8',\
            'bishop_w_c':'c1',\
            'bishop_w_f':'f1',\
            'bishop_b_c':'c8',\
            'bishop_b_f':'f8',\
            'knight_w_b':'b1',\
            'knight_w_g':'g1',\
            'knight_b_b':'b8',\
            'knight_b_g':'g8',\
            'castle_w_a':'a1',\
            'castle_w_h':'h1',\
            'castle_b_a':'a8',\
            'castle_b_h':'h8',\
            'pawn_w_a':'a2',\
            'pawn_w_b':'b2',\
            'pawn_w_c':'c2',\
            'pawn_w_d':'d2',\
            'pawn_w_e':'e2',\
            'pawn_w_f':'f2',\
            'pawn_w_g':'g2',\
            'pawn_w_h':'h2',\
            'pawn_b_a':'a7',\
            'pawn_b_b':'b7',\
            'pawn_b_c':'c7',\
            'pawn_b_d':'d7',\
            'pawn_b_e':'e7',\
            'pawn_b_f':'f7',\
            'pawn_b_g':'g7',\
            'pawn_b_h':'h7'}
            pu.reset_board()
            continue
        chess_name, taken, castling, castling_move = move_piece(move)
        if taken != '':
            pu.takeout(taken)
        pu.advance(chess_name, move)
        if castling != '':
            pu.advance(castling, castling_move)
    except KeyboardInterrupt:
        print 'Ctrl-C trapped. Exiting...'
        pu.shutdown()
        break
