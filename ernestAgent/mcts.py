from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
from .generation import generate_pieces, generate_states

MAX_MOVES = 150

# i need to check the state of the board first, to find all the possible squares i shall do mcts on
# once i have all the possible squares, i will run mcts on all of them 
# store all the value for each square, once all the squares are done , choose the highest value and place action


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
        curr: State
        playerColor: bool
) -> bool:
    if curr.moves == MAX_MOVES & noPlayerColor(curr, playerColor):
        return True
