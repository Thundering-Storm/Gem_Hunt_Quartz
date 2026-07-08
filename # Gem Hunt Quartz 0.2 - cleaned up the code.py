# Gem Hunt Quartz 0.2 - cleaned up the code
import pygame # pyright: ignore
from sys import exit
from rich import print # pyright: ignore
from random import randint

class Player():
    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: int = 75
        self.height: int = 150
        self.Y_vel: float = 0
        self.allowleverpull: bool = False
        self.debug: bool = False
        self.makeplatformdebug: bool = True

    def vertical(self) -> None:
        "Vertical Movement"
        # if you're going up
        if self.Y_vel <= 0:
            self.headhit()
            return None

        # bottom part of player
        downPlayer = pygame.Rect(self.x + 5, (self.y + self.height) + self.Y_vel * dt, self.width - 10, 5)
        touching_ground: bool = downPlayer.colliderect(ground) or any(downPlayer.colliderect(wall) for wall in currentLevelWalls)
 
        if touching_ground:
            while touching_ground:
                downPlayer.y -= 1
                touching_ground: bool = downPlayer.colliderect(ground) or any(downPlayer.colliderect(wall) for wall in currentLevelWalls)
            self.y = downPlayer.y - self.height + 5
            self.Y_vel = min(self.Y_vel, 0)
        
        else:
            self.Y_vel += 1500 * dt
            self.Y_vel = min(self.Y_vel, 2500)
            self.y += self.Y_vel * dt

        if self.debug:
            pygame.draw.rect(Window, (255, 255, 255), downPlayer)

    def horizontal(self, side: int) -> None:
        "Horizontal movement"
        SiPX = self.x + (300 * side) * dt # sideplayerx
        sidePlayer = pygame.Rect(SiPX + (70 / 2) + (int(side) * 70 / 2), self.y + 7.5, 5, 135)

        if not any(sidePlayer.colliderect(wall) for wall in currentLevelWalls):
            self.x = SiPX
        else:
            while any(sidePlayer.colliderect(wall) for wall in currentLevelWalls):
                SiPX -= 1 * side
                sidePlayer = pygame.Rect(SiPX + (70 / 2) + (int(side) * 70 / 2), self.y + 7.5, 5, 135)
            self.x = SiPX
        
        if self.debug:
            pygame.draw.rect(Window, (255, 255, 255), sidePlayer)

    def headhit(self) -> None:
            # top part of player
            upPlayer = pygame.Rect(self.x + 6, self.y - 1, 65, 5)

            if any(upPlayer.colliderect(wall) for wall in currentLevelWalls):
                self.Y_vel = 0
                # go down until not touching wall anymore
                while any(upPlayer.colliderect(wall) for wall in currentLevelWalls):
                    upPlayer = pygame.Rect(self.x + 6, self.y, 65, 5)
                    self.y += 1
            
            self.Y_vel += 1500 * dt
            self.Y_vel = min(self.Y_vel, 2500)
            self.y += self.Y_vel * dt
                        
            if self.debug:
                pygame.draw.rect(Window, (84, 213, 3), upPlayer)
    
    def checkpressed(self) -> None:
        "Checks wasd to move the player"
        keyPressed = pygame.key.get_pressed()
        if keyPressed[pygame.K_a]:
            self.horizontal(side = -1)
        if keyPressed[pygame.K_d]:
            self.horizontal(side = 1)
        if keyPressed[pygame.K_w] and self.allowjump():
            self.Y_vel = -jumpheight
        if keyPressed[pygame.K_p]: # dev thing
            print(pygame.mouse.get_pos())
        if keyPressed[pygame.K_SPACE] and self.makeplatformdebug:
            currentLevelWalls.append(pygame.Rect(self.x - 100, self.y + self.width * 2, 200, 50))
            print(currentLevelWalls)
            self.makeplatformdebug = False
        elif not True in keyPressed:
            self.makeplatformdebug = True

    def MovementLoop(self) -> None:
        "The movement loop for the player"
        self.vertical()
        self.checkpressed()

    def allowjump(self) -> bool:
        "Returns if you are touching the ground or the bottom of any walls"
        downPlayer = pygame.Rect(self.x + 6, self.y + 146, 65, 5)
        return (downPlayer.colliderect(ground) or any(downPlayer.colliderect(wall) for wall in currentLevelWalls))

    def collidelever(self, lever: pygame.Rect, changedIndex: int) -> None:
        "Checks if you are fliping a lever and changes a list if so"
        if pygame.Rect(self.x, self.y, self.width, self.height).colliderect(lever): # if you as rect are touching the lever 
            keyPressed = pygame.key.get_pressed()
            if keyPressed[pygame.K_s]:
                if self.allowleverpull:
                    self.allowleverpull = False
                    leverFliped[changedIndex] = not(leverFliped[changedIndex])
                    print(f'flipped: {changedIndex}')
            else:
                self.allowleverpull = True

def levelEnds() -> None:
    "Changes levels if you are at the end of the screen"
    global level

    for player in players:
        # left
        if player.x < 0:
            level -= 10
            player.x = windowSize[0] - 76

        # right
        if player.x > windowSize[0] - 75:
            level += 10
            player.x = 1

        # up
        if player.y < 0:
            if level + 1 != 34:
                level += 1
                player.y = windowSize[1] - 151

        # down
        if player.y > windowSize[1] - 150:
            level -= 1
            player.y = 1

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

def draw() -> None:
    pygame.draw.rect(Window, (255, 0, 0), lever)
    pygame.draw.rect(Window, (255, 0, 0), lever2)
    pygame.draw.rect(Window, (255, 0, 0), lever3)
    
    for wall in currentLevelWalls:
        pygame.draw.rect(Window, (75, 75, 75), wall)
    
    pygame.draw.rect(Window, (63, 171, 42), ground)
    
    for player in players:
        pygame.draw.rect(Window, (125, 0, 0), (player.x, player.y, player.width, player.height))
        pygame.draw.rect(Window, (255, 0, 0), (player.x, player.y, player.width, player.height), 5)

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
players = [
    Player(467, 400)
    # Player(500, 500)
]
level = 33
currentLevelWalls = []
leverFliped = [False] * 20
FPS = 120
jumpheight = 800
windowSize = (1920, 1019)
lever_x = 1700
lever2_x = -100
final_score = 0

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
            player.MovementLoop()

        levelEnds()
        levelDatabase()
        draw()

        pygame.display.update()
    else:
        print('[green]was experiencing some lag')