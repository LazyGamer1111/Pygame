import pygame
import math
import random

GREEN = (0,255,0)
running = True
stop = True

pygame.init()
surface = pygame.display.set_mode() 
bg = pygame.image.load("snakeTest/images/background.jpg")
block = pygame.image.load("snakeTest/images/block.jpg").convert()
apple = pygame.image.load("snakeTest/images/apple.jpg").convert()
mine = pygame.image.load("snakeTest/images/mine.png").convert()

ping = pygame.mixer.Sound("snakeTest/sounds/pickupCoin.wav")
music = pygame.mixer.music.load("snakeTest/sounds/music.mp3")
pygame.mixer.music.play(-1)
hit = pygame.mixer.Sound("snakeTest/sounds/hitHurt.wav") 
HEIGHT = bg.get_height()
WIDTH = bg.get_width()
APPLES = 1
MINES = 5
MUUR = 1
oneTime = True
FPS = 8
ticks = 0
applesEaten = 0


pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    print(joystick.get_name())

def askDifficulty():
    global FPS, MINES, MUUR
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
                if event.key == pygame.K_1:
                    MINES = 5
                    MUUR = 1
                    FPS = 5
                    return
                if event.key == pygame.K_2:
                    MINES = 10
                    MUUR = 2
                    FPS = 5
                    return
                if event.key == pygame.K_3:
                    MINES = 15
                    MUUR = 3
                    FPS = 20
                    return
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

def GameOver():
    global running
    running = False
    font = pygame.font.SysFont(None, 100)
    img = font.render(f'GAME OVER', True, (255,255,255))
    surface.blit(img, ((WIDTH)/2, (HEIGHT)/2))

def drawBackground(surface):
    surface.fill((255,255,0))
    font = pygame.font.SysFont(None, 24)
    img = font.render(f'Game Time: {math.floor(ticks/FPS)}', True, (255,255,255))
    img2 = font.render(f'Apples eaten: {applesEaten}', True, (255,255,255))

    surface.blit(bg, (0,0))
    surface.blit(img, (20, 20))
    surface.blit(img2, (20, 50))


askDifficulty()

class Part:
    def __init__(self, block, surface, pos):
        self.figuur = block
        self.surface = surface
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

    def addPart(self):
        if self.next == None:
            self.next = Part(self.figuur, self.surface, self.prevPos)
            self.next.previous=self
        else:
            self.next.addPart()

    def checkHit(self, pos):
        if self.pos == pos:
            hit.play()
            GameOver()
        else:
            if not self.next == None:
                self.next.checkHit(pos)
        
    def spotMag(self, pos):
        if self.pos == pos:
            return False
        if self.next == None:
            return True
        else:
            return self.next.spotMag(pos)

    def draw(self):
        self.surface.blit(self.figuur,self.pos)
        if not self.next == None:
                    self.next.draw()

    def move(self):
        global applesEaten
        self.prevPos = self.pos
        if (self.previous == None):

            self.pos = (self.pos[0]+(self.dir[0]*self.speed), self.pos[1]+(self.dir[1]*self.speed))

            self.pos = (pygame.math.clamp(self.pos[0], 0, WIDTH-block.get_width()), pygame.math.clamp(self.pos[1], 0, HEIGHT-block.get_height()))

            if self.prevPos == self.pos and not self.deathSave:
                self.deathSave = True
                self.draw()
                return
            if self.prevPos == self.pos and self.deathSave:
                GameOver()
                return
            self.deathSave = False
            for a in appleList:
                if self.pos == a.pos:
                    applesEaten += 1
                    a.move()
                    self.addPart()
                    ping.play()
            for a in Mines:
                if self.pos == a.pos:
                    GameOver()
                    return
            for a in Muren:
#                if a.pos == self.pos or (a.pos[0] == self.pos[0] and ((a.pos[1] == self.pos[1]+40) or (a.pos[1] == self.pos[1]+80))):
                if a.figuur.collidepoint(self.pos[0], self.pos[1]):
                    GameOver()
                    return
        else:
            self.pos = self.previous.prevPos

        if self.next == None:
            pass
        else:
            self.next.move()
        
        if not self.next == None:
                self.next.checkHit(self.pos)
        
        self.draw()
            

class Apple:
    def __init__(self, block, surface):
        self.figuur = block
        self.surface: pygame.SurfaceType = surface
        self.pos = (random.randrange(0,bg.get_width(), block.get_width()), random.randrange(0,bg.get_height(), block.get_height()))
        self.surface.blit(self.figuur, self.pos)

    def move(self):
        self.pos = (random.randrange(0,bg.get_width(), block.get_width()), random.randrange(0,bg.get_height(), block.get_height()))
        
        self.surface.blit(self.figuur, self.pos)

    def draw(self):
        self.surface.blit(self.figuur, self.pos)


class Mine:
    def __init__(self, block, surface):
        self.figuur = block
        self.surface: pygame.SurfaceType = surface
        self.pos = (random.randrange(0,bg.get_width(), block.width), random.randrange(0,bg.get_height(), block.height))
        self.move()

    def move(self):
        self.pos = (random.randrange(0,bg.get_width(), self.figuur.width), random.randrange(0,bg.get_height(), self.figuur.height))
        self.draw

    def draw(self):
        self.figuur.update(self.pos[0], self.pos[1], 40, 40)
        pygame.draw.rect(surface, (255,0,0), self.figuur)

class Muur:
    def __init__(self, block, surface):
        self.figuur = block
        self.surface: pygame.SurfaceType = surface
        self.pos = (random.randrange(0,bg.get_width(), block.width), random.randrange(0,bg.get_height(), block.height))
        self.move()

    def move(self):
        self.pos = (random.randrange(0,bg.get_width(), self.figuur.width), random.randrange(0,bg.get_height(), self.figuur.height))
        while not head.spotMag(self.pos):
            self.pos = (random.randrange(0,bg.get_width(), self.figuur.width), random.randrange(0,bg.get_height(), self.figuur.height))
        self.draw()

    def draw(self):
        self.figuur.update(self.pos[0], self.pos[1], 40, 120)
        pygame.draw.rect(surface, (255,0,0), self.figuur)

head = Part(block, surface, (random.randrange(0,bg.get_width(), block.get_width()), random.randrange(0,bg.get_height(), block.get_height())))
head.addPart()
head.addPart()

appleList = list()

for i in range(APPLES):
    appleList.append(Apple(apple, surface))

Mines = list()
Muren = list()

for i in range(MINES):
    Mines.append(Mine(pygame.Rect(0, 0, 40, 40), surface))

for i in range(MUUR):
    Muren.append(Muur(pygame.Rect(0, 0, 40, 120), surface))

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
                if (event.key == pygame.K_ESCAPE):
                    running = False
                    stop = False
            if event.type == pygame.JOYAXISMOTION:
                head.setDir(event)
        drawBackground(surface)
        for a in appleList:
            a.draw()
        for a in Muren:
            a.draw()
        for a in Mines:
            a.draw()
        if applesEaten%5 == 0:
            if oneTime:
                oneTime = False
                for a in Muren:
                    a.move()
                for a in Mines:
                    a.move()
        else:
            oneTime = True
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
            if event.key == pygame.K_RETURN:
                running = True
                head = Part(block, surface, (random.randrange(0,bg.get_width(), block.get_width()), random.randrange(0,bg.get_height(), block.get_height())))
                head.addPart()
                head.addPart()

                for a in appleList:
                    a.move()
                for a in Muren:
                    a.move()
                for a in Mines:
                    a.move()
        if event.type == pygame.JOYBUTTONDOWN:
            running = True
            head = Part(block, surface, (random.randrange(0,bg.get_width(), block.get_width()), random.randrange(0,bg.get_height(), block.get_height())))
            head.addPart()
            head.addPart()

            for a in appleList:
                a.move()
            for a in Muren:
                a.move()
            for a in Mines:
                a.move()

                


