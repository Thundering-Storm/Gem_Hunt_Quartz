# Gem Hunt Quartz 0.4 - total rework of leveldatabase
from json import load
import pygame
from sys import exit
from rich import print
from random import randint

class Player():
    # first the variable classes
    class Position:
        def __init__(self, x: float, y: float) -> None:
            self.x = x
            self.y = y

    class Size:
        def __init__(self, width: int, height: int) -> None:
            self.width = width
            self.height = height

    class Velocity:
        def __init__(self, x: float, y: float) -> None:
            self.x = x
            self.y = y

    class Speed:
        def __init__(self, max: float, standing_max: float, friction: float) -> None:
            self.max = max
            self.standing_max = standing_max
            self.friction = friction

    class Detection:
        def __init__(self, fat: int, subtract: int) -> None:
            self.fat = fat
            self.subtract = subtract
            self.middle = subtract / 2

    def __init__(self, x: float, y: float) -> None:
        # type definitons
        self.position: Player.Position
        self.size: Player.Size
        self.velocity: Player.Velocity
        self.speed: Player.Speed
        self.jumpheight: float
        self.detection_size: int

        # variables
        self.position = self.Position(x, y)
        self.size = self.Size(75, 150)
        self.velocity = self.Velocity(0, 0)
        self.speed = self.Speed(3.3, 0.5, 0.95)
        self.detection = self.Detection(10, 6)
        self.jumpheight = 7.5

    def gravity(self) -> None:
        "gravity"
        if self.velocity.y < 0:
            self.headhit()

        # make a future player and check if he touches the ground
        future_x = self.position.x + self.detection.middle
        future_y = (self.position.y + self.velocity.y) + self.size.height - self.detection.fat
        future_width = self.size.width - self.detection.subtract
        future_height = self.detection.fat

        future_player = pygame.Rect(future_x, future_y, future_width, future_height)
        will_touch_ground = any(future_player.colliderect(wall) for wall in wall_list)

        if will_touch_ground:
            for wall in wall_list:
                if future_player.colliderect(wall):
                    self.position.y = wall.top - self.size.height
                    self.velocity.y = 0
        else:
            self.velocity.y += 15 * dt
            self.velocity.y = min(self.velocity.y, 50)
            self.position.y += self.velocity.y

    def horizontal(self, side: int) -> None:
        "Horizontal movement"
        
        # make future player
        half_width = self.size.width / 2

        if side != 0:
            future_x = self.position.x + half_width + side * half_width + self.velocity.x - self.detection.fat / 2
            detection_side = side
        else:
            # set side to the side u were moving
            if self.velocity.x > self.speed.standing_max:
                detection_side = 1
            elif self.velocity.x < -self.speed.standing_max:
                detection_side = -1
            else:
                # if you are not moving
                detection_side = 0

            future_x = self.position.x + half_width + detection_side * half_width + self.velocity.x - self.detection.fat / 2
        
        future_y = self.position.y + self.detection.middle
        future_width = self.detection.fat
        future_height = self.size.height - self.detection.subtract

        future_player = pygame.Rect(future_x, future_y, future_width, future_height)
        will_touch_walls = any(future_player.colliderect(wall) for wall in wall_list)

        if will_touch_walls:
            for wall in wall_list:
                if future_player.colliderect(wall):
                    if detection_side == 1: # right
                        self.position.x = wall.left - self.size.width
                        self.velocity.x = 0

                    if detection_side == -1: # left 
                        self.position.x = wall.right
                        self.velocity.x = 0
        else:
            # if (side != 0) and (self.velocity.x > 0) != (side > 0):
            #     self.velocity.x = 0

            self.velocity.x += (20 * side) * dt
            
            if side == 0:
                self.velocity.x *= self.speed.friction
                if -self.speed.standing_max < self.velocity.x < self.speed.standing_max:
                    self.velocity.x = 0


            self.velocity.x = min(self.speed.max, max(-self.speed.max, self.velocity.x))

            self.position.x += self.velocity.x

    def headhit(self) -> None:
        # we make a future player
        future_x = self.position.x + self.detection.middle
        future_y = self.position.y + self.velocity.y
        future_width = self.size.width - self.detection.subtract
        future_height = self.detection.fat

        future_player = pygame.Rect(future_x, future_y, future_width, future_height)
        

        will_bonk = any(future_player.colliderect(wall) for wall in wall_list)

        if will_bonk:
            for wall in wall_list:
                if future_player.colliderect(wall):
                    self.position.y = wall.bottom
                    self.velocity.y = 0

    def allow_jump(self) -> bool:
        "Returns if you are touching the ground or the bottom of any walls"
        future_player = pygame.Rect(self.position.x + 3, (self.position.y + self.velocity.y), self.size.width - 6, 150)
        will_touch_ground = any(future_player.colliderect(wall) for wall in wall_list)

        return will_touch_ground

    def jump(self) -> None:
        self.velocity.y = -self.jumpheight

    def checkpressed(self) -> None:
        "Checks wasd to move the player"
        keyPressed = pygame.key.get_pressed()
        side = 0
        
        if keyPressed[pygame.K_a]:
            side -= 1
        if keyPressed[pygame.K_d]:
            side += 1
        
        self.horizontal(side)

        if keyPressed[pygame.K_w] and self.allow_jump():
            self.jump()

    def movement_loop(self) -> None:
        "The movement loop for the player"
        self.gravity()
        self.checkpressed()

    def allow_dash(self):
        return NotImplementedError("will be added later")
    
    def rect(self):
        return pygame.Rect(self.position.x, self.position.y, self.size.width, self.size.height)

    def draw(self):
        for player in players:
            pygame.draw.rect(Window, (125, 0, 0), (player.position.x, player.position.y, player.size.width, player.size.height))
            pygame.draw.rect(Window, (255, 0, 0), (player.position.x, player.position.y, player.size.width, player.size.height), 5)

def levelEnds() -> None:
    "Changes levels if you are at the end of the screen"
    global level

    for player in players:
        # left
        if player.position.x < 0:
            level[0] -= 1
            player.position.x = windowSize[0] - player.size.width - 1

        # right
        if player.position.x > windowSize[0] - player.size.width:
            level[0] += 1
            player.position.x = 1

        # up
        if player.position.y < 0:
            if level[1] + 1 != 34:
                level[1] += 1
                player.position.y = windowSize[1] - player.size.height - 1

        # down
        if player.position.y > windowSize[1] - player.size.height:
            level[1] -= 1
            player.position.y = 1

def level_loader() -> None:
    # first we load the data
    try:
        with open("data/scripts/levelData.json", "r") as levelData:
            data = load(levelData)[str(level)]
    except KeyError:
        raise ValueError("Illegal level") from None

    # we load the walls that cant change
    wall_positions = data["wallData"]["walls"]

    global wall_list
    wall_list = []
    try:
        for wall_square in wall_positions:
            wall = (wall_square[0], wall_square[1], wall_square[2], wall_square[3])
            
            wall_list.append(pygame.Rect(wall))
    except:
        raise NotImplementedError("moron u need to remove the final lists") from None


    # now we load the levers
    leverData: dict = data["leverData"]

    for name, info in leverData.items():
        position = info["position"]

        if len(position) == 4:
            levers[name]["position"] = pygame.Rect(position)
        else:
            levers[name]["position"] = pygame.Rect(0, 0, 0, 0)


    # now we load the extra data (f.e the ground)
    extraData = data["extraData"]

    global ground

    if "ground" in extraData:
        ground = pygame.Rect(0, 850, windowSize[0], windowSize[1])
        wall_list.append(ground)


    # now we load the walls loaded by switch
    switchWalls = data["wallData"]["switchWalls"]

    for wall in switchWalls:
        index = wall["index"]
        wall_bool = wall["switch"]
        position = wall["position"]

        if lever_flipped[index] == wall_bool:
            wall_list.append(pygame.Rect(position))

def level_modifier():
    global allow_lever_pull
    
    for player in players:
        for lever, info in levers.items():

            lever_position = info["position"]
            lever_rect = pygame.Rect(lever_position)

            index = info["index"]

            if player.rect().colliderect(lever_rect):
                keyPressed = pygame.key.get_pressed()
                if keyPressed[pygame.K_s]:
                    if allow_lever_pull:
                        allow_lever_pull = False
                        lever_flipped[index] = not(lever_flipped[index])
                        level_loader()
                else:
                    allow_lever_pull = True

def draw() -> None:
    for name, info in levers.items():
        position = info["position"]

        pygame.draw.rect(Window, (255, 0, 0), position)
        pygame.draw.rect(Window, (255, 0, 0), position)
        pygame.draw.rect(Window, (255, 0, 0), position)
    
    for wall in wall_list:
        pygame.draw.rect(Window, (75, 75, 75), wall)
    
    # pygame.draw.rect(Window, (63, 171, 42), ground)
    
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
lever_flipped: list[bool]
FPS: int
windowSize: tuple[int, int]

# variables

level = [1, 1]
level_last_frame = [0, 0]
FPS = 120

lever_x = 1700
lever2_x = -100
final_score = 0

wall_list = []
levers: dict
levers = {
    "lever1": {"position": pygame.Rect(0, 0, 0, 0), "index": 0},
    "lever2": {"position": pygame.Rect(0, 0, 0, 0), "index": 0},
    "lever3": {"position": pygame.Rect(0, 0, 0, 0), "index": 0}
}

lever_flipped = [False] * 20

players = [
    Player(768, 509)
]

windowSize = (1920, 1019)

# pygame things
pygame.init()
Window = pygame.display.set_mode(windowSize)
pygame.display.set_caption("Gem Hunt Quartz 0.4")
clock = pygame.time.Clock()

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

        levelEnds()
        
        if level != level_last_frame:
            level_loader()
        level_modifier()
        draw()
        

        pygame.display.update()

        level_last_frame = level.copy()
    else:
        print('[green]was experiencing some lag')