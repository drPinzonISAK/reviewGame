import csv

from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

# warm_up = [
#     ["Com Sci", 94, False, "Computer science is like magic for machines! The best science"],
#     ["Socializing with Friends", 3, False, "I'll really miss seeing my friends every day and just hanging out with them"],
#     ["Summer Break", 2, False, "I'll miss the super long break we get during summer. No more worry about school stuff for a while!"],
#     ["Lunchtime Chats:", 1, False, "Lunch breaks with my friends are the best. We eat together, chat, and have a great time"]
# ]
# reasons_for_academic_integrity = [
#     ["Actually Learning Stuff", 28, False, "Ever felt that \"aha\" moment? Upholding integrity in your studies brings about those lightbulb moments, leading to genuine understanding."],
#     ["Being True to You", 16, False, "It's about supporting yourself and staying true to your values. Demonstrating integrity through honesty in your work showcases your commitment to ethical principles."],
#     ["Winning in the Long Run", 14, False, "Think marathon, not sprint. Upholding integrity helps you develop skills that lead to winning in the long haul."],
#     ["Getting Ready for the Real World", 15, False, "High school is like training for the big leagues (college or whatever's next for you). Integrity now sets you up for success later."],
#     ["Building Your Character", 9, False, "Picture it as leveling up in the journey of life. Practicing integrity by being honest portrays you as someone with strong principles and a sense of responsibility"],
#     ["Playing Fair for All", 7, False, "Imagine a fair game where everyone has the same shot. Upholding integrity ensures that nobody's trying to bend the rules."],
#     ["Trust Rules", 6, False, "Maintaining integrity fosters trust with your teachers and friends. Trust acts as the magical ingredient that enhances relationships in wonderful ways."],
#     ["Being a Cool Citizen", 5, False, "In a world full of choices, choosing Integrity shows you're a responsible and awesome member of society."]
# ]
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
    global score
    score = [['A', 0], ['B', 0], ['C', 0]]
    return redirect(url_for('host',question=1))

@app.route('/host/<int:question>')
def host(question):
    global score
    index = (question - 1) * 2
    question = data[index][0]
    options = [[d, 10*len(data[index])-10*i] for i,d in enumerate(data[index][1:])]
    return render_template('host.html', question=question, options=options,teams=score)

@app.route('/player/<int:question>')
def player(question:int):
    global options, score
    index = (question - 1) * 2
    question = data[index][0]
    options = [[d, False, 10*len(data[index])-10*i] for i,d in enumerate(data[index][1:])]
    return render_template('player.html', question=question, options=options, teams=score)

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

@socketio.on('addScore_warmup')
def addScore_warmup(data):
    global score_warmup
    score_warmup[data['team']] += data['score']
    emit('updateScore_warmup',  {'score': score_warmup}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
