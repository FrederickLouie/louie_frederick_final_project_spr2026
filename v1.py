# ORGINAL (V1 - VERSION 1)

import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Runaway Escapee")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (200,50,50)
GREEN = (50,200,50)
YELLOW = (255,215,0)
BLUE = (50,50,255)
GRAY = (100,100,100)

player = pygame.Rect(50, 50, 30, 30)
player_speed = 4

coins = []
TOTAL_COINS = 8
coins_collected = 0

for i in range(TOTAL_COINS):
    x = random.randint(100, WIDTH-100)
    y = random.randint(100, HEIGHT-100)
    coins.append(pygame.Rect(x,y,15,15))

gate = pygame.Rect(WIDTH-120, HEIGHT//2-50, 20,100)

# CAR STARTS OFF SCREEN
car = pygame.Rect(WIDTH+100, HEIGHT//2-20, 60,40)
car_active = False
car_speed = 3

jail = pygame.Rect(WIDTH//2-40, HEIGHT//2-40, 80,80)

class Mob:
    def __init__(self, path):
        self.rect = pygame.Rect(path[0][0], path[0][1], 30,30)
        self.path = path
        self.target = 1
        self.speed = 2
        self.vision = 120

    def move(self):
        target_pos = self.path[self.target]

        dx = target_pos[0] - self.rect.x
        dy = target_pos[1] - self.rect.y

        dist = math.hypot(dx,dy)

        if dist < 2:
            self.target = (self.target + 1) % len(self.path)
        else:
            self.rect.x += self.speed * dx/dist
            self.rect.y += self.speed * dy/dist

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)
        pygame.draw.circle(screen, RED, self.rect.center, self.vision,1)

    def sees_player(self):
        distance = math.hypot(player.centerx-self.rect.centerx,
                              player.centery-self.rect.centery)
        return distance < self.vision

mobs = [
    Mob([(200,200),(400,200),(400,400),(200,400)]),
    Mob([(600,100),(750,100),(750,300),(600,300)])
]

MAX_SEEN_TIME = 60
seen_timer = MAX_SEEN_TIME

caught = False
escaped = False

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if not caught and not escaped:

        if keys[pygame.K_w]: player.y -= player_speed
        if keys[pygame.K_s]: player.y += player_speed
        if keys[pygame.K_a]: player.x -= player_speed
        if keys[pygame.K_d]: player.x += player_speed

    player.clamp_ip(screen.get_rect())

    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            coins_collected += 1

    if coins_collected == TOTAL_COINS:
        car_active = True

    if coins_collected < TOTAL_COINS:
        if player.colliderect(gate):
            if player.x > gate.x:
                player.x = gate.x + gate.width

    mob_sees = False

    for mob in mobs:
        mob.move()
        if mob.sees_player():
            mob_sees = True

    if mob_sees:
        seen_timer -= 1
    else:
        seen_timer = min(MAX_SEEN_TIME, seen_timer + 2)

    if seen_timer <= 0 and not caught:
        caught = True
        player.center = jail.center

    # CAR DRIVING ANIMATION
    if car_active and car.x > WIDTH-150:
        car.x -= car_speed

    if car_active and player.colliderect(car):
        escaped = True

    screen.fill(GRAY)

    pygame.draw.rect(screen, BLUE, player)

    for coin in coins:
        pygame.draw.circle(screen, YELLOW, coin.center, 7)

    for mob in mobs:
        mob.draw()

    if coins_collected < TOTAL_COINS:
        pygame.draw.rect(screen, BLACK, gate)

    # DRAW CAR
    if car_active:
        pygame.draw.rect(screen, GREEN, car)

        # SPEECH BUBBLE
        bubble_rect = pygame.Rect(car.x-20, car.y-50, 120,40)
        pygame.draw.rect(screen, WHITE, bubble_rect)
        pygame.draw.rect(screen, BLACK, bubble_rect,2)

        bubble_text = font.render("Come over here!", True, BLACK)
        screen.blit(bubble_text,(bubble_rect.x+5,bubble_rect.y+10))

    pygame.draw.rect(screen, BLACK, jail,2)

    coin_text = font.render(f"Coins: {coins_collected}/{TOTAL_COINS}", True, WHITE)
    screen.blit(coin_text,(20,20))

    if mob_sees and not caught:
        seconds_left = round(seen_timer/60,1)
        warn = font.render(f"ESCAPE VISION! {seconds_left}s", True, RED)
        screen.blit(warn,(WIDTH//2-100,20))

    if caught:
        text = font.render("Captured! You are in jail. Mission Failed.", True, WHITE)
        screen.blit(text,(WIDTH//2-200, HEIGHT//2+60))

    if escaped:
        text = font.render("Your apprentice picked you up! Escape successful!", True, WHITE)
        screen.blit(text,(WIDTH//2-230, HEIGHT//2))

    pygame.display.update()

pygame.quit()