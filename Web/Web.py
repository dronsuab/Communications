from flask import Flask
from flask import request
from flask import render_template
import time
import thread
from multiprocessing import Process, Value, Array
import socket

redDronesAlive = Value('i',0)
blueDronesAlive = Value('i',0)
redBasesConquered = Value('i',0)
blueBasesConquered = Value('i',0)
winner = Array('c', "Unknown")
app = Flask(__name__) #new object
@app.route('/')#wrap: route or routes
def index():
    global redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner
    return render_template('web.html', redDronesAlive=redDronesAlive.value, blueDronesAlive=blueDronesAlive.value, redBasesConquered = redBasesConquered.value, blueBasesConquered = blueBasesConquered.value, winner = winner.value)

@app.route('/redteam')
def redteam():
    global redDronesAlive, redBasesConquered
    return render_template('redteam.html', redDronesAlive=redDronesAlive.value, redBasesConquered=redBasesConquered.value)
@app.route('/blueteam')
def blueteam():
    global blueDronesAlive, blueBasesConquered
    return render_template('blueteam.html', blueDronesAlive=blueDronesAlive.value, blueBasesConquered=blueBasesConquered.value)
@app.route('/rules')
def rules():
    return render_template('rules.html')

def refreshData(redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner):
    #socket to comunicate with others
    while(1):
        sock = socket.socket()
        sock.bind(("localhost", 9999))
        sock.listen(0)
        sock_c, addr = sock.accept()
        dataRecived = sock_c.recv(1024)
        #print ("dataRecived:" + dataRecived)
        mlist = dataRecived.split(',')
        #print ("List dataRecived:" + str(dataRecived))
        redDronesAlive.value = int(mlist[0])
        blueDronesAlive.value = int(mlist[1])
        redBasesConquered.value = int(mlist[2])
        blueBasesConquered.value = int(mlist[3])
        winner.value = (mlist[4])
        sock_c.close()
if __name__ == '__main__':
    p = Process(target=refreshData, args=(redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner))
    p.start()
    app.run(debug=False, port=8000)


