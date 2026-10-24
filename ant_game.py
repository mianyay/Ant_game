# Little Harvester Ant: The Great Flood
import pgzrun
import pygame
import random
from pgzero.actor import Actor
from pgzero.keyboard import keys
import sys

# create constants
WIDTH = 760
HEIGHT = 480
square = 32
num_squares_width = WIDTH // square
num_squares_height = HEIGHT // square
ANT_SPEED = 150
FONT = "silkscreen"
PUDDLE_SLOW = 0.1
SMALL_PUDDLE = 42
BIG_PUDDLE = 124

# Level settings

LEVEL = [
     {"levels": "Emergency Stockpile Rush", "time": 60, "target": 20,
     "images": ["seed", "dead_insect", "dead_insect1", "fruit", "leaf"],
     "rain": 30, "slow": 0.8, "puddles": 3, "big": 2},
    {"levels": "Deep Lockdown", "time": 45, "target": 15,
     "images": ["resin1", "resin2"],
     "rain": 80, "slow": 0.6, "puddles": 4, "big": 3},
    {"levels": "The Final Seal", "time": 20, "target": 10,
     "images": ["pebble", "dirt", "sand"],
     "rain": 160, "slow": 0.4, "puddles": 5, "big": 4},
]

# resizes the sprites to a good size
def actor(name, size=32):
    actor = Actor(name)
    actor._orig_surf = actor._surf = pygame.transform.smoothscale(actor._orig_surf, (size, size))
    actor._update_pos()
    return actor

# make stuff
ant = actor("ant", 32)
items = []
rain = []
puddles = []
big_puddles = []
puddle_timer = 0
story_fade = 0 
level_index = 0
score = 0
time_left = 0
spawn_timer = 0
state = "intro" # there are "story", "intro", "playing", "level_complete", "won", "lost", and "drowned" states

introText = ("""Your home is approaching a massive rainstorm. Your massive underground chambers 
will flood unless the ants gather enough resources to survive the rainstorm.
The resources are the following: seeds, pebbles, dirt, sand, tree resin, fruit and leaves.
Your colony will survive by using food, waterproofing your nursery and blocking off the 
entrance to the chambers from floods.
It won’t be easy; you’re just a little ant."""
)

play_button = Actor("play_button")
play_button.center = (290, 402)

quit_button = Actor("quit_button")
quit_button.center = (490, 400)

def rainfall(amount):
    rain.clear()
    for i in range(amount):
        rain.append([random.randint(0, WIDTH),
                     random.randint(0, HEIGHT),
                     random.randint(300, 500)])

def spot(place):
    #spot that isnt near/where the ant is
    safe_zone = pygame.Rect(ant.left - 60, ant.top - 60, ant.width + 120, ant.height + 120)
    for attempt in range(50):
        place.left = random.randint(0, WIDTH - place.width)
        place.top = random.randint(0, HEIGHT - place.height)
        if place.colliderect(safe_zone):
            continue
        if any(place.colliderect(other) for other in puddles + big_puddles):
            continue
        return

def add_puddle(image, size, group):
    puddle = actor(image, size)
    spot(puddle)
    group.append(puddle)

def add_item():
    global LEVEL
    level = LEVEL[level_index]
    item = actor(random.choice(level["images"]), 40)

    for attempt in range(30):
        item.top = random.randint(0, num_squares_height - 1) * square
        item.left = random.randint(0, num_squares_width - 1) * square
        if not any(item.colliderect(big) for big in big_puddles):
            break
    items.append(item)

def start_story():
    global state, story_fade
    story_fade = 0
    state = "story"

def start_level():
    global score, time_left, spawn_timer, puddle_timer, state, LEVEL, level
    ant.angle = 0
    level = LEVEL[level_index]
    rainfall(level["rain"])
    score = 0
    time_left = level["time"]
    spawn_timer = 0
    puddle_timer = 0
    state = "playing"
    items.clear()
    puddles.clear()
    big_puddles.clear()
    ant.center = (WIDTH // 2, HEIGHT // 2)

    for i in range(level["big"]):
        add_puddle("puddle_big", BIG_PUDDLE, big_puddles)
    for i in range(2):
        add_puddle("puddle_small", SMALL_PUDDLE, puddles)
    for i in range(4):
        add_item()

def ant_size():
    ant.left = max(0, min(WIDTH - ant.width, ant.left))
    ant.top = max(0, min(HEIGHT - ant.height, ant.top))

# manage key controls
def on_key_down(key):
    global level_index, state

    if state == "intro":
        if key == keys.SPACE:
            start_story()
    elif state == "story":
        if key == keys.SPACE:
            start_level() 

    elif state != "playing" and key == keys.SPACE:
        if state == "level_complete":
            level_index += 1
            start_level()
        elif state == "lost":
            start_level() # allows a retry of the same level :)
        elif state == "drowned":
            start_level() # retry after drowning 
        elif state == "won":
            level_index = 0
            state = "intro" # goes back to the intro screen

def on_mouse_down(pos):
    if state == "intro":
        if play_button.collidepoint(pos):
            start_story()
        elif quit_button.collidepoint(pos):
            sys.exit()

def on_mouse_move(pos):
    if state == "intro":
        if play_button.collidepoint(pos):
            play_button.image = "play_button_hover" 
        else:
            play_button.image = "play_button"

        if quit_button.collidepoint(pos):
            quit_button.image = "quit_button_hover" 
        else:
            quit_button.image = "quit_button"

def update(secs): #secs = time since the last frme
    global score, time_left, spawn_timer, state, LEVEL, level_index, puddle_timer, story_fade

    if state == "story":
        story_fade = min(1, story_fade + secs / 1) 
        return
    
    if state != "playing":
        return

    for drop in rain:
        drop[1] += drop[2] * secs

        if drop[1] > HEIGHT:
            drop[1] = -20
            drop[0] = random.randint(0, WIDTH)

    directionX = 0
    directionY = 0
    if keyboard.left or keyboard.a:
        directionX -= 1
    if keyboard.right or keyboard.d:
        directionX += 1
    if keyboard.up or keyboard.w:
        directionY -= 1
    if keyboard.down or keyboard.s:
        directionY += 1

    speed = ANT_SPEED * LEVEL[level_index]["slow"]
    for puddle in puddles:
        if puddle.collidepoint(ant.center):
            speed = ANT_SPEED * PUDDLE_SLOW
    ant.x += directionX * speed * secs
    ant.y += directionY * speed * secs

    if directionY > 0:
        ant.angle = 180
    elif directionY < 0:
        ant.angle = 0
    elif directionX > 0:
        ant.angle = 270
    elif directionX < 0:
        ant.angle = 90

# drowing
    for big in big_puddles:
        if big.collidepoint(ant.center):
            state = "drowned"
            return

    ant_size()

    # timer
    time_left -= secs
    if time_left <= 0:
        time_left = 0
        state = "lost"
        return

    # collect items 
    for item in items[:]:
        if ant.colliderect(item):
            items.remove(item)
            score += 1

    # level complete
    if score >= LEVEL[level_index]["target"]:
        if level_index == len(LEVEL) - 1:
            state = "won"
        else:
            state = "level_complete"
        return

    # spawn a new item every 1 seconds, max 8 on screen
    spawn_timer += secs
    if spawn_timer >= 1:
        spawn_timer = 0
        if len(items) < 8:
            add_item()

    # new puddle spawn every 6 seconds 
    puddle_timer += secs
    if puddle_timer >= 6:
        puddle_timer = 0
        if len(puddles) < LEVEL[level_index]["puddles"]:
            add_puddle("puddle_small", SMALL_PUDDLE, puddles)

def draw():
     
    if state == "intro":
        screen.blit("bg_intro", (0, 0))
        screen.blit("title", (60, 50))

        play_button.draw()
        quit_button.draw()
        return

    if state == "story":
        screen.blit("bg_intro", (0, 0))
        screen.draw.text(introText, center=(WIDTH // 2, HEIGHT // 2), color="white",
                         fontsize=12, fontname=FONT, alpha=story_fade)
        if story_fade >= 1:
            screen.draw.text("PRESS THE SPACE BAR TO BEGIN", midbottom=(WIDTH // 2, HEIGHT - 30),
                             color="white", fontsize=16, fontname=FONT)
        return
    
    if state == "playing":
        screen.blit("bg", (0, 0))

    for puddle in puddles:
        puddle.draw()

    for big in big_puddles:
        big.draw()

    for item in items:
        item.draw()
    ant.draw()

    for drop in rain:
        screen.blit("raindrop", (drop[0], drop[1]))

    level = LEVEL[level_index]
    screen.draw.text(f"Level {level_index + 1}: {level['levels']}", (10, 5), color="white", fontsize=15, fontname=FONT)
    screen.draw.text(f"Collected: {score}/{level['target']} Time: {int(time_left)}", (10, 30), color="white", fontsize=15, fontname=FONT)

    if state == "level_complete":
        screen.draw.text("Level complete! Press the SPACE bar for the next level", center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=18, fontname=FONT)
    elif state == "won":
        screen.draw.text("Your ant colony has survived! Press the SPACE bar to replay", center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=15, fontname=FONT)
    elif state == "lost":
        screen.draw.text("""Time is up! The rain is coming and the colony will be flooded. 
        Press the SPACE bar to retry.""", center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=15, fontname=FONT)
    elif state == "drowned":
        screen.draw.text("""Ants are unable to swim in large puddles! The ant has drowned. 
        Press the SPACE bar to restart the level.""", center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=15, fontname=FONT)

# runs everything
pgzrun.go()
