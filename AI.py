import random, copy, os, pygame, sys
from pygame.locals import *

DEGREES_IN_CIRCLE = 360

class Obstacle:
    '''
        In order to initialize the AI object you must give in the
        position the AI will start in, size of the AI's image,
        the image that represents the AI, and the damage that
        the obstacle is capable of dealing.

        Both the size and pos paramaters must be ordered pairs (tuples). 
        e.g. (0,0), (50,50), etc
    '''	    	
	
    def __init__(self,pos,size,image):
        self.image = image
        self.facing = 'right'

        self.xPos = pos[0]
        self.yPos = pos[1]
        self.width = size[0]
        self.height = size[1]        
		
    # Here, we have the collision boundaries
    def get_rect(self):
        return pygame.Rect((self.xPos, self.yPos, self.width, self.height))

    def getPosition(self):        
        return (self.xPos, self.yPos)

    # Is the obstacle touching a particular object?
    def isTouching(self, x, y, endRangeX, endRangeY):
        if (int(self.xPos) in range(int(x), int(endRangeX)) and (int(self.yPos) in range(int(y), int(endRangeY)))):            
            return True            
        return False

# Stationary obstacles
class stationaryObstacle(Obstacle):
    
    def __init__(self,pos,size,image):
        return Obstacle.__init__(self, pos, size, image)

class spikes(stationaryObstacle):
    
    def __init__(self,pos,size,image):
        return stationaryObstacle.__init__(self, pos, size, image)

class treeLog(stationaryObstacle):

    def __init__(self,pos,size,image):
        return stationaryObstacle.__init__(self, pos, size, image)

# Obstacles that are set into motion when triggered
class triggeredObstacle(Obstacle):

    def __init__(self,pos,size,image):
        self.triggerDelay = 0
        return Obstacle.__init__(self, pos, size, image)

    def move(self, xIncrement, yIncrement): 
        self.xPos += xIncrement
        self.yPos += yIncrement

class bananaPeel(triggeredObstacle):

    def __init__(self,pos,size,image):
        self.xSpeed = 2.5
        self.ySpeed = 2.5
        self.rotation = 0
        self.slippedOn = False
        # Properties of time concerned with the last slip with this object
        self.slipTimeCounter = 0
        self.slipRiseTime = 50
        # Properties of gravity that dictate the banana peel's triggered movement
        self.gravityForce = 1
        self.gravityXCarry = -1
        return triggeredObstacle.__init__(self, pos, size, image)

    def slipRotate(self, gameFloor, rotateIncrementInit, rotateIncrementFall):
        if (self.slipTimeCounter < self.slipRiseTime and self.slippedOn):
            self.rotation += rotateIncrementInit
            return (self.rotation)
        else:
            # Did we already hit the floor?
            if (self.yPos >= gameFloor):
                self.rotation = 0
            else:
                self.rotation += rotateIncrementFall                
            return (self.rotation)

    def doBananaPeelGravity(self, obj, floor, downAccel):
        if self.yPos < floor:
            self.move(self.gravityXCarry, 0)
            # Settings on the gravity, so we have acceleration.
            self.gravityForce += (self.gravityForce * downAccel)
            self.move(0, self.gravityForce)

    def doBananaPeelAction(self, obj, gameFloor, gravAccel, winWidth):
        if (self.isTouching(obj.x, obj.y, obj.x + obj.width, obj.y + obj.height) and self.slippedOn == False):
            self.slippedOn = True

        if (self.slippedOn and self.slipTimeCounter < self.slipRiseTime):            
            self.slipTimeCounter += 1            
            self.move(-self.xSpeed, -self.ySpeed)
        else:
            # This is the point where the banana peel reaches its maximum height
            if (self.slipTimeCounter >= self.slipRiseTime):                
                self.doBananaPeelGravity(obj, gameFloor, gravAccel)                
                if (self.yPos >= gameFloor):
                    self.slippedOn = False
                    self.slipTimeCounter = 0
                    self.gravityForce = 1
                    

# Obstacles capable of moving on their own
class movingObstacle(Obstacle):

    def __init__(self,pos,size,image):        
        return Obstacle.__init__(self, pos, size, image)

    # Accepts a surface image to flip. "hori" and "vert" are booleans.
    def reflectOff(image, hori, vert):
        return pygame.transform.flip(image, hori, vert)

    def move(self, xIncrement, yIncrement): 
        self.xPos += xIncrement
        self.yPos += yIncrement        


class soccerBall(movingObstacle):        
    
    def __init__(self,pos,size,image,moveMode):
        self.soccerMoveMode = moveMode
        self.speed = 1
        self.gravityForce = 1
        self.rotation = 0
        return movingObstacle.__init__(self, pos, size, image)

    '''
        Rotate the soccer ball every certain amount of degree specified,
        depending on what direction the soccer ball is currently moving.
    '''        
    def soccerBallRotate(self, rotateIncrement):
        if self.soccerMoveMode == 'left':
            self.rotation += 1
            if self.rotation == DEGREES_IN_CIRCLE:
                self.rotation = 0
        elif self.soccerMoveMode == 'right':
            self.rotation -= 1
            if self.rotation == DEGREES_IN_CIRCLE:
                self.rotation = 0
        return self.rotation

    def doSoccerBallPhysics(self, obj, floor, downAccel):
        if self.yPos < floor:
            self.move(0, self.speed)
            # Settings on the gravity, so we have acceleration.
            self.gravityForce += (self.gravityForce * downAccel)
            self.move(0, self.gravityForce)
        else:
            self.gravityForce = 1

    def doSoccerBallAction(self, obj, gameFloor, gravAccel, winWidth):        

        # Soccer ball physics includes the gravity aspect of the ball.
        self.doSoccerBallPhysics(obj, gameFloor, gravAccel)

        # Testing for when to switch direction of the ball.
        if self.xPos == 0:
            self.soccerMoveMode = 'right'
        elif self.soccerMoveMode == 'left' and self.isTouching(obj.x, obj.y, obj.x + obj.width, obj.y + obj.height):
            self.soccerMoveMode = 'right'
        elif self.xPos == winWidth:
            self.soccerMoveMode = 'left'
        elif self.soccerMoveMode == 'right' and self.isTouching(obj.x, obj.y, obj.x + obj.width, obj.y + obj.height):
            self.soccerMoveMode = 'left'

        # Move the soccer ball in accordance to the current direction it has on now.
        if self.soccerMoveMode == 'right':
            self.move(1, 0)
        elif self.soccerMoveMode == 'left':
            self.move(-1, 0)

            