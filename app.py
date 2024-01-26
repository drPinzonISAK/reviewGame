import csv,os

from flask import Flask, render_template, redirect, url_for, request, session,abort
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)
players_queue = []

def is_local_request():
    return request.remote_addr in ['127.0.0.1', 'localhost']
def load_csv(file_path):
    data_list = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data_list.append(row)
    return data_list

data = load_csv("reviewIB.csv")
score = [['Tuv', 0], ['KAl', 0], ['Sal', 0], ['Bos', 0], ['Aie', 0], ['Maz', 0]]
options = []
@app.route('/index')
def index():
    return render_template('menu.html')

@app.route('/reset_score')
def reset_score():
    if is_local_request():
        global score
        score = [['Tuv', 0], ['KAl', 0], ['Sal', 0], ['Bos', 0], ['Aie', 0], ['Maz', 0]]
        return redirect(url_for('host', question=1))
    else:
        abort(403)


@app.route('/host/<int:question>')
def host(question):
    if is_local_request():
        global score
        index = (question - 1) * 2
        question = data[index][0]
        options = [[d, 10*len(data[index])-10*i] for i,d in enumerate(data[index][1:])]
        return render_template('host2.html', question=question, options=options,teams=score, queue=players_queue)
    else:
        abort(403)


@app.route('/player/<int:question>')
def player(question:int):
    if is_local_request():
        global options, score
        index = (question - 1) * 2
        question = data[index][0]
        options = [[d, False, 10*len(data[index])-10*i] for i,d in enumerate(data[index][1:])]
        return render_template('player.html', question=question, options=options, teams=score)
    else:
        abort(403)
@app.route('/')
def student():
    return render_template('index.html')


@socketio.on('reveal')
def reveal(data):
    global options
    id = data['button_id']
    options[id][1] = True
    emit('option_updated', {'button_id': id, 'explanation':'well done'}, broadcast=True)

@socketio.on('toggleError')
def toggleError():
    emit('flipError', broadcast=True)

@socketio.on('hideExplanation')
def hideExplanation():
    emit('hideExplanation', broadcast=True)

@socketio.on('addScore')
def addScore(data):
    global score
    t, p = data['team'], data['points']
    for item in score:
        if item[0] == t:
            item[1] += p
            break
    print(score)
    emit('updateScore',  {'data': score}, broadcast=True)

# @socketio.on('addScore_warmup')
# def addScore_warmup(data):
#     global score_warmup
#     score_warmup[data['team']] += data['score']
#     emit('updateScore_warmup',  {'score': score_warmup}, broadcast=True)

@socketio.on('raise_hand')
def handle_raise_hand(json):
    player_name = json['name']
    if player_name not in players_queue:
        players_queue.append(player_name)
        emit('update_queue', {'queue': players_queue}, broadcast=True)

@socketio.on('clear_queue')
def handle_clear_queue():
    global players_queue
    players_queue.clear()
    emit('update_queue', {'queue': players_queue}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True,allow_unsafe_werkzeug=True, host='0.0.0.0',port=2345)
