import time
import sys
import random
import math
import copy

from base_client import LiacBot

PAWN_MATERIAL   = [ 110, 110, 110, 110, 100, 100, 100,  95]
KNIGHT_MATERIAL = [ 260, 270, 270, 300, 320, 340, 350, 350]
BISHOP_MATERIAL = [ 320, 320, 330, 340, 340, 340, 350, 350]
ROOK_MATERIAL   = [ 550, 540, 530, 510, 490, 460, 450, 450]
QUEEN_MATERIAL  = [1100,1150,1200,1200,1250,1200,1250,1250]

INF = float('inf')
PAWNS_ALIVE_MATERIAL = [[INF,  0,  0,  0,  0,  0,  0,  0,  0],
                        [INF, 50, 40, 30, 20, 10,  0,  0,  0]]

PAWN_POSITIONAL      = [[INF,INF,INF,INF,INF,INF,INF,INF,
                         50, 50, 50, 50, 50, 50, 50, 50,
                         30, 20, 10, 10, 10, 10, 20, 30,
                         25, 10,  5,  5,  5,  5, 10, 25,
                         20,  0,  0,  0,  0,  0,  0, 20,
                          5,  5,  0,  5,  5,  0,  5,  5,
                        -45,-30,  5, 10, 10,  5,-30,-45,
                          0,  0,  0,  0,  0,  0,  0,  0],
                        [INF,INF,INF,INF,INF,INF,INF,INF,
                         50, 50, 50, 50, 50, 50, 50, 50,
                         10, 10, 20, 30, 30, 20, 10, 10,
                          5,  5, 10, 27, 27, 10,  5,  5,
                          0,  0,  0, 25, 25,  0,  0,  0,
                          5, -5,  0,  0,  0,  0, -5,  5,
                          5, 10,-30,-45,-45,-30, 10,  5,
                          0,  0,  0,  0,  0,  0,  0,  0]]


ROOK_POSITIONAL     =  [  0,  0,  0,  0,  0,  0,  0,  0,
                          5, 10, 10, 10, 10, 10, 10,  5,
                         -5,  0,  0,  0,  0,  0,  0, -5,
                         -5,  0,  0,  0,  0,  0,  0, -5,
                         -5,  0,  0,  0,  0,  0,  0, -5,
                         -5,  0,  0,  0,  0,  0,  0, -5,
                         -5,  0,  0,  0,  0,  0,  0, -5,
                          0,  0,  0,  5,  5,  0,  0,  0]

QUEEN_POSITIONAL    =  [-20,-10,-10, -5, -5,-10,-10,-20,
                        -10,  0,  0,  0,  0,  0,  0,-10,
                        -10,  0,  5,  5,  5,  5,  0,-10,
                         -5,  0,  5,  5,  5,  5,  0, -5,
                          0,  0,  5,  5,  5,  5,  0, -5,
                        -10,  5,  5,  5,  5,  5,  0,-10,
                        -10,  0,  5,  0,  0,  0,  0,-10,
                        -20,-10,-10, -5, -5,-10,-10,-20]

BISHOP_POSITIONAL   =  [-20,-10,-10,-10,-10,-10,-10,-20,
                        -10,  0,  0,  0,  0,  0,  0,-10,
                        -10,  0,  5, 10, 10,  5,  0,-10,
                        -10,  5,  5, 10, 10,  5,  5,-10,
                        -10,  0, 10, 10, 10, 10,  0,-10,
                        -10, 10, 10, 10, 10, 10, 10,-10,
                        -10,  5,  0,  0,  0,  0,  5,-10,
                        -20,-10,-40,-10,-10,-40,-10,-20]

KNIGHT_POSITIONAL    = [-20,-40,-30,-30,-30,-30,-40,-20,
                        -40,-20, 30,  0,  0, 30,-20,-40,
                        -30,  0, 20, 25, 25, 20,  0,-30,
                        -30, 15, 25, 30, 30, 25, 15,-30,
                        -30,  0, 25, 30, 30, 25,  0,-30,
                        -30,  5, 20, 25, 25, 20,  5,-30,
                        -40,-20,  0,  5,  5,  0,-20,-40,
                        -50,-30,-20,-30,-30,-20,-30,-50]

                        #1
KNIGHT_MOVES         = [[(2**63) >> 10, (2**63) >> 17],
                        [(2**62) >> 10, (2**62) >> 17, (2**62) >> 15],
                        [(2**61) >> 10, (2**61) >> 17, (2**61) >> 15, (2**61) >> 6],
                        [(2**60) >> 10, (2**60) >> 17, (2**60) >> 15, (2**60) >> 6],
                        [(2**59) >> 10, (2**59) >> 17, (2**59) >> 15, (2**59) >> 6],
                        [(2**58) >> 10, (2**58) >> 17, (2**58) >> 15, (2**58) >> 6],
                        [(2**57) >> 17, (2**57) >> 15, (2**57) >> 6],
                        [(2**56) >> 15, (2**56) >> 6],

                        #2
                        [(2**55) << 6, (2**55) >> 10, (2**55) >> 17],
                        [(2**54) << 6, (2**54) >> 10, (2**54) >> 17, (2**54) >> 15],
                        [(2**53) << 10, (2**53) << 6, (2**53) >> 10, (2**53) >> 17, (2**53) >> 15, (2**53) >> 6],
                        [(2**52) << 10, (2**52) << 6, (2**52) >> 10, (2**52) >> 17, (2**52) >> 15, (2**52) >> 6],
                        [(2**51) << 10, (2**51) << 6, (2**51) >> 10, (2**51) >> 17, (2**51) >> 15, (2**51) >> 6],
                        [(2**50) << 10, (2**50) << 6, (2**50) >> 10, (2**50) >> 17, (2**50) >> 15, (2**50) >> 6],
                        [(2**49) << 10, (2**49) >> 17, (2**49) >> 15, (2**49) >> 6],
                        [(2**48) << 10, (2**48) >> 15, (2**48) >> 6],

                        #3
                        [(2**47) << 15, (2**47) << 6, (2**47) >> 10, (2**47) >> 17],
                        [(2**46) << 17, (2**46) << 15, (2**46) << 6, (2**46) >> 10, (2**46) >> 17, (2**46) >> 15],
                        [(2**45) << 10, (2**45) << 17, (2**45) << 15, (2**45) << 6, (2**45) >> 10, (2**45) >> 17, (2**45) >> 15, (2**45) >> 6],
                        [(2**44) << 10, (2**44) << 17, (2**44) << 15, (2**44) << 6, (2**44) >> 10, (2**44) >> 17, (2**44) >> 15, (2**44) >> 6],
                        [(2**43) << 10, (2**43) << 17, (2**43) << 15, (2**43) << 6, (2**43) >> 10, (2**43) >> 17, (2**43) >> 15, (2**43) >> 6],
                        [(2**42) << 10, (2**42) << 17, (2**42) << 15, (2**42) << 6, (2**42) >> 10, (2**42) >> 17, (2**42) >> 15, (2**42) >> 6],
                        [(2**41) << 10, (2**41) << 17, (2**41) << 15, (2**41) >> 17, (2**41) >> 15, (2**41) >> 6],
                        [(2**40) << 10, (2**40) << 17, (2**40) >> 15, (2**40) >> 6],

                        #4
                        [(2**39) << 15, (2**39) << 6, (2**39) >> 10, (2**39) >> 17],
                        [(2**38) << 17, (2**38) << 15, (2**38) << 6, (2**38) >> 10, (2**38) >> 17, (2**38) >> 15],
                        [(2**37) << 10, (2**37) << 17, (2**37) << 15, (2**37) << 6, (2**37) >> 10, (2**37) >> 17, (2**37) >> 15, (2**37) >> 6],
                        [(2**36) << 10, (2**36) << 17, (2**36) << 15, (2**36) << 6, (2**36) >> 10, (2**36) >> 17, (2**36) >> 15, (2**36) >> 6],
                        [(2**35) << 10, (2**35) << 17, (2**35) << 15, (2**35) << 6, (2**35) >> 10, (2**35) >> 17, (2**35) >> 15, (2**35) >> 6],
                        [(2**34) << 10, (2**34) << 17, (2**34) << 15, (2**34) << 6, (2**34) >> 10, (2**34) >> 17, (2**34) >> 15, (2**34) >> 6],
                        [(2**33) << 10, (2**33) << 17, (2**33) << 15, (2**33) >> 17, (2**33) >> 15, (2**33) >> 6],
                        [(2**32) << 10, (2**32) << 17, (2**32) >> 15, (2**32) >> 6],

                        #5
                        [(2**31) << 15, (2**31) << 6, (2**31) >> 10, (2**31) >> 17],
                        [(2**30) << 17, (2**30) << 15, (2**30) << 6, (2**30) >> 10, (2**30) >> 17, (2**30) >> 15],
                        [(2**29) << 10, (2**29) << 17, (2**29) << 15, (2**29) << 6, (2**29) >> 10, (2**29) >> 17, (2**29) >> 15, (2**29) >> 6],
                        [(2**28) << 10, (2**28) << 17, (2**28) << 15, (2**28) << 6, (2**28) >> 10, (2**28) >> 17, (2**28) >> 15, (2**28) >> 6],
                        [(2**27) << 10, (2**27) << 17, (2**27) << 15, (2**27) << 6, (2**27) >> 10, (2**27) >> 17, (2**27) >> 15, (2**27) >> 6],
                        [(2**26) << 10, (2**26) << 17, (2**26) << 15, (2**26) << 6, (2**26) >> 10, (2**26) >> 17, (2**26) >> 15, (2**26) >> 6],
                        [(2**25) << 10, (2**25) << 17, (2**25) << 15, (2**25) >> 17, (2**25) >> 15, (2**25) >> 6],
                        [(2**24) << 10, (2**24) << 17, (2**24) >> 15, (2**24) >> 6],

                        #6
                        [(2**23) << 15, (2**23) << 6, (2**23) >> 10, (2**23) >> 17],
                        [(2**22) << 17, (2**22) << 15, (2**22) << 6, (2**22) >> 10, (2**22) >> 17, (2**22) >> 15],
                        [(2**21) << 10, (2**21) << 17, (2**21) << 15, (2**21) << 6, (2**21) >> 10, (2**21) >> 17, (2**21) >> 15, (2**21) >> 6],
                        [(2**20) << 10, (2**20) << 17, (2**20) << 15, (2**20) << 6, (2**20) >> 10, (2**20) >> 17, (2**20) >> 15, (2**20) >> 6],
                        [(2**19) << 10, (2**19) << 17, (2**19) << 15, (2**19) << 6, (2**19) >> 10, (2**19) >> 17, (2**19) >> 15, (2**19) >> 6],
                        [(2**18) << 10, (2**18) << 17, (2**18) << 15, (2**18) << 6, (2**18) >> 10, (2**18) >> 17, (2**18) >> 15, (2**18) >> 6],
                        [(2**17) << 10, (2**17) << 17, (2**17) << 15, (2**17) >> 17, (2**17) >> 15, (2**17) >> 6],
                        [(2**16) << 10, (2**16) << 17, (2**16) >> 15, (2**16) >> 6],

                        #7
                        [(2**15) << 15, (2**15) << 6, (2**15) >> 10],
                        [(2**14) << 17, (2**14) << 15, (2**14) << 6, (2**14) >> 10],
                        [(2**13) << 10, (2**13) << 17, (2**13) << 15, (2**13) << 6, (2**13) >> 10, (2**13) >> 6],
                        [(2**12) << 10, (2**12) << 17, (2**12) << 15, (2**12) << 6, (2**12) >> 10, (2**12) >> 6],
                        [(2**11) << 10, (2**11) << 17, (2**11) << 15, (2**11) << 6, (2**11) >> 10, (2**11) >> 6],
                        [(2**10) << 10, (2**10) << 17, (2**10) << 15, (2**10) << 6, (2**10) >> 10, (2**10) >> 6],
                        [(2**9) << 10, (2**9) << 17, (2**9) << 15, (2**9) >> 6],
                        [(2**8) << 10, (2**8) << 17, (2**8) >> 6],

                        #8
                        [(2**7) << 15, (2**7) << 6],
                        [(2**6) << 17, (2**6) << 15, (2**6) << 6],
                        [(2**5) << 10, (2**5) << 17, (2**5) << 15, (2**5) << 6],
                        [(2**4) << 10, (2**4) << 17, (2**4) << 15, (2**4) << 6],
                        [(2**3) << 10, (2**3) << 17, (2**3) << 15, (2**3) << 6],
                        [(2**2) << 10, (2**2) << 17, (2**2) << 15, (2**2) << 6],
                        [(2**1) << 10, (2**1) << 17, (2**1) << 15],
                        [(2**0) << 10, (2**0) << 17]]

TEAM = ['black', None,'white']

FirstRow      = 0b1111111100000000000000000000000000000000000000000000000000000000
SecondRow     = 0b0000000011111111000000000000000000000000000000000000000000000000
ThirdRow      = 0b0000000000000000111111110000000000000000000000000000000000000000
FourthRow     = 0b0000000000000000000000001111111100000000000000000000000000000000
FifthRow      = 0b0000000000000000000000000000000011111111000000000000000000000000
SixthRow      = 0b0000000000000000000000000000000000000000111111110000000000000000
SeventhRow    = 0b0000000000000000000000000000000000000000000000001111111100000000
EighthRow     = 0b0000000000000000000000000000000000000000000000000000000011111111
FirstColumn   = 0b1000000010000000100000001000000010000000100000001000000010000000
SecondColumn  = 0b0100000001000000010000000100000001000000010000000100000001000000
SeventhColumn = 0b0000001000000010000000100000001000000010000000100000001000000010
EighthColumn  = 0b0000000100000001000000010000000100000001000000010000000100000001

MAX_DEPTH = 3

# BOT =========================================================================
class MyBot(LiacBot):

    all_names = ['Swagosaurus', 'Swagmaster', 'Swagnator', 'DarkSwag', 'xX_Swag_Xx', 'Swag_BR']
    name = random.choice(all_names)

    def __init__(self):
        super(MyBot, self).__init__()
        self.last_move = None
        self.move_history = []
        self.repeated_move = None

    def on_move(self, state):
        if state['bad_move']:
            print state['board']
            raw_input()
        self.get_repeated_move()
        bitboard_state = self.string_to_bitboard(state)
        self.best_moves = []
        value = self.negamax(Node(bitboard_state, []), MAX_DEPTH, -INF, INF)
        self.move_history.insert(0, self.best_moves[-1])
        if not self.move_history:
            self.best_moves[-1] = repeated_move
        move = self.translate_move(self.best_moves[-1])
        self.send_move(move[0], move[1])

    def get_repeated_move(self):
        self.repeated_move = None
        count = 0
        i = 0
        last_m = None
        for m in self.move_history[:7]:
            if i%2:
                if last_m == m:
                    count += 1
                    if count >= 2:
                        self.repeated_move = m
                else:
                    count = 0
                last_m = m
            i += 1

    def string_to_bitboard(self, state):
        value = 0
        w_b = 0
        b_b = 0
        w_cells = 0
        b_cells = 0
        w_pawns = 0
        b_pawns = 0
        enpassant = None
        all_pieces = []
        piece_position = 0b1000000000000000000000000000000000000000000000000000000000000000
        pieces_alive = 0
        for i in state['board']:
            if i != '.':
                pieces_alive += 1
        for c in state['board']:
            c_ = c.lower()
            if c == c_ and c != '.':
                team = 'black'
                b_cells += piece_position
                if c_ == 'p':
                    new_piece = Pawn(piece_position, team, pieces_alive)
                    all_pieces.append(new_piece)
                    b_pawns += 1
                    value -= new_piece.value
                elif c_ == 'r':
                    new_piece = Rook(piece_position, team, pieces_alive)
                    all_pieces.append(new_piece)
                    value -= new_piece.value
                elif c_ == 'b':
                    new_piece = Bishop(piece_position, team, pieces_alive)
                    all_pieces.append(new_piece)
                    value -= new_piece.value
                    b_b += 1
                elif c_ == 'q':
                    new_piece = Queen(piece_position, team, pieces_alive)
                    all_pieces.append(new_piece)
                    value -= new_piece.value          
                elif c_ == 'n':
                    new_piece = Knight(piece_position, team, pieces_alive)
                    all_pieces.append(new_piece)
                    value -= new_piece.value
            elif c != '.':
                team = 'white'
                w_cells += piece_position
                if c_ == 'p':
                    new_piece = Pawn(piece_position, team, pieces_alive)
                    all_pieces.append(new_piece)
                    w_pawns += 1
                    value += new_piece.value
                elif c_ == 'r':
                    new_piece = Rook(piece_position, team, pieces_alive)
                    all_pieces.append(new_piece)
                    value += new_piece.value
                elif c_ == 'b':
                    new_piece = Bishop(piece_position, team, pieces_alive)
                    all_pieces.append(new_piece)
                    value += new_piece.value
                    w_b += 1
                elif c_ == 'q':
                    new_piece = Queen(piece_position, team, pieces_alive)
                    all_pieces.append(new_piece) 
                    value += new_piece.value             
                elif c_ == 'n':
                    new_piece = Knight(piece_position, team, pieces_alive)
                    all_pieces.append(new_piece)   
                    value += new_piece.value          
            piece_position = piece_position >> 1

        value -= PAWNS_ALIVE_MATERIAL[len(all_pieces)//18][w_pawns]
        value += PAWNS_ALIVE_MATERIAL[len(all_pieces)//18][b_pawns]

        if w_b == 2:
            value += 50
            w_b = 1
        else:
            w_b = 0

        if b_b == 2:
            value -= 50
            b_b = 1
        else:
            b_b = 0


        if state['enpassant']:
            enpassant = 2**(state['enpassant'][0]*8 + (7 - state['enpassant'][1]))

        return {'bitboard': all_pieces, 'value': value, 'who_moves': state['who_moves'],
                'black': b_cells, 'white': w_cells, 'empty': ~(b_cells | w_cells),
                'black_pawns': b_pawns, 'white_pawns': w_pawns, 
                'enpassant': enpassant, 'two_bishops_black': b_b, 'two_bishops_white': w_b}
   
    def translate_move(self, move):
        i = int(math.log(move[0], 2))
        ArgFrom = (i//8, 7-(i%8))
        print ArgFrom,
        i = int(math.log(move[1], 2))
        ArgTo = (i//8, 7-(i%8))
        print ArgTo
        self.last_move = [ArgFrom, ArgTo]
        return [ArgFrom, ArgTo]

    def children_sort(self, children):
        if children:
            i = (children[0].team == 'black')
            children.sort(key=lambda x:x.state['value'], reverse=i)
    
    def negamax(self, root, depth, a, b):
        if depth == 0 or root.state['value'] == -INF or root.state['value'] == INF:
            return root.state['value'] * root.state['who_moves']
        best_value = -INF
        root.generate_children()
        self.children_sort(root.children)
        for child in root.children:
            val = - self.negamax(child, depth -1, -b, -a)
            if val >= best_value:
                best_value = val
                if depth == MAX_DEPTH:
                    if child.move != self.repeated_move:
                        self.best_moves.append(child.move)
            a = max(a, val)
            if a >= b:
                break
        return best_value
        
    def on_game_over(self, state):
        print 'Game Over.'
      
# =============================================================================

# MODELS ======================================================================
class Node(object):
    def __init__(self, previous_state, move):
        self.children = []
        self.move = move
        self.state = self.get_state(previous_state)
        self.team = self.get_team()

    def generate_children(self):
        for p in self.state['bitboard']:
            if p.team == self.team:
                p.generate_moves(self.state)
                for m in p.possible_moves:
                    self.children.append(Node(self.state, [p.position, m]))
         
    def get_state(self, previous_state):
        if not self.move:
            return previous_state
        else:
            new_state = {'bitboard': [],
                        'value': previous_state['value'],
                        'black': previous_state['black'],
                        'white': previous_state['white'],
                        'black_pawns': previous_state['black_pawns'],
                        'white_pawns': previous_state['white_pawns'],
                        'who_moves': - previous_state['who_moves'],
                        'enpassant': None,
                        'empty': previous_state['empty'],
                        'two_bishops_white': previous_state['two_bishops_white'],
                        'two_bishops_black': previous_state['two_bishops_black']}
            for p in previous_state['bitboard']:
                i = 1
                if p.team == 'black':
                    i = -1
                if p.position == self.move[0]:
                    new_state['value'] -= p.value * i
                    new_state[p.team] = (previous_state[p.team] & ~p.position) | self.move[1]
                    new_piece = p.__class__(self.move[1], p.team, len(previous_state['bitboard']))
                    new_state['bitboard'].append(new_piece)
                    new_state['value'] += new_piece.value * i
                    if isinstance(p, Pawn):
                        if self.move[0] << 16 == self.move[1]:
                            new_state['enpassant'] = self.move[0] << 8
                        if self.move[0] >> 16 == self.move[1]:
                            new_state['enpassant'] = self.move[0] >> 8          
                elif p.position == self.move[1]:
                    new_state['value'] -= p.value * i
                    if isinstance(p, Pawn):
                        new_state[p.team + '_pawns'] -= 1
                        new_state['value'] += PAWNS_ALIVE_MATERIAL[len(previous_state['bitboard'])//18][previous_state[p.team + '_pawns']] * i
                        new_state['value'] -= PAWNS_ALIVE_MATERIAL[len(previous_state['bitboard'])//18][new_state[p.team + '_pawns']] * i
                    elif isinstance(p, Bishop):
                        new_state['two_bishops_' + p.team] = 0
                        if new_state['two_bishops_' + p.team] != previous_state['two_bishops_' + p.team]:
                            new_state['value'] -= 50 * i 
                    new_state[p.team] = new_state[p.team] & ~p.position 
                else:
                    new_state['bitboard'].append(p)
            new_state['empty'] = ~(new_state['black'] | new_state['white'])
            return new_state


    def get_team(self):
        i = self.state['who_moves'] + 1
        return TEAM[i]
        

class Piece(object):
    def __init__(self):
        self.position = None
        self.team = None
        self.possible_moves = []    


class Pawn(Piece):
    def __init__(self, p, t, pieces_alive):
        self.position = p
        self.team = t
        self.value = self.get_value(pieces_alive)
       
    def get_value(self, pieces_alive):
        i = int(math.log(self.position, 2))
        if self.team == 'white':
            i = 63 - i
        return PAWN_MATERIAL[pieces_alive//4] + PAWN_POSITIONAL[pieces_alive//18][i]
                
    def generate_moves(self, state):
        moves = []
        if self.team == 'black':
            if ((self.position >> 8) >> 1) | state['white'] == state['white'] and (self.position & EighthColumn) == 0:
                moves.append((self.position >> 8) >> 1)
            if ((self.position >> 8) << 1) | state['white'] == state['white'] and (self.position & FirstColumn) == 0:
                moves.append((self.position >> 8) << 1)
            if state['enpassant']:
                if (((state['enpassant'] << 8) >> 1) | ((state['enpassant'] << 8) << 1)) & self.position == self.position:
                    moves.append(state['enpassant'])
            if ((self.position >> 8) & ~state['empty']) == 0:
                moves.append(self.position >> 8)
                if (self.position | SecondRow) == SecondRow and ((self.position >> 16) & ~state['empty']) == 0:
                    moves.append(self.position >> 16)
        elif self.team == 'white':
            if ((self.position << 8) >> 1) | state['black'] == state['black'] and (self.position & EighthColumn) == 0:
               moves.append((self.position << 8) >> 1)
            if ((self.position << 8) << 1) | state['black'] == state['black'] and (self.position & FirstColumn) == 0:
                moves.append((self.position << 8) << 1)
            if state['enpassant']:
                if (((state['enpassant'] >> 8) >> 1) | ((state['enpassant'] >> 8) << 1)) & self.position == self.position:
                    moves.append(state['enpassant'])
            if ((self.position << 8) & ~state['empty']) == 0:
                moves.append(self.position << 8)
                if (self.position | SeventhRow) == SeventhRow and ((self.position << 16) & ~state['empty']) == 0:
                    moves.append(self.position << 16)

        if self.team == 'black' and ((self.position >> 8) & ~state['empty']) == 0:
            moves.append(self.position >> 8)
            if (self.position | SecondRow) == SecondRow and ((self.position >> 16) & ~state['empty']) == 0:
                moves.append(self.position >> 16)
        elif self.team == 'white' and ((self.position << 8) & ~state['empty']) == 0:
            moves.append(self.position << 8)
            if (self.position | SeventhRow) == SeventhRow and ((self.position << 16) & ~state['empty']) == 0:
                moves.append(self.position << 16)
               
        self.possible_moves = moves
   

class Rook(Piece):
    def __init__(self, p, t, pieces_alive):
        self.position = p
        self.team = t
        self.value = self.get_value(pieces_alive)

    def get_value(self, pieces_alive):
        i = int(math.log(self.position, 2))
        if self.team == 'white':
            i = 63 - i
        return ROOK_MATERIAL[pieces_alive//4] + ROOK_POSITIONAL[i]
        
    def generate_moves(self, state):
        moves = []
        previousMove = self.position
        while (((previousMove >> 8) & state[self.team]) == 0) and ((previousMove >> 8) > 0):
            moves.append(previousMove >> 8)
            previousMove = previousMove >> 8
            if previousMove & state['empty'] == 0:
                break
             
        previousMove = self.position
        while (((previousMove << 8 ) & state[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0):
            moves.append(previousMove << 8)
            previousMove = previousMove << 8
            if previousMove & state['empty'] == 0:
                break
 
        previousMove = self.position
        while (((previousMove >> 1 ) & state[self.team]) == 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append(previousMove >> 1)
            previousMove = previousMove >> 1
            if previousMove & state['empty'] == 0:
                break
 
        previousMove = self.position
        while (((previousMove << 1 ) & state[self.team]) == 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append(previousMove << 1)
            previousMove = previousMove << 1
            if previousMove & state['empty'] == 0:
                break
            
        self.possible_moves = moves


class Bishop(Piece):
    def __init__(self, p, t, pieces_alive):
        self.position = p
        self.team = t
        self.value = self.get_value(pieces_alive)

    def get_value(self, pieces_alive):
        i = int(math.log(self.position, 2))
        if self.team == 'white':
            i = 63 - i
        return BISHOP_MATERIAL[pieces_alive//4] + BISHOP_POSITIONAL[i]
        
    def generate_moves(self, state):
        moves = []
        previousMove = self.position
        while ((((previousMove >> 8) << 1) & state[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append((previousMove >> 8) << 1)
            previousMove = (previousMove >> 8) << 1
            if previousMove & state['empty'] == 0:
                break
        previousMove = self.position
        while ((((previousMove << 8) >> 1) & state[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append((previousMove << 8) >> 1)
            previousMove = (previousMove << 8) >> 1
            if previousMove & state['empty'] == 0:
                break
 
        previousMove = self.position
        while ((((previousMove >> 1 ) >> 8) & state[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append((previousMove >> 1) >> 8)
            previousMove = (previousMove >> 1) >> 8
            if previousMove & state['empty'] == 0:
                break
 
        previousMove = self.position
        while ((((previousMove << 1 ) << 8) & state[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append((previousMove << 1) << 8)
            previousMove = (previousMove << 1) << 8
            if previousMove & state['empty'] == 0:
                break
       
        self.possible_moves = moves

        
class Queen(Piece):
    def __init__(self, p, t, pieces_alive):
        self.position = p
        self.team = t
        self.value = self.get_value(pieces_alive)

    def get_value(self, pieces_alive):
        i = int(math.log(self.position, 2))
        if self.team == 'white':
            i = 63 - i
        return QUEEN_MATERIAL[pieces_alive//4] + QUEEN_POSITIONAL[i]

    def generate_moves(self, state):
        moves = []
        previousMove = self.position
        while ((((previousMove >> 8) << 1) & state[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append((previousMove >> 8) << 1)
            previousMove = (previousMove >> 8) << 1
            if previousMove & state['empty'] == 0:
                break
 
        previousMove = self.position
        while ((((previousMove << 8) >> 1) & state[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append((previousMove << 8) >> 1)
            previousMove = (previousMove << 8) >> 1
            if previousMove & state['empty'] == 0:
                break
 
        previousMove = self.position
        while ((((previousMove >> 1 ) >> 8) & state[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append((previousMove >> 1) >> 8)
            previousMove = (previousMove >> 1) >> 8
            if previousMove & state['empty'] == 0:
                break
 
        previousMove = self.position
        while ((((previousMove << 1 ) << 8) & state[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append((previousMove << 1) << 8)
            previousMove = (previousMove << 1) << 8
            if previousMove & state['empty'] == 0:
                break
    
        previousMove = self.position
        while (((previousMove >> 8) & state[self.team]) == 0) and ((previousMove >> 8) > 0):
            moves.append(previousMove >> 8)
            previousMove = previousMove >> 8
            if previousMove & state['empty'] == 0:
                break
 
        previousMove = self.position
        while (((previousMove << 8 ) & state[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0):
            moves.append(previousMove << 8)
            previousMove = previousMove << 8
            if previousMove & state['empty'] == 0:
                break
 
        previousMove = self.position
        while (((previousMove >> 1 ) & state[self.team]) == 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append(previousMove >> 1)
            previousMove = previousMove >> 1
            if previousMove & state['empty'] == 0:
                break
 
        previousMove = self.position
        while (((previousMove << 1 ) & state[self.team]) == 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append(previousMove << 1)
            previousMove = previousMove << 1
            if previousMove & state['empty'] == 0:
                break
         
        self.possible_moves = moves


class Knight(Piece):
    def __init__(self, p, t, pieces_alive):
        self.position = p
        self.team = t
        self.value = self.get_value(pieces_alive)

    def get_value(self, pieces_alive):
        i = int(math.log(self.position, 2))
        if self.team == 'white':
            i = 63 - i
        return KNIGHT_MATERIAL[pieces_alive//4] + KNIGHT_POSITIONAL[i]
        
    def generate_moves(self, state):
        i = 63 - int(math.log(self.position, 2))
        moves = copy.copy(KNIGHT_MOVES[i])
        for m in moves:
            if (m & state[self.team]) == m:
                moves.remove(m)
        self.possible_moves = moves


# =============================================================================

if __name__ == '__main__':
    port = 50100

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            port = 50200

    bot = MyBot()
    bot.port = port

    bot.start()

