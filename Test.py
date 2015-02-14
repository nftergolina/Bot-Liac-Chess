import time

move = [0b10000000000000000000000000000000000000000000000000000000000000, 0b100000000000000000000000000000000000000000000000]
previousState = {'board': "rnbqkbnrpppppppp................................PPPPPPPPRNBQKBNR", 'who_moves': -1}

newState = {}
newState['who_moves'] = previousState['who_moves']
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
print newState['board']

time.sleep(20)

