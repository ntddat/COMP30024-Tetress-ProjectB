from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
from .generation import generate_pieces, copyState, create_state
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
SMALL_NUMBER = -10000
NUM_ROLLOUT = 50
TIME_PER_MOVE = 2
# things to do 
# should i change my enemy function to choose the piece that has the least amount of player moves left + num of player blocks cleared. (seems like a good idea)

# i should implement 2 different strategy to the mcts to achieve better efficiency, maybe the first 5 moves could be light playout or even random since the start of the game
# does not matter too much
# maybe instead of 150 rollouts i can do like
# i should change the way i store the moves, i need to store them in self, and the way i update the wins should also be in self.

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
    playerColor: bool
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

def availableMoves(
        curr: State,
        playerColor: bool
) -> bool:
    if (generate_pieces(curr, playerColor) == 0):
        return True
    else:
        return False


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

    # def expand(
    #     curr: State,
    #     playerColor: bool
    # ) -> PlaceAction:
    #     """
    #     Expand the node by adding a new child node with an untried action.

    #     Returns:
    #         Node: The newly added child node.
    #     """
    #     action = random.choice(generate_pieces(curr, PlayerColor))
    #     #next_state = self.state.take_action(action)
    #     #placepiece
    #     child_node = Node(next_state, parent=curr)
    #     curr.children.append(child_node)
    #     return child_node
# the function runs the mcts and returns the optimal piece within the time limit
def mcts(
    curr: State,
    playerColor: bool
) -> PlaceAction:

    if curr.moves <= 6:
        return generateStartingMoves(curr, playerColor)
    
    testingState = copyState(curr)
    rootState = copyState(curr)

    for rollout in range(NUM_ROLLOUT):

        start_time = time.process_time()

        # if time.process_time() - start_time < TIME_PER_MOVE:
        #     return

        if not gameEndingCondition(testingState, playerColor) and not fullyExpanded(testingState):

            while (len(testingState.children) > 0):

                testingState = select_child(testingState, EXPLORATION_PARAMETER)

        playerMoves = generate_pieces(testingState, playerColor)

        if not (gameEndingCondition(testingState, playerColor)) and len(playerMoves) != 0:

            testingStateChild = expand(testingState, rootState, playerColor, playerMoves)

            result = simulate(testingStateChild, playerColor)

            backpropagate(testingStateChild, rootState, result)
        
        # to reset the state back to the original state before the next iteration.
        testingState = copyState(curr)

    # selecting the child with the most visits
    bestChild = None
    bestChildVisits = 0
    if len(rootState.children) == 0:
        return None
    for child in rootState.children:

        currentChildVisits = child.visits

        if currentChildVisits > bestChildVisits:

            bestChildVisits= currentChildVisits
            bestChild = copyState(child)

    return bestChild.piece

def bestChildPiece(
        rootState : State
) -> PlaceAction:
    bestChildPiece = None
    bestChildVisits = 0
    if len(rootState.children) == 0:
        return None 
    for child in rootState.children:
        currentChildVisit = child.visits
        if currentChildVisit > bestChildVisits:
            bestChild = copyState(child)
            bestChildVisits = currentChildVisit
    return bestChild.piece
#function to generate the first few starting moves
def generateStartingMoves(
    curr: State,
    playerColor: bool
) -> PlaceAction:
    moves = generate_pieces(curr, playerColor)
    numMoves = len(moves)
    chosenPiece = moves[random.randint(0, numMoves - 1)]
    return chosenPiece

#function to check if the current state has checked all it possible moves
def fullyExpanded(
    curr: State
) -> bool:
    numChildren = len(curr.children)
    numMoves = len(generate_pieces(curr, curr.color))
    return numChildren == numMoves

#function to the select the child to explore
def select_child(
    curr: State,
    explorationParameter: int
    ) -> State:

    bestChild = None
    bestChildScore = SMALL_NUMBER

    for child in curr.children:
        currentChildScore = calculate_ucb(child, explorationParameter)

        if currentChildScore > bestChildScore:
            bestChild = copyState(child)
            bestChildScore = currentChildScore

    return bestChild

# function to explore deeper for the current state
def expand(
    curr:State,
    root:State,
    playerColor: bool,
    playerMoves = [PlaceAction]
) -> State:
    
    action = random.choice(playerMoves)
    child_state = create_state(curr, action, playerColor)
    root.children.append(child_state)

    return child_state

# function to playout the game till it reaches the terminal state and achieve a result
def simulate(
        curr:State,
        playerColor: bool
) -> int:

    if terminal(curr):
        return evaluation(curr, playerColor)

    action = random.choice(generate_pieces(curr, playerColor))
    place_piece(curr, action, playerColor)
    enemyAction = generateRandomEnemyMove(curr, not playerColor)

    if enemyAction == None:
        return WIN
    
    place_piece(curr, action, not playerColor)
    return simulate(curr, playerColor)

# function to update all the states before the terminal state of its result
def backpropagate(
        curr: State,
        root: State,
        result: int
):
    if curr in root.children:
        for child in root.children:
            if curr == child:
                child.visits += 1
                if result == WIN:
                    child.wins += 1

    curr.visits += 1
    if result == WIN:
        curr.wins += 1
    if curr.parent != None:
        backpropagate(curr.parent, result)

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

#function checks if the number of moves is within the limit of 150
def movesLimit(
    curr:State
) -> bool:
    if curr.moves == MAX_MOVES:
        return True
    else:
        return False

def numPlayerMoves(
        curr:State
) -> bool:
    return len(generate_pieces(curr, curr.color))

# function checks if the state is terminal   
def terminal(
        curr:State
) -> bool:

    if movesLimit(curr) or numPlayerMoves(curr) == 0:
        return True
    else:
        return False
# function evaluates whether who wins
def evaluation(
        curr:State,
        playerColor:bool
) -> int:
    # if the game stops due to max moves reached
    if curr.moves == 150:
        numPlayerBlocks = 0
        numEnemyBlocks = 0

        for square in curr.board:
            if curr.color == PlayerColor.RED:
                if curr.board[square] == PlayerColor.RED:
                    numPlayerBlocks += 1
                if curr.board[square] == PlayerColor.BLUE:
                    numEnemyBlocks += 1
            else:
                if curr.board[square] == PlayerColor.BLUE:
                    numPlayerBlocks += 1
                if curr.board[square] == PlayerColor.RED:
                    numEnemyBlocks += 1

        if numPlayerBlocks > numEnemyBlocks:
            return WIN 
        elif numPlayerBlocks < numEnemyBlocks:
            return LOSE
        else:
            return DRAW
        
    # if the game ends due to one player not having any more legal moves.
    else:
        if (len(generate_pieces(curr, playerColor)) == 0):
            return LOSE
        else:
            return WIN 

def generateRandomEnemyMove(
        curr: State,
        enemyColor: bool
) -> PlaceAction:
    moves = generate_pieces(curr, enemyColor)
    if len(moves) == 0:
        return None
    else:
        return random.choice(moves)
# the function generates a enemy move
def generateEnemyMove(
        curr: State,
) -> PlaceAction:
    
    lowestPlayerMoves = BIG_NUMBER
    bestEnemyMove = None
    enemyColor = not curr.color
    enemyMoves = generate_pieces(curr, enemyColor)

    if enemyMoves == 0:
        return bestEnemyMove

    currentState = copyState(curr)

    for move in enemyMoves:
        place_piece(currentState, move, enemyColor)
        numPlayerMoves = len(generate_pieces(currentState, not enemyColor))

        if (numPlayerMoves < lowestPlayerMoves):
            bestEnemyMove = move
            lowestPlayerMoves = numPlayerMoves
        # to reset the board 
        currentState = copyState(curr)
    
    return bestEnemyMove

def calculate_ucb(self, exploration_parameter):    
    exploitation = self.wins / self.visits
    exploration = exploration_parameter * math.sqrt(math.log(self.parent.visits) / self.visits)
    ucb_score = exploitation + exploration
    return ucb_score


#         for piece in childrenPieces:
#             # time limit
#             currentTime = time.process_time()
#             if (currentTime - startTime) >= 3:
#                 return optimalPiece
            
#             # i will place the piece and then start the mcts
#             currentPieceScore = 0
#             numWins = 0
#             # placing a playerMove and then placing a enemyMove before moving to the rollout state
#             place_piece(testingState, piece, playerColor)
#             outcome = generateAndPlaceEnemyMove(testingState, playerColor)
#             if outcome == WIN:
#                 numWins += 1
                
#             # rollout stage
#             # set the rollout num and iterating through how many rollouts
#             for currentRollOut in range(rolloutNum):
#                 score = rollout(testingState, playerColor)
#                 numParentPlayouts += 1

#                 if score == WIN :
#                     numWins += 1

#                 # calculating the current piece score using the formula 
#                 currentPieceScore = selection(numWins, rolloutNum, numParentPlayouts)
#                 # checking if this piece is better than the optimal piece
#                 if currentPieceScore > optimalPieceScore:
#                     optimalPiece = piece 
#                     optimalPieceScore = currentPieceScore

#         # resetting the state to the original to not contaminate the subsequent rollout.
#         testingState = curr

#         return optimalPiece

# # the function recurse itself till the game ends.
# def rollout(
#     curr: State,
#     playerColor: bool
# ) -> int:

#     #terminating the function condition basically when the game ends
#     if gameEndingCondition(curr, playerColor):
#             return evaluation(curr, playerColor)
    
#     # if there are no more valid enemy move, player wins
#     if generateAndPlaceEnemyMove(curr, playerColor) == WIN:
#         return WIN

#     # there are enemy moves left and enemy placed a move hence continue to the random move. 
#     if generateAndPlaceEnemyMove(curr, playerColor) == CONTINUE:
#         # continue with the random placement of the player piece.
#         simulationMoves = generate_pieces(curr, playerColor)
#         numOfSimulationMoves = len(simulationMoves)

#         if numOfSimulationMoves == 0:
#             return LOSE
        
#         randomMoveNumber = random.randint(0,numOfSimulationMoves - 1)
#         randomMove = simulationMoves[randomMoveNumber]
#         place_piece(curr, randomMove, playerColor)
#         return rollout(curr, playerColor)

# # this function generates and randomly places an enemy move.
# def generateAndPlaceEnemyMove(
#     curr: State,
#     playerColor: bool
# ) -> int:
    
#     enemyColor = not playerColor

#     if (len(generate_pieces(curr, enemyColor)) == 0):
#         return WIN

#     enemyPiece = generateEnemyMove(curr, enemyColor)
#     if enemyPiece == None:
#         return WIN
#     place_piece(curr, enemyPiece, enemyColor)
#     return CONTINUE

# # def generateSimpleEnemy(
# #     curr: State,
# #     enemyColor: bool
# # ) -> PlaceAction:   

# #     enemiesLegalPieces = generate_pieces(curr, enemyColor)
# #     bestMove = None
# #     bestScore = 0

# #     for enemyMove in enemiesLegalPieces:
# #         testingState = copyState(curr)
# #         place_piece(testingState, enemyMove, enemyColor)

# #         while not gameEndingCondition(testingState, enemyColor):
# #             player_move = mcts(testingState, not enemyColor)
# #             place_piece(testingState, player_move, not enemyColor)

# #             simulationMoves = generate_pieces(testingState, enemyColor)
# #             numOfSimulationMoves = len(simulationMoves)
# #             if numOfSimulationMoves == 0:
# #                 return None
# #             randomMoveNumber = random.randint(0,numOfSimulationMoves - 1)
# #             randomMove = simulationMoves[randomMoveNumber]
# #             place_piece(testingState, randomMove, enemyColor)

# #         score = evaluation(testingState, enemyColor)
# #         if score > bestScore:
# #             bestScore = score
# #             bestMove = enemyMove
    
# #     return bestMove



# # This function is to find a enemy move that is not random but based off the number of moves 
# # and blocks the player has left after the move is made, the function will choose the move that leads to the least
# # amount of moves left and least amount of player blocks. 
# def generateEnemyMove(
#         curr: State,
#         enemyColor: bool
# ) -> PlaceAction:
    
#     lowestPlayerMoves = BIG_NUMBER
#     bestEnemyMove = None
#     enemyMoves = generate_pieces(curr, enemyColor)

#     if enemyMoves == 0:
#         return bestEnemyMove

#     testingBoard = copyState(curr)

#     for move in enemyMoves:
#         place_piece(testingBoard, move, enemyColor)
#         numPlayerMoves = len(generate_pieces(testingBoard, not enemyColor))

#         if (numPlayerMoves < lowestPlayerMoves):
#             bestEnemyMove = move
#             lowestPlayerMoves = numPlayerMoves
#         # to reset the board 
#         testingBoard = curr
    
#     return bestEnemyMove

# # the function calculates the score based on the formula.
# def selection(
#     numWins: int,
#     numPlayouts: int,
#     numParentPlayouts: int
# ) -> float:
#      return (numWins / numPlayouts) + EXPLORATION_PARAMETER * (math.sqrt(math.log10(numParentPlayouts))/numPlayouts)

