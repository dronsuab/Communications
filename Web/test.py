from flask import Flask
from flask import request
from flask import render_template
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

def refreshData(redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner, dicBase):

    print dicBase["TestBase"].name.value

if __name__ == '__main__':
    dicBase["TestBase"] = c.Base("testBase","red")
    print dicBase['TestBase'].name.value
    p = Process(target=refreshData, args=(redDronesAlive, blueDronesAlive, redBasesConquered, blueBasesConquered, winner, dicBase))
    p.start()
