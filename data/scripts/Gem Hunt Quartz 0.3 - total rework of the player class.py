# Gem Hunt Quartz 0.3 - total rework of the player class
from __future__ import annotations
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
        self.allowleverpull: bool
        self.jumpheight: float
        self.detection_size: int

        # variables
        self.position = self.Position(x, y)
        self.size = self.Size(75, 150)
        self.velocity = self.Velocity(0, 0)
        self.speed = self.Speed(3.3, 1, 0.95)
        self.detection = self.Detection(10, 6)
        self.allowleverpull = False
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
        will_touch_ground = any(future_player.colliderect(wall) for wall in currentLevelWalls)

        pygame.draw.rect(Window, (255, 255, 255), future_player)

        if will_touch_ground:
            for wall in currentLevelWalls:
                if future_player.colliderect(wall):
                    self.position.y = wall.top - self.size.height
                    self.velocity.y = 0
        else:
            self.velocity.y += 15 * dt
            min(self.velocity.y, 25)
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
        will_touch_walls = any(future_player.colliderect(wall) for wall in currentLevelWalls)

        pygame.draw.rect(Window, (255, 255, 255), future_player)

        if will_touch_walls:
            for wall in currentLevelWalls:
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
        

        will_bonk = any(future_player.colliderect(wall) for wall in currentLevelWalls)

        if will_bonk:
            for wall in currentLevelWalls:
                if future_player.colliderect(wall):
                    self.position.y = wall.bottom
                    self.velocity.y = 0

        pygame.draw.rect(Window, (255, 255, 255), future_player)

    def allow_jump(self) -> bool:
        "Returns if you are touching the ground or the bottom of any walls"
        future_player = pygame.Rect(self.position.x + 3, (self.position.y + self.velocity.y), self.size.width - 6, 150)
        will_touch_ground = any(future_player.colliderect(wall) for wall in currentLevelWalls)

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

    def collidelever(self, lever: pygame.Rect, changedIndex: int) -> None:
        "Checks if you are fliping a lever and changes a list if so"
        if pygame.Rect(self.position.x, self.position.y, self.size.width, self.size.height).colliderect(lever): # if you as rect are touching the lever 
            keyPressed = pygame.key.get_pressed()
            if keyPressed[pygame.K_s]:
                if self.allowleverpull:
                    self.allowleverpull = False
                    leverFliped[changedIndex] = not(leverFliped[changedIndex])
                    print(f'flipped: {changedIndex}')
            else:
                self.allowleverpull = True

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
            level -= 10
            player.position.x = windowSize[0] - 76

        # right
        if player.position.x > windowSize[0] - 75:
            level += 10
            player.position.x = 1

        # up
        if player.position.y < 0:
            if level + 1 != 34:
                level += 1
                player.position.y = windowSize[1] - 151

        # down
        if player.position.y > windowSize[1] - 150:
            level -= 1
            player.position.y = 1

def levelDatabase() -> None:
    "Changes the level data depending on the level you are on"
    # define the variables for the function 
    global currentLevelWalls, lever, lever2, lever3
    currentLevelWalls = []
    lever = pygame.Rect(0,0,0,0)
    lever2 = pygame.Rect(0,0,0,0)
    lever3 = pygame.Rect(0,0,0,0)

    # gives an error if you're on a level that isnt in the level system  
    levelList: list[int] = [11, 12, 13, 21, 22, 23, 31, 32, 33, 41, 42, 43, 51, 52, 53]
    if not(level in levelList): 
        raise ValueError('Illigal level')

    # creates the ground if the second number of the level is 1 (y = 1)
    global ground
    if str(level)[1] == "1":
        ground = pygame.Rect(0, 850, windowSize[0], windowSize[1])
    else:
        ground = pygame.Rect(0, 0, 0, 0)

    

    # level system
    global leverFliped

    if level == 11:
        lever = pygame.Rect(575, 434 - 50, 100, 50)
        
        currentLevelWalls = [
            pygame.Rect(windowSize[0] - 150, 389, 150, 50),
            pygame.Rect(1400, 412, 150, 50),
            pygame.Rect(1125, 365, 150, 50),
            pygame.Rect(400, 432, 500, 100),
            pygame.Rect(0, 0, 25, windowSize[1])
        ]

        for player in players:
            player.collidelever(lever = lever, changedIndex = 0)

    if level == 12:
        lever = pygame.Rect(175 / 2, 275, 100, 50)
        lever2 = pygame.Rect(1620 + 200 / 2, 825, 100, 50)

        currentLevelWalls = [
            pygame.Rect(0, 0, 25, 1019),
            pygame.Rect(0, 0, 1254, 25),
            pygame.Rect(1454, 0, 1920 - 1454, 25),
            pygame.Rect(1620, 400, 300, 200),
            pygame.Rect(1895, 400, 25, 500),
            pygame.Rect(1620, 875, 300, 25),
            pygame.Rect(1254, 261, 200, 50),
            pygame.Rect(900, 448, 200, 50),
            pygame.Rect(402, 406, 200, 50),
            pygame.Rect(0, 325, 250, 50),
            pygame.Rect(402 + 150, 406, 50, 720 - 406 + 50),
            pygame.Rect(597, 577, 50, 25),
            pygame.Rect(600, 720, 200, 50),
            pygame.Rect(850, 830, 200, 50),
            pygame.Rect(1205, 858, 200, 50),
        ]

        if not leverFliped[13]:
            currentLevelWalls.append(pygame.Rect(windowSize[0] - 300, 400, 25, 500))

        for player in players:
            player.collidelever(lever = lever, changedIndex = 12)
            player.collidelever(lever = lever2, changedIndex = 14)

    if level == 13:
        lever = pygame.Rect(225, 950, 100, 50)

        currentLevelWalls = [
            pygame.Rect(0, 0, 25, windowSize[1]),
            pygame.Rect(0, 0, windowSize[0], 25),
            pygame.Rect(0, windowSize[1] - 25, 1254, 25),
            pygame.Rect(1454, windowSize[1] - 25, 1920 - 1454, 25),
            pygame.Rect(windowSize[0] - 25, 350, 25, 425),
            pygame.Rect(0, 0, windowSize[0], 25),
            pygame.Rect(0, 200, 25, windowSize[1]),
            pygame.Rect(25, windowSize[1] - 125, 25, 25),
            pygame.Rect(200, windowSize[1] - 250, windowSize[0], 25),
            pygame.Rect(windowSize[0] - 50, windowSize[1] - 350, 25, 25),
            pygame.Rect(0, windowSize[1] - 475, windowSize[0] - 200, 25),
            pygame.Rect(25, windowSize[1] - 575, 25, 25),
            pygame.Rect(200, windowSize[1] - 675, windowSize[0] - 200, 25),
            pygame.Rect(0, 0, windowSize[0] - 500, windowSize[1] - 875),
        ]

        if not leverFliped[14]:
            currentLevelWalls.append(pygame.Rect(1720, 770, 50, 225))
        
        if not leverFliped[15]:
            currentLevelWalls.append(pygame.Rect(500, 770, 50, 225))

        for player in players:
            player.collidelever(lever = lever, changedIndex = 15)

    if level == 21:
        currentLevelWalls = [
            pygame.Rect(430, 690, 150, 250),
            pygame.Rect(170, 533, 150, 50),
            pygame.Rect(0, 389, 150, 50),
            pygame.Rect(340, 300, 150, 50),
            pygame.Rect(760, 432, 150, 50),
            pygame.Rect(1100, 352, 150, 50),
            pygame.Rect(1500, 500, 150, 50),
            pygame.Rect(1600, 500, 325, 400),
            pygame.Rect(1600, 0, 325, 250)
        ]

        if not leverFliped[0]:
            currentLevelWalls.append(pygame.Rect(1800, 250, 50, 250))

    if level == 22:
        lever = pygame.Rect(1309, 205, 100, 50)

        currentLevelWalls = [
            pygame.Rect(0, 0, windowSize[0], 25),
            pygame.Rect(1600, windowSize[1] - 25, windowSize[0] - 1600, 25),
            pygame.Rect(1700, 700, 1600, 50),
            pygame.Rect(1256, 677, 200, 50),
            pygame.Rect(751, 801, 200, 50),
            pygame.Rect(342, 672, 200, 50),
            pygame.Rect(0, 400, 200, 200),
            pygame.Rect(0, 400, 25, 500),
            pygame.Rect(200, 482, 50, 25),
            pygame.Rect(400, 261, 200, 50),
            pygame.Rect(777, 385, 200, 50),
            pygame.Rect(1158, 252, 400, 50),
            pygame.Rect(1508, 0, 50, 252)
        ]

        if not leverFliped[12]:
            currentLevelWalls.append(pygame.Rect(1158, 0, 50, 252))

        for player in players:
            player.collidelever(lever = lever, changedIndex = 13)

    if level == 23:
        currentLevelWalls = [
            pygame.Rect(0, 0, windowSize[0], 25),
            pygame.Rect(0, windowSize[1] - 25, windowSize[0], 25),
            pygame.Rect(windowSize[0] - 25, 0, 25, windowSize[1]),
            pygame.Rect(0, 350, 100, 425),
            pygame.Rect(1795, 871, 100, 50),
            pygame.Rect(1537, 738, 100, 50),
            pygame.Rect(1234, 598, 100, 50),
            pygame.Rect(895, 475, 100, 50),
            pygame.Rect(557, 370, 100, 50),
            pygame.Rect(281, 297, 100, 50)
        ]


    if level == 31:
        currentLevelWalls = [
            pygame.Rect(0, 500, 325, 400),
            pygame.Rect(0, 0, 325, 250),
            pygame.Rect(320, 575, 100, 275),
            pygame.Rect(420, 650, 100, 200),
            pygame.Rect(520, 725, 100, 125),
            pygame.Rect(620, 800, 100, 50),
            pygame.Rect(600, 450, 150, 50),
            pygame.Rect(850, 350, 150, 50),
            pygame.Rect(1100, 210, 150, 50),
            pygame.Rect(1400, 160, 130, 50),
            pygame.Rect(windowSize[0] - 25, 0, 25, windowSize[1])
        ]

    if level == 32:
        lever = pygame.Rect(325 - 150, windowSize[1] - 75, 100, 50)

        currentLevelWalls = [
            pygame.Rect(1600, 950, 150, 50),
            pygame.Rect(1700, 800, 200, 50),
            pygame.Rect(0, 700, 1600, 50),
            pygame.Rect(windowSize[0] - 25, windowSize[1] - 25, 25, 25),
            pygame.Rect(550, 0, 50, 540),
            pygame.Rect(900, 0, 50, 540),
            pygame.Rect(850, 520, 50, 20),
            pygame.Rect(600, 520 - 180, 50, 20),
            pygame.Rect(850, 520 - 360, 50, 20),
            pygame.Rect(0, 0, 550, 25),
            pygame.Rect(950, 0, windowSize[0] - 950, 25),
            pygame.Rect(0, windowSize[1] - 25, 325, 25)
        ]
        
        if not leverFliped[1]:
            currentLevelWalls.append(pygame.Rect(600, 520, 300, 20))

        if not leverFliped[2]:
            currentLevelWalls.append(pygame.Rect(600, 520 - 180, 300, 20))

        if not leverFliped[3]:
            currentLevelWalls.append(pygame.Rect(600, 520 - 360, 300, 20))
            
        if not leverFliped[15]:
            currentLevelWalls.append(pygame.Rect(100, windowSize[1] - 300, 50, 300))

        for player in players:
            player.collidelever(lever = lever, changedIndex = 2)

    if level == 33:
        global lever_x, lever2_x, final_score
        lever = pygame.Rect(lever_x, windowSize[1] - 75, 100, 50)
        lever2 = pygame.Rect(lever2_x, windowSize[1] - 75, 100, 50)

        currentLevelWalls = [
            pygame.Rect(0, windowSize[1] - 25, 600, 25),
            pygame.Rect(900, windowSize[1] - 25, windowSize[0] - 900, 25),
            pygame.Rect(0, 0, 25, windowSize[1]),
            pygame.Rect(windowSize[0] - 25, 0, 25, windowSize[1]),
        ]

        if leverFliped[16]:
            currentLevelWalls.append(pygame.Rect(0, windowSize[1] - 25, windowSize[0], 25))

            if leverFliped[16] != leverFliped[17]:
                lever_x = -100
                leverFliped[18] = not leverFliped[18]
                leverFliped[17] = True

        if leverFliped[18] != leverFliped[19]:
            lever2_x = randint(200, 1700)
            final_score += 1
            
        leverFliped[19] = leverFliped[18] # 19 = 18 last frame
        leverFliped[17] = leverFliped[16] # 17 = 16 last frame

        for player in players:
            player.collidelever(lever = lever, changedIndex = 16)
            player.collidelever(lever = lever2, changedIndex = 18)

        if final_score > 2 and final_score < 5:
            text("gg!", windowSize[0] // 2, windowSize[1] // 2)

    if level == 41:
        lever = pygame.Rect(60, 850 - 50, 100, 50)
        lever2 = pygame.Rect(750, windowSize[1] - 650, 100, 50)
        lever3 = pygame.Rect(1300, windowSize[1] - 850, 100, 50)

        currentLevelWalls = [
            pygame.Rect(0, 0, windowSize[0], 25),
            pygame.Rect(0, 0, 25, windowSize[1]),
            pygame.Rect(windowSize[0] - 75, 200, 75, windowSize[1] - 569),
            pygame.Rect(200, 850 - 150, 50, 150),
            pygame.Rect(700, windowSize[1] - 600, 200, 50),
            pygame.Rect(1250, windowSize[1] - 800, 200, 50)
        ]

        if not leverFliped[8]:
            currentLevelWalls.append(pygame.Rect(windowSize[0] - 75, 25, 50, 200))
            currentLevelWalls.append(pygame.Rect(400, windowSize[1] - 500, 150, 50))

        if not leverFliped[9]:
            currentLevelWalls.append(pygame.Rect(windowSize[0] - 75, 850 - 200, 50, 200))

        if leverFliped[11]:
            currentLevelWalls.append(pygame.Rect(1050, windowSize[1] - 700, 150, 50))

        for player in players:
            player.collidelever(lever = lever, changedIndex = 9)
            player.collidelever(lever = lever2, changedIndex = 10)
            player.collidelever(lever = lever3, changedIndex = 3)

    if level == 42:
        currentLevelWalls = [
            pygame.Rect(0, windowSize[1] - 25, windowSize[0], 25),
            pygame.Rect(0, 0, windowSize[0], 25),
            pygame.Rect(100, 700, 150, 300),
            pygame.Rect(500, 750, 150, 50),
            pygame.Rect(900, 650, 150, 50),
            pygame.Rect(1188, 475, 150, 50),
            pygame.Rect(1335, 750, 250, 50),
            pygame.Rect(1335, 650, 100, 100),
            pygame.Rect(1500, 300, 420, 50),
            pygame.Rect(1775, 700, 150, 50),
            pygame.Rect(250, windowSize[1] - 100, 100, 100)
        ]
        if not leverFliped[4]:
            currentLevelWalls.append(pygame.Rect(1500, 0, 50, 300))

    if level == 43:
        lever = pygame.Rect(50, 150, 100, 50)

        currentLevelWalls = [
            pygame.Rect(0, windowSize[1] - 25, windowSize[0], 25),
            pygame.Rect(0, 0, windowSize[0], 25),
            pygame.Rect(0, 0, 25, windowSize[1]),
            pygame.Rect(windowSize[0] - 25, 200, 25, windowSize[1] - 200),
            pygame.Rect(windowSize[0] - 175, 200, 150, 50),
            pygame.Rect(windowSize[0] - 175 * 2, 350, 150, 50),
            pygame.Rect(windowSize[0] - 175 * 3, 525, 150, 50),
            pygame.Rect(windowSize[0] - 175 * 4, 700, 150, 50),
            pygame.Rect(windowSize[0] - 175 * 5, 875, 150, 50),
            pygame.Rect(25, 200, 150, 50),
            pygame.Rect(175, 350, 150, 50),
            pygame.Rect(175 * 2, 525, 150, 50),
            pygame.Rect(175 * 3, 700, 150, 50),
            pygame.Rect(175 * 4, 875, 150, 50)
        ]

        for player in players:
            player.collidelever(lever = lever, changedIndex = 7)


    if level == 51:
        lever = pygame.Rect(1600, 800, 100, 50)
        lever2 = pygame.Rect(1400, 620, 100, 50)
        
        currentLevelWalls = [
            pygame.Rect(windowSize[0] - 25, 0, 25, windowSize[1]),
            pygame.Rect(0, 0, windowSize[0] - 420, 25),
            pygame.Rect(0, 200, 25, windowSize[1] - 569),
            pygame.Rect(windowSize[0] - 525, 200, 500, 287),
            pygame.Rect(windowSize[0] - 825, 300, 300, 187),
            pygame.Rect(25, 200, 500, 449),
            pygame.Rect(525, 300, 300, 349),
            pygame.Rect(825, 624, 75, 25),
            pygame.Rect(windowSize[0] - 900, 462, 75, 25),
            pygame.Rect(825, 300, 75, 25),
            pygame.Rect(windowSize[0] - 900, 775, 100, 75),
            pygame.Rect(1300, 487, 50, 190),
            pygame.Rect(1300, 657, 450, 25),
        ]

        if not leverFliped[8]:
            currentLevelWalls.append(pygame.Rect(200, 25, 50, 200))

        if not leverFliped[9]:
            currentLevelWalls.append(pygame.Rect(200, 850 - 201, 50, 200))

        if not leverFliped[10]:
            currentLevelWalls.append(pygame.Rect(1600, 850 - 390, 50, 200))
        
        for player in players:
            player.collidelever(lever = lever, changedIndex = 8)
            player.collidelever(lever = lever2, changedIndex = 11)

    if level == 52:
        lever = pygame.Rect(1000, 700, 100, 50)
        lever2 = pygame.Rect(1350, 450, 100, 50)
        lever3 = pygame.Rect(225, 200, 100, 50)
        
        currentLevelWalls = [
            pygame.Rect(0, windowSize[1] - 25, windowSize[0] - 450, 25),
            pygame.Rect(windowSize[0] - 25, 0, 25, windowSize[1]),
            pygame.Rect(0, 0, windowSize[0] - 200, 25),
            pygame.Rect(0, 700, 150, 50),
            pygame.Rect(400, 625, 150, 50),
            pygame.Rect(600, 475, 150, 50),
            pygame.Rect(900, 250, 600, 50),
            pygame.Rect(900, 750, 600, 50),
            pygame.Rect(900, 500, 200, 50),
            pygame.Rect(1300, 500, 200, 50),
            pygame.Rect(900, 550, 50, 200),
            pygame.Rect(1450, 300, 50, 200),
            pygame.Rect(windowSize[0] - 100, 925, 75, 25),
            pygame.Rect(1500, 775, 75, 25),
            pygame.Rect(windowSize[0] - 100, 625, 75, 25),
            pygame.Rect(1250, 500, 50, 25),
            pygame.Rect(1500, 475, 75, 25),
            pygame.Rect(windowSize[0] - 100, 325, 75, 25),
            pygame.Rect(1500, 325, 25, 25),
            pygame.Rect(1450, 750, 50, windowSize[1] - 750),
            pygame.Rect(windowSize[0] - 50, 150, 25, 25),
            pygame.Rect(0, 300, 100, 50),
            pygame.Rect(200, 250, 200, 50),
            pygame.Rect(350, 0, 50, 250)
        ]
        
        if not leverFliped[5]:
            currentLevelWalls.append(pygame.Rect(1300, 300, 50, 200))
        if not leverFliped[6]:
            currentLevelWalls.append(pygame.Rect(0, windowSize[1] - 25, windowSize[0], 25))

        for player in players:
            player.collidelever(lever = lever, changedIndex = 4)
            player.collidelever(lever = lever3, changedIndex = 5)
            player.collidelever(lever = lever2, changedIndex = 6)

    if level == 53:
        lever = pygame.Rect(1600, 300, 100, 50)
        
        currentLevelWalls = [
            pygame.Rect(windowSize[0] - 25, 0, 25, windowSize[1]),
            pygame.Rect(0, 0, windowSize[0], 25),
            pygame.Rect(0, windowSize[1] - 25, windowSize[0] - 200, 25),
            pygame.Rect(0, 200, 25, windowSize[1]),
            pygame.Rect(25, windowSize[1] - 125, 25, 25),
            pygame.Rect(200, windowSize[1] - 250, windowSize[0], 25),
            pygame.Rect(windowSize[0] - 50, windowSize[1] - 350, 25, 25),
            pygame.Rect(0, windowSize[1] - 475, windowSize[0] - 200, 25),
            pygame.Rect(25, windowSize[1] - 575, 25, 25),
            pygame.Rect(200, windowSize[1] - 675, windowSize[0] - 200, 25),
            pygame.Rect(25, 200, 25, 25)
        ]

        if not leverFliped[7]:
            currentLevelWalls.append(pygame.Rect(400, 25, 50, 325))

        for player in players:
            player.collidelever(lever = lever, changedIndex = 1)

    currentLevelWalls.append(ground)

def draw() -> None:
    pygame.draw.rect(Window, (255, 0, 0), lever)
    pygame.draw.rect(Window, (255, 0, 0), lever2)
    pygame.draw.rect(Window, (255, 0, 0), lever3)
    
    for wall in currentLevelWalls:
        pygame.draw.rect(Window, (75, 75, 75), wall)
    
    pygame.draw.rect(Window, (63, 171, 42), ground)
    
    for player in players:
        player.draw()

def text(string: str, x: float, y: float, color: tuple[int, int, int] = (255, 255, 255)) -> None:
    "Draws text on the screen"

    font = pygame.font.SysFont(None, 60)
    text = font.render(string, False, color)
    Window.blit(text, (x, y))

# set the type definitions for the variables
players: list[Player]
level: int
currentLevelWalls: list[pygame.Rect]
leverFliped: list[bool]
FPS: int
windowSize: tuple[int, int]

# variables

level = 21
currentLevelWalls = []
leverFliped = [False] * 20
FPS = 120
windowSize = (1920, 1019)
lever_x = 1700
lever2_x = -100
final_score = 0
players = [
    Player(windowSize[0] // 2.5, windowSize[1] // 2)
    # Player(500, 500)
]

# pygame things
pygame.init()
Window = pygame.display.set_mode(windowSize)
pygame.display.set_caption("Gem Hunt Quartz 0.2")
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
        levelDatabase()
        draw()

        pygame.display.update()
    else:
        print('[green]was experiencing some lag')