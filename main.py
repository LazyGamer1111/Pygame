import pygame

HEIGHT = 600
WIDTH = 1400
GREEN = (0,255,0)
running = True
boos = False

pygame.init()
surface = pygame.display.set_mode((WIDTH,HEIGHT)) 
bg = pygame.image.load("images/SJG.png")
gezichtLach = pygame.image.load("images/lach.jpg").convert()
gezichtLach = pygame.transform.rotate(gezichtLach, -90)

gezichtBoos = pygame.image.load("images/boos.jpg").convert()
gezichtBoos = pygame.transform.rotate(gezichtBoos, -90)

lastFiguur = gezichtLach

def drawBackground(surface):
    surface.fill((255,255,0))
    surface.blit(bg, (0,0))
    pygame.display.flip()

def drawFace(surface, keydown):
    global x,y,gezichtLach, lastFiguur, boos
    figuur = lastFiguur
    drawBackground(surface)
    if keydown == pygame.K_DOWN:
        y+=10
        pygame.draw.circle(surface, GREEN, (x,y), 10)
    if keydown == pygame.K_UP:
        y-=10
    if keydown == pygame.K_LEFT:
        x-=10
        if x < (WIDTH/2)-(gezichtLach.get_width()/2) and boos == True:
            figuur = gezichtLach
            boos = False
        figuur = pygame.transform.rotate(figuur, 90)
    if keydown == pygame.K_RIGHT:
        x+=10
        if x > (WIDTH/2)-(gezichtLach.get_width()/2) and boos == False:
            figuur = gezichtBoos
            boos = True
        figuur = pygame.transform.rotate(figuur, -90)

    lastFiguur = figuur
    
    surface.blit(figuur, (x,y))
    pygame.display.flip()

x=(WIDTH/2)-(gezichtLach.get_width()/2)
y=HEIGHT/2

drawBackground(surface)
surface.blit(gezichtLach, (x, y))

pygame.display.flip()
while running:
    # Check for event if user has pushed
    # any event in queue
    for event in pygame.event.get():
    # if event is of type quit then set
    # running bool to false
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE):
                running = False
            drawFace(surface, event.key)


