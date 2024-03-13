# Example file showing a circle moving on screen
import pygame

running = True
chances = 3
r = 'd'

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

gagne = False

dt = 0
espace = False

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
balle_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

player_pos.y = 680
balle_pos.y = 660
player_pos.x = (1280/2) - 30
balle_pos.x = 1280/2

while running :
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("green")
    a = pygame.Rect(640-60, 360-30, 120, 60)
    b = pygame.Rect(player_pos.x,player_pos.y,60,30)
    pygame.draw.circle(screen, "red", balle_pos, 20)
    pygame.draw.rect(screen,"white",a)
    pygame.draw.rect(screen,"blue",b)

    #print(pygame.mouse.get_pos(), player_pos)

    keys = pygame.key.get_pressed()

    #envoi de la balle et déplacement :
    if keys[pygame.K_SPACE]:
        espace = True
    if espace :
        balle_pos.y -= 3

    if player_pos.x <= 0 and not(espace):
        r = 'g'
    elif player_pos.x + 60 >= 1280 and not(espace):
        r = 'd'

    if r == 'g' and not(espace):
        player_pos.x += 5
        balle_pos.x += 5

    elif r == 'd' and not(espace) :
        player_pos.x -= 5
        balle_pos.x -= 5


    if 640-60 <= balle_pos.x-20 and balle_pos.x + 20 <= 640+60 and balle_pos.y + 20 <= 370:
        gagne = True
        running = False

    if balle_pos.y < 350 :
        if chances == 1 :
            chances = 0
            running = False
        else :
            chances -= 1
            player_pos.y = 680
            balle_pos.y = 660
            player_pos.x = (1280/2) - 30
            balle_pos.x = 1280/2
            espace = False



    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

while running == False and gagne == True :
    break

while running == False and gagne == False and chances <= 0 :
    break
