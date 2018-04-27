from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from multiprocessing import Process, Value, Array
import socket
import clases as c

#dic with players
dicBase = {}
dicDrone = {}

redDronesAlive = Value('i',0)
blueDronesAlive = Value('i',0)
redBasesConquered = Value('i',0)
blueBasesConquered = Value('i',0)
winner = Array('c', "Unknown")

app = Flask(__name__)


@app.route('/')#wrap: route or routes
def index():
    global redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner
    return render_template('web.html', redDronesAlive=redDronesAlive.value, blueDronesAlive=blueDronesAlive.value, redBasesConquered = redBasesConquered.value, blueBasesConquered = blueBasesConquered.value, winner = winner.value)

@app.route('/redteam')
def redteam():
    global redDronesAlive, redBasesConquered
    dicDroneLen = len(dicDrone)
    dicBaseLen= len(dicBase)

    return render_template('redteam.html', redDronesAlive=redDronesAlive.value, redBasesConquered=redBasesConquered.value, \
                           dicBase = dicBase, dicDrone = dicDrone, dicBaseLen= dicBaseLen)
@app.route('/blueteam')
def blueteam():
    global blueDronesAlive, blueBasesConquered
    dicBaseLen = len(dicBase)

    return render_template('blueteam.html', blueDronesAlive=blueDronesAlive.value, blueBasesConquered=blueBasesConquered.value, \
                           dicBase = dicBase, dicDrone = dicDrone, dicBaseLen= dicBaseLen)
@app.route('/MVP')
def MVP():
    dicBaseLen = len(dicBase)
    bestShooterList = theShooter()
    lenBestShooterList = len(bestShooterList)
    bestConquerorList = theConqueror()
    lenBestConquierorList = len(bestConquerorList)
    print bestShooterList
    return render_template('MVP.html',  dicBase = dicBase, dicDrone = dicDrone, dicBaseLen = dicBaseLen, \
                           lenBestShooterList = lenBestShooterList, bestShooterList = bestShooterList, \
                           bestConquerorList=bestConquerorList, lenBestConquierorList=lenBestConquierorList)
@app.route('/rules')
def rules():
    return render_template('rules.html')
@app.route('/test')
def test():
    dicDroneLen = len(dicDrone)
    dicBaseLen = len(dicBase)

    return render_template('test.html', redDronesAlive=redDronesAlive.value,
                           redBasesConquered=redBasesConquered.value, \
                           dicBase=dicBase, dicDrone=dicDrone, dicDroneLen=dicDroneLen, dicBaseLen=len(dicBase))

def refreshData(redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner, dicDrone, dicBase):
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
        fdrone = int(mlist[5])
        fbase = int(mlist[6])
        if fdrone == 1:
            # msg: dredAlives, dblueAlives, bred, bblue, winner, fdrone, fbase, name, team, right,
            # left, forward, backward, lives, shots, shotsRec, basesCaught
            if mlist[7] in dicDrone:
                drone = dicDrone[mlist[7]]
                drone.right.value = int(mlist[9])
                drone.left.value = int(mlist[10])
                drone.forward.value = int(mlist[11])
                drone.backward.value = int(mlist[12])
                drone.lives.value = int(mlist[13])
                drone.shots.value = int(mlist[14])
                drone.shotsRec.value = int(mlist[15])
                drone.basesCaught.value = int(mlist[16])

            else:
                dicDrone[mlist[7]] = c.Drone(mlist[7], mlist[8], int(mlist[9]), int(mlist[10]), int(mlist[11]), \
                                             int(mlist[12]), int (mlist[13]), int(mlist[14]), int(mlist[15]), int(mlist[16]))
        elif fbase  == 1:
            # msg: dredAlives, dblueAlives, bred, bblue, winner, fdrone, name, team
            if mlist[7] in dicBase:
                base = dicBase[mlist[7]]
                base.team.value = mlist[8]
            else:
                dicBase[mlist[7]] = c.Base(mlist[7], mlist[8])

        sock_c.close()
def theShooter():
    ''' Search who are the best shooters'''
    name = []
    maxShoots = 0
    for key in dicDrone:
        if dicDrone[key].shots.value >=  maxShoots:
            if dicDrone[key].shots.value == maxShoots:
                name.append(key)
                maxShoots = dicDrone[key].shots.value
            else:
                name = []
                name.append(key)
                maxShoots = dicDrone[key].shots.value
    return name

def theConqueror():
    ''' Search who are the best conquerors '''
    name = []
    maxConquests = 0
    for key in dicDrone:
        if dicDrone[key].basesCaught.value >= maxConquests:
            if dicDrone[key].basesCaught.value == maxConquests:
                name.append(key)
                maxConquests = dicDrone[key].basesCaught.value
            else:
                name = []
                name.append(key)
                maxConquests = dicDrone[key].basesCaught.value
    return name


if __name__ == '__main__':

    # only test
    dicBase['test'] = c.Base("Btest", "red")
    dicBase['test2'] = c.Base("Btest2", "red")
    dicDrone['test'] = c.Drone("Dtest", "red", 1, 1, 1, 1, 4, 1, 0, 0)
    dicDrone['test2'] = c.Drone("Dtest2", "red", 1, 1, 1, 1, 4, 0, 0, 0)
    redDronesAlive.value = 2

    dicBase['test3'] = c.Base("Btest3", "blue")
    dicBase['test4'] = c.Base("Btest4", "blue")
    dicDrone['test3'] = c.Drone("Dtest3", "blue", 1, 1, 1, 1, 4, 0, 0, 1)
    dicDrone['test4'] = c.Drone("Dtest4", "blue", 1, 1, 1, 1, 4, 0, 0, 0)
    blueDronesAlive.value = 2

    dicDroneLen = len(dicDrone)
    dicBaseLen = len(dicBase)
    #print dicDroneLen
    p = Process(target=refreshData, args=(redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner, dicBase, dicDrone))
    p.start()
    app.run(host="0.0.0.0", debug=False, port=80)


