import pgzrun
import random
from pgzero.actor import Actor
from pgzero.keyboard import keys

# create constants
WIDTH = 760
HEIGHT = 480
square = 32
num_squares_width = WIDTH // square
num_squares_height = HEIGHT // square

# Level settings

LEVEL = [
     {"level_1": "Gather food for the larvae", "time": 60, "target": 50,
     "images": ["seed", "dead_insect", "fruit", "leaf"]},
    {"level_2": "Collect sticky tree resin", "time": 45, "target": 25,
     "images": ["resin1", "resin2"]},
    {"level_3": "Block the nest entrance", "time": 35, "target": 10,
     "images": ["pebble", "dirt", "sand"]},
]

# make ant
ant = Actor("ant")
items = []
level_index = 0
score = 0
time_left = 0
spawn_timer = 0
state = "playing" # there are "playing", "level_complete", "won", and "lost" states

def add_item():
    global LEVEL
    level = LEVEL[level_index]
    item = Actor(random.choice(level["images"]))
    item.top = random.randint(0, num_squares_height - 1) * square
    item.left = random.randint(0, num_squares_width - 1) * square
    items.append(item)

def start_level():
    global score, time_left, spawn_timer, state, LEVEL, level
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
    global level_index

    if state == "playing":
        # down up left right
        if key == keys.DOWN or key == keys.S:
            ant.bottom += square
        elif key == keys.UP or key == keys.W:
            ant.top -= square
        elif key == keys.LEFT or key == keys.A:
            ant.left -= square
        elif key == keys.RIGHT or key == keys.D:
            ant.left += square
        ant_size()

    elif key == keys.SPACE:
        if state == "level_complete":
            level_index += 1
            start_level()
        elif state == "lost":
            start_level() # allows a retry of the same level :)
        elif state == "won":
            level_index = 0
            start_level() # whole game restarts

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
    global LEVEL, level
    screen.fill("black") # will change this to a proper background later

    for item in items:
        item.draw()
    ant.draw()

    level = LEVEL[level.index]
    screen.draw.text(f"Level {level_index + 1}: {level['name']}, (10, 5)", color="white", fontsize=24)
    screen.draw.text(f"Collected: {score}/{level['target']} Time: {int(time_left)}", (10, 30), color="yellow", fontsize=24)

    if state == "level_complete":
        screen.draw.text("Level complete! Press the SPACE bar for the next level", center=(WIDTH // 2, HEIGHT // 2), color="blue", fontsize=36)
    elif state == "won":
        screen.draw.text("Your ant colony has survived! Press the SPACE bar to replay", center=("WIDTH // 2, HEIGHT // 2"), color="green", fontsize=36)
    elif state == "lost":
        screen.draw.text("Time is up! The rain is coming and the colony will be flooded. Press the SPACE bar to retry.", center=(WIDTH // 2, HEIGHT // 2), color="red", fontsize=36)
# runs everything
pgzrun.go()
