"""
Created on Sun Mar 2 11:37 2015

@author: Franton Lin
@author: Kai Levy

"""

import pygame
import os
import random

# Colors
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
SCREEN_W = 1024
SCREEN_H = 768
CURR_DIR = os.getcwd()

MAX_GRASS = int(0.013 * SCREEN_W)

class Ninja(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # Load the sprite sheet
        self.sheet = pygame.image.load(CURR_DIR + "/images/ninja_sheet.png")
        self.index = 0          # Index for choosing which sprite image
        self.sprite_num = 0     # Index for choosing which sprite sequence
        self.dt_image = 0.0
        self.animation_speed = 0.04

        self.sprite_num

        # Size of single frame in pixels
        self.width = 88
        self.height = 88

        # Sprite position
        self.x_pos = SCREEN_W/2-self.width/2
        self.y_pos = SCREEN_H-self.height+4

        self.y_vel = 0
        self.x_vel = 0
        self.on_ground = True

        self.speed = 412

        # Rectangle object for positioning
        self.rect = pygame.Rect(self.x_pos, self.y_pos, self.width, self.height-8)  # 8 extra pixels on bottom of sprite

    def jump(self):
        self.y_vel = -1

    def move(self,x_vel,y_vel):
        self.rect = self.rect.move(x_vel,y_vel)
        if self.rect.left < 0:              # Bound character within screen on left
            self.rect.left = 0
            self.animation_speed = 0.04
        elif self.rect.right > SCREEN_W:    # Bound character within screen on right
            self.rect.right = SCREEN_W
            self.animation_speed = 0.04

    def update(self, dt, ninja_horiz, ninja_jump):
        # Add passed time to time since last image change
        self.dt_image += dt

        if ninja_jump and self.on_ground:
            self.y_vel = -1000*dt
            self.on_ground = False
            self.sprite_num = 2
            self.index = 1
            print "\t\tJUMP"

        self.animation_speed = 0.04 - 0.02 * ninja_horiz
        self.x_vel = ninja_horiz * self.speed * dt

        # Fall if in air
        if not self.on_ground:
            self.y_vel += 50*dt
            print "\tIN AIR"
        else:
            print "ON GROUND"

        self.move(self.x_vel,self.y_vel)

        # If enough time has passed, change index to use next image
        if self.dt_image > self.animation_speed and self.sprite_num == 0:
            self.index += 1
            if self.index >= 5:
                self.index = 0
            self.dt_image = 0
            self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num, self.width, self.height)) #Locate the sprite you want
            self.image = self.sheet.subsurface(self.sheet.get_clip()) # Extract the sprite you want
        elif self.sprite_num == 2:
            self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num, self.width, self.height))
            self.image = self.sheet.subsurface(self.sheet.get_clip())


    def collide(self, platforms):
        for p in platforms:
            if self.rect.colliderect(p):
                if self.y_vel > 0:
                    self.rect.bottom = p.rect.top
                    self.on_ground = True
                    self.y_vel = 0
                    self.sprite_num = 0
                    self.index = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
    # TODO: implement this class

                
class Grass(pygame.sprite.Sprite):
    """Grass class"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        rand = random.randint(1,8)
        self.image = pygame.image.load(CURR_DIR + "/images/grass%d.png"%rand)   # Load a random grass image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(SCREEN_W, SCREEN_H-self.height+3, self.width, self.height)
        self.speed = 354

    def update(self, dt):
        """Moves the grass"""
        self.rect = self.rect.move(-self.speed*dt,0)

class Background():
    """Class for background"""
    def __init__(self):
        self.width = SCREEN_W
        self.height = SCREEN_H
        self.grass = pygame.sprite.Group(Grass())
        self.num_grass = 1
        self.ground = pygame.sprite.Sprite      # Not sure if I actually did this correctly
        self.ground.rect = pygame.Rect(0, self.height - 4, self.width, 4)
        print self.ground.rect.width
        print self.ground.rect.height
        self.ground.image = pygame.Surface((self.ground.rect.width, self.ground.rect.height)) # Creates an image for ground?

    def update(self,dt):
        """Updates background with grass tufts"""
        if self.num_grass < MAX_GRASS:   # Chance of adding grass if MAX_GRASS isn't reached
            rand = random.random()
            if rand < dt*4:
                Grass().add(self.grass)
                self.num_grass += 1
        for g in self.grass:             # Remove any grass no longer on the screen from the group
            if g.rect.right < 0:
                g.kill()
                self.num_grass -= 1
        self.grass.update(dt)


class NinjaModel:
    """Model for game"""
    def __init__(self):
        self.width = SCREEN_W
        self.height = SCREEN_H
        self.my_sprite = Ninja()
        self.my_group = pygame.sprite.Group(self.my_sprite)
        self.background = Background()
        self.ninja_horiz = 0
        self.ninja_jump = 0
        self.platforms = [self.background.ground]

    def update(self,dt):
        """Updates player and background"""
        self.my_group.update(dt, self.ninja_horiz, self.ninja_jump)
        self.my_sprite.collide(self.platforms)
        self.background.update(dt)

    def get_drawables(self):
        """Return list of groups to draw"""
        return [self.my_group, self.background.grass]#, pygame.sprite.Group(self.background.ground)]

class NinjaController:
    """Controller for player"""
    def __init__(self,model):
        self.model = model
        self.done = False

    def process_events(self):
        """Manages keypresses"""
        if self.model.ninja_jump == 1:
            self.model.ninja_jump = 0   # return jump to false
        pygame.event.pump
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            if event.type == pygame.KEYDOWN:
                k = event.key
                if k == pygame.K_LEFT or k == pygame.K_a:
                    self.model.ninja_horiz = -1
                if k == pygame.K_RIGHT or k == pygame.K_d:
                    self.model.ninja_horiz = 1
                if k == pygame.K_UP or k == pygame.K_SPACE or k == pygame.K_w:  # TODO: Keep jumping if held down
                    self.model.ninja_jump = 1
            if event.type == pygame.KEYUP:
                k = event.key
                if (k == pygame.K_LEFT or k == pygame.K_a) and self.model.ninja_horiz == -1:
                    self.model.ninja_horiz = 0
                if (k == pygame.K_RIGHT or k == pygame.K_d) and self.model.ninja_horiz == 1:
                    self.model.ninja_horiz = 0
        return self.done

class NinjaView:
    """View for game"""
    def __init__(self, model):
        pygame.init()
        self.width = SCREEN_W
        self.height = SCREEN_H
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.model = model
        pygame.display.set_caption("NINJAs")

    def draw(self):
        """Redraws game window, fetching drawables from model"""
        self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(0, self.height - 4, self.width, 4))   # This is the ground
        drawables = self.model.get_drawables()
        for g in drawables:
            g.draw(self.screen)
        pygame.display.flip()

class NinjaMain:
    """Main class"""

    def __init__(self, width = SCREEN_W, height = SCREEN_H):
        self.width = width
        self.height = height
        self.model = NinjaModel()
        self.view = NinjaView(self.model)
        self.controller = NinjaController(self.model)
        self.clock = pygame.time.Clock()

    def MainLoop(self):
        """Game loop"""
        lastGetTicks = 0.0
        done = False

        while not done:
            t = pygame.time.get_ticks()
            # delta time in seconds.
            dt = (t - lastGetTicks) / 1000.0
            lastGetTicks = t

            done = self.controller.process_events()
            self.model.update(dt)
            self.view.draw()

            self.clock.tick(60)


if __name__ == '__main__':
    MainWindow = NinjaMain()
    MainWindow.MainLoop()