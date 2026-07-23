# Gem Hunt Quartz 0.8 - temporary arts
from json import load, dump
from typing import Any
import pygame
from rich import print
from sys import exit
from random import randint

class Player():
    # first the variable classes
    class Position:
        def __init__(self, x: float, y: float) -> None:
            self.x = x
            self.y = y

    class Size:
        def __init__(self) -> None:
            self.width: int
            self.height: int

            self.width = 75
            self.height = 150

    class Velocity:
        def __init__(self) -> None:
            self.x: float
            self.y: float
            
            self.x = 0
            self.y = 0

    class Acceleration:
        def __init__(self) -> None:
            self.x: int
            self.y: int

            self.x = 1100
            self.y = 1500

    class MaxSpeed:
        def __init__(self) -> None:
            self.moving: float
            self.standing: float
            self.sfx: float
            self.falling: float

            self.moving = 350
            self.standing = 25
            self.sfx = 50
            self.falling = 2500

    class Friction:
        def __init__(self) -> None:
            self.standing: float
            self.dashing: float

            self.standing = 0.9
            self.dashing = 0.95

    class Dash:
        def __init__(self) -> None:
            self.timer: float
            self.max: float
            self.dashing: bool
            self.boost_x: int
            self.boost_y: int

            self.dashing = False
            self.timer = 1
            self.max = 1
            self.boost_x = 1000
            self.boost_y = -500

    class Jump:
        def __init__(self) -> None:
            self.jumping: bool
            self.force: int
            self.release_force: int

            self.jumping = False
            self.force = 750
            self.release_force = 150

    class Detection:
        def __init__(self) -> None:
            self.size: int
            self.subtract: int
            self.middle: float

            self.size = 5
            self.subtract = 6
            self.middle = self.subtract / 2

    class PlayingSfx:
        def __init__(self) -> None:
            self.walk: bool
            self.dash: bool

            self.walk = False
            self.dash = False

    def __init__(self, x: float, y: float) -> None:
        # type definitons
        self.position: Player.Position
        self.size: Player.Size
        self.velocity: Player.Velocity
        self.speed: Player.MaxSpeed
        self.friction: Player.Friction

        # variables
        self.position = self.Position(x, y)
        self.size = self.Size()
        self.velocity = self.Velocity()
        self.max_speed = self.MaxSpeed()
        self.detection = self.Detection()
        self.jump = self.Jump()
        self.dash = self.Dash()
        self.friction = self.Friction()
        self.acceleration = self.Acceleration()
        self.playing_sfx = self.PlayingSfx()
        self.wall_list = []

    def make_wall_list(self):
        global wall_list
        self.wall_list = []

        for wall in wall_list:
            wall_rect = wall["position"]

            self.wall_list.append(wall_rect)

    def gravity(self) -> None:
        if self.velocity.y <= 0:
            self.headhit()

        # make a future player and check if he touches the ground
        future_x = self.position.x + self.detection.middle
        future_y = (self.position.y + self.velocity.y * dt) + self.size.height - self.detection.size + 1
        future_width = self.size.width - self.detection.subtract
        future_height = self.detection.size

        future_player = pygame.Rect(future_x, future_y, future_width, future_height)
        will_touch_ground = any(future_player.colliderect(wall) for wall in self.wall_list)

        if will_touch_ground:
            for wall in self.wall_list:
                if future_player.colliderect(wall):
                    self.position.y = wall.top - self.size.height
                    self.velocity.y = 0
                    self.jumping = False
                    break
        else:
            self.velocity.y += self.acceleration.y * dt
            self.velocity.y = min(self.velocity.y, self.max_speed.falling)
            self.position.y += self.velocity.y * dt

    def horizontal(self, movement_side: int) -> None:
        "Horizontal movement"
        # handle wall list

        # set detection side
        if self.velocity.x > self.max_speed.standing:
            detection_side = 1
        elif self.velocity.x < -self.max_speed.standing:
            detection_side = -1
        else:
            detection_side = 0

        half_width = self.size.width / 2

        future_x = self.position.x + half_width + detection_side * half_width + self.velocity.x * dt - self.detection.size / 2 + (0 * detection_side)
        future_y = self.position.y + self.detection.middle
        future_width = self.detection.size
        future_height = self.size.height - self.detection.subtract

        future_player = pygame.Rect(future_x, future_y, future_width, future_height)
        will_touch_walls = any(future_player.colliderect(wall) for wall in self.wall_list)

        if will_touch_walls:
            # move you away from the walls
            for wall in self.wall_list:
                if future_player.colliderect(wall):
                    if detection_side == 1: # right
                        self.position.x = wall.left - self.size.width
                        self.velocity.x = 0

                    if detection_side == -1: # left 
                        self.position.x = wall.right
                        self.velocity.x = 0
        else:
            # apply velocity
            # if youre not moving
            if movement_side == 0:
                # apply friction
                self.velocity.x *= self.friction.standing
                if abs(self.velocity.x) < self.max_speed.standing:
                    self.velocity.x = 0

            # if your speed is more then the max speed and youre not standing 
            if abs(self.velocity.x) > self.max_speed.moving and movement_side != 0:
                excess_velocity = abs(self.velocity.x) - self.max_speed.moving
                
                if self.dash.dashing:
                    excess_velocity *= self.friction.dashing
                else:
                    excess_velocity *= self.friction.standing


                self.velocity.x = 0

                if movement_side != detection_side:
                    self.velocity.x += (self.acceleration.x * movement_side) * dt

                self.velocity.x += (self.max_speed.moving + excess_velocity) * detection_side

            else:
                self.velocity.x += (self.acceleration.x * movement_side) * dt

            self.position.x += self.velocity.x * dt

        # play sfx
        if self.touching_ground() and abs(self.velocity.x) > self.max_speed.sfx:
            if not self.playing_sfx.walk:
                walk_channel.unpause()
                self.playing_sfx.walk = True
        else:
            walk_channel.pause()
            self.playing_sfx.walk = False

    def headhit(self) -> None:
        # we make a future player
        future_x = self.position.x + self.detection.middle
        future_y = self.position.y + self.velocity.y * dt
        future_width = self.size.width - self.detection.subtract
        future_height = self.detection.size

        future_player = pygame.Rect(future_x, future_y, future_width, future_height)
        will_bonk = any(future_player.colliderect(wall) for wall in self.wall_list)

        if will_bonk:
            for wall in self.wall_list:
                if future_player.colliderect(wall):
                    self.position.y = wall.bottom
                    self.velocity.y = 0

    def movement_input(self) -> None:
        key_pressed = pygame.key.get_pressed()
        left_pressed = any(key_pressed[key] for key in KEYS_LEFT)
        right_pressed = any(key_pressed[key] for key in KEYS_RIGHT)
        jump_pressed = any(key_pressed[key] for key in KEYS_UP)

        side = 0
        
        # horizontal movement
        if left_pressed:
            side -= 1
        if right_pressed:
            side += 1

        self.horizontal(side)

        # jumping
        if True:
            if jump_pressed and self.touching_ground() and not self.jump.jumping:
                self.velocity.y = -self.jump.force
                self.jump.jumping = True
                jump_channel.play(sfx_jump)

            if self.jump.jumping and not jump_pressed:
                self.jump.jumping = False
                if self.velocity.y < -self.jump.release_force:
                    self.velocity.y = -self.jump.release_force

        # dashing
        if self.dash_counter(side):
            self.dash.dashing = False

            if self.touching_ground():
                if side != 0:
                    if key_pressed[pygame.K_LSHIFT]:
                        self.velocity.x += self.dash.boost_x * side
                        self.velocity.y = self.dash.boost_y
                        self.dash.dashing = True
                        sfx_dash.play()

    def dash_counter(self, side) -> bool:
        key_pressed = pygame.key.get_pressed()

        if not(self.dash.timer >= self.dash.max):
            self.dash.timer += dt
            return False
        
        if not(self.playing_sfx.dash):
            self.playing_sfx.dash = True
            sfx_get_dash.play()

        if key_pressed[pygame.K_LSHIFT] and side != 0 and self.touching_ground():
            self.playing_sfx.dash = False
            self.dash.timer = 0
        
        return True               

    def movement_loop(self) -> None:
        "The movement loop for the player"
        self.movement_input()
        self.gravity()
    
    def touching_ground(self) -> bool:
        # make a future player and check if he touches the ground
        future_x = self.position.x + self.detection.middle
        future_y = (self.position.y + self.velocity.y * dt) + self.size.height - self.detection.size + 1
        future_width = self.size.width - self.detection.subtract
        future_height = self.detection.size

        future_player = pygame.Rect(future_x, future_y, future_width, future_height)
        will_touch_ground = any(future_player.colliderect(wall) for wall in self.wall_list)

        if will_touch_ground:
            return True
        else:
            return False

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.position.x, self.position.y, self.size.width, self.size.height)

    def draw(self) -> None:
        topleft = (self.position.x, self.position.y)

        Window.blit(png_player, topleft)

    def level_ends(self) -> None:
        global level
        # left
        if self.position.x < 0:
            level[0] -= 1
            self.position.x = windowSize[0] - self.size.width - 1

        # right
        if self.position.x > windowSize[0] - self.size.width:
            level[0] += 1
            self.position.x = 1

        # up
        if self.position.y < 0:
            if level[1] + 1 != 34:
                level[1] += 1
                self.position.y = windowSize[1] - self.size.height - 1

        # down
        if self.position.y > windowSize[1] - self.size.height:
            level[1] -= 1
            self.position.y = 1

def level_loader() -> None:
    # first we load the data
    try:
        with open("data/scripts/levelData.json", "r") as levelData:
            data = load(levelData)[str(level)]
    except KeyError:
        raise ValueError("Illegal level") from None
    

    # we load the walls that cant change
    global wall_list
    wall_list = []

    wall_positions = data["wallData"]["walls"]

    for wall in wall_positions:
        wall_list.append({"position": pygame.Rect(wall), "visible": True})
    

    # now we load the walls that can change
    global switch_list
    switch_list = []

    switchWalls = data["wallData"]["switchWalls"]

    for wall in switchWalls:
        index = wall["index"]
        wall_bool: bool = wall["switch"]
        position = wall["position"]

        variable = lever_flipped[index] == wall_bool

        if variable:
            switch_list.append({"position": pygame.Rect(position), "index": index, "visible": variable})
            wall_list.append({"position": pygame.Rect(position), "visible": False})



    # now we load the levers
    leverData: dict = data["leverData"]
    
    global levers
    levers = {
    "lever1": {"position": [], "index": 0},
    "lever2": {"position": [], "index": 0},
    "lever3": {"position": [], "index": 0}
    }

    for name, info in leverData.items():
        position = info["position"]

        if len(position) == 2: # this is used as a way to know that its a real lever
            # this is because the levels were build with the size being (100, 50) but i have to change it for drawing
            x, y = info["position"]
            y = 50 - LEVER_DETECTION_SIZE[1] + y

            levers[name]["position"] = (x, y)
            levers[name]["index"] = info["index"]
        else:
            pass # we already set the levers to 0
            pass


    # now we load the extra data (f.e the ground)
    global ground, final_score

    extraData = data["extraData"]

    if "ground" in extraData:
        ground = pygame.Rect(0, 850, 1920, 169)
        wall_list.append({"position": ground, "visible": True})
    else:
        ground = pygame.Rect(0, 0, 0, 0)

    if "final_level" in extraData:
        lever_data = leverData["lever1"]["position"]
        levers["lever1"]["position"] = [lever1_x, lever_data[1]]
        lever_data = leverData["lever2"]["position"]
        levers["lever2"]["position"] = [lever2_x, lever_data[1]]

def level_modifier() -> None:
    global allow_lever_pull
    
    for player in players:
        for lever, info in levers.items():

            lever_position = info["position"]
            try:
                lever_rect = pygame.Rect(lever_position[0], lever_position[1], LEVER_DETECTION_SIZE[0], LEVER_DETECTION_SIZE[1])
            except IndexError:
                break

            index = info["index"]

            if player.rect().colliderect(lever_rect):

                key_pressed = pygame.key.get_pressed()
                lever_pulled = any(key_pressed[key] for key in KEYS_DOWN)

                if lever_pulled:
                    if allow_lever_pull:
                        allow_lever_pull = False
                        lever_flipped[index] = not(lever_flipped[index])

                        lever_sfxs[randint(0, 7)].play()

                        level_loader()
                else:
                    allow_lever_pull = True

    global lever1_x, lever2_x, final_score

    if lever_flipped[16]:
        lever_flipped[16] = False
        lever_flipped[18] = True
        lever1_x = -100
        lever2_x = randint(200, 1720)
        level_loader()

    if lever_flipped[17]:
        lever_flipped[17] = False
        lever2_x = randint(200, 1720)
        final_score += 1

    if 2 < final_score < 5:
        text("gg", 1920 / 2, 1080 / 2, (255, 255, 255))

def drawSyntax() -> None:
    raise NotImplementedError("im too lazy to do this rn but i will add it")
    
def draw() -> None:
    # background
    match level[1]:
        case 1:
            Window.blit(png_bg_y1, (0, 0))
        case 2:
            Window.blit(png_bg_y2, (0, 0))
        case 3:
            Window.blit(png_bg_y3, (0, 0))
        case _:
            print("error error on the wall")

    # lever
    for name, info in levers.items():
        position = info["position"]

        # draw lever sprite
        index = info["index"]
        index_bool = lever_flipped[index]

        # get color
        if len(position) > 0:
            lever_x_add = (150 - LEVER_DETECTION_SIZE[0]) / 4

            # get the color
            color_data = index_colors[str(index)]
            color = tuple(color_data) # <- turning it from [0, 0, 0] to (0, 0, 0) for pygame

            pygame.draw.rect(Window, color, (position[0] + lever_x_add, position[1], LEVER_DETECTION_SIZE[0], LEVER_DETECTION_SIZE[1]))

            if not index_bool:
                Window.blit(png_lever_false, (position[0], position[1] - lever_size[1] + LEVER_DETECTION_SIZE[1]))
            else:
                Window.blit(png_lever_true, (position[0], position[1] - lever_size[1] + LEVER_DETECTION_SIZE[1]))
         
    # walls
    if True:
        # switch walls
        for switch_wall in switch_list:
            rect = switch_wall["position"]
            index = switch_wall["index"]
            visible = switch_wall["visible"]
        

            # we grab the color data        
            color_data = index_colors[str(index)]
            alpha = 32
            color = (*color_data, alpha * 2)

            rect_surface = pygame.Surface(rect.size, pygame.SRCALPHA)

            pygame.draw.rect(rect_surface, color, rect_surface.get_rect())

            if visible:
                wall_drawn = png_wall.subsurface(rect)
                wall_drawn.set_alpha(alpha * 7)
                rect_surface.blit(wall_drawn, (0, 0))

            Window.blit(rect_surface, rect.topleft)


        # normal walls
        for wall_rect_new in wall_list:

            rect = wall_rect_new["position"]
            visible = wall_rect_new["visible"]

            wall_png = png_wall.subsurface(rect)

            if visible:
                Window.blit(wall_png, rect.topleft)

    if ground != pygame.Rect(0, 0, 0, 0):
        Window.blit(png_ground, ground.topleft)

    for player in players:
        player.draw()

def text(string: str, x: float, y: float, color: tuple[int, int, int] = (255, 255, 255)) -> None:
    "Draws text on the screen"

    font = pygame.font.SysFont(None, 60)
    text = font.render(string, False, color)
    Window.blit(text, (x, y))

# set the type definitions for the variables
players: list[Player]
level: list[int]
level_last_frame: list[int]
FPS: int
lever1_x: int
lever2_x: int
final_score: int
wall_list: list
switch_list: list[dict]
levers: dict
lever_flipped: list[bool]
FPS: int

# variables
level = [3, 2]
level_last_frame = [0, 0]
wall_list = []
switch_list = []
levers = {}
index_colors = {}
lever_flipped = [False] * 19
allow_lever_pull = True
lever1_x = 1700
lever2_x = -100
final_score = 0

players = [Player(768, 509)]
FPS = 120

KEYS_LEFT = [pygame.K_a, pygame.K_j, pygame.K_LEFT]
KEYS_RIGHT = [pygame.K_d, pygame.K_l, pygame.K_RIGHT]
KEYS_UP = [pygame.K_w, pygame.K_SPACE, pygame.K_i, pygame.K_UP]
KEYS_DOWN = [pygame.K_s, pygame.K_k, pygame.K_DOWN]

# pygame things
pygame.mixer.pre_init(48000, -16, 2, 256)
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(32)

windowSize = (1920, 1019)
Window = pygame.display.set_mode(windowSize) # here goes stuff

pygame.display.set_caption("Gem Hunt Quartz 0.8")
clock = pygame.time.Clock() 

# sprites
png_wall = pygame.image.load("data/assets/sprites/wall.png", ".png")

png_bg_y1 = pygame.image.load("data/assets/sprites/background_y1.png", ".png")
png_bg_y2 = pygame.image.load("data/assets/sprites/background_y2.png", ".png")
png_bg_y3 = pygame.image.load("data/assets/sprites/background_y3.png", ".png")

png_ground = pygame.image.load("data/assets/sprites/ground.png", ".png")

png_lever_false = pygame.image.load("data/assets/sprites/lever_false.png", ".png")
png_lever_true = pygame.image.load("data/assets/sprites/lever_true.png", ".png")

png_player = pygame.image.load("data/assets/sprites/player.png", ".png")

lever_size = (100, 100)
LEVER_DETECTION_SIZE = (50, 17)

png_lever_false = pygame.transform.scale(png_lever_false, (lever_size))
png_lever_true = pygame.transform.scale(png_lever_true, (lever_size))


# sfx
sfx_jump = pygame.mixer.Sound("data/assets/sfx/jump.wav")
jump_channel = pygame.mixer.Channel(0)

sfx_walk = pygame.mixer.Sound("data/assets/sfx/walk.wav")
walk_channel = pygame.mixer.Channel(1)
walk_channel.set_volume(2)
walk_channel.play(sfx_walk, -1)

sfx_get_dash = pygame.mixer.Sound("data/assets/sfx/get_dash.wav")
sfx_dash = pygame.mixer.Sound("data/assets/sfx/dash.wav")

lever_sfxs = [
    pygame.mixer.Sound(f"data/assets/sfx/lever/lever{i}.wav") for i in range(1, 9)
]

for lever in lever_sfxs:
    lever.set_volume(0.5)

# bgm = pygame.mixer.music.load("data/assets/sfx/bgm.wav")
# pygame.mixer.music.set_volume(0.6)
# pygame.mixer.music.play(-1)

with open("data/scripts/indexColors.json", "r") as indexColors:
    index_colors = load(indexColors)

# game loop
while True:
    # delta time
    dt = clock.tick_busy_loop(FPS) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit('Exiting the program')

    # this makes it so that if it takes 3 times as long to register an update it doesnt update,
    # so that it doesnt change players position whlie dragging the window or smth
    # if dt < (1 / FPS) * 3:
    Window.fill((255, 0, 0))

    for player in players:
        player.movement_loop()
        player.level_ends()
    
    if level != level_last_frame:
        level_loader()
        for player in players:
            player.make_wall_list()
    level_modifier()
    draw()

    pygame.display.update()

    level_last_frame = level.copy()
    # else:
    #     print('[green]was experiencing some lag')