from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from multiprocessing import Process, Value, Array, Manager
import socket
import clases as c
import operator

redDronesAlive = Value('i',0)
blueDronesAlive = Value('i',0)
redBasesConquered = Value('i',0)
blueBasesConquered = Value('i',0)
winner = Array('c', "Unknown")
initDronesPlaying = Value('i',0)
initRedDronesPlaying = Value('i',0)
initBlueDronesPlaying = Value('i',0)
initBasesPlaying = Value('i',0)
initBlueBasesPlaying = Value('i',0)
initRedBasesPlaying = Value('i',0)

app = Flask(__name__)


@app.route('/')#wrap: route or routes
def index():
    global redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner
    remainingDrones = redDronesAlive.value + blueDronesAlive.value
    return render_template('web.html', redDronesAlive=redDronesAlive.value, blueDronesAlive=blueDronesAlive.value, \
                           redBasesConquered = redBasesConquered.value, blueBasesConquered = blueBasesConquered.value,\
                           winner = winner.value, initBasesPlaying=initBasesPlaying.value, initDronesPlaying=initDronesPlaying.value,\
                           initRedBasesPlaying=initRedBasesPlaying.value, initBlueBasesPlaying=initBlueBasesPlaying.value,\
                           initRedDronesPlaying=initRedDronesPlaying.value, initBlueDronesPlaying=initBlueDronesPlaying.value,\
                           remainingDrones=remainingDrones)

@app.route('/redteam')
def redteam():
    global redDronesAlive, redBasesConquered
    dicDroneLen = len(dicDrone)
    dicBaseLen= len(dicBase)
    dicDroneLocal = dict(dicDrone)
    dicBaseLocal = dict(dicBase)
    dicDroneLocal = dict(dicDrone)
    dicBaseLocal = dict(dicBase)


    return render_template('redteam.html', redDronesAlive=redDronesAlive.value, redBasesConquered=redBasesConquered.value, \
                           dicBase = sorted(dicBaseLocal.items(), key=operator.itemgetter(0)), dicDrone = sorted(dicDroneLocal.items(), key=operator.itemgetter(0)),\
                           dicBaseLen= dicBaseLen)
@app.route('/blueteam')
def blueteam():
    global blueDronesAlive, blueBasesConquered
    dicBaseLen = len(dicBase)
    dicDroneLocal = dict(dicDrone)
    dicBaseLocal = dict(dicBase)

    return render_template('blueteam.html', blueDronesAlive=blueDronesAlive.value, blueBasesConquered=blueBasesConquered.value, \
                           dicBase = sorted(dicBaseLocal.items(), key=operator.itemgetter(0)), dicDrone = sorted(dicDroneLocal.items(), key=operator.itemgetter(0)), dicBaseLen= dicBaseLen)
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

def refreshData(redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner, dicBase, dicDrone, initBasesPlaying, initRedBasesPlaying, initBlueBasesPlaying, initDronesPlaying, initRedDronesPlaying, initBlueDronesPlaying):
    #socket to comunicate with others

        sock = socket.socket()
        sock.bind(("localhost", 9999))
        sock.listen(10)
        while (1):
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
                # left, forward, backward, lives, shots, shotsRec, basesCaught, basesCaughtRecord, numPenalties, penalties, penaltiesRecord
                caughtRecordInitIndex = 17
                caughtRecordFinishIndex = int(17 + int(mlist[16])*2)
                if caughtRecordFinishIndex == caughtRecordInitIndex:
                    caughtRecordFinishIndex += 1
                caughtRecordList = mlist[caughtRecordInitIndex:caughtRecordFinishIndex]

                dronePenaltiesInitIndex = caughtRecordFinishIndex + 1
                dronePenaltiesFinishIndex = dronePenaltiesInitIndex + int(mlist[dronePenaltiesInitIndex-1])
                dronePenalties = mlist[dronePenaltiesInitIndex:dronePenaltiesFinishIndex]
                if len(dronePenalties) > 0:
                    dronePenaltiesRecordInitIndex = dronePenaltiesFinishIndex
                else:
                    dronePenaltiesRecordInitIndex = dronePenaltiesFinishIndex + 1

                penaltiesRecordList = mlist[dronePenaltiesRecordInitIndex:]
                count = 0
                auxList = []

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
                    drone.numPenalties = int(mlist[dronePenaltiesInitIndex-1])
                    drone.penalties = dronePenalties
                    drone.basesCaughtRecord = []
                    for item in caughtRecordList:
                        count += 1
                        auxList.append(item)
                        if count == 2:
                            drone.basesCaughtRecord.append(auxList)
                            auxList = []
                            count = 0
                    count = 0
                    auxList = []
                    drone.penaltiesRecord = []
                    for penalty in penaltiesRecordList:
                        count += 1
                        auxList.append(penalty)
                        if count == 4:
                            drone.penaltiesRecord.append(auxList)
                            auxList = []
                            count = 0
                    drone.lenPenaltiesRecord = len(drone.penaltiesRecord)
                    dicDrone[mlist[7]] = drone

                else:
                    caughtRecordTupList = []
                    for item in caughtRecordList:
                        count += 1
                        auxList.append(item)
                        if count == 2:
                            caughtRecordTupList.append(auxList)
                    penaltiesRecordTupList = []
                    count = 0
                    auxList = []
                    for item in penaltiesRecordList:
                        count += 1
                        auxList.append(item)
                        if count == 4:
                            penaltiesRecordTupList.append(auxList)
                    dicDrone[mlist[7]] = c.Drone(mlist[7], mlist[8], int(mlist[9]), int(mlist[10]), int(mlist[11]), \
                                                 int(mlist[12]), int(mlist[13]), int(mlist[14]), int(mlist[15]),\
                                                 int(mlist[16]), caughtRecordTupList, int(mlist[(17 + int(mlist[16])*2 + 1)]), \
                                                 penaltiesRecordList, penaltiesRecordTupList, len(penaltiesRecordTupList))

            elif fbase == 1:
                #msg: dredAlives, dblueAlives, bred, bblue, winner, fdrone, name, team, timesConquered, conquRecord

                conqRecordList = mlist[10:]
                count = 0
                auxList = []
                if mlist[7] in dicBase:
                    base = dicBase[mlist[7]]
                    base.team = mlist[8]
                    base.timesConquered = int(mlist[9])
                    base.conqRecord=[]
                    for item in conqRecordList:
                        count += 1
                        auxList.append(item)
                        if count == 3:
                            base.conqRecord.append(auxList)
                            auxList = []
                            count = 0
                    dicBase[mlist[7]] = base
                else:
                    conqRecordTupleList = []
                    for item in conqRecordList:
                        count += 1
                        auxList.append(item)
                        if count == 3:
                            conqRecordTupleList.append(auxList)
                            auxList = []
                            count = 0
                    dicBase[mlist[7]] = c.Base(mlist[7], mlist[8], int(mlist[9]), conqRecordTupleList)
            else:
                # msg: dredAlives, dblueAlives, bred, bblue, winner, fdrone, fbase, initDronesPlaying, initRedDronesPlaying,
                # initBlueDronesPlaying, initBasesPlaying, initBlueBasesPlaying, initRedBasesPlaying
                initDronesPlaying.value = int(mlist[7])
                initRedDronesPlaying.value = int(mlist[8])
                initBlueDronesPlaying.value = int(mlist[9])
                initBasesPlaying.value = int(int(mlist[10]))
                initBlueBasesPlaying.value = int(mlist[11])
                initRedBasesPlaying.value = int(mlist[12])
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
    name.sort()
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
    name.sort()
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
    name.sort()
    return name

if __name__ == '__main__':

    manager = Manager()
    # dic with players
    dicDrone = manager.dict()
    dicBase = manager.dict()

    p = Process(target=refreshData, args=(redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner, \
                                          dicBase, dicDrone, initBasesPlaying, initRedBasesPlaying, initBlueBasesPlaying, \
                                          initDronesPlaying, initRedDronesPlaying, initBlueDronesPlaying))
    p.start()
    app.run(host="0.0.0.0", debug=False, port=80)


