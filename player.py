import random, copy, os, pygame, sys
from pygame.locals import *

class Player:
    '''
        In order to initialize the player object you must give in the
        position the player will start in, size of the player's image
        and the image that represents the player.

        Both the size and pos paramaters must be ordered pairs. 
        e.g. (0,0), (50,50), etc
    '''
    def __init__(self,pos,size,image):
        self.image = image
        self.facing = 'right'

        self.x = pos[0]
        self.y = pos[1]
        self.width = size[0]
        self.height = size[1]

    def get_rect(self):
        return pygame.Rect((self.x, self.y, self.width, self.height))