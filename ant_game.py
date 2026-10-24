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

# Level settings

LEVEL = [
     {"levels": "Emergency Stockpile Rush", "time": 60, "target": 20,
     "images": ["seed", "dead_insect", "dead_insect1", "fruit", "leaf"]},
    {"levels": "Deep Lockdown", "time": 45, "target": 15,
     "images": ["resin1", "resin2"]},
    {"levels": "The Final Seal", "time": 20, "target": 10,
     "images": ["pebble", "dirt", "sand"]},
]

# resizes the sprites to a good size
def actor(name, size=32):
    actor = Actor(name)
    actor._orig_surf = actor._surf = pygame.transform.smoothscale(actor._orig_surf, (size, size))
    actor._update_pos()
    return actor

# make ant
ant = actor("ant", 32)
items = []
level_index = 0
score = 0
time_left = 0
spawn_timer = 0
state = "intro" # there are "intro", "playing", "level_complete", "won", and "lost" states

introText = ("""Your home is approaching a massive rainstorm. Your massive underground chambers will flood unless the ants gather enough resources to survive the rainstorm.
The resources are the following: seeds, pebbles, dirt, sand, tree resin, fruit and leaves.
Your colony will survive by using food, waterproofing your nursery and blocking off the entrance to the chambers from floods.
It won’t be easy; you’re just a little ant."""
)

play_button = Actor("play_button")
play_button.center = (WIDTH // 2, 355)

quit_button = Actor("quit_button")
quit_button.center = (WIDTH // 2, 420)

def add_item():
    global LEVEL
    level = LEVEL[level_index]
    item = actor(random.choice(level["images"]), 88)
    item.top = random.randint(0, num_squares_height - 1) * square
    item.left = random.randint(0, num_squares_width - 1) * square
    items.append(item)

def start_level():
    global score, time_left, spawn_timer, state, LEVEL, level
    ant.angle = 0
    level = LEVEL[level_index]
    score = 0
    time_left = level["time"]
    spawn_timer = 0
    state = "playing"
    items.clear()
    ant.center = (WIDTH // 2, HEIGHT // 2)
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
            start_level()
    elif state == "playing":
        # down up left right
        if key == keys.DOWN or key == keys.S:
            ant.bottom += square
            ant.angle = 180
        elif key == keys.UP or key == keys.W:
            ant.top -= square
            ant.angle = 0
        elif key == keys.LEFT or key == keys.A:
            ant.left -= square
            ant.angle = 90
        elif key == keys.RIGHT or key == keys.D:
            ant.left += square
            ant.angle = 270
        ant_size()

    elif key == keys.SPACE:
        if state == "level_complete":
            level_index += 1
            start_level()
        elif state == "lost":
            start_level() # allows a retry of the same level :)
        elif state == "won":
            level_index = 0
            state = "intro" # goes back to the intro screen

def on_mouse_down(pos):
    if state == "intro":
        if play_button.collidepoint(pos):
            start_level()
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

def update(secs):
    global score, time_left, spawn_timer, state, LEVEL, level_index

    if state != "playing":
        return

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

def draw():
     
    if state == "intro":
        screen.blit("bg_intro", (0, 0))
        screen.blit("title", (WIDTH // 2 - 200, 10))
        screen.draw.text(introText, center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=12)

        play_button.draw()
        quit_button.draw()
        return

    screen.fill("black") # will change this to a proper background later

    for item in items:
        item.draw()
    ant.draw()

    level = LEVEL[level_index]
    screen.draw.text(f"Level {level_index + 1}: {level['levels']}", (10, 5), color="white", fontsize=24)
    screen.draw.text(f"Collected: {score}/{level['target']} Time: {int(time_left)}", (10, 30), color="white", fontsize=24)

    if state == "level_complete":
        screen.draw.text("Level complete! Press the SPACE bar for the next level", center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=36)
    elif state == "won":
        screen.draw.text("Your ant colony has survived! Press the SPACE bar to replay", center=(WIDTH // 2, HEIGHT // 2), color="green", fontsize=36)
    elif state == "lost":
        screen.draw.text("Time is up! The rain is coming and the colony will be flooded. Press the SPACE bar to retry.", center=(WIDTH // 2, HEIGHT // 2), color="red", fontsize=36)

# runs everything
pgzrun.go()
