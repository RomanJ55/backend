from .piece import Piece
from .rook import Rook


class King(Piece):
    def __init__(self, x, y, player):
        super().__init__(x=x, y=y, player=player)
        self.type = 5
        self.marked = False
        self.incheck = False
        self.checkmate = False
        self.set_image()

    def put_incheck(self):
        self.incheck = True
        self.set_image()

    def put_outof_check(self):
        self.incheck = False
        self.set_image()

    def mate(self, game):
        self.checkmate = True
        game.stop_game("black" if game.turn == "white" else "white")

    def set_image(self):
        color_num = 0 if self.player == "white" else 1
        if not self.incheck:
            self.image = f"img\\{color_num}0{self.type}.png"
        else:
            self.image = f"img\\{color_num}0{self.type}c.png"

    def get_threats(self, game):
        threats = []
        for i in range(game.rows):
            for j in range(game.columns):
                if (game.board[i][j] != 0) and (game.board[i][j].player != self.player):
                    threats.extend(
                        game.board[i][j].get_valid_moves(game))
        return threats

    def get_valid_moves(self, game):
        valid_moves = []
        valid_castlemoves = []
        moves = [(self.x, self.y-1), (self.x+1, self.y-1), (self.x+1, self.y+1  # up, up+left/right
                                                            ),
                 (self.x-1, self.y), (self.x+1, self.y  # left, right
                                      ),
                 (self.x, self.y+1), (self.x-1, self.y-1), (self.x-1, self.y+1)]  # down, down+left/right
        castle_moves = [[(self.x+1, self.y), (self.x+2, self.y), "queen"],  # queenside
                        [(self.x-1, self.y), (self.x-2, self.y), "king"]  # kingside
                        ]

        if self.move_counter == 0 and not self.incheck:
            if isinstance(game.board[self.x+4][self.y], Rook):
                if game.board[self.x+4][self.y].player == self.player and game.board[self.x+4][self.y].move_counter == self.move_counter:
                    if game.board[self.x+1][self.y] == 0 and game.board[self.x+2][self.y] == 0 and game.board[self.x+3][self.y] == 0:
                        valid_castlemoves.append(castle_moves[0])
            if isinstance(game.board[self.x-3][self.y], Rook):
                if game.board[self.x-3][self.y].player == self.player and game.board[self.x-3][self.y].move_counter == self.move_counter:
                    if game.board[self.x-1][self.y] == 0 and game.board[self.x-2][self.y] == 0:
                        valid_castlemoves.append(castle_moves[1])

        for move in moves:
            if game.move_within_bounds(move):
                if not game.cell_is_piece(move):
                    valid_moves.append(move)
                if (game.cell_is_piece(move)) and game.board[move[0]][move[1]].player != self.player:
                    valid_moves.append(move)

        return valid_moves, valid_castlemoves
