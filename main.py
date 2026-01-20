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

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    print(joystick.get_name())


def drawBackground(surface):
    surface.fill((255,255,0))
    surface.blit(bg, (0,0))

class foto:
    def __init__(self, lach, boos, surface, key):
        self.lach = lach
        self.boos = boos
        self.surfaec = surface
        self.blockx = (WIDTH/2)-(self.lach.get_width()/2)
        self.blocky = 100
        self.current = lach
        self.boosB = False
        self.key = key
        self.dir = "u"
    
    def setDir(self, event):
        if event.axis == 0:
            # Horizontaal
            if event.value > 0.1:
                self.dir = "r"
            if event.value < -0.1:
                self.dir = "l"
        if event.axis == 1:
            # Vertikaal
            if event.value > 0.1:
                self.dir = "d"
            if event.value < -0.1:
                self.dir = "u"


    def drawFace(self):
        figuur = self.current
        drawBackground(surface)
        if self.dir == "d":
            self.blocky+=10
        if self.dir == "u":
            self.blocky-=10
        if self.dir == "l":
            self.blockx-=10
            if self.blockx < (WIDTH/2)-(gezichtLach.get_width()/2) and self.boosB == True:
                figuur = self.lach
                self.boosB = False
        if self.dir == "r":
            self.blockx+=10
            if self.blockx > (WIDTH/2)-(gezichtLach.get_width()/2) and self.boosB == False:
                figuur = self.boos
                self.boosB = True

        self.current = figuur

        # self.blockx = min(WIDTH-figuur.get_width(), self.blockx)
        # self.blockx = max(0, self.blockx)
        self.blockx = pygame.math.clamp(self.blockx, 0, WIDTH-figuur.get_width())
        # self.blocky = min(HEIGHT-figuur.get_height(), self.blocky)
        # self.blocky = max(0, self.blocky)
        self.blocky = pygame.math.clamp(self.blocky, 0, HEIGHT-figuur.get_height())


        
        surface.blit(figuur, (self.blockx,self.blocky))

rick = foto(rickL, rickB, surface, pygame.K_r)
burn = foto(gezichtLach, gezichtBoos, surface, pygame.K_k)
gezichten = {rick, burn}

currentFoto = burn

clock = pygame.time.Clock()

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
        if event.type == pygame.JOYAXISMOTION:
            currentFoto.setDir(event)
    currentFoto.drawFace()
    pygame.display.update()
    clock.tick(60)


