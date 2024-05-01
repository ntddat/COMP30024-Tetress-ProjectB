# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord, BOARD_N
from .state import State
from .generation import generate_states, create_state
from .algorithm import Search
from .utils import render_board
import copy
import cProfile

VERY_BIG_NUMBER = 100000
VERY_SMALL_NUMBER = -100000

"""
Plan:
Minimax with Alpha-Beta Pruning
State representation: 
- As of now can just use Part A's, but can change later (especially stuff to do with move generation)
- Also can add an array to store number of squares filled in each row/column, to help with line deletion
- Can maybe use bitboards hmmm ?
Optimizations:
- Quiescence search for moves that delete lines
- Transposition table
- Move ordering (not sure how to do this yet tho)
- Iterative deepening maybe
- Neural networks
"""

"""
Maybe just do MCTS lmao
Make a random agent to fight
"""

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.

    *** AGENT v3: 
    MINIMAX with ALPHA-BETA PRUNING
    ITERATIVE DEEPENING
    (implementing: TRANSPOSITION TABLE using ZOBRIST KEY HASHING)
    TIME LIMIT ON EACH MOVE ***

    """

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        self._color = color
        board: dict[Coord, PlayerColor] = {}
        self._state = State(board, None, [0]*BOARD_N, [0]*BOARD_N, 0)
        self._search = Search()
        match color:
            case PlayerColor.RED:
                print("Testing: I am playing as RED")
            case PlayerColor.BLUE:
                print("Testing: I am playing as BLUE")

    def action(self, **referee: dict) -> Action:
        """
        This method is called by the referee each time it is the agent's turn
        to take an action. It must always return an action object. 

        """


        if self._state.moves == 0:
            return PlaceAction(
                Coord(3, 3), 
                Coord(3, 4), 
                Coord(4, 3), 
                Coord(4, 4)
            )
        
        if self._state.moves == 1:
            return PlaceAction(
                Coord(2, 3), 
                Coord(2, 4), 
                Coord(2, 5), 
                Coord(2, 6)
            )
        """
        if self._state.moves == 2:
            return PlaceAction(
                Coord(3, 1), 
                Coord(3, 2), 
                Coord(2, 2), 
                Coord(3, 0)
            )

        if self._state.moves == 3:
            return PlaceAction(
                Coord(1, 5), 
                Coord(1, 4), 
                Coord(0, 4), 
                Coord(1, 3)
            )
        if self._state.moves == 4:
            return PlaceAction(
                Coord(3, 6), 
                Coord(3, 7), 
                Coord(3, 8), 
                Coord(3, 9)
            )
        """
        """
        if self._state.moves == 10:
            return
        """
        print("BOARD:")
        print(render_board(self._state.board, True))
        print("ROW:")
        print(self._state.row_filled)
        print("COL:")
        print(self._state.col_filled)
        """
        next_states = generate_states(self._state, maxPlayer)
        print(len(next_states))
        state_values = dict()
        for state in next_states:
            state_values[state.piece] = minimax(state, 0, VERY_SMALL_NUMBER, VERY_BIG_NUMBER, maxPlayer)
        """
        x, y = self._search.iterativeDeepening(self._state, self._color)
        print("TIME REMAINING:")
        print(referee["time_remaining"])
        print("EVALUATION:")
        print(x)
        return y
        
        if self._color == PlayerColor.RED:
            state_values = {k: v for k, v in sorted(state_values.items(), key=lambda item: item[1])}
        else:
            state_values = {k: v for k, v in sorted(state_values.items(), key=lambda item: item[1], reverse=True)}
        print("Testing: RED is playing a PLACE action")
        print("EVAL:")
        print(state_values[next(iter(state_values))])
        return next(iter(state_values))


        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        match self._color:
            case PlayerColor.RED:
                print("Testing: RED is playing a PLACE action")
                return PlaceAction(
                    Coord(3, 3), 
                    Coord(3, 4), 
                    Coord(4, 3), 
                    Coord(4, 4)
                )
            case PlayerColor.BLUE:
                print("Testing: BLUE is playing a PLACE action")
                return PlaceAction(
                    Coord(2, 3), 
                    Coord(2, 4), 
                    Coord(2, 5), 
                    Coord(2, 6)
                )

    def update(self, color: PlayerColor, action: Action, **referee: dict):
        """
        This method is called by the referee after an agent has taken their
        turn. You should use it to update the agent's internal game state. 
        """

        # There is only one action type, PlaceAction
        place_action: PlaceAction = action
        c1, c2, c3, c4 = place_action.coords

        # Here we are just printing out the PlaceAction coordinates for
        # demonstration purposes. You should replace this with your own logic
        # to update your agent's internal game state representation.
        print(f"Testing: {color} played PLACE action: {c1}, {c2}, {c3}, {c4}")
        maxPlayer = True
        if color == PlayerColor.BLUE:
            maxPlayer = False
        self._state = create_state(self._state, place_action, maxPlayer)