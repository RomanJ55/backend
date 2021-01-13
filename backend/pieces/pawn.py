from .piece import Piece


class Pawn(Piece):
    def __init__(self, x, y, player):
        super().__init__(x=x, y=y, player=player)
        self.type = 0
        self.set_image()

    def set_image(self):
        color_num = 0 if self.player == "white" else 1
        self.image = f"img\\{color_num}0{self.type}.png"

    def get_valid_moves(self, game):
        valid_moves = []
        moves_w = [(self.x, self.y-1), (self.x, self.y-2),
                   (self.x-1, self.y-1), (self.x + 1, self.y-1)]
        moves_b = [(self.x, self.y+1), (self.x, self.y+2),
                   (self.x-1, self.y+1), (self.x + 1, self.y+1)]

        if self.player == "white":
            if game.move_within_bounds(moves_w[0]):
                if not game.cell_is_piece((moves_w[0][0], moves_w[0][1])):
                    valid_moves.append(moves_w[0])
            if game.move_within_bounds(moves_w[1]):
                if not game.cell_is_piece((moves_w[1][0], moves_w[1][1])
                                          ) and not game.cell_is_piece((self.x, self.y-1)) and self.y == 6:
                    valid_moves.append(moves_w[1])
            for i in range(2, len(moves_w)):
                if game.move_within_bounds(moves_w[i]):
                    if (game.cell_is_piece((moves_w[i][0], moves_w[i][1])
                                           ) and game.board[moves_w[i][0]][moves_w[i][1]].player != self.player):
                        valid_moves.append(moves_w[i])
        else:
            if game.move_within_bounds(moves_b[0]):
                if not game.cell_is_piece((moves_b[0][0], moves_b[0][1])):
                    valid_moves.append(moves_b[0])
            if game.move_within_bounds(moves_b[1]):
                if not game.cell_is_piece((moves_b[1][0], moves_b[1][1])
                                          ) and not game.cell_is_piece((self.x, self.y+1)) and self.y == 1:
                    valid_moves.append(moves_b[1])
            for i in range(2, len(moves_b)):
                if game.move_within_bounds(moves_b[i]):
                    if (game.cell_is_piece((moves_b[i][0], moves_b[i][1])
                                           ) and game.board[moves_b[i][0]][moves_b[i][1]].player != self.player):
                        valid_moves.append(moves_b[i])

        return valid_moves
