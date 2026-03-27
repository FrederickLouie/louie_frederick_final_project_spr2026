import pygame
from settings import *
import random
import math

pygame.init()

def load_assets():
    pass


def create_game_objects():
    player = pygame.Rect(50, 50, 30, 30)

    coins = []
    for i in range(TOTAL_COINS):
        x = random.randint(100, WIDTH-100)
        y = random.randint(100, HEIGHT-100)
        coins.append(pygame.Rect(x, y, 15, 15))

    gate = pygame.Rect(WIDTH-120, HEIGHT//2-50, 20, 100)
    car = pygame.Rect(WIDTH+100, HEIGHT//2-20, 60, 40)
    jail = pygame.Rect(WIDTH//2-40, HEIGHT//2-40, 80, 80)

    return player, coins, gate, car, jail


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

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)
        pygame.draw.circle(screen, RED, self.rect.center, self.vision,1)

    def sees_player(self, player):
        distance = math.hypot(player.centerx-self.rect.centerx,
                              player.centery-self.rect.centery)
        return distance < self.vision


def create_mobs():
    return [
        Mob([(200,200),(400,200),(400,400),(200,400)]),
        Mob([(600,100),(750,100),(750,300),(600,300)]),
        Mob([(400,400),(500,100),(600,200),(200,400)])
    ]


def handle_input(player, speed, keys):
    if keys[pygame.K_w]: player.y -= speed
    if keys[pygame.K_s]: player.y += speed
    if keys[pygame.K_a]: player.x -= speed
    if keys[pygame.K_d]: player.x += speed


def update_coins(player, coins):
    collected = 0
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            collected += 1
    return collected


def update_mobs(mobs, player):
    sees = False
    for mob in mobs:
        mob.move()
        if mob.sees_player(player):
            sees = True
    return sees


def update_car(car, active):
    if active and car.x > WIDTH-150:
        car.x -= 3


def draw_game(screen, player, coins, mobs, gate, car, jail, car_img,
              coins_collected, seen_timer, mob_sees, caught, escaped,
              font, car_active, current_time, best_time):

    screen.fill(GRAY)

    pygame.draw.rect(screen, BLUE, player)

    for coin in coins:
        pygame.draw.circle(screen, YELLOW, coin.center, 7)

    for mob in mobs:
        mob.draw(screen)

    if coins_collected < TOTAL_COINS:
        pygame.draw.rect(screen, BLACK, gate)

    if car_active:
        pygame.draw.rect(screen, GREEN, car)

        bubble_rect = pygame.Rect(car.x-20, car.y-50, 120,40)
        pygame.draw.rect(screen, WHITE, bubble_rect)
        pygame.draw.rect(screen, BLACK, bubble_rect,2)

        bubble_text = font.render("Come over here!", True, BLACK)
        screen.blit(bubble_text,(bubble_rect.x+5,bubble_rect.y+10))

    pygame.draw.rect(screen, BLACK, jail,2)

    # COINS
    coin_text = font.render(f"Coins: {coins_collected}/{TOTAL_COINS}", True, WHITE)
    screen.blit(coin_text,(20,20))

    # TIMER
    display_time = 0 if current_time is None else round(current_time, 2)
    time_text = font.render(f"Time: {display_time}s", True, WHITE)
    screen.blit(time_text, (20, 60))

    # BEST TIME
    if best_time is not None:
        best_text = font.render(f"Best: {round(best_time, 2)}s", True, WHITE)
        screen.blit(best_text, (20, 100))

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


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Runaway Escapee")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    car_img = load_assets()

    best_time = None

    def reset_game():
        player, coins, gate, car, jail = create_game_objects()
        mobs = create_mobs()

        return {
            "player": player,
            "coins": coins,
            "gate": gate,
            "car": car,
            "jail": jail,
            "mobs": mobs,
            "coins_collected": 0,
            "car_active": False,
            "seen_timer": 60,
            "caught": False,
            "escaped": False,
            "start_time": pygame.time.get_ticks(),  # ⭐ TIMER START
            "final_time": None
        }

    state = reset_game()

    player_speed = 4
    MAX_SEEN_TIME = 60

    running = True

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    state = reset_game()

        keys = pygame.key.get_pressed()

        # unpack
        player = state["player"]
        coins = state["coins"]
        gate = state["gate"]
        car = state["car"]
        jail = state["jail"]
        mobs = state["mobs"]
        coins_collected = state["coins_collected"]
        car_active = state["car_active"]
        seen_timer = state["seen_timer"]
        caught = state["caught"]
        escaped = state["escaped"]
        start_time = state["start_time"]
        final_time = state["final_time"]

        game_over = caught or escaped

        # TIMER CALC
        if not game_over:
            current_time = (pygame.time.get_ticks() - start_time) / 1000
        else:
            current_time = final_time

        # PLAYER
        if not game_over:
            handle_input(player, player_speed, keys)

        player.clamp_ip(screen.get_rect())

        # COINS
        if not game_over:
            coins_collected += update_coins(player, coins)

        if coins_collected == TOTAL_COINS:
            car_active = True

        # GATE
        if coins_collected < TOTAL_COINS:
            if player.colliderect(gate) and player.x > gate.x:
                player.x = gate.x + gate.width

        # MOBS
        if not game_over:
            mob_sees = update_mobs(mobs, player)
        else:
            mob_sees = False

        # SEEN TIMER
        if not game_over:
            if mob_sees:
                seen_timer -= 1
            else:
                seen_timer = min(MAX_SEEN_TIME, seen_timer + 2)

        # CAUGHT / ESCAPE
        if not game_over:
            if seen_timer <= 0:
                caught = True
                player.center = jail.center

            if car_active and player.colliderect(car):
                escaped = True
                final_time = (pygame.time.get_ticks() - start_time) / 1000

                if best_time is None or final_time < best_time:
                    best_time = final_time

        # CAR
        if not game_over:
            update_car(car, car_active)

        # SAVE STATE
        state.update({
            "coins_collected": coins_collected,
            "car_active": car_active,
            "seen_timer": seen_timer,
            "caught": caught,
            "escaped": escaped,
            "final_time": final_time
        })

        # DRAW
        draw_game(screen, player, coins, mobs, gate, car, jail, car_img,
                  coins_collected, seen_timer, mob_sees, caught, escaped,
                  font, car_active, current_time, best_time)

        if game_over:
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - 120, HEIGHT//2 + 100))

        pygame.display.update()

    pygame.quit()


TOTAL_COINS = 8

if __name__ == "__main__":
    main()