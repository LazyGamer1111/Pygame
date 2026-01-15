import pygame

HEIGHT = 600
WIDTH = 1400
GREEN = (0,255,0)
running = True

pygame.init()
surface = pygame.display.set_mode((WIDTH,HEIGHT)) 
bg = pygame.image.load("images/SJG.png")
gezichtLach = pygame.image.load("images/lach.jpg").convert()
gezichtLach = pygame.transform.rotate(gezichtLach, -90)

gezichtBoos = pygame.image.load("images/boos.jpg").convert()
gezichtBoos = pygame.transform.rotate(gezichtBoos, -90)

rickL = pygame.image.load("images/rickL.png").convert()
rickL = pygame.transform.rotate(rickL, -90)

rickB = pygame.image.load("images/rickB.png").convert()
rickB = pygame.transform.rotate(rickB, -90)


def drawBackground(surface):
    surface.fill((255,255,0))
    surface.blit(bg, (0,0))
    pygame.display.flip()

class foto:
    def __init__(self, lach, boos, surface, key):
        self.lach = lach
        self.boos = boos
        self.surfaec = surface
        self.blockx = 100
        self.blocky = 100
        self.current = lach
        self.boos = False
        self.key = key
    def drawFace(self, keydown):
        figuur = self.current
        drawBackground(surface)
        if keydown == pygame.K_DOWN:
            self.blocky+=10
            pygame.draw.circle(surface, GREEN, (self.blockx,self.blocky), 10)
        if keydown == pygame.K_UP:
            self.blocky-=10
        if keydown == pygame.K_LEFT:
            self.blockx-=10
            if self.blockx < (WIDTH/2)-(gezichtLach.get_width()/2) and self.boos == True:
                figuur = self.lach
                self.boos = False
            figuur = pygame.transform.rotate(figuur, 90)
        if keydown == pygame.K_RIGHT:
            self.blockx+=10
            if self.blockx > (WIDTH/2)-(gezichtLach.get_width()/2) and self.boos == False:
                figuur = self.boos
                self.boos = True
            figuur = pygame.transform.rotate(figuur, -90)

        self.current = figuur
        
        surface.blit(figuur, (self.blockx,self.blocky))
        pygame.display.flip()

rick = foto(rickL, rickB, surface, pygame.K_r)
burn = foto(gezichtLach, gezichtBoos, surface, pygame.K_k)
gezichten = {rick, burn}

currentFoto = burn

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
            for gezicht in gezichten:
                if event.key == gezicht.key:
                    currentFoto = gezicht
            currentFoto.drawFace(event.key)


