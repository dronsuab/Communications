class Drone:
    def __init__(self, name, team, controller, right, left, forward, backward, lifes):
        self.name = name
        self.team = team
        self.controller = controller
        self.right = right
        self.left = left
        self.forward = forward
        self.backward = backward
        self.lifes = lifes
        self.shots = 0
        self.shotsRec = 0
        self.basesCaught = 0

    def isDead(self):
        if self.lifes <= 0:
            return True
        else:
            return False
class Base:
    def __init__(self, name, team):
        self.name = name
        self.team = team
class Controller:
    def __init__(self, name, drone, team, right, left, forward, backward):
        self.name = name
        self.drone = drone
        self.team = team
        self.right = right
        self.left = left
        self.forward = forward
        self.backward = backward
        self.dead = False
