# This code talks to the Stockfish Chess Engine. Entries are to be made in algebraic
# chess notation (eg. e2e4). Stockfish is set to think for a maximum of 1 sec.

import sys
import subprocess as S


def make_hori_grid():
    print(' +---+---+---+---+---+---+---+---+')


def make_row(r):
    col_index = ord('a')
    row = str(r+1)
    while col_index <= ord('h'):
        row += '| '
        if board[chr(col_index)][r] != 'E':
            row += board[chr(col_index)][r] + ' '
        else:
            row += '  '
        col_index += 1
    row += '|'
    print(row)


def render_board():
    make_hori_grid()
    row_index = 7
    while row_index >= 0:
        make_row(row_index)
        row_index -= 1
        make_hori_grid()
    print('   a   b   c   d   e   f   g   h')


def move_piece(path):
    start_c = path[0]
    start_r = int(path[1])-1
    end_c = path[2]
    end_r = int(path[3])-1
    piece = board[start_c][start_r]
    board[end_c][end_r] = piece
    board[start_c][start_r] = 'E'

board = {'a': ['C', 'P', 'E', 'E', 'E', 'E', 'P', 'C'],
         'b': ['N', 'P', 'E', 'E', 'E', 'E', 'P', 'N'],
         'c': ['B', 'P', 'E', 'E', 'E', 'E', 'P', 'B'],
         'd': ['Q', 'P', 'E', 'E', 'E', 'E', 'P', 'Q'],
         'e': ['K', 'P', 'E', 'E', 'E', 'E', 'P', 'K'],
         'f': ['B', 'P', 'E', 'E', 'E', 'E', 'P', 'B'],
         'g': ['N', 'P', 'E', 'E', 'E', 'E', 'P', 'N'],
         'h': ['C', 'P', 'E', 'E', 'E', 'E', 'P', 'C']}
render_board()
chess = r'/usr/local/bin/stockfish'.split()['linux' in sys.platform]
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
    print(text)
    if text == "uciok":
        break

print('Choose skill level (0-20):')
skillLevel = input()
proc.stdin.write('setoption name Skill Level value '+skillLevel+'\n')
proc.stdin.write('ucinewgame\n')

moveList = 'position startpos moves '
checkmate = False
while checkmate is False:
    print('Enter move:')
    move = input()
    move_piece(move)
    render_board()
    moveList = moveList+move+' '
    proc.stdin.write(moveList+'\n')
    proc.stdin.write('go movetime 1000\n')
    print('Computer moves:')
    while True:
        text = proc.stdout.readline().strip()
        if text[0:8] == 'bestmove':
            cpuMove = text[9:13]
            print(cpuMove)
            moveList = moveList+cpuMove+' '
            move_piece(cpuMove)
            render_board()
            break