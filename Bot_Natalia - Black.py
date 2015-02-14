import time
import sys
import random

from base_client import LiacBot

WHITE = 1
BLACK = -1
NONE  = 0

FirstRow      = 0b1111111100000000000000000000000000000000000000000000000000000000
SecondRow     = 0b0000000011111111000000000000000000000000000000000000000000000000
SeventhRow    = 0b0000000000000000000000000000000000000000000000001111111100000000
EighthRow     = 0b0000000000000000000000000000000000000000000000000000000011111111
FirstColumn   = 0b1000000010000000100000001000000010000000100000001000000010000000
SecondColumn  = 0b0100000001000000010000000100000001000000010000000100000001000000
SeventhColumn = 0b0000001000000010000000100000001000000010000000100000001000000010
EighthColumn  = 0b0000000100000001000000010000000100000001000000010000000100000001

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

        self.bestMove = []
        move = []
        self.depth = 1
        value = self.negamax(Node(state, []), self.depth, float('-inf'), float('inf'))
        move = self.translate_move(self.bestMove)
        self.send_move(move[0], move[1])
        
   
    def translate_move(self, move):
        i = 0
        while move[0] > 1:
            move[0] = move[0] >> 1
            i += 1
        ArgFrom = (i//8, 7-(i%8))
        print 'From: ', ArgFrom
        i = 0
        while move[1] > 1:
            move[1] = move[1] >> 1
            i += 1
        ArgTo = (i//8, 7-(i%8))
        print 'To:   ', ArgTo
        self.last_move = [ArgFrom, ArgTo]
        print 'Move sent'
        return [ArgFrom, ArgTo]
    
    
    def negamax(self, root, depth, a, b):
        if depth == 0 or root.value == float('-inf') or root.value == float('inf'):
            return root.value * root.state['who_moves']
        bestValue = float('-inf')
        root.generateChildren()
        for child in root.children:
            val = - self.negamax(child, depth -1, -b, -a)
            if val > bestValue:
                bestValue = val
                if depth == self.depth:
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
    def __init__(self, previousState, move):
        self.children = []
        self.move = []
        self.move.extend(move)
        if move:
            self.state = self.getState(previousState, move)
        else:
            self.state = previousState
        self.board = Board(self.state)
        self.value = self.board.BoardValue
        self.team = self.board.BotTeam

    def generateChildren(self):
        for p in self.board.AllPieces:
            if p.team == self.team:
                for m in p.possibleMoves:
                    self.children.append(Node(self.state, [p.position, m]))
         
    def getState(self, previousState, move):
        newState = {}
        newState['who_moves'] = - previousState['who_moves']
        newState['board'] = []
        for char in previousState['board']:
            newState['board'].append(char)
        i = 0
        while move[0] < 2**63:
            move[0] = move[0] << 1
            i += 1
        movedChar = newState['board'][i]
        newState['board'][i] = '.'
        i = 0
        while move[1] < 2**63:
            move[1] = move[1] << 1
            i += 1
        newState['board'][i] = movedChar
        newState['board'] = ''.join(newState['board'])
        return newState
    
        

    
class Board(object):
    def __init__(self, state):
        self.BotTeam = None
        self.BotEnemy = None
        self.AllPieces = []
        self.OccupiedCells = {}
        self.BoardValue = 0
        self.whitePawnsAlive = 0
        self.blackPawnsAlive = 0 

        self.getBotTeam(state)
        self.getIndividualPositions(state)

        self.OccupiedCells['white'] = 0
        self.OccupiedCells['black'] = 0
        
        for p in self.AllPieces:
            self.OccupiedCells[p.team] += p.position
        
        self.EmptyCells = ~( self.OccupiedCells['white'] | self.OccupiedCells['black'] )

        for p in self.AllPieces:
            p.generatePossibleMoves(self)

        self.getBoardValue()


    def getBotTeam(self, state):
        if state['who_moves'] == WHITE:
            self.BotTeam = 'white'
            self.BotEnemy = 'black'
        else:
            self.BotTeam = 'black'
            self.BotEnemy = 'white'

                
    def getIndividualPositions(self, state):
        bitboardBase = 0b1000000000000000000000000000000000000000000000000000000000000000
        i = 0
        j = 0
        for p in state['board']:
            if p == p.lower():
                team = 'black'
            else:
                team = 'white'
            if p.lower() == 'p':
                self.AllPieces.append(Pawn(bitboardBase, team, self))
                if team == 'white':
                    i += 1
                elif team == 'black':
                    j += 1
            elif p.lower() == 'r':
                self.AllPieces.append(Rook(bitboardBase, team, self))     
            elif p.lower() == 'b':
                self.AllPieces.append(Bishop(bitboardBase, team, self))                
            elif p.lower() == 'q':
                self.AllPieces.append(Queen(bitboardBase, team, self))                
            elif p.lower() == 'n':
                self.AllPieces.append(Knight(bitboardBase, team, self))              
            bitboardBase = bitboardBase >> 1
        self.whitePawnsAlive = i
        self.blackPawnsAlive = j
        

    def getBoardValue(self):
        for p in self.AllPieces:
            if p.team == 'white':
                self.BoardValue += p.value
            elif p.team == 'black':
                self.BoardValue -= p.value
        self.BoardValue -= (self.whitePawnsAlive - 10)**2
        self.BoardValue += (self.blackPawnsAlive - 10)**2
        if self.whitePawnsAlive == 0:
            self.BoardValue = float('-inf')
        elif self.blackPawnsAlive == 0:
            self.BoardValue = float('inf')
            
        

class Piece(object):
    def __init__(self):
        self.position = None
        self.team = None
        self.value = None
        self.possibleMoves = []
        

class Pawn(Piece):
    def __init__(self, p, t, board):
        self.position = p
        self.team = t
        self.getPawnValue()
       
    def getPawnValue(self):
        p = self.position
        i = 0
        if self.team == 'white':
            while p > 1:
                p = p >> 8
                i += 1
            if (self.position & FirstRow) == self.position:
                i = float('inf')
        elif self.team == 'black':
            while p < 2**63:
                p = p << 8
                i += 1
            if (self.position & EighthRow) == self.position:
                i = float('inf')
        self.value = 5*i

    def generatePossibleMoves(self, board):
        moves = []
        if self.team == 'black':
            if ((self.position >> 8) >> 1) | board.OccupiedCells['white'] == board.OccupiedCells['white'] and (self.position & EighthColumn) == 0:
                moves.append((self.position >> 8) >> 1)
            if ((self.position >> 8) << 1) | board.OccupiedCells['white'] == board.OccupiedCells['white'] and (self.position & FirstColumn) == 0:
                moves.append((self.position >> 8) << 1)
            if ((self.position >> 8) & ~board.EmptyCells) == 0:
                moves.append(self.position >> 8)
                if (self.position | SecondRow) == SecondRow and ((self.position >> 16) & ~board.EmptyCells) == 0:
                    moves.append(self.position >> 16)
        elif self.team == 'white':
            if ((self.position << 8) >> 1) | board.OccupiedCells['black'] == board.OccupiedCells['black'] and (self.position & EighthColumn) == 0:
               moves.append((self.position << 8) >> 1)
            if ((self.position << 8) << 1) | board.OccupiedCells['black'] == board.OccupiedCells['black'] and (self.position & FirstColumn) == 0:
                moves.append((self.position << 8) << 1)
            if ((self.position << 8) & ~board.EmptyCells) == 0:
                moves.append(self.position << 8)
                if (self.position | SeventhRow) == SeventhRow and ((self.position << 16) & ~board.EmptyCells) == 0:
                    moves.append(self.position << 16)

        if self.team == 'black' and ((self.position >> 8) & ~board.EmptyCells) == 0:
            moves.append(self.position >> 8)
            if (self.position | SecondRow) == SecondRow and ((self.position >> 16) & ~board.EmptyCells) == 0:
                moves.append(self.position >> 16)
        elif self.team == 'white' and ((self.position << 8) & ~board.EmptyCells) == 0:
            moves.append(self.position << 8)
            if (self.position | SeventhRow) == SeventhRow and ((self.position << 16) & ~board.EmptyCells) == 0:
                moves.append(self.position << 16)
                
        self.possibleMoves = moves
   

class Rook(Piece):
    def __init__(self, p, t, board):
        self.position = p
        self.team = t
        self.value = 15
        
    def generatePossibleMoves(self, board):
         moves = []
         previousMove = self.position
         while (((previousMove >> 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0):
             moves.append(previousMove >> 8)
             previousMove = previousMove >> 8
             if previousMove & board.EmptyCells == 0:
                 break
             
 
         previousMove = self.position
         while (((previousMove << 8 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0):
             moves.append(previousMove << 8)
             previousMove = previousMove << 8
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while (((previousMove >> 1 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove | EighthColumn) != EighthColumn):
             moves.append(previousMove >> 1)
             previousMove = previousMove >> 1
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while (((previousMove << 1 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove | FirstColumn) != FirstColumn):
             moves.append(previousMove << 1)
             previousMove = previousMove << 1
             if previousMove & board.EmptyCells == 0:
                 break
             
         self.possibleMoves = moves


class Bishop(Piece):
    def __init__(self, p, t, board):
        self.position = p
        self.team = t
        self.value = 18
        
    def generatePossibleMoves(self, board):
         moves = []
         previousMove = self.position
         while ((((previousMove >> 8) << 1) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | FirstColumn) != FirstColumn):
             moves.append((previousMove >> 8) << 1)
             previousMove = (previousMove >> 8) << 1
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while ((((previousMove << 8) >> 1) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | EighthColumn) != EighthColumn):
             moves.append((previousMove << 8) >> 1)
             previousMove = (previousMove << 8) >> 1
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while ((((previousMove >> 1 ) >> 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | EighthColumn) != EighthColumn):
             moves.append((previousMove >> 1) >> 8)
             previousMove = (previousMove >> 1) >> 8
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while ((((previousMove << 1 ) << 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | FirstColumn) != FirstColumn):
             moves.append((previousMove << 1) << 8)
             previousMove = (previousMove << 1) << 8
             if previousMove & board.EmptyCells == 0:
                 break
       
         self.possibleMoves = moves
        

class Queen(Piece):
    def __init__(self, p, t, board):
        self.position = p
        self.team = t
        self.value = 25

    def generatePossibleMoves(self, board):
         moves = []
         previousMove = self.position
         while ((((previousMove >> 8) << 1) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | FirstColumn) != FirstColumn):
             moves.append((previousMove >> 8) << 1)
             previousMove = (previousMove >> 8) << 1
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while ((((previousMove << 8) >> 1) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | EighthColumn) != EighthColumn):
             moves.append((previousMove << 8) >> 1)
             previousMove = (previousMove << 8) >> 1
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while ((((previousMove >> 1 ) >> 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0) and ((previousMove | EighthColumn) != EighthColumn):
             moves.append((previousMove >> 1) >> 8)
             previousMove = (previousMove >> 1) >> 8
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while ((((previousMove << 1 ) << 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0) and ((previousMove | FirstColumn) != FirstColumn):
             moves.append((previousMove << 1) << 8)
             previousMove = (previousMove << 1) << 8
             if previousMove & board.EmptyCells == 0:
                 break
    
         previousMove = self.position
         while (((previousMove >> 8) & board.OccupiedCells[self.team]) == 0) and ((previousMove >> 8) > 0):
             moves.append(previousMove >> 8)
             previousMove = previousMove >> 8
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while (((previousMove << 8 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove << 8)%(2**64) != 0):
             moves.append(previousMove << 8)
             previousMove = previousMove << 8
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while (((previousMove >> 1 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove | EighthColumn) != EighthColumn):
             moves.append(previousMove >> 1)
             previousMove = previousMove >> 1
             if previousMove & board.EmptyCells == 0:
                 break
 
         previousMove = self.position
         while (((previousMove << 1 ) & board.OccupiedCells[self.team]) == 0) and ((previousMove | FirstColumn) != FirstColumn):
             moves.append(previousMove << 1)
             previousMove = previousMove << 1
             if previousMove & board.EmptyCells == 0:
                 break
         
         self.possibleMoves = moves

class Knight(Piece):
    def __init__(self, p, t, board):
        self.position = p
        self.team = t
        self.value = 20
        
    def generatePossibleMoves(self, board):
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
            if (m & board.OccupiedCells[self.team]) == 0:
                self.possibleMoves.append(m)


# =============================================================================

if __name__ == '__main__':
    color = 1
    port = 50200

    if len(sys.argv) > 1:
        if sys.argv[1] == 'white':
            color = 0
            port = 50100

    bot = MyBot()
    bot.port = port

    bot.start()

