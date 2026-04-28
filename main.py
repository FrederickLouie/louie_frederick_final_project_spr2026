import pygame
from settings import *
import random
import math

pygame.init()

# for sounds
pygame.mixer.init()

# importing sounds
def load_sounds():
    # Use .wav for short sound effects
    return {
        "coin": pygame.mixer.Sound("chieuk_coin_sound.wav"),
    }

# define UI area for boundary checking and drawing
UI_RECT = pygame.Rect(0, 0, 220, 140)

# importing custom made images (Piskel)
def load_assets():
    car_img = pygame.image.load('car_img.png').convert_alpha()
    coin_img = pygame.image.load('money_bag.png').convert_alpha()
    mob_img = pygame.image.load('mob_img.png').convert_alpha()
    player_img = pygame.image.load('player_img.png').convert_alpha()
    
    return (
        pygame.transform.scale(car_img, (120, 100)),
        pygame.transform.scale(coin_img, (40, 40)),
        pygame.transform.scale(mob_img, (65, 65)),
        pygame.transform.scale(player_img, (65, 65))
    )

def create_game_objects():
    # define shapes first so they exist for checking
    gate = pygame.Rect(WIDTH-120, HEIGHT//2-50, 20, 100)
    car = pygame.Rect(WIDTH+100, HEIGHT//2-20, 100, 80)
    jail = pygame.Rect(WIDTH//2-40, HEIGHT//2-40, 80, 80)
    
    player = pygame.Rect(100, 150, 65, 65) 

    coins = []
    for i in range(TOTAL_COINS):
        valid_pos = False
        while not valid_pos:
            x = random.randint(0, WIDTH - 40)
            y = random.randint(0, HEIGHT - 40)
            new_coin = pygame.Rect(x, y, 40, 40)
            
            # check collision with UI, Gate, and Jail to ensure clear spawning
            if not (new_coin.colliderect(UI_RECT) or 
                    new_coin.colliderect(gate) or 
                    new_coin.colliderect(jail)):
                valid_pos = True
                coins.append(new_coin)

    return player, coins, gate, car, jail

    # setting up dimensions 
    gate = pygame.Rect(WIDTH-120, HEIGHT//2-50, 20, 100)
    car = pygame.Rect(WIDTH+100, HEIGHT//2-20, 100, 80)
    jail = pygame.Rect(WIDTH//2-40, HEIGHT//2-40, 80, 80)

    return player, coins, gate, car, jail

class Mob:
    def __init__(self, start_pos):
        self.rect = pygame.Rect(start_pos[0], start_pos[1], 30, 30)
        self.speed = 2.5
        self.vision = 120
        # now this will work because the method is inside the class
        self.destination = self.get_random_target()

    def get_random_target(self):
        # generate a random position within the screen
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT - 50)
        return (x, y)

    def move(self):
        dx = self.destination[0] - self.rect.x
        dy = self.destination[1] - self.rect.y
        dist = math.hypot(dx, dy)

        if dist < 5:
            self.destination = self.get_random_target()
        else:
            self.rect.x += self.speed * dx / dist
            self.rect.y += self.speed * dy / dist

    def draw(self, screen, mob_img):
        screen.blit(mob_img, self.rect.topleft)
        pygame.draw.circle(screen, (255, 0, 0), self.rect.center, self.vision, 1)

    def sees_player(self, player):
        distance = math.hypot(player.centerx - self.rect.centerx,
                              player.centery - self.rect.centery)
        return distance < self.vision

def create_mobs():
    # only pass starting positions now
    return [
        Mob((300, 200)),
        Mob((600, 100)),
        Mob((400, 400))
    ]

def handle_input(player, speed, keys, is_dashing):
    # if dashing, triple the speed, otherwise use normal speed
    current_speed = speed * 3 if is_dashing else speed
    
    if keys[pygame.K_w]: player.y -= current_speed
    if keys[pygame.K_s]: player.y += current_speed
    if keys[pygame.K_a]: player.x -= current_speed
    if keys[pygame.K_d]: player.x += current_speed

# used to update coin counter in top-left UI (?/8 coins collected)
def update_coins(player, coins):
    collected = 0
    for coin in coins[:]:
        if player.colliderect(coin):
            coins.remove(coin)
            collected += 1
    return collected

# used to see if the player is in the mob's radius or not
def update_mobs(mobs, player):
    sees = False
    for mob in mobs:
        mob.move()
        if mob.sees_player(player):
            sees = True
    return sees

# when all coins are collected, car moves
def update_car(car, active):
    if active and car.x > WIDTH-150:
        car.x -= 3

def draw_game(screen, player, coins, mobs, gate, car, jail, car_img, coin_img, mob_img, player_img,
              coins_collected, seen_timer, mob_sees, caught, escaped,
              font, car_active, current_time, best_time, dash_cooldown):

    screen.fill(bg_color)

    # draw UI box and border
    pygame.draw.rect(screen, (30, 30, 30), UI_RECT) 
    pygame.draw.rect(screen, WHITE, UI_RECT, 2)    

    screen.blit(player_img, player.topleft) # applying player image

    for coin in coins:
        screen.blit(coin_img, coin.topleft) # applying coin image

    for mob in mobs:
        mob.draw(screen, mob_img) # applying mob image

    if coins_collected < TOTAL_COINS:
        pygame.draw.rect(screen, gate_color, gate)

    if car_active:
        screen.blit(car_img, (car.x, car.y)) # applying car image
        bubble_width = 200
        bubble_height = 40
        bubble_x = max(10, min(car.x - 20, WIDTH - bubble_width - 10))
        bubble_y = max(10, car.y - 50)
        # display a text bubble telling the player to come over to the car
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        pygame.draw.rect(screen, WHITE, bubble_rect)
        pygame.draw.rect(screen, BLACK, bubble_rect, 2)
        bubble_text = font.render("Come over here!", True, BLACK) 
        screen.blit(bubble_text, (bubble_rect.x + 5, bubble_rect.y + 10))

    pygame.draw.rect(screen, BLACK, jail, 2)

    # establishing UI text (includes coins collected, current time, and best time)
    coin_text = font.render(f"Coins: {coins_collected}/{TOTAL_COINS}", True, WHITE)
    screen.blit(coin_text, (10, 10))

    display_time = 0 if current_time is None else round(current_time, 2)
    time_text = font.render(f"Time: {display_time}s", True, WHITE)
    screen.blit(time_text, (10, 50))

    if best_time is not None:
        best_text = font.render(f"Best: {round(best_time, 2)}s", True, WHITE)
        screen.blit(best_text, (10, 90))


    # draw dash cooldown bar
    bar_width = 200
    bar_x = WIDTH // 2 - bar_width // 2
    bar_y = HEIGHT - 40
    
    # calculate percentage (0 to 1) and clamp it
    cooldown_percent = min(dash_cooldown / 120, 1.0)
    fill_width = int(cooldown_percent * bar_width)
    
    # Background of bar
    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, 20))
    # Filled part
    pygame.draw.rect(screen, BLUE, (bar_x, bar_y, fill_width, 20))
    # Border
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, 20), 2)
    
    dash_text = font.render("Press Q to Dash", True, WHITE)
    screen.blit(dash_text, (bar_x, bar_y - 30))


    # player warning if in mob's radius
    if mob_sees and not caught:
        seconds_left = round(seen_timer/60, 1)
        warn = font.render(f"ESCAPE VISION! {seconds_left}s", True, RED)
        screen.blit(warn, (WIDTH//2-100, 20))

    # player if in mob's radius too long (over the 1 second grace period)
    if caught:
        text = font.render("Captured! You are in jail. Mission Failed.", True, WHITE)
        screen.blit(text, (WIDTH//2-200, HEIGHT//2+60))

    # player if collected all 8 coins and touched the car
    if escaped:
        text = font.render("Your apprentice picked you up! Escape successful!", True, WHITE)
        screen.blit(text, (WIDTH//2-230, HEIGHT//2))

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cops and Robbers")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    car_img, coin_img, mob_img, player_img = load_assets()
    best_time = None
    sounds = load_sounds()

    def reset_game():
        player, coins, gate, car, jail = create_game_objects()
        mobs = create_mobs()
        return {
            "player": player, "coins": coins, "gate": gate, "car": car, "jail": jail,
            "mobs": mobs, "coins_collected": 0, "car_active": False, "seen_timer": 60,
            "caught": False, "escaped": False, "start_time": pygame.time.get_ticks(),
            "final_time": None
        }

    state = reset_game()
    player_speed = 4
    MAX_SEEN_TIME = 60
    
    # dash variables
    dash_cooldown = 120
    is_dashing = False
    dash_duration = 10 
    dash_timer = 0
    
    running = True

    # sets up the quit and restart mechanics of the game
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    state = reset_game()

        keys = pygame.key.get_pressed()
        
        # dash activation
        if keys[pygame.K_q] and dash_cooldown >= 120:
            is_dashing = True
            dash_timer = dash_duration
            dash_cooldown = 0
        
        if is_dashing:
            dash_timer -= 1
            if dash_timer <= 0:
                is_dashing = False
        
        if dash_cooldown < 120:
            dash_cooldown += 1

        # unpack state
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

        if not game_over:
            collected_this_frame = update_coins(player, coins)
            if collected_this_frame > 0:
                sounds["coin"].play() # plays the coin sound when player touches it
            coins_collected += collected_this_frame

        if not game_over:
            current_time = (pygame.time.get_ticks() - start_time) / 1000
        else:
            current_time = final_time

        if not game_over:
            old_pos = player.topleft
            handle_input(player, player_speed, keys, is_dashing)
            if player.colliderect(UI_RECT):
                player.topleft = old_pos
            player.clamp_ip(screen.get_rect())

        # if all coins collected, car move
        if coins_collected == TOTAL_COINS:
            car_active = True

        # if all coins not collected, gate remains 
        if coins_collected < TOTAL_COINS:
            if player.colliderect(gate) and player.x > gate.x:
                player.x = gate.x + gate.width

        if not game_over:
            mob_sees = update_mobs(mobs, player)
        else:
            mob_sees = False

        if not game_over:
            if mob_sees:
                seen_timer -= 1
            else:
                seen_timer = min(MAX_SEEN_TIME, seen_timer + 2)

        if not game_over:
            if seen_timer <= 0:
                caught = True
                player.center = jail.center
            if car_active and player.colliderect(car):
                escaped = True
                final_time = (pygame.time.get_ticks() - start_time) / 1000
                if best_time is None or final_time < best_time:
                    best_time = final_time

        if not game_over:
            update_car(car, car_active)

        state.update({
            "coins_collected": coins_collected, "car_active": car_active,
            "seen_timer": seen_timer, "caught": caught, "escaped": escaped,
            "final_time": final_time
        })

        draw_game(screen, player, coins, mobs, gate, car, jail, car_img, coin_img, mob_img, player_img,
                  coins_collected, seen_timer, mob_sees, caught, escaped,
                  font, car_active, current_time, best_time, dash_cooldown )

        if game_over:
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - 120, HEIGHT//2 + 100))

        pygame.display.update()
    pygame.quit()

TOTAL_COINS = 8
if __name__ == "__main__":
    main()