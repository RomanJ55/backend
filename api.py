import json
from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, emit, send, rooms
from game import Game
import eventlet
eventlet.monkey_patch()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*",
                    manage_session=False, max_http_buffer_size=1e8, async_mode='eventlet')

games = {0: Game()}


@socketio.on('join', "/game")
def on_join(data):
    room = data['room']
    join_room(room)
    games[room] = Game()
    #send(username + ' has entered the room.', room=room)


@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    #send(username + ' has left the room.', room=room)


@socketio.on("data", "/game")
def on_data():
    game = None
    room = rooms()
    if len(room) > 1:
        game = games[room[1]]
    else:
        game = games[0]
    socketio.sleep(0)
    json_str = json.dumps(
        game, default=lambda x: x.__dict__, indent=2)
    emit("data", json_str)


@socketio.on("gameStart", "/game")
def on_start():
    game = None
    room = rooms()
    if len(room) > 1:
        game = games[room[1]]
    else:
        game = games[0]
    game.run_game()
    emit("gameStart", "game started!")


@socketio.on("gameEnd", "/game")
def on_end():
    game = None
    room = rooms()
    if len(room) > 1:
        game = games[room[1]]
    else:
        game = games[0]
    game.stop_game("black" if game.turn == "white" else "white")
    emit("gameEnd", "game ended!")


@socketio.on("clicked", "/game")
def on_clicked(data):
    game = None
    room = rooms()
    if len(room) > 1:
        game = games[room[1]]
    else:
        game = games[0]
    piece_color = 0
    x, y = data["x"], data["y"]
    if len(data) > 2:
        piece_color = data["player"]
    if piece_color:
        if piece_color == game.turn:
            game.unselect_all()
            game.board[x][y].select()
        else:
            socketio.sleep(0)
            initiate_piece_move(x, y, game)
    else:
        socketio.sleep(0)
        initiate_piece_move(x, y, game)
    emit("clicked", "Done!")


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html", async_mode=socketio.async_mode)


def initiate_piece_move(x, y, chess_game):
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
    socketio.run(app)
