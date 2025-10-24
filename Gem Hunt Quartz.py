# game test 3 - levels
import pygame
import math

def ResetVariables():
    global WindowIsOpen, playerX, playerY, jumpForce, DEBUGDRAW, justJumped, Level, touchedEdge, currentLevelWalls
    WindowIsOpen = True
    playerX = displayWidth // 2.5
    playerY = displayHeight // 3
    jumpForce = 0
    DEBUGDRAW = 0
    justJumped = False
    Level = 31
    touchedEdge = False
    currentLevelWalls = []
    
def Falling(Mode): # gravity and fix downwards movement
    global playerY, jumpForce, downPlayer, PSBe, PSBeY, playerBOX, justJumped
    downPlayer = pygame.Rect(playerX + 6, playerY + 146, 65, 5)
    PSBeY = playerY + 6
    PSBe = pygame.Rect(playerX + 6, PSBeY, 65, 145)
    if Mode == 1:
        return downPlayer.colliderect(ground), any(downPlayer.colliderect(wall) for wall in currentLevelWalls)
    
    if Mode == 0:
        if downPlayer.colliderect(ground) or any(downPlayer.colliderect(wall) for wall in currentLevelWalls):
            if not justJumped:
                while PSBe.colliderect(ground) or any(PSBe.colliderect(wall) for wall in currentLevelWalls):
                    PSBeY -= 1
                    PSBe = pygame.Rect(playerX + 6, PSBeY, 65, 150)
                playerY = PSBeY
                if jumpForce > 0:
                    jumpForce = 0
        else:
            jumpForce += 2000 * Time
            if jumpForce > 500:
                jumpForce = 500
            justJumped = False
    
    playerY += math.ceil(jumpForce * Time)

    if DEBUGDRAW == 1:
        pygame.draw.rect(Window, (255, 0, 0), PSBe)
        pygame.draw.rect(Window, (255, 125, 0), downPlayer)

def TouchingWalls(Side): # when moving left or right fix movement
    global leftPlayer, rightPlayer, playerX
    LPX = playerX - 300 * Time
    RPX = playerX + 300 * Time
    leftPlayer = pygame.Rect(LPX - 1, playerY + 3, 5, 140)
    rightPlayer = pygame.Rect(RPX + 70, playerY + 3, 5, 140)
    if Side == -1:
        if not any(leftPlayer.colliderect(wall) for wall in currentLevelWalls):
            playerX += math.floor(-300 * Time)
        else:
            while any(leftPlayer.colliderect(wall) for wall in currentLevelWalls):
                LPX += 1
                leftPlayer = pygame.Rect(LPX + 3, playerY + 5, 75, 140)
            playerX = LPX - 1

    if Side == 1:
        if not any(rightPlayer.colliderect(wall) for wall in currentLevelWalls):
            playerX += math.ceil(300 * Time)
        else:
            while any(rightPlayer.colliderect(wall) for wall in currentLevelWalls):
                RPX -= 1
                rightPlayer = pygame.Rect(RPX + 3, playerY + 5, 70, 140)
            playerX = RPX + 1

    if DEBUGDRAW == 1:
        pygame.draw.rect(Window, (142, 57, 16), leftPlayer)
        pygame.draw.rect(Window, (61, 75, 241), rightPlayer)

def HeadHit(): # if the player hits their head on a wall
    global upPlayer, jumpForce
    upPlayer = pygame.Rect(playerX + 6, playerY - 1, 65, 5)
    if any(upPlayer.colliderect(wall) for wall in currentLevelWalls):
        jumpForce = 0

    if DEBUGDRAW == 1:
        pygame.draw.rect(Window, (84, 213, 3), upPlayer)

def LevelEnds(Mode):
    global playerBOX, touchedEdge, Level, playerX, playerY
    levelEdge_left = pygame.Rect(0, 0, 1, displayHeight)
    levelEdge_right = pygame.Rect(displayWidth, 0, 1, displayHeight)
    levelEdge_up = pygame.Rect(0, 0, displayWidth, 1)
    levelEdge_down = pygame.Rect(0, displayHeight, displayWidth, 1)
    
    if Mode == 0:
        if not touchedEdge:
            if playerBOX.colliderect(levelEdge_left):
                Level -= 10
                touchedEdge = True
                playerX = displayWidth - 1
            if playerBOX.colliderect(levelEdge_right):
                Level += 10
                touchedEdge = True
                playerX = 0
            if playerBOX.colliderect(levelEdge_up):
                Level += 1
                touchedEdge = True
                playerY = displayHeight - 1
            if playerBOX.colliderect(levelEdge_down):
                Level -= 1
                touchedEdge = True
                playerY = 0
        if not any(LevelEnds(1)):
            touchedEdge = False
    
    if Mode == 1:
        return playerBOX.colliderect(levelEdge_left), playerBOX.colliderect(levelEdge_right), playerBOX.colliderect(levelEdge_up), playerBOX.colliderect(levelEdge_down)
    
    if DEBUGDRAW == 1:
        pygame.draw.rect(Window, (255, 0, 0), levelEdge_left)
        pygame.draw.rect(Window, (255, 0, 0), levelEdge_right)
        pygame.draw.rect(Window, (255, 0, 0), levelEdge_up)
        pygame.draw.rect(Window, (255, 0, 0), levelEdge_down)

def LevelDatabase():
    global Level, currentLevelWalls

    currentLevelWalls = []
    
    if Level == 21: # x1 y1
        currentLevelWalls = [
            pygame.Rect(432, 645, 150, 150),
            pygame.Rect(176, 533, 150, 50),
            pygame.Rect(432, 389, 150, 50),
            pygame.Rect(865, 432, 150, 50)
        ]
    


def PlayerMovement():
    global jumpForce, justJumped
    keyPressed = pygame.key.get_pressed()
    if keyPressed[pygame.K_a]:
        TouchingWalls(-1)
    if keyPressed[pygame.K_d]:
        TouchingWalls(1)
    if keyPressed[pygame.K_w] and any(Falling(1)):
        jumpForce = -800
        justJumped = True


pygame.init()

info = pygame.display.Info()
clock = pygame.time.Clock()
displayHeight = info.current_h - 50
displayWidth = info.current_w

Window = pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption("game test 3 - levels")

ResetVariables()

while WindowIsOpen:
    Time = clock.tick(120) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            WindowIsOpen = False

    Window.fill((13, 32, 132))
    
    playerBOX = pygame.Rect(playerX, playerY, 75, 150)
    ground = pygame.Rect(0, displayHeight / 1.35, displayWidth, displayHeight)

    # Movement
    Falling(0)
    HeadHit()
    PlayerMovement()

    # Levels
    LevelEnds(0)
    LevelDatabase()
    
    for wall in currentLevelWalls:
        pygame.draw.rect(Window, (75, 75, 75), wall)
    pygame.draw.rect(Window, (63, 171, 42), ground)
    pygame.draw.rect(Window, (45, 0, 0), playerBOX)
    
    pygame.display.flip()

pygame.quit()