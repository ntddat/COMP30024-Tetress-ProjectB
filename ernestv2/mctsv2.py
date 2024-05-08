from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
from .generation import generate_pieces, generate_states
import math
import random 
import time

class State:
    # Implement the State class as described in the previous response.

def mcts_search(root_state, num_simulations, exploration_param=1.0):
    """
    Perform Monte Carlo Tree Search to find the best action from the root state.

    Args:
        root_state (State): The root state of the game.
        num_simulations (int): The number of simulations to run.
        exploration_param (float, optional): The exploration parameter for UCT. Defaults to 1.0.

    Returns:
        State: The best next state found by MCTS.
    """
    root_node = Node(root_state)

    for _ in range(num_simulations):
        node = root_node

        # Selection
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.select_child(exploration_param)

        # Expansion
        if not node.is_terminal():
            node = node.expand()

        # Simulation
        result = node.simulate()

        # Backpropagation
        node.backpropagate(result)

    best_child = max(root_node.children, key=lambda child: child.visits)
    return best_child.state

def isFullyExpanded(
        curr: State,
        playerColor : bool      
) -> bool:
    numChildren = len(curr.children)
    numMoves = len(generate_pieces(curr, playerColor))
    return numChildren == numMoves

def selectChild(
        curr: State,
        explorationParamter: int
) -> PlaceAction:
        return max(curr.children, key=lambda child: child.wins / child.visits + explorationParamter * math.sqrt(math.log(curr.visits) / child.visits))

def expansion(
          curr: State,
          playerColor: bool
) -> PlaceAction:
    move = random.choice(generate_pieces(curr, playerColor))
    placePiece
    