# Gem Hunt Quartz 0.7.2 - sfx for dashing
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
            self.timer = 0
            self.max = 1
            self.boost_x = 1000
            self.boost_y = -500

    class Jump:
        def __init__(self) -> None:
            self.jumping: bool
            self.force: int
            self.release_force: int

            self.jumping = False
            self.force = 800
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

    def gravity(self) -> None:
        if self.velocity.y <= 0:
            self.headhit()

        # make a future player and check if he touches the ground
        future_x = self.position.x + self.detection.middle
        future_y = (self.position.y + self.velocity.y * dt) + self.size.height - self.detection.size + 1
        future_width = self.size.width - self.detection.subtract
        future_height = self.detection.size

        future_player = pygame.Rect(future_x, future_y, future_width, future_height)
        will_touch_ground = any(future_player.colliderect(wall) for wall in wall_list)

        if will_touch_ground:
            for wall in wall_list:
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
        
        # set detection side
        if self.velocity.x > self.max_speed.standing:
            detection_side = 1
        elif self.velocity.x < -self.max_speed.standing:
            detection_side = -1
        else:
            detection_side = 0

        half_width = self.size.width / 2

        future_x = self.position.x + half_width + detection_side * half_width + self.velocity.x * dt - self.detection.size / 2 + (1 * detection_side)
        future_y = self.position.y + self.detection.middle
        future_width = self.detection.size
        future_height = self.size.height - self.detection.subtract

        future_player = pygame.Rect(future_x, future_y, future_width, future_height)
        will_touch_walls = any(future_player.colliderect(wall) for wall in wall_list)

        if will_touch_walls:
            # move you away from the walls
            for wall in wall_list:
                if future_player.colliderect(wall):
                    if detection_side == 1: # right
                        self.position.x = wall.left - self.size.width
                        self.velocity.x = 0

                    if detection_side == -1: # left 
                        self.position.x = wall.right
                        self.velocity.x = 0
        else:
            # apply velocity
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
                print(self.velocity.x)

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
        will_bonk = any(future_player.colliderect(wall) for wall in wall_list)

        if will_bonk:
            for wall in wall_list:
                if future_player.colliderect(wall):
                    self.position.y = wall.bottom
                    self.velocity.y = 0

    def movement_imput(self) -> None:
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
                        self.velocity.y += self.dash.boost_y
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

        if key_pressed[pygame.K_LSHIFT] and side != 0:
            self.playing_sfx.dash = False
            self.dash.timer = 0
        
        return True               

    def movement_loop(self) -> None:
        "The movement loop for the player"
        self.movement_imput()
        self.gravity()
    
    def touching_ground(self) -> bool:
        # make a future player and check if he touches the ground
        future_x = self.position.x + self.detection.middle
        future_y = (self.position.y + self.velocity.y * dt) + self.size.height - self.detection.size + 1
        future_width = self.size.width - self.detection.subtract
        future_height = self.detection.size

        future_player = pygame.Rect(future_x, future_y, future_width, future_height)
        will_touch_ground = any(future_player.colliderect(wall) for wall in wall_list)

        if will_touch_ground:
            return True
        else:
            return False

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.position.x, self.position.y, self.size.width, self.size.height)

    def draw(self) -> None:
        pygame.draw.rect(Window, (125, 0, 0), (self.position.x, self.position.y, self.size.width, self.size.height))
        pygame.draw.rect(Window, (255, 0, 0), (self.position.x, self.position.y, self.size.width, self.size.height), 5)

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
        wall_list.append(pygame.Rect(wall))
    

    # now we load the walls that can change
    switchWalls = data["wallData"]["switchWalls"]

    for wall in switchWalls:
        index = wall["index"]
        wall_bool = wall["switch"]
        position = wall["position"]

        if lever_flipped[index] == wall_bool:
            wall_list.append(pygame.Rect(position))


    # now we load the levers
    leverData: dict = data["leverData"]

    for name, info in leverData.items():
        position = info["position"]

        if len(position) == 4: # this is used as a way to know that its a real lever
            levers[name]["position"] = pygame.Rect(position)
            levers[name]["index"] = info["index"]
        else:
            levers[name]["position"] = pygame.Rect(0, 0, 0, 0)


    # now we load the extra data (f.e the ground)
    global ground, final_score
    ground = pygame.Rect(0, 0, 0, 0)

    extraData = data["extraData"]

    if "ground" in extraData:
        ground = pygame.Rect(0, 850, windowSize[0], windowSize[1])
        wall_list.append(ground)

    if "final_level" in extraData:
        lever_data = leverData["lever1"]["position"]
        levers["lever1"]["position"] = pygame.Rect(lever1_x, lever_data[1], lever_data[2], lever_data[3])
        lever_data = leverData["lever2"]["position"]
        levers["lever2"]["position"] = pygame.Rect(lever2_x, lever_data[1], lever_data[2], lever_data[3])

def level_modifier() -> None:
    global allow_lever_pull
    
    for player in players:
        for lever, info in levers.items():

            lever_position = info["position"]
            lever_rect = pygame.Rect(lever_position)

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

def draw() -> None:
    for name, info in levers.items():
        position = info["position"]

        pygame.draw.rect(Window, (255, 0, 0), position)
    
    for wall in wall_list:
        pygame.draw.rect(Window, (75, 75, 75), wall)
    
    try:
        pygame.draw.rect(Window, (63, 171, 42), ground)
    except:
        # there is no ground
        pass

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
wall_list: list[pygame.Rect]
levers: dict
lever_flipped: list[bool]
FPS: int

# variables
level = [2, 1]
level_last_frame = [0, 0]
wall_list = []
levers = {
    "lever1": {"position": pygame.Rect(0, 0, 0, 0), "index": 0},
    "lever2": {"position": pygame.Rect(0, 0, 0, 0), "index": 0},
    "lever3": {"position": pygame.Rect(0, 0, 0, 0), "index": 0}
}
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
Window = pygame.display.set_mode(windowSize)
pygame.display.set_caption("Gem Hunt Quartz 0.6.1")
clock = pygame.time.Clock() 

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

bgm = pygame.mixer.music.load("data/assets/sfx/bgm.wav")
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1)

# game loop
while True:
    # delta time
    dt = clock.tick(FPS) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit('Exiting the program')

    # this makes it so that if it takes 3 times as long to register an update it doesnt update,
    # so that it doesnt changes players position whlie dragging the window or smth
    if dt < (1 / FPS) * 3:
        Window.fill((12, 12, 100))
        
        for player in players:
            player.movement_loop()
            player.level_ends()
        
        if level != level_last_frame:
            level_loader()
        level_modifier()
        draw()

        pygame.display.update()

        level_last_frame = level.copy()
    else:
        print('[green]was experiencing some lag')