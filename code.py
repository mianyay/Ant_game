# Miranda Nguyen
import pgzrun
import random

# set grid size

print("Welcome to the Candy Catcher game! \n1 point for each candy collected \nBombs will take 3 seconds off the timer \n20 points to win!")


# make hero
hero = Actor("hero")

# create constants
WIDTH = 760
HEIGHT = 480
square = 32
num_squares_width = WIDTH // square
num_squares_height = HEIGHT // square

candies = []
def add_candy():
    candy = Actor("candy")
    candy.top = random.randint(0, num_squares_height - 1) * square
    candy.left = random.randint(0, num_squares_width - 1) * square
    candies.append(candy)
for i in range(3):
    add_candy()

# add game bits
win = False
# make timer
frames = 0

# manage key controls
def on_key_down(key):
    # down up left right
    if key == keys.DOWN or key == keys.S:
        hero.bottom += square
    elif key == keys.UP or key == keys.W:
        hero.top -= square
    elif key == keys.LEFT or key == keys.A:
        hero.left -= square
    elif key == keys.RIGHT or key == keys.D:
        hero.right += square

    

# update everything
def update():
    global frames, win

    if win == True:
        return

    for candy in candies:
        if hero.colliderect(candy):
            candies.remove(candy)

    if len(candies) == 0:
        print("You won")
        win = True
    # timer
    frames += 1
    # add a new candy
    if (frames % 180) == 0:
        add_candy()
        

# draw everything to screen
def draw():
    global win
        
    # empty screen
    screen.fill("black")
    
    # draw candies
    for candy in candies:
        candy.draw()
    # draw hero
    hero.draw()
    if win == True:
        return

    screen.draw.text(("You win"),(0,5), color="white",fontsize=20)

# runs everything
pgzrun.go()

# Copy your code from the last section here first!