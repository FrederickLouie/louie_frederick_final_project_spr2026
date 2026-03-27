import pygame
import random
from settings import *
from utils import distance


class Player:

    def __init__(self):
        self.rect = pygame.Rect(50,50,PLAYER_SIZE,PLAYER_SIZE)

    # WASD control
    def move(self, keys):
        if keys[pygame.K_w]:
            self.rect.y -= PLAYER_SPEED

        if keys[pygame.K_s]:
            self.rect.y += PLAYER_SPEED

        if keys[pygame.K_a]:
            self.rect.x -= PLAYER_SPEED

        if keys[pygame.K_d]:
            self.rect.x += PLAYER_SPEED


class Coin:

    def __init__(self):

        x = random.randint(100, WIDTH-100)
        y = random.randint(100, HEIGHT-100)

        self.rect = pygame.Rect(x,y,15,15)


class Mob:

    def __init__(self, path):

        self.path = path
        self.target = 1

        self.rect = pygame.Rect(path[0][0],path[0][1],MOB_SIZE,MOB_SIZE)

    def move(self):

        target = self.path[self.target]

        dx = target[0] - self.rect.x
        dy = target[1] - self.rect.y

        # using the distance function defined in utils
        dist = distance(self.rect.x,self.rect.y,target[0],target[1])

        if dist < 3:
            self.target = (self.target + 1) % len(self.path)

        else:
            self.rect.x += MOB_SPEED * dx/dist
            self.rect.y += MOB_SPEED * dy/dist

    # if player in mob's radius
    def sees_player(self, player):

        d = distance(
            self.rect.centerx,
            self.rect.centery,
            player.rect.centerx,
            player.rect.centery
        )

        return d < MOB_VISION