import time
import sys
import random
import math

from base_client import LiacBot

PAWN_MATERIAL   = 100
KNIGHT_MATERIAL = 320
BISHOP_MATERIAL = 330
ROOK_MATERIAL   = 500
QUEEN_MATERIAL  = 900

PAWNS_ALIVE_MATERIAL = [float('inf'), 600, 300, 200, 100, 50, 20, 10, 0]
BISHOPS_ALIVE_MATERIAL = [0, 0, 20]

PAWN_POSITIONAL = [float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'), float('inf'),
                    500, 400, 500, 500, 500, 500, 400, 500,
                    100, 150, 200, 300, 300, 200, 150, 100,
                     35,  45,  35, 100, 100,  35,  45,  35,
                     30,  40,  30,  60,  60,  30,  40,  30,
                     25,  30,  10,  50,  50,  10,  30,  25,
                     20,  10,   5,  25,  25,   5,  10,  20,
                      0,   0,   0,   0,   0,   0,   0,   0]

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

DEPTH = 1

# BOT =========================================================================
class MyBot(LiacBot):
    name = "Natalia's Bot"

    def __init__(self):
        super(MyBot, self).__init__()
        self.last_move = None

    def on_move(self, state):
        if state['bad_move']:
            print state['board']
            raw_input()


        BitBoardState = self.string_to_bitboard(state)
        
        self.bestMove = []
        move = []
        value = self.negamax(Node(BitBoardState, []), DEPTH, float('-inf'), float('inf'))
        move = self.translate_move(self.bestMove)
        self.send_move(move[0], move[1])

    def string_to_bitboard(self, state):
        w_cells = 0
        b_cells = 0
        w_pawns = 0
        b_pawns = 0
        w_bishops = 0
        b_bishops = 0
        all_pieces = []
        piece_position = 0b1000000000000000000000000000000000000000000000000000000000000000
        for c in state['board']:
            c_ = c.lower()
            if c == c_ and c != '.':
                team = 'black'
                b_cells += piece_position
            elif c != '.':
                team = 'white'
                w_cells += piece_position
            if c_ == 'p':
                all_pieces.append(Pawn(piece_position, team))
                if team == 'black':
                    b_pawns += 1
                elif team == 'white':
                    w_pawns += 1
            elif c_ == 'r':
                all_pieces.append(Rook(piece_position, team))
            elif c_ == 'b':
                all_pieces.append(Bishop(piece_position, team))
                if team == 'black':
                    b_bishops += 1
                elif team == 'white':
                    w_bishops += 1
            elif c_ == 'q':
                all_pieces.append(Queen(piece_position, team))              
            elif c_ == 'n':
                all_pieces.append(Knight(piece_position, team))             
            piece_position = piece_position >> 1

        return {'bitboard': all_pieces, 'who_moves': state['who_moves'], 'black': b_cells, 'white': w_cells, 'empty': ~(b_cells | w_cells), 'black_bishops': b_bishops, 'white_bishops': w_bishops, 'black_pawns': b_pawns, 'white_pawns': w_pawns}
   
    def translate_move(self, move):
        i = int(math.log(move[0], 2))
        ArgFrom = (i//8, 7-(i%8))
        print 'From: ', ArgFrom
        i = int(math.log(move[1], 2))
        ArgTo = (i//8, 7-(i%8))
        print 'To:   ', ArgTo
        self.last_move = [ArgFrom, ArgTo]
        print 'Move sent'
        return [ArgFrom, ArgTo]
    
    def negamax(self, root, depth, a, b):
        if depth == 0 or root.value == float('-inf') or root.value == float('inf'):
            return root.value * root.state['who_moves']
        bestValue = float('-inf')
        root.generate_children()
        for child in root.children:
            val = - self.negamax(child, depth -1, -b, -a)
            if val >= bestValue:
                bestValue = val
                if depth == DEPTH:
                    self.bestMove = child.move
            a = max(a, val)
            if a >= b:
                break
        return bestValue
        
    def on_game_over(self, state):
        print 'Game Over.'
        # sys.exit()
      
# =============================================================================

# MODELS ======================================================================
class Node(object):
    def __init__(self, previous_state, move):
        self.children = []
        self.move = []
        self.move = move
        self.state = self.get_state(previous_state)
        self.value = self.get_value()
        self.team = self.get_team()

    def generate_children(self):
        for p in self.state['bitboard']:
            if p.team == self.team:
                p.generate_moves(self.state)
                for m in p.possibleMoves:
                    self.children.append(Node(self.state, [p.position, m]))
         
    def get_state(self, new_state):
        if not self.move:
            return new_state
        for p in new_state['bitboard']:
            if p.position == self.move[0]:
                p.position = self.move[1]
            elif p.position == self.move[1]:
                if p.team == 'black':
                    new_state['black'] = new_state['black'] & (~p.position)
                    if isinstance(p, Pawn):
                        new_state['black_pawns'] -= 1
                    elif isinstance(p, Bishop):
                        new_state['black_bishops'] -= 1
                elif p.team == 'white':
                    new_state['white'] = new_state['white'] & (~p.position)
                    if isinstance(p, Pawn):
                        new_state['white_pawns'] -= 1
                    elif isinstance(p, Bishop):
                        new_state['white_bishops'] -= 1
                new_state['bitboard'].remove(p)
        new_state['who_moves'] = - new_state['who_moves']
        return new_state

    def get_value(self):
        value = 0
        if self.state['white_pawns'] == 0:
            value = float('-inf')
        elif self.state['black_pawns'] == 0:
            value = float('inf')
        else:
            for p in self.state['bitboard']:
                if p.team == 'white':
                    value += p.value
                elif p.team == 'black':
                    value -= p.value
            value -= PAWNS_ALIVE_MATERIAL[self.state['white_pawns']]
            value += PAWNS_ALIVE_MATERIAL[self.state['black_pawns']]
            value += BISHOPS_ALIVE_MATERIAL[self.state['white_bishops']]
            value -= BISHOPS_ALIVE_MATERIAL[self.state['black_bishops']]
        return value

    def get_team(self):
        i = self.state['who_moves'] + 1
        return TEAM[i]
        

class Piece(object):
    def __init__(self):
        self.position = None
        self.team = None
        self.value = None
        self.possibleMoves = []       


class Pawn(Piece):
    def __init__(self, p, t):
        self.position = p
        self.team = t
        self.getPawnValue()
       
    def getPawnValue(self):      
        self.value = PAWN_MATERIAL
        i = int(math.log(self.position, 2))
        if self.team == 'black':
            i = 63 - i    
        self.value += PAWN_POSITIONAL[i]
                

    def generate_moves(self, state):
        moves = []
        if self.team == 'black':
            if ((self.position >> 8) >> 1) | state['white'] == state['white'] and (self.position & EighthColumn) == 0:
                moves.append((self.position >> 8) >> 1)
            if ((self.position >> 8) << 1) | state['white'] == state['white'] and (self.position & FirstColumn) == 0:
                moves.append((self.position >> 8) << 1)
            if ((self.position >> 8) & ~state['empty']) == 0:
                moves.append(self.position >> 8)
                if (self.position | SecondRow) == SecondRow and ((self.position >> 16) & ~state['empty']) == 0:
                    moves.append(self.position >> 16)
        elif self.team == 'white':
            if ((self.position << 8) >> 1) | state['black'] == state['black'] and (self.position & EighthColumn) == 0:
               moves.append((self.position << 8) >> 1)
            if ((self.position << 8) << 1) | state['black'] == state['black'] and (self.position & FirstColumn) == 0:
                moves.append((self.position << 8) << 1)
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
               
        self.possibleMoves = moves

    def check_piece(self):
        print self.team, ' Pawn'
        print bin(self.position)
   

class Rook(Piece):
    def __init__(self, p, t):
        self.position = p
        self.team = t
        self.value = ROOK_MATERIAL
        
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
             
         self.possibleMoves = moves

    def check_piece(self):
        print self.team, ' Rook'
        print bin(self.position)


class Bishop(Piece):
    def __init__(self, p, t):
        self.position = p
        self.team = t
        self.value = BISHOP_MATERIAL
        
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
       
         self.possibleMoves = moves

    def check_piece(self):
        print self.team, ' Bishop'
        print bin(self.position)
        

class Queen(Piece):
    def __init__(self, p, t):
        self.position = p
        self.team = t
        self.value = QUEEN_MATERIAL

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
         
         self.possibleMoves = moves

    def check_piece(self):
        print self.team, ' Queen'
        print bin(self.position)


class Knight(Piece):
    def __init__(self, p, t):
        self.position = p
        self.team = t
        self.value = KNIGHT_MATERIAL
        
    def generate_moves(self, state):
        i = 0
        j = 0
        k = 0
        l = 0
        moves = [(self.position >> 16) >> 1,
                 (self.position >> 16) << 1,
                 (self.position << 16) >> 1,
                 (self.position << 16) << 1,
                 (self.position >> 8) >> 2,
                 (self.position >> 8) << 2,
                 (self.position << 8) >> 2,
                 (self.position << 8) << 2]
        
        if (self.position | FirstRow) == FirstRow:
            moves.remove((self.position << 16) << 1)
            moves.remove((self.position << 16) >> 1)
            moves.remove((self.position << 8) << 2)
            moves.remove((self.position << 8) >> 2)
            i = 1
        elif (self.position | SecondRow) == SecondRow:
            moves.remove((self.position << 16) << 1)
            moves.remove((self.position << 16) >> 1)
            j = 1
        elif (self.position | SeventhRow) == SeventhRow:
            moves.remove((self.position >> 16) >> 1)
            moves.remove((self.position >> 16) << 1)
            k = 1
        elif (self.position | EighthRow) == EighthRow:
            moves.remove((self.position >> 16) << 1)
            moves.remove((self.position >> 16) >> 1)
            moves.remove((self.position >> 8) << 2)
            moves.remove((self.position >> 8) >> 2)
            l = 1

        if (self.position | FirstColumn) == FirstColumn:
            if l == 0 and k == 0: 
                moves.remove((self.position >> 16) << 1)
            if l == 0:
                moves.remove((self.position >> 8) << 2)
            if i == 0 and j == 0:
                moves.remove((self.position << 16) << 1)
            if i == 0:
                moves.remove((self.position << 8) << 2)
        elif (self.position | SecondColumn) == SecondColumn:
            if l == 0:
                moves.remove((self.position >> 8) << 2)
            if i == 0:
                moves.remove((self.position << 8) << 2)
        elif (self.position | SeventhColumn) == SeventhColumn:
            if l == 0:
                moves.remove((self.position >> 8) >> 2)
            if i == 0:
                moves.remove((self.position << 8) >> 2)
        elif (self.position | EighthColumn) == EighthColumn:
            if l == 0 and k == 0:
                moves.remove((self.position >> 16) >> 1)
            if i == 0 and j == 0:
                moves.remove((self.position << 16) >> 1)
            if l == 0:
                moves.remove((self.position >> 8) >> 2)
            if i == 0:
                moves.remove((self.position << 8) >> 2)
        self.possibleMoves = []
        for m in moves:
            if (m & state[self.team]) == 0:
                self.possibleMoves.append(m)


    def check_piece(self):
        print self.team, ' Knight'
        print bin(self.position)


# =============================================================================

if __name__ == '__main__':
    port = 50100

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            port = 50200

    bot = MyBot()
    bot.port = port

    bot.start()

