# Little Harvester Ant: The Great Flood
import pgzrun
import pygame
import random
from pgzero.actor import Actor
from pgzero.keyboard import keys
import sys

# constants
WIDTH = 760
HEIGHT = 480
SQUARE = 32
num_squares_width = WIDTH // SQUARE
num_squares_height = HEIGHT // SQUARE
ANT_SPEED = 150
FONT = "silkscreen"
PUDDLE_SLOW = 0.1
SMALL_PUDDLE = 42
BIG_PUDDLE = 124
DROWN_PIXEL = 40

overlay = pygame.Surface((WIDTH, HEIGHT))
overlay.fill((0, 0, 0))
overlay.set_alpha(150)   #

def overlay_screen():
    screen.surface.blit(overlay, (0, 0))

# Level settings

LEVEL = [
     {"levels": "Emergency Stockpile Rush", "time": 60, "target": 20,
     "images": ["seed", "dead_insect", "dead_insect1", "fruit", "leaf"],
     "rain": 30, "slow": 0.8, "puddles": 3, "big": 2, "music": "level1_music", "rain_sound": "rain_1", "level_complete": "Level completed. \nYou and your best buddies managed to carry in \nthe last bit of seeds before the rain suddenly increased. \nYou contributed to the pool of food to feed the colony for \ndays and look after the larvaes. \nSPACE bar for next level", 
     "fail": "One of your leg got trapped in a sticky \npatch of mud and one of your fellow ant had to take your place. \nEvery ant rushed into the anthill for shelter, \nbut you were unfortunately left behind. \nYou drown under the rain. \nSPACE bar to retry"},
    {"levels": "Deep Lockdown", "time": 45, "target": 15,
     "images": ["resin1", "resin2"],
     "rain": 80, "slow": 0.6, "puddles": 4, "big": 3, "music": "level2_music", "rain_sound": "rain_2", "level_complete": "Level completed. \nAll the tree resin your colony has gathered were used to block the underground \nchambers of your home; essentially waterproofing so water couldn’t get in.\nSPACE bar for next level", 
     "fail": "You couldn’t get enough resin in time. \n You can only hope your queen and her babies live on to the next day. \nYou died.\n SPACE bar to retry"},
    {"levels": "The Final Seal", "time": 20, "target": 10,
     "images": ["pebble", "dirt", "sand"],
     "rain": 160, "slow": 0.4, "puddles": 5, "big": 4, "music": "level3_music", "rain_sound": "rain_3", "fail": "With all the dirt gathered to the best\n of your family’s abilities, the main entrance was blocked off. \nHowever in just 24 hours, you find the walls of your home soaked wet. \nSoon enough every ants around you were submerged in water. \nIt wasn’t enough time to form an emergency raft to float ontop of the flood or evacuate. \nPerhaps little guys are still little after all. \nSPACE bar to retry"}
]
# resizes the sprites to a good size
def actor(name, size=32):
    actor = Actor(name)
    actor._orig_surf = actor._surf = pygame.transform.smoothscale(actor._orig_surf, (size, size))
    actor._update_pos()
    return actor

# variables
ant = actor("ant", 32)
items = []
rain = []
puddles = []
big_puddles = []
puddle_timer = 0
story_fade = 0 
current_music = None
step_timer = 0
current_rain = None
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
        rain.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(300, 500)])

def safety_spot(place):
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

def water_ant(puddle):
    if not ant.colliderect(puddle):
        return False
    ant_mask = pygame.mask.from_surface(ant._surf, 100)
    offset = (ant.left - puddle.left, ant.top - puddle.top)
    return puddle.mask.overlap_area(ant_mask, offset) >= DROWN_PIXEL

def add_puddle(image, size, group):
    puddle = actor(image, size)
    puddle.mask = pygame.mask.from_surface(puddle._surf, 100)
    safety_spot(puddle)
    group.append(puddle)

def add_item():
    global LEVEL
    level = LEVEL[level_index]
    item = actor(random.choice(level["images"]), 40)

    for attempt in range(30):
        item.top = random.randint(0, num_squares_height - 1) * SQUARE
        item.left = random.randint(0, num_squares_width - 1) * SQUARE
        if not any(item.colliderect(big) for big in big_puddles):
            break
    items.append(item)

def play_music(name):
    global current_music
    if current_music == name:
        return
    current_music = name
    if name is None:
        music.stop()
    else:
        music.set_volume(0.4)
        music.play(name)   # loops until stopped

def update_music():
    if state in ("intro", "story"):
        play_music("intro")
    elif state == "playing":
        play_music(LEVEL[level_index]["music"])
    else:
        play_music(None)

def update_rain_sound():
    global current_rain

    if state == "playing":
        rainy = LEVEL[level_index]["rain_sound"]
    else:
        rainy = None
    if rainy == current_rain:
        return
    if current_rain is not None:
        getattr(sounds, current_rain).stop()
    current_rain = rainy
    if rainy is not None:
        rain_sound = getattr(sounds, rainy)
        rain_sound.set_volume(0.3)
        rain_sound.play(-1)   # loops forever

# plays the win/lose sound
def end_level(new_state):
    global state, current_rain
    state = new_state
    play_music(None)
    sounds.step.stop()
    if current_rain is not None:
        getattr(sounds, current_rain).stop()
        current_rain = None
    if new_state in ("lost", "drowned"):
        sounds.lose.play()
    else:
        sounds.win.play()   

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
    global step_timer, score, time_left, spawn_timer, state, LEVEL, level_index, puddle_timer, story_fade

    update_music()
    update_rain_sound()

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

    # footstep sounds
    if directionX != 0 or directionY != 0:
        step_timer -= secs
        if step_timer <= 0:
            sounds.step.play()
            step_timer = 0.25
    else:
        step_timer = 0
        sounds.step.stop()

# drowing
    for big in big_puddles:
        if water_ant(big):
            end_level("drowned")
            return

    ant_size()

    # timer
    time_left -= secs
    if time_left <= 0:
        time_left = 0
        end_level("lost")
        return

    # collect items 
    for item in items[:]:
        if ant.colliderect(item):
            items.remove(item)
            score += 1
            sounds.collect.play()

    # level complete
    if score >= LEVEL[level_index]["target"]:
        if level_index == len(LEVEL) - 1:
            end_level("won")
        else:
            end_level("level_complete")
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
        screen.blit("bg_intro_dark", (0, 0))
        screen.draw.text(introText, center=(WIDTH // 2, HEIGHT // 2), color="white",
                         fontsize=12, fontname=FONT, alpha=story_fade)
        if story_fade >= 1:
            screen.draw.text("PRESS THE SPACE BAR TO BEGIN", midbottom=(WIDTH // 2, HEIGHT - 30),
                             color="white", fontsize=16, fontname=FONT)
        return
    
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
    screen.draw.text(f"Level {level_index + 1}: {level['levels']}", (10, 5), color="white", fontsize=12, fontname=FONT)
    screen.draw.text(f"Collected: {score}/{level['target']} Time: {int(time_left)}", (10, 30), color="white", fontsize=12, fontname=FONT)

    if state == "level_complete":
        overlay_screen()
        screen.draw.text(level["level_complete"], center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=12, fontname=FONT)
    elif state == "won":
        screen.blit("bg_win", (0, 0))
        screen.draw.text("""Your colony managed to block off the final entrance to your home with dirt and stones.
It was hard, who would’ve expected little guys to accomplish something bigger their size?
The next 9 days the rainstorm ended. You survived. 
You stepped outside the drying land to be grazed by the sun’s warmth, 
to continue working to keep your survival.
You live.""", center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=12, fontname=FONT)
    elif state == "lost":
        overlay_screen()
        screen.draw.text(level["fail"], center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=12, fontname=FONT)
    elif state == "drowned":
        overlay_screen()
        screen.draw.text("""Ants are unable to swim in large puddles! The ant has drowned. 
        Press the SPACE bar to restart the level.""", center=(WIDTH // 2, HEIGHT // 2), color="white", fontsize=15, fontname=FONT)

# runs everything
pgzrun.go()
