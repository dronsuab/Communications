import paho.mqtt.client as mqtt
import thread
import sys
import time
import re
import clases as c
import socket
initDroneLifes = 4
dblueAlives = 0
dredAlives = 0
initDronesPlaying = 0
initRedDronesPlaying = 0
initBlueDronesPlaying = 0
initBasesPlaying = 0
initBlueBasesPlaying = 0
initRedBasesPlaying = 0

bred = 0
bblue = 0
penaltyTime = 10
winner = "Unknown"
#pi broker
#broker = "192.168.1.103"
#test broker
broker = "192.168.1.102"
#dic with players
dicBase = {}
dicDrone = {}
dicController = {}
#defining callbacks
def on_connect(client, userdata, flags, rc):
   if rc != 0:
       #print "connection successful"
       print "connection refused, rc = " + rc
def on_subscribe(client, userdata, mid, granted_qos):
    pass
def on_message(client, userdata, message):
    if message.topic == "WantToPlay":
        subscribePlayer(message.payload)
    else:
        applyProtocol(message.topic, message.payload)

def subscribeTags(client,tags):
    for tag in tags:
        client.subscribe(tag)
def sendMessage(tag, msg):
    clientSender = mqtt.Client("clientSender")
    clientSender.on_connect = on_connect
    clientSender.connect(broker)
    clientSender.loop_start()
    clientSender.publish(tag, msg)
    clientSender.disconnect()
    clientSender.loop_stop()

def updateWeb(fdrone, fbase, object):
    sock = socket.socket()
    sock.connect(("localhost", 9999))
    if fdrone:
        # msg: dredAlives, dblueAlives, bred, bblue, winner, fdrone, fbase, name, team, right,
        #left, forward, backward, lifes, shots, shotsRec, basesCaught, basesCaughtRecord, numPenalties ,penalties, penaltiesRecord
        if object.basesCaught == 0:
            if len(object.penaltiesRecord) == 0:
                sock_msg = str(dredAlives) + ',' + str(dblueAlives) + ',' + str(bred) + ',' + str(bblue) + ',' + winner + ',' + str(fdrone) \
                           + ',' + str(fbase) + ',' + str(object.name) + ',' + str(object.team) + ',' + str(object.right) \
                           + ',' + str(object.left) + ',' + str(object.forward) + ',' + str(object.backward) + ',' + str(object.lifes) \
                           + ',' + str(object.shots) + ',' + str(object.shotsRec) + ',' + str(object.basesCaught) \
                           + ',' + str(object.basesCaughtRecord) + ',' + str(object.numPenalties) + ',' + (','.join(object.penalties))\
                           + ',' + object.penaltiesRecord
            else:
                sock_msg = str(dredAlives) + ',' + str(dblueAlives) + ',' + str(bred) + ',' + str(bblue) + ',' + winner + ',' + str(fdrone) \
                           + ',' + str(fbase) + ',' + str(object.name) + ',' + str(object.team) + ',' + str(object.right) \
                           + ',' + str(object.left) + ',' + str(object.forward) + ',' + str(object.backward) + ',' + str(object.lifes) \
                           + ',' + str(object.shots) + ',' + str(object.shotsRec) + ',' + str(object.basesCaught) + \
                           ',' + str(object.basesCaughtRecord) + ',' + str(object.numPenalties) + ',' + (','.join(object.penalties)) + object.penaltiesRecord

        else:
            sock_msg = str(dredAlives) + ',' + str(dblueAlives) + ',' + str(bred) + ',' + str(bblue) + ',' + winner + ',' + str(fdrone) \
                    + ',' + str(fbase) +',' + str(object.name) + ',' + str(object.team) + ',' + str(object.right) \
                    + ',' + str(object.left) + ',' + str(object.forward) + ',' + str(object.backward) + ',' + str(object.lifes) \
                    + ',' + str(object.shots) + ',' + str(object.shotsRec) + ',' + str(object.basesCaught) \
                    + str(object.basesCaughtRecord) + ',' + str(object.numPenalties) + ',' + (','.join(object.penalties)) + object.penaltiesRecord
    elif fbase:
        # msg: dredAlives, dblueAlives, bred, bblue, winner, fdrone, fbase, name, team, timesConquered, conqRecord[]
        sock_msg = str(dredAlives) + ',' + str(dblueAlives) + ',' + str(bred) + ',' + str(bblue) + ',' + winner \
                   + ',' + str(fdrone) + ',' + str(fbase) +  ',' + str(object.name) + ',' + str(object.team) + ',' \
                   + str(object.timesConquered) + ',' + object.conqRecord

    # Initial game values: code 0,0
    else:
        #msg: dredAlives, dblueAlives, bred, bblue, winner, fdrone, fbase, initDronesPlaying, initRedDronesPlaying,
        # initBlueDronesPlaying, initBasesPlaying, initBlueBasesPlaying, initRedBasesPlaying
        sock_msg = str(dredAlives) + ',' + str(dblueAlives) + ',' + str(bred) + ',' + str(bblue) + ',' + winner + ',' + str(fdrone) \
                    + ',' + str(fbase) + ',' + str(initDronesPlaying) + ',' + str(initRedDronesPlaying) + ',' + str(initBlueDronesPlaying) \
                    + ',' + str(initBasesPlaying) + ',' + str(initBlueBasesPlaying) + ',' + str(initRedBasesPlaying)
    sock.send(sock_msg)
    #print("socket: msg sent")
    #print(sock_msg)
    sock.close()
    #print("Web page socket not available")

    #if the socket still opened we must close it
    try:
        sock.close()
    except:
        pass

def gameOver():
    tagtosend = "GOVER"
    msgtosend = "GOVER"
    sendMessage(tagtosend, msgtosend)
    clientServer.disconnect()
    clientServer.loop_stop()
    global winner, bblue, bred, dblueAlives, dredAlives
    if dredAlives == 0 and dblueAlives > 0:
        winner = "BLUE"
    elif dblueAlives == 0 and dredAlives > 0:
        winner = "RED"
    elif bred == 0 and bblue > 0:
        winner = "BLUE"
    elif bblue == 0 and bred > 0:
        winner = "RED"
    sendMessage("Ginfo", "Winner team: " + winner)
    print "Winner team: " + winner
def subscribePlayer(message):
    global dicBase, dicController, dicDrone, dblueAlives, dredAlives, bred, bblue, initBasesPlaying, \
    initRedBasesPlaying, initBlueBasesPlaying, initDronesPlaying, initRedDronesPlaying, initBlueDronesPlaying
    msg = message.split(",")
    valid = False
    if msg[0].find("base") != -1 and len(msg) == 2:
        # [baseName, team]
        if not (msg[0] in dicBase):
            if msg[1] == "red":
                bred += 1
                valid = True
                initBasesPlaying += 1
                initRedBasesPlaying += 1
            elif msg[1] == "blue":
                bblue += 1
                valid = True
                initBasesPlaying += 1
                initBlueBasesPlaying += 1
            else:
                sendMessage("Ginfo", "Err: " + msg[0] + ": team is not valid")
            if valid:
                dicBase[msg[0]] = c.Base(msg[0], msg[1])
                sendMessage("Ginfo", msg[0] + " signed up")
                updateWeb(0, 1, dicBase[msg[0]])
                updateWeb(0, 0, object)
        else:
            sendMessage("Ginfo", "Err: " + msg[0] + " was already signed up")

    elif msg[0].find("controller") != -1 and len(msg) == 3:
        # [controllerName, team, drone]
        if not (msg[0] in dicController):
            if msg[1] == "red":
                valid = True
            elif msg[1] == "blue":
                valid = True
            else:
                sendMessage("Ginfo", "Err: " + msg[0] + ": team is not valid")
            if valid:
                dicController[msg[0]] = c.Controller(msg[0], msg[1], msg[2], 1, 1, 1, 1)
                sendMessage("Ginfo", msg[0] + " signed up")
        else:
                sendMessage("Ginfo", "Err: " + msg[0] + " was already signed up")

    elif msg[0].find("drone") != -1 and len(msg) == 3:
            # [droneName, team, controller]
        if not (msg[0] in dicDrone):
            if msg[1] == "red":
                dredAlives += 1
                valid = True
                initDronesPlaying += 1
                initRedDronesPlaying += 1
            elif msg[1] == "blue":
                dblueAlives += 1
                valid = True
                initDronesPlaying += 1
                initBlueDronesPlaying += 1
            else:
                sendMessage("Ginfo", "Err: " + msg[0] + ": team is not valid")
            if valid:
                dicDrone[msg[0]] = c.Drone(msg[0], msg[1], msg[2], 1, 1, 1, 1, initDroneLifes)
                sendMessage("Ginfo", msg[0] + " signed up")
                updateWeb(1, 0, dicDrone[msg[0]])
                updateWeb(0, 0, object)
        else:
            sendMessage("Ginfo", "Err: " + msg[0] + " was already signed up")
def applyPenaltyTime(side, dhurt):
    global penaltyTime
    try:
        updateWeb(1, 0, dhurt)
        time.sleep(penaltyTime)
        if side == "right":
            dhurt.right = 1
        elif side == "left":
            dhurt.left = 1
        elif side == "forward":
            dhurt.forward = 1
        elif side == "backward":
            dhurt.backward = 1
        dhurt.penalties.remove(side)
        dhurt.numPenalties -= 1
        tagtosend = "MOVEMENT"
        msgtosend = tagtosend + "," + str(dhurt.controller) + "," + str(dhurt.right) + "," + str(dhurt.left) + "," + str(dhurt.forward) + "," + str(dhurt.backward) + "," + "penalty"
        sendMessage(tagtosend, msgtosend)
        updateWeb(1, 0, dhurt)
    except:
        print("In APPLY PENALTY TIME, error in Update Web")
def applyProtocol(tag,message):
    global dicBase, dicController, dicDrone, dblueAlives, dredAlives, bred, bblue
    msg = message.split(",")
    if str(tag) == "FIRE":
        #<FIRE,droneT,droneS,weapon,side>
        if len(msg) == 5:
            if msg[1] in dicDrone and msg[2] in dicDrone:
                dhurt = dicDrone[msg[1]]
                dshooter = dicDrone[msg[2]]
                if not dhurt.team == dshooter.team and not dshooter.isDead() and not dhurt.isDead():
                    side = ""
                    actualTime = time.strftime("%H:%M:%S")
                    dhurt.lifes -= 1
                    if msg[4] == "right":
                        dhurt.right = 0
                        side = "right"
                    elif msg[4] == "left":
                        dhurt.left = 0
                        side = "left"
                    elif msg[4] == "forward":
                        dhurt.forward = 0
                        side = "forward"
                    elif msg[4] == "backward":
                        dhurt.backward = 0
                        side = "backward"
                    dhurt.numPenalties += 1
                    dhurt.penalties.append(side)
                    dhurt.penaltiesRecord += "," + actualTime + "," + side + ',' + dshooter.name + ',' + str(msg[3])
                    dhurt.shotsRec += 1
                    dshooter.shots += 1
                    #answering
                    tagtosend = "MOVEMENT"
                    msgtosend = tagtosend + "," + str(dhurt.controller) + "," + str(dhurt.right) + "," + str(dhurt.left) + "," + str(dhurt.forward) + "," + str(dhurt.backward) + "," + str(msg[3])
                    sendMessage(tagtosend, msgtosend)
                    tagtosend = "LED"
                    msgtosend = tagtosend + "," + str(dhurt.name) + "," + str(dhurt.right) + "," + str(dhurt.left) + "," + str(dhurt.forward) + "," + str(dhurt.backward)
                    sendMessage(tagtosend, msgtosend)
                    if dhurt.isDead():
                        global dblueAlives, dredAlives
                        if dhurt.team == "blue":
                            dblueAlives -= 1
                        elif dhurt.team == "red":
                            dredAlives -= 1
                        tagtosend = "DEAD"
                        msgtosend = str(tagtosend) + "," + str(dhurt.controller) + "," + str(dhurt.name)
                        sendMessage(tagtosend, msgtosend)
                        if dblueAlives == 0 or dredAlives == 0:
                            gameOver()
                    thread.start_new_thread(applyPenaltyTime, (side, dhurt))
                    #updating web statistics
                    try:
                        updateWeb(1, 0, dhurt)
                        updateWeb(1, 0, dshooter)
                    except:
                        print("In FIRE, error in Update Web")
            else:
                sendMessage("Ginfo", "Err: fire from a not signed up dron")
        else:
            print "invalid message"
    if str(tag) == "CATCH":
        #<CATCH,base,drone>
        if len(msg) == 3:
            global bblue, bred
            if msg[1] in dicBase and msg[2] in dicDrone:
                auxBase = dicBase[msg[1]]
                auxDrone = dicDrone[msg[2]]
                if not auxDrone.team == auxBase.team and not auxDrone.isDead():
                    #anwering
                    actualTime = time.strftime("%H:%M:%S")
                    auxBase.conqRecord += "," + actualTime +","+ auxDrone.team + "," + auxDrone.name
                    auxDrone.basesCaught += 1
                    auxDrone.basesCaughtRecord += "," + auxBase.name + "," + actualTime
                    auxBase.timesConquered += 1
                    auxBase.team = auxDrone.team
                    tagtosend = "CBASE"
                    msgtosend = tagtosend + "," + auxBase.name + "," + auxDrone.team
                    sendMessage(tagtosend, msgtosend)
                    if auxDrone.team == "blue":
                        bblue += 1
                        bred -= 1
                    elif auxDrone.team == "red":
                        bblue -= 1
                        bred += 1
                    if bblue == 0 or bred == 0:
                        gameOver()
                    try:
                        updateWeb(0, 1, auxBase)
                        updateWeb(1, 0, auxDrone)
                    except:
                        print("In CATCH, error in Update Web")

            else:
                sendMessage("Ginfo", "Err: CATCH from a not signed up dron or base")
        else:
            print "invalid message"

#Connection
clientServer = mqtt.Client("ClientServer")
#binding callbacks
clientServer.on_connect = on_connect
clientServer.on_subscribe = on_subscribe
clientServer.on_message = on_message
#defining tags to connect
clientServer.connect(broker)
#subscribing on tags
tags = ["FIRE", "CATCH", "WantToPlay"]
subscribeTags(clientServer, tags)
clientServer.loop_forever()




