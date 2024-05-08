from referee.game import PlayerColor, Action, PlaceAction, Coord, BOARD_N
from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State
from .generation import generate_pieces, generate_states
import math
import random 
import time
class Node:
    def __init__(self, state, parent=None, color: PlayerColor, **referee: dict):
        """
        Initialize a new node in the MCTS tree.

        Args:
            state (State): The state represented by this node.
            parent (Node, optional): The parent node of this node. Defaults to None.
        """

        self.color = color
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0

    def is_fully_expanded(self, curr: State):
        """
        Check if all possible actions from this state have been explored.

        Returns:
            bool: True if fully expanded, False otherwise.
        """
        return len(self.children) == len(generate_pieces(curr, self.color))

    def select_child(self, exploration_param=1.0):
        """
        Select a child node using the UCT formula.

        Args:
            exploration_param (float, optional): Exploration parameter. Defaults to 1.0.

        Returns:
            Node: The selected child node.
        """
        return max(self.children, key=lambda child: child.wins / child.visits + exploration_param * math.sqrt(math.log(self.visits) / child.visits))

    def expand(self):
        """
        Expand the node by adding a new child node with an untried action.

        Returns:
            Node: The newly added child node.
        """
        action = random.choice(self.state.get_legal_actions())
        next_state = self.state.take_action(action)
        child_node = Node(next_state, parent=self)
        self.children.append(child_node)
        return child_node

    def simulate(self):
        """
        Simulate a random playout from this node and return the result.

        Returns:
            int: The result of the playout (+1 for win, 0 for draw, -1 for loss).
        """
        current_state = self.state
        while not current_state.is_terminal():
            action = random.choice(current_state.get_legal_actions())
            current_state = current_state.take_action(action)
        return current_state.get_result()

    def backpropagate(self, result):
        """
        Update the node and its ancestors with the result of the playout.

        Args:
            result (int): The result of the playout (+1 for win, 0 for draw, -1 for loss).
        """
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)
