from flask import Flask
from flask import request
from flask import render_template
from multiprocessing import Process, Value, Array, Manager
import socket
import clases as c
import operator

def sortdict(d):
    l =  sorted(d.items(), key=operator.itemgetter(0))
    sortedDict = {}
    for tup in l:
        sortedDict[tup[0]]= tup[1]
    return sortedDict

if __name__ == "__main__":

    d = {"drone2":2, "drone1":3}
    sortedD = sortdict(d)
    for k in sortedD:
        print k + "," + str(sortedD[k])