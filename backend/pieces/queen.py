from .piece import Piece


class Queen(Piece):
    def __init__(self, x, y, player):
        super().__init__(x=x, y=y, player=player)
        self.type = 4
        self.set_image()

    def set_image(self):
        color_num = 0 if self.player == "white" else 1
        self.image = f"img\\{color_num}0{self.type}.png"

    def get_valid_moves(self, game):
        valid_moves = []
        moves = [[(self.x, self.y-j) for j in range(1, 8)],  # | up
                 [(self.x+j, self.y) for j in range(1, 8)],  # -- right
                 [(self.x-j, self.y) for j in range(1, 8)],  # -- left
                 [(self.x, self.y+j) for j in range(1, 8)],  # | down
                 [(self.x-j, self.y-j) for j in range(1, 8)],  # \ up-left
                 [(self.x+j, self.y-j) for j in range(1, 8)],  # / up-right
                 [(self.x-j, self.y+j) for j in range(1, 8)],  # / down-left
                 [(self.x+j, self.y+j) for j in range(1, 8)]  # \ down-right
                 ]
        for directions in moves:
            for move in directions:
                if game.move_within_bounds(move):
                    if game.cell_is_piece(move):
                        if game.board[move[0]][move[1]].player != self.player:
                            valid_moves.append(move)
                        break
                    valid_moves.append(move)

        return valid_moves
