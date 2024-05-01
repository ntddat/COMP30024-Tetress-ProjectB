from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
from .generation import generate_pieces, generate_states
import math
import random 

MAX_MOVES = 150
WIN = 1
DRAW = 0
LOSE = -1
EXPLORATION_PARAMETER = math.sqrt(2)

# things to do 
# i need to implement the scoring function based on the formula in google 
# i need store the number of wins/playouts for each piece and store them and return 
# the piece with the best value based on the function. That will ne the optimal piece to place


# checking if there is any red/blue square in the board, if there is not red square in the board and it is red turn, 
# the function will return true. 

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

def gameEndingCondition(
    curr: State,
    playerColor: bool,
) -> bool:
    if curr.moves == MAX_MOVES or noPlayerColor(curr, playerColor):
        return True
    else:
        return False
    
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

def numEnemyAvailMoves(
        curr: State,
        playerColor: bool
) -> int:
    enemyColor = not playerColor
    return len(generate_pieces(curr.board, enemyColor))
    
    
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

def mcts(
    curr: State,
    playerColor: bool
) -> PlaceAction:
    
    optimalPiece = None
    optimalPieceScore = 0
    rolloutNum = 50
    numParentPlayouts = 0
    childrenPieces = generate_pieces(curr.board, playerColor)

    for piece in childrenPieces:
        currentPieceScore = 0
        numWins = 0
        place_piece(curr.board,piece, playerColor)

        for currentRollOut in range(rolloutNum):
            score = rollout(curr.board, playerColor)
            numParentPlayouts += 1
            if score == 1 :
                numWins += 1
        
        currentPieceScore = selection(numWins, rolloutNum, numParentPlayouts)
        if currentPieceScore > optimalPieceScore:
            optimalPiece = piece 
            optimalPieceScore = currentPieceScore

    
    return optimalPiece


def rollout(
    curr: State,
    playerColor: bool
) -> int:

    if gameEndingCondition(curr.board, playerColor):
            return evaluation(curr.board, playerColor)
    
    if generateAndPlaceRandomEnemyMove(curr.board, playerColor) != 1:

        simulationMoves = generate_pieces(curr.board, playerColor)
        numOfSimulationMoves = len(simulationMoves)
        if numOfSimulationMoves == 0:
            return LOSE
        randomMoveNumber = random.randit(0,numOfSimulationMoves)
        randomMove = simulationMoves[randomMoveNumber]
        place_piece(curr.board, randomMove, playerColor)
        rollout(curr.board, playerColor)


def generateAndPlaceRandomEnemyMove(
    curr: State,
    playerColor: bool
):
    
    gameContinues = 0
    if playerColor:
        enemyColor = PlayerColor.BLUE
    else:
        enemyColor = PlayerColor.RED

    enemiesLegalPieces = generate_pieces(curr.board, not playerColor)                                           
    numberOfPieces = len(enemiesLegalPieces)
    if (numberOfPieces == 0):
        return WIN

    chosenPieceNumber = random.randint(0, numberOfPieces)
    enemyPiece = enemiesLegalPieces[chosenPieceNumber]
    place_piece(curr.board, enemyPiece, enemyColor)
    return gameContinues

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

def selection(
    numWins: int,
    numPlayouts: int,
    numParentPlayouts: int
) -> float 
     return (numWins / numPlayouts) + EXPLORATION_PARAMETER * (math.sqrt(math.log10(numParentPlayouts))/numPlayouts)
