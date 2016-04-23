#!/usr/bin/env python
# This code talks to the Stockfish Chess Engine. Entries are to be made in algebraic
# chess notation (eg. e2e4). Stockfish is set to think for a maximum of 1 sec.

import sys
import subprocess as S
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
            if c == 'king_w' and path[0:2] == 'e1':
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
            elif c == 'king_b' and path[0:2] == 'e8':
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

chess_table = {'king_w':'e1',\
            'king_b':'e8',\
            'queen_w':'d1',\
            'queen_b':'d8',\
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

chess = r'/home/js4768/stockfish-7-linux/src/stockfish'
getprompt = 'isready\n'
done = 'readyok'

proc = S.Popen(chess, stdin=S.PIPE, stdout=S.PIPE, bufsize=1, universal_newlines=True, shell=True)

while True:
    proc.stdin.write(getprompt)
    text = proc.stdout.readline().strip()
    if text == done:
        break

proc.stdin.write('uci\n')
while True:
    text = proc.stdout.readline().strip()
    print text
    if text == "uciok":
        break
skillLevel = raw_input('Choose skill level (0-20):')
proc.stdin.write('setoption name Skill Level value '+str(skillLevel)+'\n')
proc.stdin.write('ucinewgame\n')

# Load ROS chess position reader
pu = DP.PositionUpdater()
pu.update_all_positions()
pu.get_all_positions()

moveList = 'position startpos moves '
checkmate = False
while checkmate is False:
    try:
        move = raw_input('Enter move:')
        if move == 'exit':
            print 'Exiting program...'
            pu.shutdown()
            break
        chess_name, taken, castling, castling_move = move_piece(move)
        if taken != '':
            pu.takeout(taken)
        pu.advance(chess_name, move)
        if castling != '':
            pu.advance(castling, castling_move)
        moveList = moveList+move+' '
        proc.stdin.write(moveList+'\n')
        proc.stdin.write('go movetime 1000\n')
        print 'Computer moves:'
        while True:
            text = proc.stdout.readline().strip()
            if text[0:8] == 'bestmove':
                cpuMove = text[9:13]
                print cpuMove
                moveList = moveList+cpuMove+' '
                chess_name, taken, castling, castling_move = move_piece(cpuMove)
                if taken != '':
                    pu.takeout(taken)
                pu.advance(chess_name, cpuMove)
                if castling != '':
                    pu.advance(castling, castling_move)
                break
    except KeyboardInterrupt:
        print 'Ctrl-C trapped. Exiting...'
        pu.shutdown()
        break
