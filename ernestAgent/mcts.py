from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
from .generation import generate_pieces, generate_states
import math
import random 
import time

MAX_MOVES = 150
WIN = 1
DRAW = 0
LOSE = -1
CONTINUE = 0
EXPLORATION_PARAMETER = 1.5
TIME_LIMIT = 180
BIG_NUMBER = 10000
NUM_ROLLOUT = 100
# things to do 
# should i change my enemy function to choose the piece that has the least amount of player moves left + num of player blocks cleared. (seems like a good idea)

# i should implement 2 different strategy to the mcts to achieve better efficiency, maybe the first 5 moves could be light playout or even random since the start of the game
# does not matter too much
# maybe instead of 150 rollouts i can do like
# i should change the way i store the moves, i need to store them in self, and the way i update the wins should also be in self.

# function to check if the board has any of either red or blue left

class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.color = None
        self.visits = 0
        self.wins = 0

    def fullyExpanded(self):
        numChildren = len(self.children)
        numMoves = len(generate_pieces(self.state, self.color))
        return numChildren == numMoves
    
    def select_child(self, explorationParameter):
        return max(self.children, key=lambda child: child.wins / child.visits + 
                   explorationParameter * math.sqrt(math.log(self.visits) / child.visits))
    
    def expand(self):
        action = random.choice(generate_pieces(self.state, self.color))
        next_state = place_piece(testingState, action, self.color)
        child_node = Node(next_state, parent=self)
        self.children.append(child_node)
        return child_node


    
def noPlayerColor( 
    curr: State,
    playerColor: bool 
) -> bool:
    if curr.moves <= 2:
        return False
    
    if playerColor:
        for key in curr.board:
            if curr.board[key] == PlayerColor.RED:
                return False
            
    else:
        for key in curr.board:
            if curr.board[key] == PlayerColor.BLUE:
                return False
    
    return True

# the function checks if the game will end either by not generating any more legal moves or no playercolor on the board
def gameEndingCondition(
    curr: State,
    playerColor: bool,
) -> bool:
    if curr.moves == MAX_MOVES or noPlayerColor(curr, playerColor):
        return True
    else:
        return False

# the function checks who is winner if the number of moves hits 150, by checking who has more squares  
def evaluation(
    curr: State,
    playerColor: bool
) -> int:
    numRedSquares = 0
    numBlueSquares = 0
    for square in curr.board:
        if curr.board[square] == PlayerColor.RED:
            numRedSquares += 1
        if curr.board[square] == PlayerColor.BLUE:
            numBlueSquares += 1

    return result(numRedSquares, numBlueSquares, playerColor)

# the function return the number of enemy moves.
def numEnemyAvailMoves(
        curr: State,
        playerColor: bool
) -> int:
    enemyColor = not playerColor
    return len(generate_pieces(curr, enemyColor))
    
# the function returns the result of who wins by checking the number of squares each player have    
def result(
    redSquares: int,
    blueSquares: int,
    playerColor: bool
) -> int:
    
    if playerColor:
        if redSquares > blueSquares:
            return WIN 
        if redSquares < blueSquares:
            return LOSE
        else:
            return DRAW
        
    else:
        if blueSquares > redSquares:
            return WIN 
        if blueSquares < redSquares:
            return LOSE 
        else: 
            return DRAW

def copyState(
        curr: State
) -> State:
    testingState = State(curr.board.copy(), curr.piece, curr.row_filled.copy(), curr.col_filled.copy(), curr.moves)
    return testingState

    def expand(
        curr: State,
        playerColor: bool
    ) -> PlaceAction:
        """
        Expand the node by adding a new child node with an untried action.

        Returns:
            Node: The newly added child node.
        """
        action = random.choice(generate_pieces(curr, PlayerColor))
        #next_state = self.state.take_action(action)
        #placepiece
        child_node = Node(next_state, parent=curr)
        curr.children.append(child_node)
        return child_node
# the function runs the mcts and returns the optimal piece within the time limit
def mcts(
    curr: State,
    playerColor: bool
) -> PlaceAction:
    
    testingState = copyState(curr)
    optimalPiece = None
    optimalPieceScore = 0
    rolloutNum = 250
    numParentPlayouts = 0
    childrenPieces = generate_pieces(testingState, playerColor)
    startTime = time.process_time()

    if curr.moves <= 6:
        return generateStartingMoves(curr, playerColor)
    
    for rollout in range(NUM_ROLLOUT):

        # selection function to select the best child 
        # expand the child 
        # simulate 
        # backprogate




        for piece in childrenPieces:
            # time limit
            currentTime = time.process_time()
            if (currentTime - startTime) >= 3:
                return optimalPiece
            
            # i will place the piece and then start the mcts
            currentPieceScore = 0
            numWins = 0
            # placing a playerMove and then placing a enemyMove before moving to the rollout state
            place_piece(testingState, piece, playerColor)
            outcome = generateAndPlaceEnemyMove(testingState, playerColor)
            if outcome == WIN:
                numWins += 1
                
            # rollout stage
            # set the rollout num and iterating through how many rollouts
            for currentRollOut in range(rolloutNum):
                score = rollout(testingState, playerColor)
                numParentPlayouts += 1

                if score == WIN :
                    numWins += 1

                # calculating the current piece score using the formula 
                currentPieceScore = selection(numWins, rolloutNum, numParentPlayouts)
                # checking if this piece is better than the optimal piece
                if currentPieceScore > optimalPieceScore:
                    optimalPiece = piece 
                    optimalPieceScore = currentPieceScore

        # resetting the state to the original to not contaminate the subsequent rollout.
        testingState = curr

        return optimalPiece

# the function recurse itself till the game ends.
def rollout(
    curr: State,
    playerColor: bool
) -> int:

    #terminating the function condition basically when the game ends
    if gameEndingCondition(curr, playerColor):
            return evaluation(curr, playerColor)
    
    # if there are no more valid enemy move, player wins
    if generateAndPlaceEnemyMove(curr, playerColor) == WIN:
        return WIN

    # there are enemy moves left and enemy placed a move hence continue to the random move. 
    if generateAndPlaceEnemyMove(curr, playerColor) == CONTINUE:
        # continue with the random placement of the player piece.
        simulationMoves = generate_pieces(curr, playerColor)
        numOfSimulationMoves = len(simulationMoves)

        if numOfSimulationMoves == 0:
            return LOSE
        
        randomMoveNumber = random.randint(0,numOfSimulationMoves - 1)
        randomMove = simulationMoves[randomMoveNumber]
        place_piece(curr, randomMove, playerColor)
        return rollout(curr, playerColor)

# this function generates and randomly places an enemy move.
def generateAndPlaceEnemyMove(
    curr: State,
    playerColor: bool
) -> int:
    
    enemyColor = not playerColor

    if (len(generate_pieces(curr, enemyColor)) == 0):
        return WIN

    enemyPiece = generateEnemyMove(curr, enemyColor)
    if enemyPiece == None:
        return WIN
    place_piece(curr, enemyPiece, enemyColor)
    return CONTINUE

# def generateSimpleEnemy(
#     curr: State,
#     enemyColor: bool
# ) -> PlaceAction:   

#     enemiesLegalPieces = generate_pieces(curr, enemyColor)
#     bestMove = None
#     bestScore = 0

#     for enemyMove in enemiesLegalPieces:
#         testingState = copyState(curr)
#         place_piece(testingState, enemyMove, enemyColor)

#         while not gameEndingCondition(testingState, enemyColor):
#             player_move = mcts(testingState, not enemyColor)
#             place_piece(testingState, player_move, not enemyColor)

#             simulationMoves = generate_pieces(testingState, enemyColor)
#             numOfSimulationMoves = len(simulationMoves)
#             if numOfSimulationMoves == 0:
#                 return None
#             randomMoveNumber = random.randint(0,numOfSimulationMoves - 1)
#             randomMove = simulationMoves[randomMoveNumber]
#             place_piece(testingState, randomMove, enemyColor)

#         score = evaluation(testingState, enemyColor)
#         if score > bestScore:
#             bestScore = score
#             bestMove = enemyMove
    
#     return bestMove



# This function is to find a enemy move that is not random but based off the number of moves 
# and blocks the player has left after the move is made, the function will choose the move that leads to the least
# amount of moves left and least amount of player blocks. 
def generateEnemyMove(
        curr: State,
        enemyColor: bool
) -> PlaceAction:
    
    lowestPlayerMoves = BIG_NUMBER
    bestEnemyMove = None
    enemyMoves = generate_pieces(curr, enemyColor)

    if enemyMoves == 0:
        return bestEnemyMove

    testingBoard = copyState(curr)

    for move in enemyMoves:
        place_piece(testingBoard, move, enemyColor)
        numPlayerMoves = len(generate_pieces(testingBoard, not enemyColor))

        if (numPlayerMoves < lowestPlayerMoves):
            bestEnemyMove = move
            lowestPlayerMoves = numPlayerMoves
        # to reset the board 
        testingBoard = curr
    
    return bestEnemyMove

def generateStartingMoves(
        curr: State,
        playerColor: bool
) -> PlaceAction:
    moves = generate_pieces(curr, playerColor)
    numMoves = len(moves)
    chosenPiece = moves[random.randint(0, numMoves - 1)]
    return chosenPiece

def place_piece(
    curr: State,
    piece: PlaceAction,
    playerColor: bool
):
    color = PlayerColor.BLUE
    if playerColor:
        color = PlayerColor.RED
    curr.board.update({piece.c1: color})
    curr.board.update({piece.c2: color})
    curr.board.update({piece.c3: color})
    curr.board.update({piece.c4: color})

    curr.row_filled[piece.c1.r] += 1
    curr.col_filled[piece.c1.c] += 1
    curr.row_filled[piece.c2.r] += 1
    curr.col_filled[piece.c2.c] += 1
    curr.row_filled[piece.c3.r] += 1
    curr.col_filled[piece.c3.c] += 1
    curr.row_filled[piece.c4.r] += 1
    curr.col_filled[piece.c4.c] += 1

    delete_lines(curr)
    curr.moves += 1
    

def delete_lines(state: State):
    delete_entries = []

    # ROWS
    for i in range(0, BOARD_N):
        if state.row_filled[i] == BOARD_N:
            for key in state.board:
                if key.r == i:
                    delete_entries.append(key)
    
    # COLUMNS
    for i in range(0, BOARD_N):
        if state.col_filled[i] == BOARD_N:
            for key in state.board:
                if key.c == i:
                    delete_entries.append(key)
    
    for key in delete_entries:
        if key in state.board:
            state.row_filled[key.r] -= 1
            state.col_filled[key.c] -= 1
            del state.board[key]

# the function calculates the score based on the formula.
def selection(
    numWins: int,
    numPlayouts: int,
    numParentPlayouts: int
) -> float:
     return (numWins / numPlayouts) + EXPLORATION_PARAMETER * (math.sqrt(math.log10(numParentPlayouts))/numPlayouts)

