import json
from flask_api import FlaskAPI
from flask import jsonify, request
from flask_cors import CORS
from game import Game


app = FlaskAPI(__name__)
CORS(app)


chess_game = Game()


@app.route('/', methods=['GET'])
def home():
    return "Chess Api"


@app.route('/api/chess', methods=['GET'])
def api_all():
    json_str = json.dumps(chess_game, default=lambda x: x.__dict__, indent=2)
    return jsonify(json_str)


@app.route('/api/chess/post', methods=['POST'])
def handle_post():
    result = request.get_json()
    piece_color = 0
    x, y = result["x"], result["y"]
    if len(result) > 2:
        piece_color = result["player"]
    if piece_color:
        if piece_color == chess_game.turn:
            chess_game.unselect_all()
            chess_game.board[x][y].select()
        else:
            initiate_piece_move(x, y)
    else:
        initiate_piece_move(x, y)
    return "Done!"


@app.route("/api/chess/startend", methods=['POST'])
def handle_startend():
    result = request.get_json()
    command = result["command"]

    if command == "start":
        chess_game.run_game()
    if command == "end":
        chess_game.stop_game("black" if chess_game.turn ==
                             "white" else "white")
    return f"Game {command}"


def initiate_piece_move(x, y):
    piece = chess_game.get_selected_piece()
    if piece is not None:
        if not piece.get_type() == 5:  # if it's not a king
            valid_moves = piece.get_valid_moves(chess_game)
            if (x, y) in valid_moves:
                chess_game.handle_piece_move(
                    piece, (x, y))
        else:  # if it's a king, we have to check the normal and castle moves
            valid_kingmoves, valid_castle_moves = piece.get_valid_moves(
                chess_game)
            if (x, y) in valid_kingmoves:
                chess_game.handle_piece_move(
                    piece, (x, y))
            elif len(valid_castle_moves) > 0 and ((x, y) == valid_castle_moves[0][1] or (x, y) == valid_castle_moves[1][1]):
                if (x, y) == valid_castle_moves[0][1]:
                    chess_game.handle_castle_move(
                        piece, valid_castle_moves[0])
                else:
                    chess_game.handle_castle_move(
                        piece, valid_castle_moves[1])


if __name__ == '__main__':
    app.run()
