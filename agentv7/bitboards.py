# COMP30024 Artificial Intelligence, Semester 1 2024
# Project Part B: Game Playing Agent

from referee.game import Coord, PlayerColor, BOARD_N, PlaceAction

class Bitboard:
    base: int
    no_left: int
    no_right: int
    around: list[int]
    masks_on_square: list[list[int]]
    pieces_on_square: list[list[int]]
    turn_two_losses: list[int]

    def __init__(self):
        self.base = 0
        self.no_left = 2657157283220261725413961158117816318
        self.no_right = 1328578641610130862706980579058908159
        self.around = [0]*121
        self.masks_on_square = [[]]*121
        self.pieces_on_square = [[]]*121
        self.turn_two_losses = [0]*242
        for i in range(0, 11):
            for j in range(0, 11):
                self.around[i*11 + j] = self.squares_around(i, j)
                self.masks_on_square[i*11 + j] = []
                self.pieces_on_square[i*11 + j] = []
                self.find_loss(i, j) 
                self.piece_masks(i, j)

    def set_bit(self, bitboard: int, square: int):
        return bitboard | (1 << square)

    def get_bit(self, bitboard: int, square: int):
        return bitboard & (1 << square)

    def pop_bit(self, bitboard: int, square: int):
        if self.get_bit(bitboard, square):
            return bitboard ^ (1 << square)
        else:
            return bitboard
    
    def print_bitboard(self, bitboard: int):
        for i in range(0, 11):
            for j in range(0, 11):
                if self.get_bit(bitboard, i*11 + j):
                    print(1, end = " ")
                else:
                    print(0, end = " ")
            print()
         
        print("NUMBER:")
        print(bitboard)

    def find_loss(self, row: int, col: int):
        num_hor = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
        num_ver = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
        
        square = Coord(row, col)
        num_hor = self.set_bit(num_hor, square.r*BOARD_N + square.c)
        num_ver = self.set_bit(num_ver, square.r*BOARD_N + square.c)
        for i in range(1, 8):
            temp_hor = square.left(i)
            temp_ver = square.down(i)
            num_hor = self.set_bit(num_hor, temp_hor.r*BOARD_N + temp_hor.c)
            num_ver = self.set_bit(num_ver, temp_ver.r*BOARD_N + temp_ver.c)

        self.turn_two_losses.append(num_hor)
        self.turn_two_losses.append(num_ver)
    
    def squares_around(self, row: int, col: int) -> int:
        around = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)

        if col + 1 > 10:
            around = self.set_bit(around, row*11)
        else:
            around = self.set_bit(around, row*11 + col + 1)
        if col - 1 < 0:
            around = self.set_bit(around, row*11 + 10)
        else:
            around = self.set_bit(around, row*11 + col - 1)
        if row + 1 > 10:
            around = self.set_bit(around, col)
        else:
            around = self.set_bit(around, (row + 1)*11 + col)
        if row - 1 < 0:
            around = self.set_bit(around, 10*11 + col)
        else:
            around = self.set_bit(around, (row - 1)*11 + col)

        return around

    def piece_masks(self, row: int, col: int) -> list[int]:
        self.I_piece_masks(row, col)
        self.L_piece_masks(row, col)
        self.J_piece_masks(row, col)
        self.Z_piece_masks(row, col)
        self.S_piece_masks(row, col)
        self.T_piece_masks(row, col)
        self.O_piece_masks(row, col)

    def I_piece_masks(self, row: int, col: int):
        
        square = Coord(row, col)
        temps = []
        temps.append(square.down())
        temps.append(square.up(4))
        temps.append(square.left())
        temps.append(square.left().up())
        temps.append(square.left().up(2))
        temps.append(square.left().up(3))
        temps.append(square.right())
        temps.append(square.right().up())
        temps.append(square.right().up(2))
        temps.append(square.right().up(3))

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.down(), temp.down(2), temp.down(3)))

        temps = []
        temps.append(square.left())
        temps.append(square.right(4))
        temps.append(square.up())
        temps.append(square.up().right())
        temps.append(square.up().right(2))
        temps.append(square.up().right(3))
        temps.append(square.down())
        temps.append(square.down().right())
        temps.append(square.down().right(2))
        temps.append(square.down().right(3))

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.left(), temp.left(2), temp.left(3)))

    def L_piece_masks(self, row: int, col: int) -> list[int]:

        square = Coord(row, col)
        # L piece rotated 0 degrees
        temps = []
        temps.append(square.up())
        temps.append(square.up().right())
        temps.append(square.down())
        temps.append(square.down(2))
        temps.append(square.left())
        temps.append(square.down(3).right())
        temps.append(square.right(2).down(2))
        temps.append(square.right(2).down())
        temps.append(square.right(2))

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.left(), temp.left().up(), temp.left().up(2)))

        # L piece rotated 90 degrees to the right
        temps = []
        temps.append(square.right())
        temps.append(square.right().down())
        temps.append(square.left())
        temps.append(square.left(2))
        temps.append(square.up())
        temps.append(square.left(3).down())
        temps.append(square.down(2).left(2))
        temps.append(square.down(2).left())
        temps.append(square.down(2))

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.up(), temp.up().right(), temp.up().right(2)))

        # L piece rotated 180 degrees to the right
        temps = []
        temps.append(square.down())
        temps.append(square.down().left())
        temps.append(square.up())
        temps.append(square.up(2))
        temps.append(square.right())
        temps.append(square.up(3).left())
        temps.append(square.left(2).up(2))
        temps.append(square.left(2).up())
        temps.append(square.left(2))

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.right(), temp.right().down(), temp.right().down(2)))

        # J piece rotated 270 degrees to the right
        temps = []
        temps.append(square.left())
        temps.append(square.left().up())
        temps.append(square.right())
        temps.append(square.right(2))
        temps.append(square.down())
        temps.append(square.right(3).up())
        temps.append(square.up(2).right(2))
        temps.append(square.up(2).right())
        temps.append(square.up(2))
        
        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.down(), temp.down().left(), temp.down().left(2)))

    def J_piece_masks(self, row: int, col: int):

        square = Coord(row, col)
        # J piece rotated 0 degrees
        temps = []
        temps.append(square.up())
        temps.append(square.up().left())
        temps.append(square.down())
        temps.append(square.down(2))
        temps.append(square.right())
        temps.append(square.down(3).left())
        temps.append(square.left(2).down(2))
        temps.append(square.left(2).down())
        temps.append(square.left(2))

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.right(), temp.right().up(), temp.right().up(2)))

        # J piece rotated 90 degrees to the right
        temps = []
        temps.append(square.right())
        temps.append(square.right().up())
        temps.append(square.left())
        temps.append(square.left(2))
        temps.append(square.down())
        temps.append(square.left(3).up())
        temps.append(square.up(2).left(2))
        temps.append(square.up(2).left())
        temps.append(square.up(2))

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.down(), temp.down().right(), temp.down().right(2)))

        # J piece rotated 180 degrees to the right
        temps = []
        temps.append(square.down())
        temps.append(square.down().right())
        temps.append(square.up())
        temps.append(square.up(2))
        temps.append(square.left())
        temps.append(square.up(3).right())
        temps.append(square.right(2).up(2))
        temps.append(square.right(2).up())
        temps.append(square.right(2))

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.left(), temp.left().down(), temp.left().down(2)))

        # J piece rotated 270 degrees to the right
        temps = []
        temps.append(square.left())
        temps.append(square.left().down())
        temps.append(square.right())
        temps.append(square.right(2))
        temps.append(square.up())
        temps.append(square.right(3).down())
        temps.append(square.down(2).right(2))
        temps.append(square.down(2).right())
        temps.append(square.down(2))
        
        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.up(), temp.up().left(), temp.up().left(2)))

    def Z_piece_masks(self, row: int, col: int):

        square = Coord(row, col)

        # Z piece rotated 0 degrees
        temps = []
        temps.append(square.right(2).down())
        temps.append(square.right(2))
        temps.append(square.up())
        temps.append(square.up().right())
        temps.append(square.left())
        temps.append(square.down())
        temps.append(square.down(2).right(2))
        temps.append(square.down(2).right())

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.left(), temp.left().up(), temp.left(2).up()))

        # Z piece rotated 90 degrees
        temps = []
        temps.append(square.down(3).left())
        temps.append(square.down(2))
        temps.append(square.right())
        temps.append(square.right().down())
        temps.append(square.up())
        temps.append(square.left())
        temps.append(square.left(2).down(2))
        temps.append(square.left(2).down())

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.up(), temp.up().right(), temp.up(2).right()))
    
    def S_piece_masks(self, row: int, col: int):

        square = Coord(row, col)

        # S piece rotated 0 degrees
        temps = []
        temps.append(square.left(3).down())
        temps.append(square.left(2))
        temps.append(square.up())
        temps.append(square.up().left())
        temps.append(square.right())
        temps.append(square.down())
        temps.append(square.down(2).left(2))
        temps.append(square.down(2).left())

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.right(), temp.right().up(), temp.right(2).up()))

        # S pieces rotated 90 degrees
        temps = []
        temps.append(square.up(3).left())
        temps.append(square.up(2))
        temps.append(square.right())
        temps.append(square.right().up())
        temps.append(square.down())
        temps.append(square.left())
        temps.append(square.left(2).up(2))
        temps.append(square.left(2).up())

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.down(), temp.down().right(), temp.down(2).right()))

    def T_piece_masks(self, row: int, col: int):

        square = Coord(row, col)

        # T piece rotated 0 degrees
        temps = []
        temps.append(square.up())
        temps.append(square.left())
        temps.append(square.right())
        temps.append(square.left(2).down())
        temps.append(square.right(2).down())
        temps.append(square.down(2).right())
        temps.append(square.down(2))
        temps.append(square.down(2).left())

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = temp.up().left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.up(), temp.up().left(), temp.up().right()))

        # T piece rotated 90 degrees
        temps = []
        temps.append(square.right())
        temps.append(square.up())
        temps.append(square.down())
        temps.append(square.up(2).left())
        temps.append(square.down(2).left())
        temps.append(square.left(2).down())
        temps.append(square.left(2))
        temps.append(square.left(2).up())

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = temp.right().up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.right(), temp.right().up(), temp.right().down()))

        # T piece rotated 180 degrees
        temps = []
        temps.append(square.down())
        temps.append(square.right())
        temps.append(square.left())
        temps.append(square.right(2).up())
        temps.append(square.left(2).up())
        temps.append(square.up(2).left())
        temps.append(square.up(2))
        temps.append(square.up(2).right())

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = temp.down().right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.down(), temp.down().right(), temp.down().left()))

        # T piece rotated 270 degrees
        temps = []
        temps.append(square.left())
        temps.append(square.down())
        temps.append(square.up())
        temps.append(square.down(2).right())
        temps.append(square.up(2).right())
        temps.append(square.right(2).up())
        temps.append(square.right(2))
        temps.append(square.right(2).down())

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = temp.left().down()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.left(), temp.left().down(), temp.left().up()))

    def O_piece_masks(self, row: int, col: int):

        square = Coord(row, col)

        temps = []
        temps.append(square.up())
        temps.append(square.up().right())
        temps.append(square.right(2).down())
        temps.append(square.right(2))
        temps.append(square.down(2).right())
        temps.append(square.down(2))
        temps.append(square.left().down())
        temps.append(square.left())

        for temp in temps:
            piece = int("00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000", 2)
            t = temp
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.left()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.up()
            piece = self.set_bit(piece, t.r*11 + t.c)
            t = t.right()
            piece = self.set_bit(piece, t.r*11 + t.c)
            self.masks_on_square[row*11 + col].append(piece)
            self.pieces_on_square[row*11 + col].append(PlaceAction(temp, temp.left(), temp.left().up(), temp.up()))
