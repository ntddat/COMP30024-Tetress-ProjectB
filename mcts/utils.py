# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Single Player Tetress

from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction
from .state import State

def apply_ansi(
    text: str, 
    bold: bool = True, 
    color: str | None = None
):
    """
    Wraps some text with ANSI control codes to apply terminal-based formatting.
    Note: Not all terminals will be compatible!
    """
    bold_code = "\033[1m" if bold else ""
    color_code = ""
    if color == "r":
        color_code = "\033[31m"
    if color == "b":
        color_code = "\033[34m"
    return f"{bold_code}{color_code}{text}\033[0m"

def render_board(
    board: dict[Coord, PlayerColor], 
    ansi: bool = False
) -> str:
    """
    Visualise the Tetress board via a multiline ASCII string, including
    optional ANSI styling for terminals that support this.

    If a target coordinate is provided, the token at that location will be
    capitalised/highlighted.
    """
    output = ""
    for r in range(BOARD_N):
        for c in range(BOARD_N):
            if board.get(Coord(r, c), None):
                color = board[Coord(r, c)]
                color = "r" if color == PlayerColor.RED else "b"
                text = f"{color}" 
                if ansi:
                    output += apply_ansi(text, color=color)
                else:
                    output += text
            else:
                output += "."
            output += " "
        output += "\n"
    return output