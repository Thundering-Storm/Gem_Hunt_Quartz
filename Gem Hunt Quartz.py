# game test 2 - walls
import pygame
import math

def ResetVariables():
    global WindowIsOpen, playerX, playerY, pressedToGoUp, jumpForce, bottomOfGround, wPressed, DEBUGDRAW, wLocked, justJumped
    WindowIsOpen = True
    playerX = displayWidth // 2.5
    playerY = displayHeight // 3
    pressedToGoUp = 0
    bottomOfGround = False
    wPressed = 0
    jumpForce = 0
    DEBUGDRAW = 0
    wLocked = 0
    justJumped = False
    
def Falling(Mode):
    global playerY, jumpForce, downPlayer, PSBe, PSBeY, playerBOX, justJumped
    downPlayer = pygame.Rect(playerX + 6, playerY + 145, 65, 5)
    PSBeY = playerY + 6
    PSBe = pygame.Rect(playerX + 6, PSBeY, 65, 145)
    if Mode == 1:
        return downPlayer.colliderect(ground), downPlayer.colliderect(wall)
    
    if Mode == 0:
        if downPlayer.colliderect(ground) or downPlayer.colliderect(wall):
            if not justJumped:
                while PSBe.colliderect(ground) or PSBe.colliderect(wall):
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

def TouchingWalls(Side):
    global leftPlayer, rightPlayer, playerX
    LPX = playerX - 300 * Time
    RPX = playerX + 300 * Time
    leftPlayer = pygame.Rect(LPX - 1, playerY + 3, 5, 140)
    rightPlayer = pygame.Rect(RPX + 70, playerY + 3, 5, 140)
    if Side == -1:
        if not leftPlayer.colliderect(wall):
            playerX += math.floor(-300 * Time)
        else:
            while leftPlayer.colliderect(wall):
                LPX += 1
                leftPlayer = pygame.Rect(LPX + 3, playerY + 5, 75, 150)
            playerX = LPX - 1

    if Side == 1:
        if not rightPlayer.colliderect(wall):
            playerX += math.ceil(300 * Time)
        else:
            while rightPlayer.colliderect(wall):
                RPX -= 1
                rightPlayer = pygame.Rect(RPX + 3, playerY + 5, 70, 145)
            playerX = RPX + 1

    if DEBUGDRAW == 1:
        pygame.draw.rect(Window, (142, 57, 16), leftPlayer)
        pygame.draw.rect(Window, (61, 75, 241), rightPlayer)

def HeadHit():
    global upPlayer, jumpForce
    upPlayer = pygame.Rect(playerX + 10, playerY - 4, 65, 5)
    if upPlayer.colliderect(wall):
        jumpForce = 0

    if DEBUGDRAW == 1:
        pygame.draw.rect(Window, (84, 213, 3), upPlayer)

def PlayerMovement():
    global jumpForce, justJumped
    keyPressed = pygame.key.get_pressed()
    if keyPressed[pygame.K_a]:
        TouchingWalls(-1)
    if keyPressed[pygame.K_d]:
        TouchingWalls(1)
    if keyPressed[pygame.K_w] and any(Falling(1)):
        jumpForce = -600
        justJumped = True

def Movement():
    # down
    Falling(0)
    # up
    HeadHit()
    # player
    PlayerMovement()

pygame.init()

info = pygame.display.Info()
clock = pygame.time.Clock()
displayHeight = info.current_h - 50
displayWidth = info.current_w

Window = pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption("game test 2 - walls")

ResetVariables()

while WindowIsOpen:
    Time = clock.tick(120) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            WindowIsOpen = False

    Window.fill((13, 32, 132))

    playerBOX = pygame.Rect(playerX, playerY, 75, 150)
    ground = pygame.Rect(0, displayHeight / 1.35, displayWidth, displayHeight)
    wall = pygame.Rect(452, 425, 150, 150)

    Movement()

    pygame.draw.rect(Window, (63, 171, 42), ground)
    pygame.draw.rect(Window, (75, 75, 75), wall)
    pygame.draw.rect(Window, (45, 0, 0), playerBOX)
    
    pygame.display.flip()

pygame.quit()