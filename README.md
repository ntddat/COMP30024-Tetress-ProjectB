# Tetress Game Playing Agent

A game-playing agent for the game Tetress (designed by the University of Melbourne's teaching staff for the subject Artificial Intelligence in Semester 1, 2024) that utilizes **Negamax with Alpha-Beta Pruning**, **Iterative Deepening**, **Principal Variation**, a **Transposition Table** with **Zobrist Hashing**, and **Bitboards**. More information can be found in ![**report.pdf**](/report.pdf).

Done by Thanh Dat Nguyen and Ernest Tay Jie Jun

## Tetress Game

A brief explanation of Tetress' rules, adapted from the game specification made by the subject's staff.

Tetress is a two-player game played on an 11 by 11 game board. Each player will take turns placing Tetrominoes (i.e. pieces normally found in the popular game Tetris), with the goal of taking territory of the board and stopping the other player from being able to place their own pieces.

### Game Board

- The board has a size of 11 by 11 squares.
- Despite this, the board technically spans an infinitely spanning space, meaning that pieces can wrap around to the other side of the board.
- Each square always has 4 adjacent squares, even corner and side squares (because of the wrap-around)
Below a coordinate representation of the game board (made by the subject staff) can be found
![](/gameboard.png)
