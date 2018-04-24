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
bred = 0
bblue = 0
penaltyTime = 10
winner = "Unknown"
broker = "172.20.10.2"
#broker = "192.168.1.3"
#dic with players
dicBase = {}
dicDrone = {}
dicController = {}
#defining callbacks
def on_connect(client, userdata, flags, rc):
   if rc == 0:
       print "connection successful"
   else:
       print "connection refused, rc = " + rc
def on_subscribe(client, userdata, mid, granted_qos):
    pass
def on_message(client, userdata, message):
    if message.topic == "WantToPlay":
        subscribePlayer(message.payload)
    else:
        applyProtocol(message.topic, message.payload)
    updateWeb()

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

def updateWeb():
    try:
        sock = socket.socket()
        sock.connect(("localhost", 9999))
        #msg: dredAlives,dblueAlives,bred, bblue,winner
        sock_msg = str(dredAlives)+','+str(dblueAlives)+','+str(bred)+','+str(bblue) +','+winner
        sock.send(sock_msg)
        print("socket: msg sent")
        sock.close()
    except:
        print("Web page socket not available")
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
def applyPenaltyTime(side, dhurt):
    global penaltyTime
    time.sleep(penaltyTime)
    if side == "right":
        dhurt.right = 1
    elif side == "left":
        dhurt.left = 1
    elif side == "forward":
        dhurt.forward = 1
    elif side == "backward":
        dhurt.backward = 1

    tagtosend = "MOVEMENT"
    msgtosend = tagtosend + "," + str(dhurt.controller) + "," + str(dhurt.right) + "," + str(dhurt.left) + "," + str(dhurt.forward) + "," + str(dhurt.backward) + "," + "penalty"
    sendMessage(tagtosend, msgtosend)

def subscribePlayer(message):
    global dicBase, dicController, dicDrone, dblueAlives, dredAlives, bred, bblue
    msg = message.split(",")
    valid = False
    if msg[0].find("base") != -1 and len(msg) == 2:
        # [baseName, team]
        if not (msg[0] in dicBase):
            if msg[1] == "red":
                bred += 1
                valid = True
            elif msg[1] == "blue":
                bblue += 1
                valid = True
            else:
                sendMessage("Ginfo", "Err: " + msg[0] + ": team is not valid")
            if valid:
                dicBase[msg[0]] = c.Base(msg[0], msg[1])
                sendMessage("Ginfo", msg[0] + " signed up")
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
            elif msg[1] == "blue":
                dblueAlives += 1
                valid = True
            else:
                sendMessage("Ginfo", "Err: " + msg[0] + ": team is not valid")
            if valid:
                dicDrone[msg[0]] = c.Drone(msg[0], msg[1], msg[2], 1, 1, 1, 1, initDroneLifes)
                sendMessage("Ginfo", msg[0] + " signed up")
        else:
            sendMessage("Ginfo", "Err: " + msg[0] + " was already signed up")
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

                    #answering
                    tagtosend = "MOVEMENT"
                    msgtosend = tagtosend + "," + str(dhurt.controller) + "," + str(dhurt.right) + "," + str(dhurt.left) + "," + str(dhurt.forward) + "," + str(dhurt.backward) + "," + str(msg[3])
                    sendMessage(tagtosend, msgtosend)
                    thread.start_new_thread(applyPenaltyTime,(side,dhurt))

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




