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
EXPLORATION_PARAMETER = math.sqrt(2)
TIME_LIMIT = 180

# things to do 
# i need to reset the board after placing a piece in my mst. resst it before i return the optimal piece back

# function to check if the board has any of either red or blue left
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

# the function runs the mcts and returns the optimal piece within the time limit
def mcts(
    curr: State,
    playerColor: bool
) -> PlaceAction:
    
    testingState = copyState(curr)
    optimalPiece = None
    optimalPieceScore = 0
    rolloutNum = 150
    numParentPlayouts = 0
    childrenPieces = generate_pieces(testingState, playerColor)
    startTime = time.process_time()

    # iterating all possible pieces generated.
    for piece in childrenPieces:
        # time limit
        currentTime = time.process_time()
        if (currentTime - startTime) >= 3:
            return optimalPiece
        
        # i will place the piece and then start the mcts
        currentPieceScore = 0
        numWins = 0
        place_piece(testingState, piece, playerColor)

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

    return optimalPiece

# the function recurse itself till the game ends.
def rollout(
    curr: State,
    playerColor: bool
) -> int:

    #terminating the function condition basically when the game ends
    if gameEndingCondition(curr, playerColor):
            return evaluation(curr, playerColor)
    
    # very basic move for now to generate and randomly places an enemy move, could be refined later on.
    if generateAndPlaceRandomEnemyMove(curr, playerColor) == CONTINUE:

        # continue with the random placement of the player piece.
        simulationMoves = generate_pieces(curr, playerColor)
        numOfSimulationMoves = len(simulationMoves)
        if numOfSimulationMoves == 0:
            return LOSE
        randomMoveNumber = random.randint(0,numOfSimulationMoves - 1)
        randomMove = simulationMoves[randomMoveNumber]
        place_piece(curr, randomMove, playerColor)
        rollout(curr, playerColor)


# this function generates and randomly places an enemy move.
def generateAndPlaceRandomEnemyMove(
    curr: State,
    playerColor: bool
) -> int:
    
    if playerColor:
        enemyColor = PlayerColor.BLUE
    else:
        enemyColor = PlayerColor.RED

    enemiesLegalPieces = generate_pieces(curr, not playerColor)                                           
    numberOfPieces = len(enemiesLegalPieces)
    if (numberOfPieces == 0):
        return WIN

    chosenPieceNumber = random.randint(0, numberOfPieces - 1)
    enemyPiece = enemiesLegalPieces[chosenPieceNumber]
    place_piece(curr, enemyPiece, enemyColor)
    return CONTINUE


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
