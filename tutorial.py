import os                            #a way of using operating system-dependent functionality like reading or writing to the filesystem
import random                        #This module implements pseudo-random number generators for various distributions
import math                          #This module provides mathematical functions
import pygame                        #library used for creating game in python
from os import listdir               #This imports the listdir function, which returns a list of the names of the entries in a given directory
from os.path import isfile, join     #These functions help in checking if a path is a file and joining paths respectively
pygame.init()                        #This initializes all the Pygame modules

pygame.display.set_caption("Platformer")

BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 700
FPS = 60                             # This sets the frames per second 
PLAYER_VEL = 5                       # indicating how many pixels the player can move per frame


window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):                 # this function takes a list of sprites (images) and returns a new list where each sprite is flipped horizontally (mirrored).
    return [pygame.transform.flip(sprite, True, False)for sprite in sprites]  #if ture it will flip horizontally ,if false then vertically

def load_sprite_sheets(dir1, dir2, width, height, direction=False):   #This function loads sprite sheets from a specified directory, extracts individual sprites, and optionally creates mirrored versions for left-facing animations
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]
    
    all_sprites = {}
    
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width,height),pygame.SRCALPHA, 32)
            rect = pygame.Rect(i*width,0,width,height)
            surface.blit(sprite_sheet,(0,0),rect) 
            sprites.append(pygame.transform.scale2x(surface))
            
            
        if direction:   #if True, the sprites are stored with keys for both right-facing and left-facing versions (using the flip function to create the left-facing sprites) and if false only the right-facing sprites are stored
            all_sprites[image.replace(".png","")+ "_right"] = sprites
            all_sprites[image.replace(".png","")+ "_left"] = flip(sprites)
        
        else:
            all_sprites[image.replace(".png","")] = sprites
            
    return all_sprites

def get_block(size):
    path = join("assets","Terrain","Terrain.png")    #Constructs the path to the terrain image located in the "Terrain" directory
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size),pygame.SRCALPHA,32)
    rect = pygame.Rect(96, 4, size, size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)

                     
class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)      # Defines a constant color for the player (red in this case)
    GRAVITY = 1              # a constant for gravity affecting the player
    SPRITES = load_sprite_sheets("MainCharacters", "PinkMan", 32, 32, True)
    ANIMATION_DELAY = 4      # Sets a delay for sprite animation, controlling how quickly the frames change

    def __init__(self, x, y, width, height):           # object with position (x, y) and dimensions (width, height)
        super().__init__()   
        self.rect = pygame.Rect(x, y, width, height)   # A rectangle representing the player's position and size
        self.x_vel = 0            #Initializes the player's horizontal (x_vel) to zero
        self.y_vel = 0            # Initialize  vertical (y_vel) velocities to zero
        self.mask = None          # Initializes a mask for collision detection
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0 
        self.jump_count = 0
        self.hit = False         #Initializes a flag to indicate if the player has been hit and a counter for how long the hit state lasts
        self.hit_count = 0
      
    def jump(self):
        self.y_vel = -self.GRAVITY * 10 # the vertical velocity to a negative value, simulating an upward jump
        self.animation_count = 0
        self.jump_count += 1            # to keep track of how many times the player has jumped
        if self.jump_count == 1:        # If this is the first jump reset the fall count
            self.fall_count = 0

        
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        
    def make_hit(self):
        self.hit = True
        self.hit_count = 0
        
    def move_left(self, vel):
        self.x_vel = -vel               # Sets the horizontal velocity to a negative value, moving the player to the left
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
        
    def move_right(self, vel):         # Sets the horizontal velocity to a positive value, moving the player to the right
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0
    
    def landed(self):                  # Resets the fall count, sets the vertical velocity to zero, and resets the jump count when the player lands
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
        
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1  
        
    def loop(self, fps):             # Updates the vertical velocity based on gravity and the fall count, ensuring it doesn't exceed a certain value
        self.y_vel += min(1,(self.fall_count / fps)* self.GRAVITY)
        self.move(self.x_vel, self.y_vel)
        
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps*2:
            self.hit = False
        
        self.fall_count += 1
        self.update_sprite()
    
    def update_sprite(self):
         sprite_sheet = "idle"
         if self.hit:
            sprite_sheet = "hit"
         elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
         elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
         elif self.x_vel != 0:
            sprite_sheet = "run"

         sprite_sheet_name = sprite_sheet + "_" + self.direction
         sprites = self.SPRITES[sprite_sheet_name]
         sprite_index = (self.animation_count // self.ANIMATION_DELAY) %len(sprites)
         self.sprite = sprites[sprite_index]
         self.animation_count += 1
         self.update()
        
    def update(self):
        self.rect = self.sprite.get_rect(topleft =(self.rect.x,self.rect.y))    
        self.mask = pygame.mask.from_surface(self.sprite) 
          
    def draw(self, win, offset_x):
        
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None): 
        super().__init__() 
        self.rect =pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width,height),pygame.SRCALPHA)
        self.width = width 
        self.height = height
        self.name = name 
    
    def draw(self, win, offset_x):
        win.blit(self.image,(self.rect.x - offset_x, self.rect.y))
    
class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block =get_block(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3
        
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
            
    def on(self):
        self.animation_name = "on"
        
    def off(self):
        self.animation_name = "off"
        
    def loop(self):
        
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) %len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft =(self.rect.x,self.rect.y))    
        self.mask = pygame.mask.from_surface(self.image) 
        
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


class Fan(Object):
    ANIMATION_DELAY = 3
        
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fan")
        self.fan = load_sprite_sheets("Traps", "Fan", width, height)
        self.image = self.fan["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"
            
    def on(self):
        self.animation_name = "on"
        
    def off(self):
        self.animation_name = "off"
        
    def loop(self):
        
        sprites = self.fan[self.animation_name]
        sprite_index = (self.animation_count // 
                        self.ANIMATION_DELAY) %len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft =(self.rect.x,self.rect.y))    
        self.mask = pygame.mask.from_surface(self.image) 
        
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

        
def get_background(name):
    image = pygame.image.load(join("assets","Background",name))
    _,_,width,height = image.get_rect()
    tiles = []
    
    for i in range(WIDTH // width+1):
        for j in range(HEIGHT // height+1):
            pos = [i*width, j*height]
            tiles.append(pos)
    
    return tiles, image

def draw(window, background, bg_image, player, objects, fire, fan, offset_x):
    for tile in background:
        window.blit(bg_image, tuple(tile))

    for obj in objects:
        obj.draw(window, offset_x)
    
    fire.draw(window, offset_x)
    fan.draw(window, offset_x)
    player.draw(window, offset_x)
    
    pygame.display.update()
 
def handle_vertical_collision(player, objects, dy):
    collided_objects = []  
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
                
            collided_objects.append(obj)  
    return collided_objects 

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
        
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right,*vertical_collide]
    
    for obj in vertical_collide:
        if obj.name == "fire":
            player.make_hit()
            
    for obj in vertical_collide:
        if obj.name == "fan":
            player.make_hit()
    
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")
    
    block_size = 96 
    
    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()  # Turn on the fire animation
    
    fan = Fan(300, HEIGHT - block_size - 24, 8, 32)
    fan.on() 

    # Create the floor blocks
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, WIDTH * 2 // block_size)]
    
    # Create additional platform blocks
    y_positions = [HEIGHT - block_size * i for i in [4, 4, 4, 6, 6, 6, 2, 2, 5, 5, 3, 3, 4, 3, 2, 4, 4, 3]]
    x_positions = [0, 96, -96, -250, -154, -58, 300, 396, 300, 396, 500, 596, 700, 900, 1000, 1000, 1096, 1196]
    blocks = [Block(x, y, block_size) for x, y in zip(x_positions, y_positions)]
    
    # Combine all objects, including fire
    objects = [*floor, *blocks, fire]
    objects = [*floor, *blocks, fan]
    
    offset_x = 0
    scroll_area_width = 200
    
    run = True
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump()
        
        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, fire, offset_x)    
        
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= WIDTH - scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel
            
    pygame.quit()
    quit()

    
if __name__ == "__main__":
    main(window)
    
