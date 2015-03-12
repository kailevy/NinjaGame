"""
Created on Sun Mar 2 11:37 2015

@author: Franton Lin
@author: Kai Levy

TO DO FOR TOMORROW:
- add death animation and delay before restart game
- potentially separate into separate files (not urgent)
- potentially add way to stop stay-at-back exploitation
- add more comments and documentation
- potentially fine-tune difficulty parameters (speedboost, max shurikens) for good difficulty settings

"""

import pygame
import os
import random
import pickle

FRAMERATE = 60

# Colors
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
SCREEN_W = 1024
SCREEN_H = 768
CURR_DIR = os.path.dirname(os.path.realpath(__file__))

MAX_GRASS = int(0.013 * SCREEN_W)

GROUND = 0
BUILDING1 = 1
BUILDING2 = 2

GROUNDSPEED = 354
BUILDINGS = [pygame.image.load(CURR_DIR + "/images/building1.png"), pygame.image.load(CURR_DIR + "/images/building2.png")]

class Ninja(pygame.sprite.Sprite):
    """Class for the Ninja, which represents the player"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.alive = True       #if false, game ends

        # Load the sprite sheet
        self.sheet = pygame.image.load(CURR_DIR + "/images/ninja_sheet.png")
        self.index = 0          # Index for choosing which sprite image
        self.sprite_num = 0     # Index for choosing which sprite sequence
        self.dt_image = 0.0
        self.animation_speed = 0.04

        # Size of single frame in pixels
        self.width = 88
        self.height = 88

        # Parameters for movement in window
        self.y_vel = 0
        self.x_vel = 0
        self.on_ground = True
        self.jump_counter = 0

        # Starting position
        self.x_pos = SCREEN_W / 2 - self.width / 2
        self.y_pos = SCREEN_H - self.height + 4

        # Defines ninja's speed and jump parameters
        self.speed = 412
        self.min_jump = int(FRAMERATE/15)
        self.max_jump = int(FRAMERATE/10)

        # Rectangle object for positioning
        self.rect = pygame.Rect(self.x_pos, self.y_pos, self.width, self.height-8)  # 8 extra pixels on bottom of sprite
        self.hitbox = pygame.Rect(self.rect.x + 16, self.rect.y + 16, self.width - 32, self.height - 34)
        self.feet = pygame.Rect(self.x_pos + 24, self.y_pos + self.height - 8, 40, 2)

        # Locates the approprates sprite
        self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height)) 
        self.image = self.sheet.subsurface(self.sheet.get_clip())
        self.index += 1

    def jump(self, ninja_jump):
        """Makes the ninja jump"""
        if ninja_jump and self.jump_counter < self.max_jump:
            self.y_vel += -248
            self.jump_counter += 1
            self.on_ground = False
            self.sprite_num = 2
            self.index = 1
        elif self.jump_counter > 0 and self.jump_counter < self.min_jump:
            self.y_vel += -248
            self.jump_counter += 1
        elif self.jump_counter > 0:
            self.jump_counter = self.max_jump

    def move(self,x_vel,y_vel):
        """Moves rectangles for drawing, feet, and hitbox"""
        self.rect = self.rect.move(x_vel,y_vel)
        self.feet = self.feet.move(x_vel,y_vel)
        self.hitbox = self.hitbox.move(x_vel,y_vel)
        if self.rect.left < 0:              # Bound character within screen on left
            self.hitbox.left = 16
            self.animation_speed = 0.04
        elif self.rect.right > SCREEN_W:    # Bound character within screen on right
            self.hitbox.right = SCREEN_W - 16
            self.animation_speed = 0.04

    def update(self, dt, ninja_horiz, ninja_jump,platforms):
        """Updates the ninja, including collisions"""
        # Add passed time to time since last image change
        self.dt_image += dt

        self.jump(ninja_jump)

        # Update animation and speed based
        self.animation_speed = 0.04 - 0.02 * ninja_horiz
        self.x_vel = ninja_horiz * self.speed

        # Fall if in air
        if not self.on_ground:
            self.y_vel += 57


        self.move(self.x_vel*dt,self.y_vel*dt)
        self.collide(platforms)
        
        # If enough time has passed, change index to use next image
        if self.dt_image > self.animation_speed and self.sprite_num == 0:
            self.index += 1
            if self.index >= 5:
                self.index = 0
            self.dt_image = 0
            self.sheet.set_clip(pygame.Rect(self.index * self.width, self.sprite_num * self.height, self.width, self.height)) # Locate the sprite you want
            self.image = self.sheet.subsurface(self.sheet.get_clip()) # Extract the sprite you want
        elif self.sprite_num == 2:
            self.sheet.set_clip(pygame.Rect(self.index * self.width, 0, self.width, self.height))   # 2nd frame of walk is better jump image
            self.image = self.sheet.subsurface(self.sheet.get_clip())

    def collide(self, platforms):
        """Checks for collisions with platforms"""
        walking = False
        for p in platforms:
            self.correct_boxes()    
            if self.feet.colliderect(p.safebox) and not self.on_ground:
                self.hitbox.bottom = p.rect.top - 10
                self.on_ground = True
                self.y_vel = 0
                self.sprite_num = 0
                self.index = 0
                self.jump_counter = 0
            if self.feet.colliderect(p.safebox):
                walking = True
            if self.hitbox.colliderect(p.safebox):
                if self.hitbox.left < p.safebox.left:
                    self.hitbox.right = p.safebox.left
                elif self.hitbox.right > p.safebox.right:
                    self.hitbox.left = p.safebox.right
            if self.hitbox.colliderect(p.killbox1) or self.hitbox.colliderect(p.killbox2):
                self.alive = False
            self.correct_boxes()

        if not walking:
            if self.on_ground == True:
                self.jump_counter = self.max_jump
            self.on_ground = False


    def correct_boxes(self):
        """Corrects the rectangles during collisions based off of hitbox"""
        self.feet.left = self.hitbox.left + 8
        self.feet.top = self.hitbox.bottom + 10
        self.rect.left = self.hitbox.left - 16
        self.rect.top = self.hitbox.top - 16

class Shuriken(pygame.sprite.Sprite):
    """Shuriken class"""
    def __init__(self, x_pos,model,speedboost):
        pygame.sprite.Sprite.__init__(self)

        self.model = model

        # Load the sprite sheet
        self.sheet = pygame.image.load(CURR_DIR + "/images/shuriken_sheet.png")
        self.index = 0          # Index for choosing which sprite image
        self.dt_image = 0.0
        self.animation_speed = 0.02

        # Size of single frame in pixels
        self.width = 42
        self.height = 42

        # Velocities for updating position
        self.y_vel = 650
        self.x_vel = (GROUNDSPEED + speedboost) * (random.random() * 4 - 1)
        self.on_ground = False

        self.rect = pygame.Rect(x_pos, -self.height, self.width, self.height)

        self.sheet.set_clip(pygame.Rect(self.index * self.width, 0, self.width, self.height)) # Locate the sprite you want
        self.image = self.sheet.subsurface(self.sheet.get_clip())
        self.index += 1

    def update(self, dt, speedboost):
        """Updates shuriken"""
        self.dt_image += dt

        if not self.on_ground:
            self.y_vel += 10
            if self.dt_image > self.animation_speed:
                self.index += 1
                if self.index >= 3:
                    self.index = 0
                self.dt_image = 0
                self.sheet.set_clip(pygame.Rect(self.index * self.width, 0, self.width, self.height)) # Locate the sprite you want
                self.image = self.sheet.subsurface(self.sheet.get_clip()) # Extract the sprite you want
        else: self.x_vel = GROUNDSPEED + speedboost
        self.rect = self.rect.move(-self.x_vel*dt, self.y_vel*dt)

    def collide(self, collideable):
        """Collides with platforms and ninja"""
        for p in collideable:
            if type(p) is Ninja:
                if self.rect.colliderect(p.hitbox) and not self.on_ground:
                    p.alive = False
                    return 0
                elif self.rect.colliderect(p.hitbox) and self.on_ground:
                    self.model.score += 50
                    self.kill()
                    return 1
                else: return 0

            elif self.rect.colliderect(p.safebox):
                if self.index == 0:
                    self.rect.bottom = p.safebox.top + 7
                elif self.index == 1 or self.index == 2:
                    self.rect.bottom = p.safebox.top + 5
                self.on_ground = True
                self.y_vel = 0

class Projectiles():
    """Represents all the shurikens"""
    def __init__(self,model):
        self.model = model
        self.shurikens = pygame.sprite.Group(Shuriken(SCREEN_W/2+SCREEN_W/2*random.random(),self.model,0))
        self.num_shurikens = 1

    def update(self,dt,platforms,my_group,max_num,speedboost):
        """Adds shurikens"""
        num_gone = 0
        self.shurikens.update(dt,speedboost)
        for p in self.shurikens:
            p.collide(platforms)
            num_gone += p.collide(my_group)
        for p in self.shurikens:
            if p.rect.right < 0 or p.rect.left > (SCREEN_W + 400):
                p.kill()
                self.num_shurikens -= 1
        self.num_shurikens -= num_gone 
        if self.num_shurikens < max_num:
            rand = random.random()
            if rand < dt * 1.6:
                Shuriken(SCREEN_W/2+SCREEN_W/2*random.random(),self.model,speedboost).add(self.shurikens)
                self.num_shurikens += 1
                
class Grass(pygame.sprite.Sprite):
    """Grass class"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        rand = random.randint(1,8)
        self.image = pygame.image.load(CURR_DIR + "/images/grass%d.png"%rand)   # Load a random grass image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(SCREEN_W, SCREEN_H-self.height+3, self.width, self.height)
        self.speed = GROUNDSPEED 

    def update(self, dt,speedboost):
        """Moves the grass"""
        self.rect = self.rect.move(-(self.speed + speedboost)*dt,0)

class Background():
    """Class for background"""
    def __init__(self):
        self.grass = pygame.sprite.Group(Grass())
        self.num_grass = 1

    def update(self,dt,speedboost):
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
        self.grass.update(dt,speedboost)

class Platform(pygame.sprite.Sprite):
    """Class for platforms that the Ninja can land on"""
    def __init__(self,x,style,story=-1):
        pygame.sprite.Sprite.__init__(self)
        if style == GROUND:
            self.image = pygame.Surface([SCREEN_W + 400, 1000])
            self.image.fill(BLACK)
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = SCREEN_H - 4
            self.speed = 0
            self.safebox = self.rect
            self.killbox1 = pygame.Rect(0,0,0,0)
            self.killbox2 = pygame.Rect(0,0,0,0)
        else:
            self.image = BUILDINGS[style-1]
            self.speed = GROUNDSPEED
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = SCREEN_H - story*self.rect.height - 4
            self.safebox = pygame.Rect(self.rect.x + 11, self.rect.y, self.rect.width - 22, self.rect.height)
            self.killbox1 = pygame.Rect(self.rect.x + 4, self.rect.y + 6, 8, self.rect.height - 6)
            self.killbox2 = pygame.Rect(self.rect.x + self.rect.width - 12, self.rect.y + 6, 7, self.rect.height - 6)

    def update(self, dt, speedboost):
        """Move the platforms"""
        if self.speed != 0:
            self.rect = self.rect.move(-(self.speed + speedboost)*dt,0)
        else:
            pass
        self.safebox = pygame.Rect(self.rect.x + 11, self.rect.y, self.rect.width - 22, self.rect.height)   
        self.killbox1 = pygame.Rect(self.rect.x + 4, self.rect.y + 6, 8, self.rect.height - 6)
        self.killbox2 = pygame.Rect(self.rect.x + self.rect.width - 12, self.rect.y + 6, 7, self.rect.height - 6)

class PlatformHandler():
    """Class to handle the platforms"""
    def __init__(self):
        ground = Platform(0, GROUND)
        self.platforms = pygame.sprite.Group(ground)
        self.release_platform = True
        self.append_platform = True
        self.num_platforms = 0

    def update(self,dt,speedboost):
        """Updates all platforms, generates more and removes obsolete ones"""
        self.release_platform = True
        for p in self.platforms:        # Remove any platforms no longer on the screen from the group
            p.update(dt,speedboost)
            if p.rect.height < 1000:    # Do not check ground
                if p.rect.right < 0:
                    p.kill()
                elif p.safebox.right - SCREEN_W > 0 and p.safebox.right - SCREEN_W < 10 and self.append_platform:
                    rand = random.random()
                    if rand > 0.75:
                        rand = random.random()
                        if rand < 0.5:
                            Platform(SCREEN_W-12 + (p.safebox.right-SCREEN_W),BUILDING1,1).add(self.platforms)
                        else:
                            Platform(SCREEN_W-12 + (p.safebox.right-SCREEN_W),BUILDING2,1).add(self.platforms)
                        self.append_platform = False
                elif p.safebox.right - SCREEN_W < 0 and SCREEN_W - p.safebox.right < 10:
                    self.append_platform = True

                if p.rect.right > SCREEN_W - 40:
                    self.release_platform = False

        if self.release_platform:
            rand = random.random()
            if rand > 0.995:
                rand = random.random()
                if rand < 0.5:
                    Platform(SCREEN_W,BUILDING1,1).add(self.platforms)
                else:
                    Platform(SCREEN_W,BUILDING2,1).add(self.platforms)


class NinjaModel:
    """Model for game"""
    def __init__(self):
        self.width = SCREEN_W
        self.height = SCREEN_H

        self.score = 0
        self.score_dt = 0
        self.score_speed = 0.5      # 10 pts every half second

        self.my_sprite = Ninja()
        self.my_group = pygame.sprite.Group(self.my_sprite)
        self.platform_handler = PlatformHandler()

        self.speedboost = 0
        self.alive = self.my_sprite.alive

        self.projectiles = Projectiles(self)
        
        self.background = Background()

        self.ninja_horiz = 0
        self.ninja_jump = 0

    def update(self,dt):
        """Updates player and background"""
        # update ninja
        self.my_group.update(dt, self.ninja_horiz, self.ninja_jump, self.platform_handler.platforms)

        # update and collide projectiles
        self.projectiles.update(dt,self.platform_handler.platforms,self.my_group,self.score/120 + 1,self.speedboost)

        self.background.update(dt,self.speedboost)

        self.platform_handler.update(dt,self.speedboost)
        self.score_dt += dt

        self.alive = self.my_sprite.alive

        if self.score_dt >= self.score_speed:
            self.update_score()
            self.score_dt = 0
        self.speedboost = self.score / 10

    def update_score(self):
        """Adds 10 to score"""
        self.score += 10 

    def get_drawables(self):
        """Return list of groups to draw"""
        return [self.my_group, self.background.grass, self.platform_handler.platforms, self.projectiles.shurikens]

class NinjaController:
    """Controller for player"""
    def __init__(self,model):
        self.model = model
        self.done = False
        self.pause = False

    def process_events(self):
        """Manages keypresses"""
        pygame.event.pump
        self.pause = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True
            elif event.type == pygame.KEYDOWN:
                k = event.key   
                if k == pygame.K_LEFT or k == pygame.K_a:
                    self.model.ninja_horiz = -1
                elif k == pygame.K_RIGHT or k == pygame.K_d:
                    self.model.ninja_horiz = 1
                elif k == pygame.K_UP or k == pygame.K_SPACE or k == pygame.K_w:
                    self.model.ninja_jump = k
            elif event.type == pygame.KEYUP:
                k = event.key
                if k == pygame.K_p:
                    self.pause = True
                elif (k == pygame.K_LEFT or k == pygame.K_a) and self.model.ninja_horiz == -1:
                    self.model.ninja_horiz = 0
                elif (k == pygame.K_RIGHT or k == pygame.K_d) and self.model.ninja_horiz == 1:
                    self.model.ninja_horiz = 0
                elif k == self.model.ninja_jump:
                    self.model.ninja_jump = 0
        return (self.done,self.pause)

class NinjaView:
    """View for game"""
    def __init__(self, model):
        pygame.init()
        self.width = SCREEN_W
        self.height = SCREEN_H
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.model = model
        pygame.font.init()

        self.font = pygame.font.Font(CURR_DIR + '/visitor2.ttf', 80)
        self.pause_surf = self.font.render("PRESS P!", False, BLACK)
        self.instructions_surf = self.font.render("MOVE WITH ARROWS OR WASD", False, BLACK)
        self.startup_surf = self.font.render("PRESS ANY KEY TO BEGIN", False, BLACK)
        self.startup_surf2 = self.font.render("PRESS P TO PAUSE", False, BLACK)
        self.game_over_surf = self.font.render("GAME OVER", False, RED)
        self.restart_surf = self.font.render("PRESS ANY KEY TO RESTART", False, RED)
        if os.path.exists(CURR_DIR + '/hiscore.txt'):
            hiscore = str(pickle.load(open(CURR_DIR + '/hiscore.txt')))
        else: hiscore = '0'
        self.hiscore_surf = self.font.render("HI: " + hiscore, False, BLACK)
        pygame.display.set_caption("NINJAs")

    def draw(self):
        """Redraws game window, fetching drawables from model"""
        self.screen.fill(WHITE)

        pygame.draw.rect(self.screen, [0, 255, 0], self.model.my_sprite.hitbox)

        for p in self.model.platform_handler.platforms:
            pygame.draw.rect(self.screen, [255,0,0],p.killbox1)
            pygame.draw.rect(self.screen, [255,0,0],p.killbox2)
        drawables = self.model.get_drawables()
        for g in drawables:
            g.draw(self.screen)

        pygame.draw.rect(self.screen, [255,0,0], self.model.my_sprite.feet)

        self.draw_score()
        pygame.display.flip()

    def draw_pause(self):
        """Draws pause menu"""
        self.screen.fill(WHITE)
        self.screen.blit(self.pause_surf,(380,200))
        self.screen.blit(self.instructions_surf, (70,90))
        pygame.display.flip()

    def draw_score(self):
        """Draws score in corner"""
        self.score_surf = self.font.render(str(self.model.score), False, BLACK)
        self.screen.blit(self.score_surf, (20,70))
        self.screen.blit(self.hiscore_surf, (20,10))

    def draw_start(self):
        """Draws screen for startup"""
        self.draw()
        self.screen.blit(self.instructions_surf, (70, 140))
        self.screen.blit(self.startup_surf, (100, 200))
        self.screen.blit(self.startup_surf2, (215, 260))
        pygame.display.flip()

    def draw_game_over(self):
        """Prints game over screen"""
        self.screen.blit(self.game_over_surf,(350,350))
        self.screen.blit(self.restart_surf,(100,420))
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
        self.pause = False

    def setup(self):
        """Resets values for replay"""
        self.model = NinjaModel()
        self.view = NinjaView(self.model)
        self.controller = NinjaController(self.model)
        self.clock = pygame.time.Clock()
        self.pause = False

    def startup(self):
        """Displays startup window and waits for user"""
        start = False
        self.view.draw_start()
        while not start:
            for event in pygame.event.get():
                if event.type == pygame.KEYUP:
                    start = True 

    def MainLoop(self):
        """Game loop"""
        done = False 
        lastGetTicks = pygame.time.get_ticks()

        while not done:
            if self.pause:
                self.view.draw_pause()
                for event in pygame.event.get():
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_p:
                            self.pause = False
                            lastGetTicks = pygame.time.get_ticks()
                            self.model.ninja_jump = 0
                            self.model.ninja_horiz = 0
                    elif event.type == pygame.QUIT:
                        done = True 
            elif self.model.alive:
                t = pygame.time.get_ticks()
                # delta time in seconds.
                dt = (t - lastGetTicks) / 1000.0
                lastGetTicks = t

                done, self.pause = self.controller.process_events()
                self.model.update(dt)
                self.view.draw()
                self.clock.tick(60)
            else: 
                done = True 
                if os.path.exists(CURR_DIR + '/hiscore.txt'):
                    count = pickle.load(open(CURR_DIR + '/hiscore.txt', 'rb'))
                else: count = 0
                if self.model.score > count:
                    count = self.model.score
                pickle.dump(count,open(CURR_DIR + '/hiscore.txt', 'wb'))    


def gameover(MainWindow):
    """Allows player to restart"""
    start = True
    while start:
        MainWindow.view.draw_game_over()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                MainWindow.setup()
                MainWindow.MainLoop()
            elif event.type == pygame.QUIT:
                start = False
                break        

if __name__ == '__main__':
    MainWindow = NinjaMain()
    MainWindow.startup()
    MainWindow.MainLoop()   
    gameover(MainWindow)
