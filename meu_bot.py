import time
import sys
import random

from base_client import LiacBot

WHITE = 1
BLACK = -1
NONE = 0

# BOT =========================================================================
class MyBot(LiacBot):
    name = 'Random Bot'

    def __init__(self):
        super(RandomBot, self).__init__()
        self.last_move = None

    def on_move(self, state):
        print 'Generating a move...'
        board = Board(state)
        moveList = []
        for piece in Board.AllPieces:
            for moveAux in piece.possibleMoves:
                if piece.team == sys.argv[1]:
                    moveList.append([piece.char, piece.position, moveAux])

        move = random.choice(moveList)
        i = 0
        while move[1] < 2**63:
            move[1] = move[1] << 1

        ArgFrom = (i//8, i%8)

        i = 0
        while move[2] < 2**63:
            move[2] = move[2] << 1

        ArgTo = (i//8, i%8)

        self.send_move(ArgFrom, ArgTo)
        

        
            
        
        # EVALUATE each possible move and it's possible responses
        '''
        for pieceType in Board.AllPieces:
            for piece in pieceType:
                for move in piece.possibleMoves:
                    if (move || Board.EmptyCells) == Board.EmptyCells:
                        moveValue = 0 # continuar daqui
        '''
                
        

        if state['bad_move']:
            print state['board']
            raw_input()



    def on_game_over(self, state):
        print 'Game Over.'
        # sys.exit()
# =============================================================================

# MODELS ======================================================================
class Board(object):
    AllPieces = []
    WhitePieces = {}
    BlackPieces = {}
    Pawns = []
    Rooks = []
    Bishops = []
    Queens = []
    Knights = []
    OccupiedCells = {}
    EmptyCells  = None
    
    def __init__(state):
        Board.WhitePieces['Pawns'] = getGeneralPosition(state, 'P')
        Board.WhitePieces['Rooks'] = getGeneralPosition(state, 'R')
        Board.WhitePieces['Bishop'] = getGeneralPosition(state, 'B')
        Board.WhitePieces['Queen'] = getGeneralPosition(state, 'Q')
        Board.WhitePieces['Knight'] = getGeneralPosition(state, 'N')

        Board.BlackPieces['Pawns'] = getGeneralPosition(state, 'p')
        Board.BlackPieces['Rooks'] = getGeneralPosition(state, 'r')
        Board.BlackPieces['Bishop'] = getGeneralPosition(state, 'b')
        Board.BlackPieces['Queen'] = getGeneralPosition(state, 'q')
        Board.BlackPieces['Knight'] = getGeneralPosition(state, 'n')

        Board.OccupiedCells['white'] = Board.WhitePieces['Pawns'] | Board.WhitePieces['Rooks'] | Board.WhitePieces['Bishop'] | Board.WhitePieces['Queen'] | Board.WhitePieces['Knight']
        Board.OccupiedCells['black'] = Board.EmptyCells | Board.BlackPieces['Pawns'] | Board.BlackPieces['Rooks'] | Board.BlackPieces['Bishop'] | Board.BlackPieces['Queen'] | Board.BlackPieces['Knight']
        Board.EmptyCells = ~( Board.OccupiedCells['white'] | Board.OccupiedCells['black'] )

        getIndividualPositions(state)

        Board.AllPieces = [Pawns, Rooks, Bishops, Queens, Knights]

    def getGeneralPosition(state, pieceCode):
        i = 0
        bitboardBase = 0b1000000000000000000000000000000000000000000000000000000000000000 
        for piece in state['board']:
            if piece == pieceCode: 
                bitboard += bitboardBase >> i
            i += 1
        return bitboard
                
    def getIndividualPositions(state):
        i, j, k, l, m, n = 0
        bitboardBase = 0b1000000000000000000000000000000000000000000000000000000000000000
        for piece in state['board']:
            if piece == piece.lower():
                team = 'black'
            else:
                team = 'white'
            if piece.lower() == 'p':
                Board.Pawns[j] = Pawn(bitboardBase >> i, team)
                j += 1
            elif piece.lower() == 'r':
                Board.Rooks[k] = Rook(bitboardBase >> i, team)
                k += 1
            elif piece.lower() == 'b':
                Board.Bishops[l] = Bishop(bitboardBase >> i, team)
                l += 1
            elif piece.lower() == 'q':
                Board.Queens[m] = Queen(bitboardBase >> i, team)
                m += 1
            elif piece.lower() == 'n':
                Board.Knights[n] = Knight(bitboardBase >> i, team)
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
    def __init__(self, p, t):
        self.position = p
        self.team = t
        if self.team == 'black':
            self.char = 'p'
            i = 0
            aux = self.position
            while aux != 2**64:
                aux << 1
                i += 1
            self.value = i*i
        elif self.team == 'white':
            self.char = 'P'
            i = 0
            aux = self.position
            while aux != 0:
                aux >> 1
                i += 1
            self.value = i*i      
        self.possibleMoves = self.generatePossibleMoves(self)
        
    def generatePossibleMoves(self):
        SecondRow  = 0b0000000010000000000000000000000000000000000000000000000000000000
        ThirdRow  = 0b0000000000000000100000000000000000000000000000000000000000000000

        SeventhRow  = 0b0000000000000000000000000000000000000000000000001000000000000000
        EighthRow  = 0b0000000000000000000000000000000000000000000000000000000010000000

        if self.team == 'white':
            moves = [(self.position >> 8) & ~Board.OccupiedCells['white']]
            if (self.position >= SecondRow) and (self.position < ThirdRow):
                moves.append((self.position >> 16) & ~Board.OccupiedCells['white'])
        elif self.team == 'black':
            moves = [(self.position << 8) & ~Board.OccupiedCells['black']]
            if (self.position >= SeventhRow) and (self.position < EighthRow):
                moves.append((self.position << 16) & ~Board.OccupiedCells['black'])
                
        return moves
   

class Rook(Piece):
    Alive = None
    def __init__(self, p, t):
        self.position = p
        self.team = t
        if self.team == 'black':
            self.char = 'r'
        elif self.team == 'white':
            self.char = 'R'
        self.value = 10
        self.possibleMoves = self.generatePossibleMoves(self)
        

    def generatePossibleMoves(self):
        FirstColumn = 0b1000000010000000100000001000000010000000100000001000000010000000
        EighthColumn = 0b0000000100000001000000010000000100000001000000010000000100000001  
        moves = []
        previousMove = self.position
        # while the move doesn't overlap other pieces from the same team and doesn't leave the board
        while (((previousMove >> 8) and Board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) != 0):
            moves.append(previousMove >> 8)

        previousMove = self.position
        while (((previousMove << 8 ) and Board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0):
            moves.append(previousMove << 8)

        previousMove = self.position
        while (((previousMove >> 1 ) and Board.OccupiedCells[self.team]) == 0) and ((previousMove or EighthColumn) != EighthColumn):
            moves.append(previousMove >> 1)

        previousMove = self.position
        while (((previousMove << 1 ) and Board.OccupiedCells[self.team]) == 0) and ((previousMove or FirstColumn) != FirstColumn):
            moves.append(previousMove << 1)
     
        return moves


class Bishop(Piece):
    Alive = None
    def __init__(self, p, t):
        self.position = p
        self.team = t
        if self.team == 'black':
            self.char = 'b'
        elif self.team == 'white':
            self.char = 'B'
        self.value = 12
        self.possibleMoves = self.generatePossibleMoves(self)
        

    def generatePossibleMoves(self):
        FirstColumn = 0b1000000010000000100000001000000010000000100000001000000010000000
        EighthColumn = 0b0000000100000001000000010000000100000001000000010000000100000001
        moves = []
        previousMove = self.position
        # while the move doesn't overlap other pieces from the same team and doesn't leave the board
        while ((((previousMove >> 8) << 1) and Board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) != 0) and ((previousMove or FirstColumn) != FirstColumn):
            moves.append((previousMove >> 8) << 1)

        previousMove = self.position
        while ((((previousMove << 8) >> 1) and Board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove or EighthColumn) != EighthColumn):
            moves.append((previousMove << 8) >> 1)

        previousMove = self.position
        while ((((previousMove >> 1 ) >> 8) and Board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) != 0) and ((previousMove or EighthColumn) != EighthColumn):
            moves.append((previousMove >> 1) >> 8)

        previousMove = self.position
        while ((((previousMove << 1 ) << 8) and Board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove or FIrstColumn) != FirstColumn):
            moves.append((previousMove << 1) << 8)
      
        return moves

class Queen(Piece):
    Alive = None
    def __init__(self, p, t):
        self.position = p
        self.team = t
        if self.team == 'black':
            self.char = 'q'
        elif self.team == 'white':
            self.char = 'Q'
        self.value = 20
        self.possibleMoves = self.generatePossibleMoves(self)
        

    def generatePossibleMoves(self):
        FirstColumn = 0b1000000010000000100000001000000010000000100000001000000010000000
        EighthColumn = 0b0000000100000001000000010000000100000001000000010000000100000001
        moves = []
        previousMove = self.position
        # while the move doesn't overlap other pieces from the same team and doesn't leave the board
        while ((((previousMove >> 8) << 1) and Board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) != 0) and ((previousMove or FirstColumn) != FirstColumn):
            moves.append((previousMove >> 8) << 1)

        previousMove = self.position
        while ((((previousMove << 8) >> 1) and Board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove or EighthColumn) != EighthColumn):
            moves.append((previousMove << 8) >> 1)

        previousMove = self.position
        while ((((previousMove >> 1 ) >> 8) and Board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) != 0) and ((previousMove or EighthColumn) != EighthColumn):
            moves.append((previousMove >> 1) >> 8)

        previousMove = self.position
        while ((((previousMove << 1 ) << 8) and Board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove or FirstColumn) != FirstColumn):
            moves.append((previousMove << 1) << 8)
   
        previousMove = self.position
        while (((previousMove >> 8) and Board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) != 0):
            moves.append(previousMove >> 8)

        previousMove = self.position
        while (((previousMove << 8 ) and Board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0):
            moves.append(previousMove << 8)

        previousMove = self.position
        while (((previousMove >> 1 ) and Board.OccupiedCells[self.team]) == 0) and ((previousMove or EighthColumn) != EighthColumn):
            moves.append(previousMove >> 1)

        previousMove = self.position
        while (((previousMove << 1 ) and Board.OccupiedCells[self.team]) == 0) and ((previousMove or FirstColumn) != FirstColumn):
            moves.append(previousMove << 1)
        
        return moves

class Knight(Piece):
    Alive = None
    def __init__(self, p, t):
        self.position = p
        self.team = t
        if self.team == 'black':
            self.char = 'n'
        elif self.team == 'white':
            self.char = 'N'
        self.value = 10
        self.possibleMoves = self.generatePossibleMoves(self)
        

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

        if (self.position or FirstColumn) == FirstColumn:
            moves.remove((self.position >> 16) << 1)
            moves.remove((self.position << 16) << 1)
            moves.remove((self.position >> 8) << 2)
            moves.remove((self.position << 8) << 2)
        elif (self.position or SecondColumn) == SecondColumn:
            moves.remove((self.position >> 8) << 2)
            moves.remove((self.position << 8) << 2)
        elif (self.position or SeventhColumn) == SeventhColumn:
            moves.remove((self.position >> 8) >> 2)
            moves.remove((self.position << 8) >> 2)
        elif (self.position or EighthColumn) == EighthColumn:
            moves.remove((self.position >> 16) >> 1)
            moves.remove((self.position << 16) >> 1)
            moves.remove((self.position >> 8) >> 2)
            moves.remove((self.position << 8) >> 2)
                
        for m in moves:
            if (m == 0) or (m >= 2**64):
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

    bot = RandomBot()
    bot.port = port

    bot.start()






