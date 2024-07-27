# Tetress Game Playing Agent

A game-playing agent for the game Tetress (designed by the University of Melbourne's teaching staff for the subject Artificial Intelligence in Semester 1, 2024) that utilizes **Negamax with Alpha-Beta Pruning**, **Iterative Deepening**, **Principal Variation**, a **Transposition Table** with **Zobrist Hashing**, and **Bitboards**. More information can be found in ![**report.pdf**](/report.pdf).

The game-playing agents are done by Thanh Dat Nguyen and Ernest Tay Jie Jun.
Grade given: 21/22.

## Tetress Game

A brief explanation of Tetress' rules, adapted from the game specification made by the subject's staff.

Tetress is a two-player game played on an 11 by 11 game board. Each player will take turns placing Tetrominoes (i.e. pieces normally found in the popular game Tetris), with the goal of taking territory of the board and stopping the other player from being able to place their own pieces.

### Game Board

- The board has a size of 11 by 11 squares.
- Despite this, the board technically spans an infinitely spanning space, meaning that pieces can wrap around to the other side of the board.
- Each square always has 4 adjacent squares, even corner and side squares (because of the wrap-around).

Below a coordinate representation of the game board (made by the subject staff) can be found.
![](/gameboard.png)

### Game Rules

The basic gameplay sequence of Tetress is as follows.

- At the start of the game, the board is empty. Each player's first action allows them to place their piece anywhere on the board.
- The two players (RED and BLUE) continues taking turns placing pieces on empty squares (all 4 squares of the piece must be placed on an empty square). Note that the pieces following the first must also be placed so that one of their squares are placed adjacent (horizontally or vertically) to a pre-existing square of the same colour. 
- Special Rule: If after any piece placement, a row/column has no empty squares, then that entire row/column is cleared of squares (all coloured squares are replaced by empty squares)
- The game ends when a player can no longer make a legal move, or when 150 moves have been made by both players (in total). In the latter case, the player with more squares of their colour on the board is declared the winner. If there is a tie, then the game ends in a draw.

## Content

The repository contains multiple agents that can play the game at varying degrees of effectiveness (developed by us), as well as a way to test the agents against each other (developed by the staff of the subject). Explanations for some of the packages in the repository is below.

- `agentv7`: The latest version of the agent. Utilizes all the features mentioned in the introduction and the report.
- `agentv4` and `agentv3`: Older versions of the agent with insignificant differences. Utilizes some of the features mentioned, including **Negamax with Alpha-Beta Pruning**, **Iterative Deepening**, and a **Transposition Table** with **Zobrist Hashing**, in an ineffectve and potentially incorrect way.
- `agent`: One of the earliest versions of the agent. Utilizes **Minimax**.
- `mcts`: An agent that uses Monte Carlo Tree Search to play the game. The agent proved to be less successful than our final version (not because MCTS is necessarily less effective, but rather because we didn't explore it enough)
- `agentrandom`: An agent that makes completely random actions. Useful for testing purposes.
- `referee`: The package developed by subject staff to enforce the rules of the game and make the agents play against each other.

In order to test any two agents against one another, simply run the command:
```
python -m referee <agent_name> <agent_name>
```
where <agent_name> is replaced by the package name. So, for example, if we wish to test the latest version agent against the random agent, we run the command:
```
python -m referee agentv7 agentrandom
```
In this case, agentv7 will play as RED and move first, and the random agent will play as BLUE and move second.
