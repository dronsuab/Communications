from multiprocessing import Value, Array
class Drone:
    def __init__(self, name, team, right, left, forward, backward, lives, shots, shotsRec, basesCaught):
        self.name = Array('c', name)
        self.team = Array('c', team)
        self.right = Value('i',right)
        self.left = Value('i',left)
        self.forward = Value('i',forward)
        self.backward = Value('i',backward)
        self.lives = Value('i',lives)
        self.shots = Value('i',shots)
        self.shotsRec = Value('i', shotsRec)
        self.basesCaught = Value('i', basesCaught)
    def isDead(self):
        if self.lives.value <= 0:
            return True
        else:
            return False
class Base:
    def __init__(self, name, team):
        self.name = Array('c', name)
        self.team = Array('c', team)

