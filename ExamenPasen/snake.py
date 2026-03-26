import pygame
import math
import random

GREEN = (0,255,0)
running = True
stop = True

pygame.init()
surface = pygame.display.set_mode() 
bg = pygame.image.load("ExamenPasen/images/background.jpg")
blockF = pygame.image.load("ExamenPasen/images/packman.png").convert()
ballonF = pygame.image.load("ExamenPasen/images/balloon.png").convert()
kittenF = pygame.image.load("ExamenPasen/images/kitten.png").convert()

ballon = pygame.mixer.Sound("ExamenPasen/sounds/balloon.mp3")
music = pygame.mixer.music.load("ExamenPasen/sounds/music.mp3")
pygame.mixer.music.play(-1)
kat = pygame.mixer.Sound("ExamenPasen/sounds/meow.mp3")
crash = pygame.mixer.Sound("ExamenPasen/sounds/crash.mp3")
HEIGHT = bg.get_height()
WIDTH = bg.get_width()
APPLES = 1
KATTEN = 1
oneTime = True
FPS = 3
ticks = 0
applesEaten = 0


pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    print(joystick.get_name())

def askDifficulty():
    global FPS, MINES, MUUR
    font = pygame.font.SysFont(None, 50)
    img = font.render(f'Kies moeilijkheid', True, (255,255,255))
    img1 = font.render(f'Makkelijk = 0.7s (1) / Middel = 0.5s (2) / Moeilijk = 0.3s (3)', True, (255,255,255))

    surface.blit(img, ((WIDTH)/2-img.get_width()/2, (HEIGHT)/2-200))
    surface.blit(img1, ((WIDTH)/2-img1.get_width()/2, (HEIGHT)/2-100))
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    FPS = 1
                if event.key == pygame.K_2:
                    FPS = 2
                if event.key == pygame.K_3:
                    FPS = 3
                if event.key == pygame.K_s:
                    return
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def GameOver():
    global running
    running = False
    font = pygame.font.SysFont(None, 100)
    surface.fill((255,0,0))
    img = font.render(f'Game is over! Your score is {applesEaten}', True, (255,255,255))
    img2 = font.render(f'You control your own wins and losses', True, (255,255,255))
    surface.blit(img, ((WIDTH-img.get_width())/2, (HEIGHT-img.get_height())/2-100))
    surface.blit(img2, ((WIDTH-img2.get_width())/2, (HEIGHT-img2.get_height())/2+100))

def drawBackground(surface):
    surface.fill((255,255,0))
    font = pygame.font.SysFont(None, 24)
    img = font.render(f'Snelheid: {FPS}', True, (255,255,255))
    img2 = font.render(f'Score: {applesEaten}', True, (255,255,255))

    surface.blit(bg, (0,0))
    surface.blit(img, (20, 20))
    surface.blit(img2, (20, 50))


askDifficulty()

class Part:
    def __init__(self, block, surface, pos):
        self.figuur = block
        self.surface = surface
        self.cur = self.figuur
        self.pos = pos
        self.dir = (0,1)
        self.speed = self.figuur.get_height()
        self.next: None | Part = None
        self.previous: None | Part = None
        self.prevPos = (pos[0], pos[1]+1)
        self.deathSave = False
    
    def setDir(self, event):
        if event.axis == 0:
            # Horizontaal
            if event.value > 0.1:
                self.dir = (1,0)
            if event.value < -0.1:
                self.dir = (-1,0)
        if event.axis == 1:
            # Vertikaal
            if event.value > 0.1:
                self.dir = (0,1)
            if event.value < -0.1:
                self.dir = (0,-1)
            
    def setDirKey(self, event):
        if event.key == pygame.K_RIGHT:
            self.dir = (1,0)
        if event.key == pygame.K_LEFT:
            self.dir = (-1,0)
        if event.key == pygame.K_UP:
            self.dir = (0,-1)
        if event.key == pygame.K_DOWN:
            self.dir = (0,1)
            

    def addPart(self):
        if self.next == None:
            self.next = Part(self.figuur, self.surface, self.prevPos)
            self.next.previous=self
        else:
            self.next.addPart()

    def checkHit(self, pos):
        if self.pos == pos:
            crash.play()
            GameOver()
            return True
        else:
            if not self.next == None:
                return self.next.checkHit(pos)
            else:
                return False
        
    def spotMag(self, pos):
        if self.pos == pos:
            return False
        if self.next == None:
            return True
        else:
            return self.next.spotMag(pos)

    def draw(self):
        self.surface.blit(self.cur,self.pos)
        if not self.next == None:
            self.next.draw()

    def move(self):
        global applesEaten, FPS
        self.prevPos = self.pos
        self.prevFig = self.cur
        if (self.previous == None):

            self.pos = (self.pos[0]+(self.dir[0]*self.speed), self.pos[1]+(self.dir[1]*self.speed))

            if not self.dir[0] == 0:
                if self.dir[0] == 1:
                    self.cur = pygame.transform.rotate(self.figuur, 0)
                if self.dir[0] == -1:
                    self.cur = pygame.transform.rotate(self.figuur, 180)
            if not self.dir[1] == 0:
                if self.dir[1] == 1:
                    self.cur = pygame.transform.rotate(self.figuur, -90)
                if self.dir[1] == -1:
                    self.cur = pygame.transform.rotate(self.figuur, 90)

            self.pos = (pygame.math.clamp(self.pos[0], 0, WIDTH-self.figuur.get_width()), pygame.math.clamp(self.pos[1], 0, HEIGHT-self.figuur.get_height()))

            if self.prevPos == self.pos:
                GameOver()
                return
            
            self.deathSave = False
            for a in appleList:
                if self.pos[0] + self.figuur.get_width() > a.pos[0] and self.pos[0] < a.pos[0] + a.figuur.get_width() and  self.pos[1] + self.figuur.get_height() > a.pos[1] and self.pos[1] < a.pos[1] + a.figuur.get_height():
                    applesEaten += 1
                    if not FPS == 1:
                        FPS -= 1
                    a.move()
                    self.addPart()
                    ballon.play()
            for a in Katten:
                if self.pos[0] + self.figuur.get_width() > a.pos[0] and self.pos[0] < a.pos[0] + a.figuur.get_width() and  self.pos[1] + self.figuur.get_height() > a.pos[1] and self.pos[1] < a.pos[1] + a.figuur.get_height():
                    FPS += 1
                    applesEaten += 2
                    a.move()
                    self.addPart()
                    self.addPart()
                    kat.play()
        else:
            self.pos = self.previous.prevPos
            self.cur = self.previous.prevFig

        if self.next == None:
            pass
        else:
            self.next.move()
        
        if not self.next == None:
            if self.next.checkHit(self.pos):
                return
        
        self.draw()            

class Ballon:
    def __init__(self, block, surface):
        self.figuur = block
        self.surface: pygame.SurfaceType = surface
        self.pos = (random.randrange(0,bg.get_width(), block.get_width()), random.randrange(0,bg.get_height(), block.get_height()))
        self.surface.blit(self.figuur, self.pos)

    def move(self):
        self.pos = (random.randrange(0,bg.get_width(), self.figuur.get_width()), random.randrange(0,bg.get_height(), self.figuur.get_height()))
        
        self.surface.blit(self.figuur, self.pos)

    def draw(self):
        self.surface.blit(self.figuur, self.pos)


class Kat:
    def __init__(self, block, surface):
        self.figuur = block
        self.surface: pygame.SurfaceType = surface
        self.pos = (random.randrange(0,bg.get_width(), block.get_width()), random.randrange(0,bg.get_height(), block.get_height()))
        self.move()

    def move(self):
        self.pos = (random.randrange(0,bg.get_width(), self.figuur.get_width()), random.randrange(0,bg.get_height(), self.figuur.get_height()))
        while not head.spotMag(self.pos):
            self.pos = (random.randrange(0,bg.get_width(), self.figuur.get_width()), random.randrange(0,bg.get_height(), self.figuur.get_height()))
        self.draw()

    def draw(self):
        surface.blit(self.figuur, self.pos)


head = Part(blockF, surface, (random.randrange(0,bg.get_width(), blockF.get_width()), random.randrange(0,bg.get_height(), blockF.get_height())))
head.addPart()
head.addPart()

appleList = list()

for i in range(APPLES):
    appleList.append(Ballon(ballonF, surface))

Katten = list()

for i in range(KATTEN):
    Katten.append(Kat(kittenF, surface))

clock = pygame.time.Clock()

while stop:
    while running:
        ticks+=1
        # Check for event if user has pushed
        # any event in queue
        for event in pygame.event.get():
        
        # if event is of type quit then set
        # running bool to false
            if event.type == pygame.QUIT:
                running = False
                stop=False

            if event.type == pygame.KEYDOWN:
                head.setDirKey(event)
                if (event.key == pygame.K_ESCAPE):
                    running = False
                    stop = False
            if event.type == pygame.JOYAXISMOTION:
                head.setDir(event)
        drawBackground(surface)
        for a in appleList:
            a.draw()
        for a in Katten:
            a.draw()
        head.move()
        pygame.display.update()
        clock.tick(FPS)

    for event in pygame.event.get():
        ticks = 0
        applesEaten = 0
        # if event is of type quit then set
        # running bool to false
        if event.type == pygame.QUIT:
            running = False
            stop=False
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_ESCAPE):
                running = False
                stop=False
            # if event.key == pygame.K_RETURN:
            #     running = True
            #     head = Part(block, surface, (random.randrange(0,bg.get_width(), block.get_width()), random.randrange(0,bg.get_height(), block.get_height())))
            #     head.addPart()
            #     head.addPart()

            #     for a in appleList:
            #         a.move()
            #     for a in Muren:
            #         a.move()
            #     for a in Mines:
            #         a.move()
        # if event.type == pygame.JOYBUTTONDOWN:
        #     running = True
        #     head = Part(block, surface, (random.randrange(0,bg.get_width(), block.get_width()), random.randrange(0,bg.get_height(), block.get_height())))
        #     head.addPart()
        #     head.addPart()

        #     for a in appleList:
        #         a.move()
        #     for a in Muren:
        #         a.move()
        #     for a in Mines:
        #         a.move()

                


