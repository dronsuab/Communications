from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from multiprocessing import Process, Value, Array, Manager
import socket
import clases as c

redDronesAlive = Value('i',0)
blueDronesAlive = Value('i',0)
redBasesConquered = Value('i',0)
blueBasesConquered = Value('i',0)
winner = Array('c', "Unknown")

app = Flask(__name__)


@app.route('/')#wrap: route or routes
def index():
    global redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner
    return render_template('web.html', redDronesAlive=redDronesAlive.value, blueDronesAlive=blueDronesAlive.value, \
                           redBasesConquered = redBasesConquered.value, blueBasesConquered = blueBasesConquered.value,\
                           winner = winner.value)

@app.route('/redteam')
def redteam():
    global redDronesAlive, redBasesConquered
    dicDroneLen = len(dicDrone)
    dicBaseLen= len(dicBase)
    dicDroneLocal = dict(dicDrone)
    dicBaseLocal = dict(dicBase)

    return render_template('redteam.html', redDronesAlive=redDronesAlive.value, redBasesConquered=redBasesConquered.value, \
                           dicBase = dicBaseLocal, dicDrone = dicDroneLocal, dicBaseLen= dicBaseLen)
@app.route('/blueteam')
def blueteam():
    global blueDronesAlive, blueBasesConquered
    dicBaseLen = len(dicBase)
    dicDroneLocal = dict(dicDrone)
    dicBaseLocal = dict(dicBase)

    return render_template('blueteam.html', blueDronesAlive=blueDronesAlive.value, blueBasesConquered=blueBasesConquered.value, \
                           dicBase = dicBaseLocal, dicDrone = dicDroneLocal, dicBaseLen= dicBaseLen)
@app.route('/MVP')
def MVP():
    dicBaseLen = len(dicBase)
    bestShooterList = theShooter()
    lenBestShooterList = len(bestShooterList)
    bestConquerorList = theConqueror()
    lenBestConquierorList = len(bestConquerorList)
    mostConqueredList = theMostConquered()
    lenMostConqueredList = len(mostConqueredList)
    dicDroneLocal = dict(dicDrone)
    dicBaseLocal = dict(dicBase)

    print mostConqueredList

    return render_template('MVP.html',  dicBase = dicBaseLocal, dicDrone = dicDroneLocal, dicBaseLen = dicBaseLen, \
                           lenBestShooterList = lenBestShooterList, bestShooterList = bestShooterList, \
                           bestConquerorList=bestConquerorList, lenBestConquierorList=lenBestConquierorList, \
                           mostConqueredList=mostConqueredList, lenMostConqueredList=lenMostConqueredList)
@app.route('/rules')
def rules():
    return render_template('rules.html')
@app.route('/test')
def test():

    global redDronesAlive, redBasesConquered
    dicDroneLen = len(dicDrone)
    dicBaseLen = len(dicBase)
    dicDroneLocal = dict(dicDrone)
    dicBaseLocal = dict(dicBase)

    return render_template('test.html', redDronesAlive=redDronesAlive.value,
                           redBasesConquered=dicBaseLen, \
                           dicBase=dicBaseLocal, dicDrone=dicDroneLocal, dicBaseLen=dicBaseLen)

def refreshData(redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner, dicBase, dicDrone):
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
                drone.right = int(mlist[9])
                drone.left = int(mlist[10])
                drone.forward = int(mlist[11])
                drone.backward = int(mlist[12])
                drone.lives = int(mlist[13])
                drone.shots = int(mlist[14])
                drone.shotsRec = int(mlist[15])
                drone.basesCaught = int(mlist[16])

            else:
                dicDrone[mlist[7]] = c.Drone(mlist[7], mlist[8], int(mlist[9]), int(mlist[10]), int(mlist[11]), \
                                             int(mlist[12]), int (mlist[13]), int(mlist[14]), int(mlist[15]), int(mlist[16]))
        elif fbase  == 1:
            #msg: dredAlives, dblueAlives, bred, bblue, winner, fdrone, name, team

            conqRecordList = mlist[9:]
            count = 0
            auxList = []
            if mlist[7] in dicBase:
                dicBase[mlist[7]].team = mlist[8]
                for item in conqRecordList:
                    count += 1
                    auxList.append(item)
                    if count == 3:
                        dicBase[mlist[7]].conqRecord.append(auxList)
                        auxList = []
                        count = 0
            else:
                conqRecordTupleList = []
                for item in conqRecordList:
                    count += 1
                    auxList.append(item)
                    if count == 3:
                        conqRecordTupleList.append(auxList)
                        auxList = []
                        count = 0
                dicBase[mlist[7]] = c.Base(mlist[7], mlist[8], conqRecordTupleList)
        sock_c.close()
def theShooter():
    ''' Search who are the best shooters'''
    name = []
    maxShoots = 0
    dicDroneLocal = dict(dicDrone)
    for key in dicDroneLocal:
        if dicDroneLocal[key].shots >=  maxShoots:
            if dicDroneLocal[key].shots == maxShoots:
                name.append(key)
                maxShoots = dicDroneLocal[key].shots
            else:
                name = []
                name.append(key)
                maxShoots = dicDroneLocal[key].shots
    return name

def theConqueror():
    ''' Search who are the best conquerors '''
    name = []
    maxConquests = 0
    dicDroneLocal = dict(dicDrone)
    for key in dicDroneLocal:
        if dicDroneLocal[key].basesCaught >= maxConquests:
            if dicDroneLocal[key].basesCaught == maxConquests:
                name.append(key)
                maxConquests = dicDroneLocal[key].basesCaught
            else:
                name = []
                name.append(key)
                maxConquests = dicDroneLocal[key].basesCaught
    return name
def theMostConquered():
    name = []
    maxConquered = 0
    dicBaseLocal = dict(dicBase)
    for key in dicBaseLocal:
        if len(dicBaseLocal[key].conqRecord) >= maxConquered:
            if len(dicBaseLocal[key].conqRecord) == maxConquered:
                name.append(key)
            else:
                name = []
                name.append(key)
                maxConquered = len(dicBaseLocal[key].conqRecord)
    return name



if __name__ == '__main__':

    manager = Manager()
    # dic with players
    dicDrone = manager.dict()
    dicBase = manager.dict()

    #print dicDroneLen
    p = Process(target=refreshData, args=(redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner, dicBase, dicDrone))
    p.start()
    app.run(host="0.0.0.0", debug=False, port=80)


