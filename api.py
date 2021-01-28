import json
from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, emit, rooms
from game import Game
import eventlet
eventlet.monkey_patch()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*",
                    manage_session=False, max_http_buffer_size=1e8)


def make_dummy_game(timer=900):
    dgame = Game(timer)
    dgame.reset_game()
    dgame.game_running = True
    dgame.turn = "not started"
    return dgame


games = {0: ["", "", False,  make_dummy_game(), 1800]}


@socketio.on('createGame', "/game")
def on_createGame(data):
    username = data['username']
    room = data['room']
    timer = int(data['timer'])*60

    join_room(room)
    games[room] = [username, "", False, Game(timer), timer]
    emit("createGame", "success")


@socketio.on('joinExisting', "/game")
def on_joinExisting(data):
    username = data['username']
    if data['room'] is not None:
        room = int(data['room'])
        if room in games.keys():
            if games[room][1] == "":
                games[room][1] = username
                join_room(room)
                emit("joinExisting", "joined")
            elif games[room][0] == "":
                games[room][0] = username
                join_room(room)
                emit("joinExisting", "joined")
            else:
                emit("joinExisting", "Room is full")
        else:
            emit("joinExisting", "Room doesn't exist")


@socketio.on('leave', "/game")
def on_leave(data):
    room = data["room"]
    username = data["username"]

    game = games[room]
    if game[0] == username:
        game[0] = ""
    if game[1] == username:
        game[1] = ""
    game[3].reset_game()
    game[3].game_running = False
    game[2] = False

    if (game[0] == "" and game[1] == ""):
        games.pop(room)
    leave_room(room)


@socketio.on("data", "/game")
def on_data(data):
    if data['room'] in games:
        game_entry = games[data['room']]
        game = game_entry[3]

        json_str = json.dumps(
            game, default=lambda x: x.__dict__, indent=2)
        emit("data", json_str, room=data['room'])


@socketio.on("gameStart", "/game")
def on_gameStart():
    room = rooms()
    room_id = get_room_id(room)
    game_entry = games[room_id]
    game_entry[2] = True
    game_entry[3].run_game()


@socketio.on("gameEnd", "/game")
def on_gameEnd():
    room = rooms()
    room_id = get_room_id(room)
    game_entry = games[room_id]
    game_entry[2] = False
    game_entry[3].stop_game(
        "black" if game_entry[3].turn == "white" else "white")


@socketio.on("giveup", "/game")
def on_giveup(data):
    winner = None
    game_entry = games[data['room']]
    if data['username'] == game_entry[0]:
        winner = "black"
    else:
        winner = "white"
    game_entry[2] = False
    game_entry[3].stop_game(winner)


@socketio.on("restart", "/game")
def on_restart():
    room = rooms()
    room_id = get_room_id(room)
    game_entry = games[room_id]
    game_entry[2] = True
    game_entry[3].run_game()


@socketio.on("clicked", "/game")
def on_clicked(data):
    room = rooms()
    room_id = get_room_id(room)
    game_entry = games[room_id]
    game = game_entry[3]

    if game.game_running:
        if ((data['name'] == game_entry[0]) and game.turn == "white") or ((data['name'] == game_entry[1]) and game.turn == "black"):
            piece_color = 0
            x, y = data["x"], data["y"]
            if len(data) > 3:
                piece_color = data["player"]
            if piece_color:
                if piece_color == game.turn:
                    game.unselect_all()
                    game.board[x][y].select()
                else:
                    initiate_piece_move(x, y, game)
            else:
                initiate_piece_move(x, y, game)
            emit("clicked", "success")
        else:
            emit("clicked", "Wrong turn")
    else:
        emit("clicked", "not running")


@socketio.on("roomData", "/game")
def on_roomData(data):
    if data['room'] in games:
        game_entry = games[data['room']]
        emit("roomData", [game_entry[0], game_entry[1],
                          game_entry[2], game_entry[4]], room=data['room'])


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html", async_mode=socketio.async_mode)


def get_room_id(room):
    for r in room:
        if isinstance(r, int):
            return r
    return 0


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
