import pygame, random
HEIGHT = 400
WIDTH = 1200
GREEN = (0,255,0)
running = True

pygame.init()
surface = pygame.display.set_mode((WIDTH,HEIGHT)) 
bg = pygame.image.load("images/wolken.jpg")
F22 = pygame.image.load("images/f22gif2.gif").convert()
F35 = pygame.image.load("images/f35gif2.gif").convert()
F35 = pygame.transform.rotate(F35, -90)
putin = pygame.image.load("images/putingif.gif").convert()

score = 0

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    print(joystick.get_name())


def drawBackground(surface):
    surface.fill((255,255,0))
    surface.blit(bg, (0,0))

def drawScore(surface):
    font = pygame.font.SysFont(None, 24)
    img2 = font.render(f'Score: {score}', True, (255,255,255))
    surface.blit(img2, (20, 20))


class putinFoto:
    def __init__(self, block, surface):
        self.figuur = block
        self.surface: pygame.SurfaceType = surface
        self.pos = (1000, random.randrange(0,300))
        self.surface.blit(self.figuur, self.pos)

    def move(self):
        self.pos = (1000, random.randrange(0,300))
        self.surface.blit(self.figuur, self.pos)

    def draw(self):
        self.surface.blit(self.figuur, self.pos)

class foto:
    def __init__(self, f, surface):
        self.current = f
        self.surfaec = surface
        self.F35bool = True
        self.blocky = 100
        self.dir = ""
    
    def setDir(self, event):
        if event.axis == 0:
            # Horizontaal
            if event.value > 0.1:
                self.dir = "r"
            elif event.value < -0.1:
                self.dir = "l"
            else: self.dir = ""
        if event.axis == 1:
            # Vertikaal
            if event.value > 0.1:
                self.dir = "d"
            elif event.value < -0.1:
                self.dir = "u"
            else: self.dir = ""


    def drawFace(self):
        figuur = self.current
        drawBackground(surface)
        if self.dir == "d":
            self.blocky+=10
        if self.dir == "u":
            self.blocky-=10
        
        surface.blit(figuur, (40,self.blocky))

    def shoot(self):
        global score
        height = self.blocky+self.current.get_height()/2
        if putinF.pos[1]+20 <= height and putinF.pos[1]+80 >= height:
            score+=1
            putinF.move()

F22F = foto(F22, surface)
F35F = foto(F35, surface)
putinF = putinFoto(putin, surface)
curFoto = F22F

clock = pygame.time.Clock()

drawBackground(surface)

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
            if (event.key == pygame.K_a):
                curFoto = F22F
            if (event.key == pygame.K_b):
                curFoto = F35F
        if event.type == pygame.JOYAXISMOTION:
            curFoto.setDir(event)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == pygame.CONTROLLER_BUTTON_B:
                curFoto.shoot()
    curFoto.drawFace()
    putinF.draw()
    drawScore(surface)
    pygame.display.update()
    clock.tick(60)