from multiprocessing import Value, Array
class Drone:
    def __init__(self, name, team, right, left, forward, backward, lives, shots, shotsRec, basesCaught, basesCaughtRecord):
        self.name = name
        self.team = team
        self.right = right
        self.left = left
        self.forward = forward
        self.backward = backward
        self.lives = lives
        self.shots = 0
        self.shotsRec = 0
        self.basesCaught = 0
        self.basesCaughtRecord = basesCaughtRecord
    def isDead(self):
        if self.lives <= 0:
            return True
        else:
            return False
class Base:
    def __init__(self, name, team, timesConquered, conqRecord):
        self.name = name
        self.team = team
        self.conqRecord = conqRecord
        self.timesConquered = timesConquered