import copy
import threading
from pieces.pawn import Pawn
from pieces.king import King
from pieces.knight import Knight
from pieces.queen import Queen
from pieces.bishop import Bishop
from pieces.rook import Rook
from pieces.piece import Piece


class Game:
    def __init__(self, timer=900):
        self.rows = 8
        self.columns = 8
        self.board = [[]]
        self.turn = "white"  # white starts
        self.game_running = False
        self.is_winner = False
        self.winner = None
        self.timer_save = timer
        self.white_time = 0
        self.black_time = 0

    def run_game(self):
        self.reset_game()
        self.populate_board()
        self.game_running = True

    def stop_game(self, win):
        self.game_running = False
        self.is_winner = True
        self.winner = win

    def is_game_running(self):
        return True if self.game_running else False

    def reset_game(self):
        self.white_time = self.timer_save
        self.black_time = self.timer_save
        self.is_winner = False
        self.winner = None
        self.turn = "white"
        self.board = [[0 for c in range(self.rows)]
                      for r in range(self.columns)]

    def change_turn(self):
        enemy_king = self.get_hostile_king()
        enemy_king.put_outof_check()
        enemy_threats = enemy_king.get_threats(self)

        if enemy_king.position in enemy_threats:
            enemy_king.put_incheck()

        if self.turn == "white":
            self.turn = "black"
        else:
            self.turn = "white"

        if self.is_checkmate():
            king = self.get_friendly_king()
            if king.incheck:
                king.mate(self)
            else:
                self.stop_game("Draw...")

    def update_timer(self):
        if self.turn == "white":
            self.white_time -= 1
        else:
            self.black_time -= 1
        try:
            threading.Timer(1.0, self.update_timer).start()
        except RuntimeError:
            pass

    def is_checkmate(self):
        for row in self.board:
            for element in row:
                if element != 0 and element.player == self.turn:
                    if not element.get_type() == 5:
                        moves = element.get_valid_moves(self)
                        for move in moves:
                            allowed = self.try_move(element, move)
                            if allowed:
                                return False
                    else:
                        king_moves, castle_moves = element.get_valid_moves(
                            self)
                        for move in king_moves:
                            allowed = self.try_move(element, move)
                            if allowed:
                                return False
                        if len(castle_moves) > 0:
                            for castle_move in castle_moves:
                                allowed = self.try_move(
                                    element, castle_move[0])
                                allowed2 = self.try_move(
                                    element, castle_move[1])
                                if (allowed and allowed2):
                                    return False
        return True

    def move_within_bounds(self, move):
        if (-1 < move[0] < self.rows) and (-1 < move[1] < self.columns):
            return True
        return False

    def cell_is_piece(self, cell):
        if isinstance(self.board[cell[0]][cell[1]], Piece):
            return True
        return False

    def get_selected_piece(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if self.cell_is_piece((i, j)):
                    if self.board[i][j].is_selected():
                        temp = self.board[i][j]
                        return temp
        return None

    def unselect_all(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if self.cell_is_piece((i, j)):
                    self.board[i][j].unselect()

    def get_friendly_king(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if self.cell_is_piece((i, j)) and self.board[i][j].get_type() == 5 and self.board[i][j].player == self.turn:
                    return self.board[i][j]
        return None

    def get_hostile_king(self):
        for i in range(self.rows):
            for j in range(self.columns):
                if self.cell_is_piece((i, j)) and self.board[i][j].get_type() == 5 and self.board[i][j].player != self.turn:
                    return self.board[i][j]
        return None

    def try_move(self, piece, move):
        for i in range(self.rows):
            for j in range(self.columns):
                if self.cell_is_piece((i, j)):
                    self.board[i][j].image_garbo = None
        # piece.image_garbo is a tk PhotoImage object. need to remove it before deepcopy

        board_copy = copy.deepcopy(self)
        board_copy.board[piece.x][piece.y] = 0
        board_copy.board[move[0]][move[1]] = copy.deepcopy(piece)
        board_copy.board[move[0]][move[1]].move(move)
        # queeening
        if isinstance(board_copy.board[move[0]][move[1]], Pawn) and (move[1] == 0 or move[1] == 7):
            board_copy.board[move[0]][move[1]] = Queen(
                move[0], move[1], piece.player)

        king = board_copy.get_friendly_king()
        threats = king.get_threats(board_copy)
        if king.position in threats:
            return False
        return True

    def handle_piece_move(self, piece, destination):
        allowed = self.try_move(piece, destination)
        king = self.get_friendly_king()
        if allowed:
            king.put_outof_check()
            king.marked = False
            self.board[piece.x][piece.y] = 0
            piece.move((destination[0], destination[1]))
            # queeening
            if isinstance(piece, Pawn) and (destination[1] == 0 or destination[1] == 7):
                piece = Queen(destination[0], destination[1], piece.player)
            self.board[destination[0]][destination[1]] = piece

            self.change_turn()
        else:
            piece.unselect()
            king.marked = True  # to indicante why we couldn't take the move

    def handle_castle_move(self, king_piece, castle_move):
        allowed = self.try_move(king_piece, castle_move[0])
        allowed1 = self.try_move(king_piece, castle_move[1])

        if (allowed and allowed1):
            king_piece.put_outof_check()
            king_piece.marked = False
            self.board[king_piece.x][king_piece.y] = 0
            king_piece.move((castle_move[1][0], castle_move[1][1]))
            self.board[castle_move[1][0]][castle_move[1][1]] = king_piece

            if castle_move[2] == "queen":
                temp = self.board[king_piece.x+2][king_piece.y]
                temp.move((king_piece.x-1, king_piece.y))
                self.board[king_piece.x-1][king_piece.y] = temp
                self.board[king_piece.x+2][king_piece.y] = 0
            if castle_move[2] == "king":
                temp = self.board[king_piece.x-1][king_piece.y]
                temp.move((king_piece.x+1, king_piece.y))
                self.board[king_piece.x+1][king_piece.y] = temp
                self.board[king_piece.x-1][king_piece.y] = 0
            self.change_turn()
        else:
            king_piece.unselect()
            king_piece.marked = True  # to indicante why we couldn't take the move

    def populate_board(self):
        self.board[0][0] = Rook(0, 0, "black")
        self.board[1][0] = Knight(1, 0, "black")
        self.board[2][0] = Bishop(2, 0, "black")
        self.board[4][0] = Queen(4, 0, "black")
        self.board[3][0] = King(3, 0, "black")
        self.board[5][0] = Bishop(5, 0, "black")
        self.board[6][0] = Knight(6, 0, "black")
        self.board[7][0] = Rook(7, 0, "black")
        for i in range(8):
            self.board[i][1] = Pawn(i, 1, "black")
            self.board[i][6] = Pawn(i, 6, "white")

        self.board[0][7] = Rook(0, 7, "white")
        self.board[1][7] = Knight(1, 7, "white")
        self.board[2][7] = Bishop(2, 7, "white")
        self.board[4][7] = Queen(4, 7, "white")
        self.board[3][7] = King(3, 7, "white")
        self.board[5][7] = Bishop(5, 7, "white")
        self.board[6][7] = Knight(6, 7, "white")
        self.board[7][7] = Rook(7, 7, "white")
