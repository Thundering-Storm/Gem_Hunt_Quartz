# game test
import pygame
import math

def ResetVariables():
    global WindowIsOpen, playerX, playerY, pressedToGoUp, jumpForce, bottomOfGround, wPressed, DEBUGMODE, wLocked, justJumped, wPressedLastFrame
    WindowIsOpen = True
    playerX = displayWidth // 2.5
    playerY = displayHeight // 3
    pressedToGoUp = 0
    bottomOfGround = False
    wPressed = 0
    jumpForce = 0
    DEBUGMODE = 0
    wLocked = 0
    justJumped = False
    wPressedLastFrame = False
    
def TouchingGround(Mode):
    global playerY, bottomOfGround, jumpForce, belowPlayer, PSBe, PSBeY, playerBOX, justJumped
    belowPlayer = pygame.Rect(playerX, playerY + 1, 75, 150)
    PSBeY = playerY
    PSBe = pygame.Rect(playerX, PSBeY, 75, 150)
    if Mode == 1:
        return belowPlayer.colliderect(ground)
    
    if Mode == 0:
        if belowPlayer.colliderect(ground):
            if not justJumped:
                while PSBe.colliderect(ground):
                    PSBeY -= 1
                    PSBe = pygame.Rect(playerX, PSBeY, 75, 150)
                playerY = PSBeY
                if jumpForce > 0:
                    jumpForce = 0
        else:
            jumpForce += 2000 * Time
            if jumpForce > 500:
                jumpForce = 500
            justJumped = False
    playerY += jumpForce * Time


pygame.init()

info = pygame.display.Info()
clock = pygame.time.Clock()
displayHeight = info.current_h - 50
displayWidth = info.current_w

Window = pygame.display.set_mode((displayWidth, displayHeight))
pygame.display.set_caption("game test")

ResetVariables()

while WindowIsOpen:
    Time = clock.tick(120) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            WindowIsOpen = False


    Window.fill((13, 32, 132))

    playerBOX = pygame.Rect(playerX, playerY, 75, 150)
    ground = pygame.Rect(0, displayHeight / 1.35, displayWidth, displayHeight)

    keyPressed = pygame.key.get_pressed()
    if keyPressed[pygame.K_a]:
        playerX -= math.floor(300 * Time)
    if keyPressed[pygame.K_d]:
        playerX += math.floor(300 * Time)
    if keyPressed[pygame.K_w] and TouchingGround(1):
        jumpForce = -800
        justJumped = True

    TouchingGround(0)

    pygame.draw.rect(Window, (63, 171, 42), ground)
    if DEBUGMODE == 1:
        pygame.draw.rect(Window, (255,0,0), PSBe)
    pygame.draw.rect(Window, (45, 0, 0), playerBOX)
    
    pygame.display.flip()

pygame.quit()