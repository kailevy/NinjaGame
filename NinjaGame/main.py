"""
Created on Sun Mar 2 11:37 2015

@author: Franton Lin
@author: Kai Levy

"""

import pygame
import random

# Colors
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)

ninja_horiz = 0
ninja_jump = 0
num_grass = 0
MAX_GRASS = 21

class Ninja(pygame.sprite.Sprite):
    global ninja_horiz

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # Load the sprite sheet
        self.sheet = pygame.image.load("images/ninja_sheet.png")

        # Size of single frame in pixels
        self.width = 88
        self.height = 88

        # Index for choosing which image and time since last change of image
        self.index = 0
        self.dt_image = 0.0
        self.animation_speed = 0.04
        self.speed = 412

        # Rectangle object for positioning
        self.rect = pygame.Rect(800-self.width/2, 848-self.height+4, self.width, self.height)

    def update(self, dt):
        # Add passed time to time since last image change
        self.dt_image += dt

        # Change animation speed based on which direction ninja is moving
        if ninja_horiz == -1:
            if self.rect.left > 0:
                self.animation_speed = 0.06
                self.rect = self.rect.move(-self.speed*dt,0)   # Bound character within screen
                if self.rect.left < 0:
                    self.rect.left = 0
            else:
                self.animation_speed = 0.04
        elif ninja_horiz == 0:
            self.animation_speed = 0.04
        elif ninja_horiz == 1:
            if self.rect.right < 1600:
                self.animation_speed = 0.02
                self.rect = self.rect.move(self.speed*dt,0)    # Bound character within screen
                if self.rect.right > 1600:
                    self.rect.right = 1600
            else:
                self.animation_speed = 0.04

        # If enough time has passed, change index to use next image
        if self.dt_image > self.animation_speed:
            self.index += 1
            if self.index >= 5:
                self.index = 0
            self.dt_image = 0
        self.sheet.set_clip(pygame.Rect(self.index * self.width, 0, self.width, self.height)) #Locate the sprite you want
        self.image = self.sheet.subsurface(self.sheet.get_clip()) # Extract the sprite you want

class Grass(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        rand = random.randint(1,8)
        self.image = pygame.image.load("images/grass%d.png"%rand)   # Load a random grass image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(1600, 848-self.height+3, self.width, self.height)
        self.speed = 354

    def update(self, dt):
        self.rect = self.rect.move(-self.speed*dt,0)

pygame.init()

# Create pygame window
#infoObject = pygame.display.Info()
#screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
screen = pygame.display.set_mode((1600, 848))
pygame.display.set_caption("NINJAs")

# Set clock and stuff
done = False
clock = pygame.time.Clock()

# Initialize sprite
my_sprite = Ninja()
#my_ground = Ground()
my_group = pygame.sprite.Group(my_sprite)
grass = pygame.sprite.Group(Grass())
num_grass = 1

#game = ninjas.Ninjas()

lastGetTicks = 0.0

# Actually run the game
while not done:
    t = pygame.time.get_ticks()
    # delta time in seconds.
    dt = (t - lastGetTicks) / 1000.0
    lastGetTicks = t

    # Event processing
    #done = game.proccess_events()
    pygame.event.pump
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                ninja_horiz = -1
            if event.key == pygame.K_RIGHT:
                ninja_horiz = 1
            if event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                ninja_jump = 1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT and ninja_horiz == -1:
                ninja_horiz = 0
            if event.key == pygame.K_RIGHT and ninja_horiz == 1:
                ninja_horiz = 0

    # Game Logic
    if num_grass < MAX_GRASS:   # Chance of adding grass if MAX_GRASS isn't reached
        rand = random.random()
        if rand < dt*4:
            Grass().add(grass)
            num_grass += 1
    for g in grass:             # Remove any grass no longer on the screen from the group
        if g.rect.right < 0:
            g.kill()
            num_grass -= 1
    grass.update(dt)
    my_group.update(dt)

    # Drawing
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, pygame.Rect(0, 848 - 4, 1600, 4))   # This is the ground
    my_group.draw(screen)
    grass.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()