import time
import sys
import random

from base_client import LiacBot

WHITE = 1
BLACK = -1
NONE = 0

# BOT =========================================================================
class MyBot(LiacBot):
    name = "Natalia's Bot"

    def __init__(self):
        super(MyBot, self).__init__()
        self.last_move = None

    def on_move(self, state):
        board = Board(state, 'white') # **
        
        if state['bad_move']:
            print state['board']
            raw_input()

        print 'Board generated'
        
        '''if state['bad_move']:
            print state['board']
            raw_input()'''

        print 'Board validated'
        moveList = []
        for piece in board.AllPieces:
            for moveAux in piece.possibleMoves:
                if piece.team == 'white': # * not generalized
                    moveList.append([piece.position, moveAux])
        print 'Possible moves found'
        
        # EVALUATE each possible move and it's possible responses
        move = random.choice(moveList)
        print 'Move chosen'

        i = 0
        while move[0] < 2**63:
            move[0] = move[0] << 1
            i += 1
        ArgFrom = (i%8, i//8)
        print 'From: ', ArgFrom
        
        i = 0
        while move[1] < 2**63:
            move[1] = move[1] << 1
            i += 1
        ArgTo = (i%8, i//8)
        print 'To:   ', ArgTo
    
        print 'Move translated'
        self.last_move = [ArgFrom, ArgTo]
        self.send_move(ArgFrom, ArgTo)
        print 'Move sent'
        

    def on_game_over(self, state):
        print 'Game Over.'
        # sys.exit()
# =============================================================================

# MODELS ======================================================================
class Board(object):
    def __init__(self, state, team):
        self.AllPieces = []
        self.WhitePieces = {'Pawns': 0,'Rooks': 0,'Bishop': 0,'Queen': 0,'Knight': 0}
        self.BlackPieces = {'Pawns': 0,'Rooks': 0,'Bishop': 0,'Queen': 0,'Knight': 0}
        self.Pawns = []
        self.Rooks = []
        self.Bishops = []
        self.Queens = []
        self.Knights = []
        self.OccupiedCells = {}
        self.EmptyCells  = 0
        self.Value = 0
    
        self.WhitePieces['Pawns'] = self.getGeneralPosition(state, 'p')
        self.WhitePieces['Rooks'] = self.getGeneralPosition(state, 'r')
        self.WhitePieces['Bishop'] = self.getGeneralPosition(state, 'b')
        self.WhitePieces['Queen'] = self.getGeneralPosition(state, 'q')
        self.WhitePieces['Knight'] = self.getGeneralPosition(state, 'n')

        self.BlackPieces['Pawns'] = self.getGeneralPosition(state, 'P')
        self.BlackPieces['Rooks'] = self.getGeneralPosition(state, 'R')
        self.BlackPieces['Bishop'] = self.getGeneralPosition(state, 'B')
        self.BlackPieces['Queen'] = self.getGeneralPosition(state, 'Q')
        self.BlackPieces['Knight'] = self.getGeneralPosition(state, 'N')

        self.OccupiedCells['white'] = self.WhitePieces['Pawns'] | self.WhitePieces['Rooks'] | self.WhitePieces['Bishop'] | self.WhitePieces['Queen'] | self.WhitePieces['Knight']
        self.OccupiedCells['black'] = self.EmptyCells | self.BlackPieces['Pawns'] | self.BlackPieces['Rooks'] | self.BlackPieces['Bishop'] | self.BlackPieces['Queen'] | self.BlackPieces['Knight']
        self.EmptyCells = ~( self.OccupiedCells['white'] | self.OccupiedCells['black'] )

        self.getIndividualPositions(state)
            
        self.AllPieces.extend(self.Pawns)
        self.AllPieces.extend(self.Rooks)
        self.AllPieces.extend(self.Bishops)
        self.AllPieces.extend(self.Queens)
        self.AllPieces.extend(self.Knights)

        self.getBoardValue(team)


    def getBoardValue(self, team):
        for p in self.AllPieces:
            if p.team == team:
                self.Value += p.value
            else:
                self.Value -= p.value

    def getGeneralPosition(self, state, pieceCode):
        i = 0
        bitboard = 0
        bitboardBase = 0b1000000000000000000000000000000000000000000000000000000000000000 
        for p in state['board']:
            if p == pieceCode: 
                bitboard += bitboardBase >> i
            i += 1
        return bitboard
                
    def getIndividualPositions(self, state):
        i = 0
        j = 0
        k = 0
        l = 0
        m = 0
        n = 0
        bitboardBase = 0b1000000000000000000000000000000000000000000000000000000000000000
        for p in state['board']:
            if p == p.lower():
                team = 'white'
            else:
                team = 'black'
            if p.lower() == 'p':
                self.Pawns.append(Pawn(bitboardBase >> i, team, self))
                j += 1
            elif p.lower() == 'r':
                self.Rooks.append(Rook(bitboardBase >> i, team, self))
                k += 1
            elif p.lower() == 'b':
                self.Bishops.append(Bishop(bitboardBase >> i, team, self))
                l += 1
            elif p.lower() == 'q':
                self.Queens.append(Queen(bitboardBase >> i, team, self))
                m += 1
            elif p.lower() == 'n':
                self.Knights.append(Knight(bitboardBase >> i, team))
                n += 1
            i += 1
            
        Pawn.Alive = j
        Rook.Alive = k
        Bishop.Alive = l
        Queen.Alive = m
        Knight.Alive = n

        


class Piece(object):
    def __init__(self):
        self.position = None
        self.team = None
        self.possibleMoves = None
        self.value = None
        self.char = None
        

class Pawn(Piece):
    Alive = None
    def __init__(self, p, t, board):
        self.position = p
        self.team = t
        if self.team == 'black':
            self.char = 'P'
            i = 0
            aux = self.position
            while aux < 2**64:
                aux = aux << 1
                i += 1
            self.value = i*i
        elif self.team == 'white':
            self.char = 'p'
            i = 0
            aux = self.position
            while aux > 0:
                aux = aux >> 1
                i += 1
            self.value = i*i      
        self.possibleMoves = self.generatePossibleMoves(board)
        
    def generatePossibleMoves(self, board):
        SecondRow  = 0b0000000010000000000000000000000000000000000000000000000000000000
        ThirdRow  = 0b0000000000000000100000000000000000000000000000000000000000000000

        SeventhRow  = 0b0000000000000000000000000000000000000000000000001000000000000000
        EighthRow  = 0b0000000000000000000000000000000000000000000000000000000010000000

        moves = []

        if self.team == 'white' and (((self.position >> 8) and board.OccupiedCells['white']) != (self.position >> 8)):
            moves.append(self.position >> 8)
            if (self.position >= SecondRow) and (self.position > ThirdRow) and (((self.position >> 16) and board.OccupiedCells['white']) != (self.position >> 16)):
                moves.append(self.position >> 16)
        elif self.team == 'black' and (((self.position << 8) and board.OccupiedCells['black']) != (self.position << 8)):
            moves.append(self.position << 8)
            if (self.position >= SeventhRow) and (self.position < EighthRow) and (((self.position << 16) and board.OccupiedCells['black']) != (self.position << 16)):
                moves.append(self.position << 16)
                
        return moves
   

class Rook(Piece):
    Alive = None
    def __init__(self, p, t, board):
        self.position = p
        self.team = t
        if self.team == 'black':
            self.char = 'R'
        elif self.team == 'white':
            self.char = 'r'
        self.value = 10
        self.possibleMoves = self.generatePossibleMoves(board)
        

    def generatePossibleMoves(self, board):
        FirstColumn = 0b1000000010000000100000001000000010000000100000001000000010000000
        EighthColumn = 0b0000000100000001000000010000000100000001000000010000000100000001  
        moves = []
        previousMove = self.position
        # while the move doesn't overlap other pieces from the same team and doesn't leave the board
        while (((previousMove >> 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0):
            moves.append(previousMove >> 8)
            previousMove = previousMove >> 8

        previousMove = self.position
        while (((previousMove << 8 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0):
            moves.append(previousMove << 8)
            previousMove = previousMove << 8

        previousMove = self.position
        while (((previousMove >> 1 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append(previousMove >> 1)
            previousMove = previousMove >> 1

        previousMove = self.position
        while (((previousMove << 1 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append(previousMove << 1)
            previousMove = previousMove << 1
     
        return moves


class Bishop(Piece):
    Alive = None
    def __init__(self, p, t, board):
        self.position = p
        self.team = t
        if self.team == 'black':
            self.char = 'B'
        elif self.team == 'white':
            self.char = 'b'
        self.value = 12
        self.possibleMoves = self.generatePossibleMoves(board)
        

    def generatePossibleMoves(self, board):
        FirstColumn = 0b1000000010000000100000001000000010000000100000001000000010000000
        EighthColumn = 0b0000000100000001000000010000000100000001000000010000000100000001
        moves = []
        previousMove = self.position
        # while the move doesn't overlap other pieces from the same team and doesn't leave the board
        while ((((previousMove >> 8) << 1) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append((previousMove >> 8) << 1)
            previousMove = (previousMove >> 8) << 1

        previousMove = self.position
        while ((((previousMove << 8) >> 1) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append((previousMove << 8) >> 1)
            previousMove = (previousMove << 8) >> 1

        previousMove = self.position
        while ((((previousMove >> 1 ) >> 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append((previousMove >> 1) >> 8)
            previousMove = (previousMove >> 1) >> 8

        previousMove = self.position
        while ((((previousMove << 1 ) << 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | FIrstColumn) != FirstColumn):
            moves.append((previousMove << 1) << 8)
            previousMove = (previousMove << 1) << 8

        for m in moves:
            print bin(m)
      
        return moves

class Queen(Piece):
    Alive = None
    def __init__(self, p, t, board):
        self.position = p
        self.team = t
        if self.team == 'black':
            self.char = 'Q'
        elif self.team == 'white':
            self.char = 'q'
        self.value = 20
        self.possibleMoves = self.generatePossibleMoves(board)
        

    def generatePossibleMoves(self, board):
        FirstColumn = 0b1000000010000000100000001000000010000000100000001000000010000000
        EighthColumn = 0b0000000100000001000000010000000100000001000000010000000100000001
        moves = []
        previousMove = self.position
        # while the move doesn't overlap other pieces from the same team and doesn't leave the board
        while ((((previousMove >> 8) << 1) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append((previousMove >> 8) << 1)
            previousMove = (previousMove >> 8) << 1

        previousMove = self.position
        while ((((previousMove << 8) >> 1) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append((previousMove << 8) >> 1)
            previousMove = (previousMove << 8) >> 1

        previousMove = self.position
        while ((((previousMove >> 1 ) >> 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append((previousMove >> 1) >> 8)
            previousMove = (previousMove >> 1) >> 8

        previousMove = self.position
        while ((((previousMove << 1 ) << 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append((previousMove << 1) << 8)
            previousMove = (previousMove << 1) << 8
   
        previousMove = self.position
        while (((previousMove >> 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0):
            moves.append(previousMove >> 8)
            previousMove = previousMove >> 8

        previousMove = self.position
        while (((previousMove << 8 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0):
            moves.append(previousMove << 8)
            previousMove = previousMove << 8

        previousMove = self.position
        while (((previousMove >> 1 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove | EighthColumn) != EighthColumn):
            moves.append(previousMove >> 1)
            previousMove = previousMove >> 1

        previousMove = self.position
        while (((previousMove << 1 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove | FirstColumn) != FirstColumn):
            moves.append(previousMove << 1)
            previousMove = previousMove << 1
        
        return moves

class Knight(Piece):
    Alive = None
    def __init__(self, p, t):
        self.position = p
        self.team = t
        if self.team == 'black':
            self.char = 'N'
        elif self.team == 'white':
            self.char = 'n'
        self.value = 10
        self.possibleMoves = self.generatePossibleMoves()
        

    def generatePossibleMoves(self):
        FirstColumn = 0b1000000010000000100000001000000010000000100000001000000010000000
        SecondColumn = 0b0100000001000000010000000100000001000000010000000100000001000000
        SeventhColumn = 0b0000001000000010000000100000001000000010000000100000001000000010
        EighthColumn = 0b0000000100000001000000010000000100000001000000010000000100000001
        moves = [(self.position >> 16) >> 1,
                 (self.position >> 16) << 1,
                 (self.position << 16) >> 1,
                 (self.position << 16) << 1,
                 (self.position >> 8) >> 2,
                 (self.position >> 8) << 2,
                 (self.position << 8) >> 2,
                 (self.position << 8) << 2]

        if (self.position | FirstColumn) == FirstColumn:
            moves.remove((self.position >> 16) << 1)
            moves.remove((self.position << 16) << 1)
            moves.remove((self.position >> 8) << 2)
            moves.remove((self.position << 8) << 2)
        elif (self.position | SecondColumn) == SecondColumn:
            moves.remove((self.position >> 8) << 2)
            moves.remove((self.position << 8) << 2)
        elif (self.position | SeventhColumn) == SeventhColumn:
            moves.remove((self.position >> 8) >> 2)
            moves.remove((self.position << 8) >> 2)
        elif (self.position | EighthColumn) == EighthColumn:
            moves.remove((self.position >> 16) >> 1)
            moves.remove((self.position << 16) >> 1)
            moves.remove((self.position >> 8) >> 2)
            moves.remove((self.position << 8) >> 2)
                
        for m in moves:
            if (m == 0) or (m > 2**63):
                moves.remove(m)

        return moves

   
# =============================================================================

if __name__ == '__main__':
    color = 0
    port = 50100

    if len(sys.argv) > 1:
        if sys.argv[1] == 'black':
            color = 1
            port = 50200

    bot = MyBot()
    bot.port = port

    bot.start()






