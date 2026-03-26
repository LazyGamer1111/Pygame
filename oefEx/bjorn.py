import pygame
import math
import random

GREEN = (0,255,0)
running = True
stop = True

pygame.init()
surface = pygame.display.set_mode((700,1000)) 
zwaardI = pygame.image.load("oefEx/images/sword.png").convert()
ballonI = pygame.image.load("oefEx/images/balloon.png").convert()
katI = pygame.image.load("oefEx/images/kitten.png").convert()

ping = pygame.mixer.Sound("oefEx/sounds/balloon.mp3")
hit = pygame.mixer.Sound("oefEx/sounds/meow.mp3")
HEIGHT = 1000
WIDTH = 700
APPLES = 10
FPS = 8
ticks = 0
score = 0


pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    print(joystick.get_name())

def askDifficulty():
    global FPS
    font = pygame.font.SysFont(None, 100)
    img = font.render(f'Choose difficulty', True, (255,255,255))
    img1 = font.render(f'Easy: 1', True, (255,255,255))
    img2 = font.render(f'Medium: 2', True, (255,255,255))
    img3 = font.render(f'Hard: 3', True, (255,255,255))

    surface.blit(img, ((WIDTH)/2-300, (HEIGHT)/2-200))
    surface.blit(img1, ((WIDTH)/2-300, (HEIGHT)/2-100))
    surface.blit(img2, ((WIDTH)/2-300, (HEIGHT)/2))
    surface.blit(img3, ((WIDTH)/2-300, (HEIGHT)/2+100))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP1:
                    FPS = 20
                if event.key == pygame.K_KP2:
                    FPS = 40
                if event.key == pygame.K_KP3:
                    FPS = 80
                if event.key == pygame.K_s:
                    return
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def GameOver():
    global running
    running = False
    surface.fill((255,0,0))
    font = pygame.font.SysFont(None, 100)
    img = font.render(f'GAME OVER', True, (255,255,255))
    img2 = font.render(f'Score: {score}', True, (255,255,255))
    surface.blit(img, ((WIDTH-img.get_width())/2, (HEIGHT-img.get_height())/2))
    surface.blit(img2, ((WIDTH-img2.get_width())/2, (HEIGHT-img2.get_height())/2+200))


def drawBackground(surface):
    surface.fill((0,255,0))
    font = pygame.font.SysFont(None, 24)
    img = font.render(f'Game Time: {math.floor(ticks/FPS)}', True, (255,255,255))
    img2 = font.render(f'Score: {score}', True, (255,255,255))

    surface.blit(img, (20, 20))
    surface.blit(img2, (20, 50))


askDifficulty()

class Part:
    def __init__(self, block, surface, pos):
        self.figuur = block
        self.surface = surface
        self.pos = pos
        self.dir = (0,1)
        self.speed = 10
    
    def setDir(self, event):
        if event.axis == 0:
            # Horizontaal
            if event.value > 0.1:
                self.dir = (1,0)
            if event.value < -0.1:
                self.dir = (-1,0)
            if event.value < 0.1 and event.value > -0.1:
                self.dir = (0,0)
    def setDirKey(self, event):
        if event.key == pygame.K_RIGHT:
            self.dir = (1,0)
        if event.key == pygame.K_LEFT:
            self.dir = (-1,0)
        if event.key == pygame.K_KP_PLUS:
            self.speed += 5
        if event.key == pygame.K_KP_MINUS:
            self.speed -= 5
        self.speed = pygame.math.clamp(self.speed, 5, 50)

    def setStop(self, event):
        if event.key == pygame.K_RIGHT:
            self.dir = (0,0)
        if event.key == pygame.K_LEFT:
            self.dir = (0,0)

    def draw(self):
        self.surface.blit(self.figuur,self.pos)

    def move(self):
        global score
        self.prevPos = self.pos

        self.pos = (self.pos[0]+(self.dir[0]*self.speed), self.pos[1])

        self.pos = (pygame.math.clamp(self.pos[0], 0, WIDTH-self.figuur.get_width()), self.pos[1])

        if self.pos[1] + self.figuur.get_height() > ballon.pos[1] and (self.pos[0] > ballon.pos[0] and self.pos[0] - self.figuur.get_width() < ballon.pos[0] + ballonI.get_width()) and ballon.hitB == False:
            score += 1
            ballon.hit()
            ping.play()
        if self.pos[1] + self.figuur.get_height() > kat.pos[1] and (self.pos[0] > kat.pos[0] and self.pos[0] - self.figuur.get_width() < kat.pos[0] + katI.get_width()):
            hit.play()
            GameOver()

        if running:
            self.draw()
            

class deel:
    def __init__(self, block, surface):
        self.figuur = block
        self.surface: pygame.SurfaceType = surface
        self.pos = (random.randrange(0,WIDTH-self.figuur.get_width()), HEIGHT)
        self.surface.blit(self.figuur, self.pos)
        self.hitB = False

    def hit(self):
        self.hitB = True

    def move(self):
        self.pos = (self.pos[0], self.pos[1] - 5)
        if self.pos[1] + self.figuur.get_height() < 0:
            self.reset()
        self.draw()

    def draw(self):
        self.surface.blit(self.figuur, self.pos)

    def reset(self):
        self.pos = (random.randrange(0,WIDTH-self.figuur.get_width()), HEIGHT)
        self.hitB = False


zwaard = Part(zwaardI, surface, (WIDTH/2,0))

ballon = deel(ballonI, surface)
kat = deel(katI, surface)


clock = pygame.time.Clock()

while stop:
    while running:
        ticks+=1
        # Check for event if user has pushed
        # any event in queue
        for event in pygame.event.get():
            print(event)
        # if event is of type quit then set
        # running bool to false
            if event.type == pygame.QUIT:
                running = False
                stop=False

            if event.type == pygame.KEYDOWN:
                zwaard.setDirKey(event)
                if (event.key == pygame.K_ESCAPE):
                    running = False
                    stop = False
            if event.type == pygame.JOYAXISMOTION:
                zwaard.setDir(event)
            if event.type == pygame.KEYUP:
                zwaard.setStop(event)
        drawBackground(surface)
        print(ballon.pos)
        ballon.move()
        kat.move()
        zwaard.move()
        pygame.display.update()
        clock.tick(FPS)

    for event in pygame.event.get():
        ticks = 0
        score = 0
        # if event is of type quit then set
        # running bool to false
        if event.type == pygame.QUIT:
            running = False
            stop=False
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE):
                running = False
                stop=False
            if event.key == pygame.K_RETURN:
                running = True
        if event.type == pygame.JOYBUTTONDOWN:
            ballon.reset()
            kat.reset()
            running = True

                


