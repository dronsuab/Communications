import paho.mqtt.client as mqtt
import threading
import sys
global myself
global myteam
global mycontroller
global mydrone
global tags

stop = False

broker = "172.20.10.9"
def printMenu():
    global mycontroller, myself, myteam, mydrone, tags
    '''Prints test menu
        :returns 1 if drone, 2 if controller, 3 if base and -1 if wrong'''
    print("-----------------TEST MENU-----------------\n")
    print("1: What are you? (drone, controller or base)\n")
    player = raw_input()
    if player == "drone":
        print("which drone are you? (1,2,3,etc)\n")
        tdrone = raw_input()
        myself = "drone"+tdrone
        print("Which team do you play in? (blue or red)\n")
        myteam = raw_input()
        mycontroller = "controller"+tdrone
        msg = myself + ","+ myteam +","+ mycontroller
        sendMessage("WantToPlay",msg)
        tags = ["GOVER", "DEAD", "LED", "CFIRE"]
        return 1
    elif player == "controller":
        print("which controller are you? (1,2,3,etc)\n")
        tcontroller = raw_input()
        myself = "controller" + tcontroller
        print("Which team do you play in? (blue or red)\n")
        myteam = raw_input()
        mydrone = "drone"+ tcontroller
        msg = myself + "," + myteam + "," + mydrone
        sendMessage("WantToPlay",msg)
        tags = ["MOVEMENT", "DEAD", "GOVER"]
        return 2
    elif player == "base":
        print("Which base are you? (1,2,3,etc)\n")
        tbase = raw_input()
        myself = "base" + tbase
        print("Which team do you play in? (blue or red)\n")
        myteam = raw_input()
        msg = myself + "," + myteam
        sendMessage("WantToPlay", msg)
        tags = ["CBASE", "GOVER"]
        return 3
    else:
        print("Wrong input\n")
        return -1
def droneMenu():
    '''Prints drone test menu'''
    print("Choose an option:\n")
    print("\t 1: I've been fired\n")
    option = raw_input()
    if option == '1' and stop == False:
        print("\t\t Who has shot you?\n")
        shooter = raw_input()
        print("\t\t In which side have you been shot?\n")
        side = raw_input()
        print("\t\t Which weapon?\n")
        weapon = raw_input()
        msg = "FIRE,"+ myself + "," + shooter + "," + weapon + "," + side
        sendMessage("FIRE", msg)
    elif option != '1':
        print("Wrong input\n")

def controllerMenu():
    '''Prints controller test menu'''
    print("Choose an option:\n")
    print("\t 1: I want to shoot!!!\n")
    option = raw_input()
    if option == '1' and stop == False:
        print("\t\t Which weapon do you want to use?\n")
        weapon = raw_input()
        msg = "CFIRE," + myself + "," + weapon
        sendMessage("CFIRE", msg)
    elif option != '1':
        print("Wrong input\n")
def baseMenu():
    '''Prints base test menu'''
    print("Choose an option:\n")
    print("\t 1: I've been caught !!\n")
    option = raw_input()
    if option == '1' and stop == False:
        print("\t\t Who has caught you?\n")
        catcher = raw_input()
        msg = "CATCH," + myself + "," + catcher
        sendMessage("CFIRE", msg)
    elif option != 1:
        print("Wrong input\n")

def sendMessage(tag, msg):
    clientSender = mqtt.Client(myself)
    clientSender.on_connect = on_connect
    clientSender.connect(broker)
    clientSender.loop_start()
    clientSender.publish(tag, msg)
    clientSender.disconnect()
    clientSender.loop_stop()

def on_subscribe(client, userdata, mid, granted_qos):
    pass
def on_connect(client, userdata, flags, rc):
   if rc == 0:
       print "connection successful"
   else:
       print "connection refused, rc = " + rc
def on_message(client, userdata, message):
    global stop
    print("\n/**/MESSAGE RECIVED/**/\n")
    print(message.payload)
    print("\n/**/MESSAGE END/**/\n")
    if message.topic == "GOVER" or message.topic == "DEAD":
        clientListener.loop_stop(True)
        stop = True
        sys.exit(1)
def displayMenus(nextMenu):
    if nextMenu == 1:
        droneMenu()
    elif nextMenu == 2:
        controllerMenu()
    elif nextMenu == 3:
        baseMenu()

if __name__ == "__main__":
    nextMenu = printMenu()
    # Connection
    clientListener = mqtt.Client(myself + "Listener")
    # binding callbacks
    clientListener.on_connect = on_connect
    clientListener.on_subscribe = on_subscribe
    clientListener.on_message = on_message
    # defining tags to connect
    clientListener.connect(broker)
    # subscribing on tags
    for tag in tags:
        clientListener.subscribe(tag)
    while(stop == False):
        #t = threading.Thread(target=displayMenus(nextMenu))
        t2 = threading.Thread(target=clientListener.loop_start())
        t2.start()
        if stop == False:
            t = threading.Thread(target=displayMenus(nextMenu))
            t.setDaemon(True)
            t.start()



