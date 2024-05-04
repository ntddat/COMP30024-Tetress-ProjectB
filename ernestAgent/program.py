# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import PlayerColor, Action, PlaceAction, Coord, BOARD_N
from .generation import generate_states, create_state
from .utils import render_board
from .state import State
from .mcts import mcts

class Agent:
    """
    This class is the "entry point" for your agent, providing an interface to
    respond to various Tetress game events.
    """

    def __init__(self, color: PlayerColor, **referee: dict):
        """
        This constructor method runs when the referee instantiates the agent.
        Any setup and/or precomputation should be done here.
        """
        board: dict[Coord, PlayerColor] = {}
        self._state = State(board, None, [0]*BOARD_N, [0]*BOARD_N, 0)
        self._color = color
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

        # Below we have hardcoded two actions to be played depending on whether
        # the agent is playing as BLUE or RED. Obviously this won't work beyond
        # the initial moves of the game, so you should use some game playing
        # technique(s) to determine the best action to take.
        print(self._state.board)

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
        
        # representing the playerColor red as true
        playerColor = True
        if self._color == PlayerColor.BLUE:
            playerColor = False

        # representing the board
        # the row would print out the number of filled squares in a list same for column 
        print("BOARD:")
        print(render_board(self._state.board, True))
        print("ROW:")
        print(self._state.row_filled)
        print("COL:")
        print(self._state.col_filled)

        return mcts(self._state,playerColor)



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
        playerColor = True
        if color == PlayerColor.BLUE:
            playerColor = False
        self._state = create_state(self._state, place_action, playerColor)
