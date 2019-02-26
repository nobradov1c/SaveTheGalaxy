import random
import os.path
import pygame
import sys
from pygame.locals import *

WIDTH = 800
HEIGHT = 640
FPS = 60
POWERUP_TIME = 4000
RELOAD = 300
NUMSTARS = 30
TYPING_SPEED = 300
PLAYER_MAX_HEALTH = 100

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 211, 0)
LIGHT_GREEN = (185, 235, 98)

FONT = 'MyFont.ttf'

pygame.mixer.pre_init(44100, -16, 1, 512)  # Decreasing the size of the buffer will reduce the latency
pygame.mixer.init()  # handles sound
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Save The Galaxy')
clock = pygame.time.Clock()


if hasattr(sys, '_MEIPASS'):
    main_dir = sys._MEIPASS
else: main_dir = os.path.split(os.path.abspath(__file__))[0] + '\\data'
textfile_dir = os.path.split(os.path.abspath(__file__))[0]

FONT = main_dir + '\\' + FONT


def loadImage(file):
    file = os.path.join(main_dir, file)
    img = pygame.image.load(file)
    return img.convert_alpha()


iconImg = pygame.transform.scale(loadImage('icon.png'), (30, 30))
pygame.display.set_icon(iconImg)
loadingScreenImg = pygame.transform.scale(loadImage('loadingscreen.png'), (WIDTH, HEIGHT))
loadingScreenImgRect = loadingScreenImg.get_rect()
screen.blit(loadingScreenImg, loadingScreenImgRect)
pygame.display.update()


def loadSound(file):
    file = os.path.join(main_dir, file)
    sound = pygame.mixer.Sound(file)
    return sound


def printText(surface, text, size, x, y, color, center = 0):
    font = pygame.font.Font(FONT, size)
    font.set_bold(True)
    textSurface = font.render(text, True, color)
    text_rect = textSurface.get_rect()
    if center == 0:
        text_rect.bottomleft = (x, y)
    else:
        text_rect.center = center
    surface.blit(textSurface, text_rect)


def slowType(s, y):
    global TYPING_SPEED
    typeFPS = 60
    k = len(s)
    i = 0
    x = 30
    lastLetter = pygame.time.get_ticks()
    while i < k:
        clock.tick(typeFPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_KP_ENTER or event.key == K_ESCAPE:
                    typeFPS = 0

        if (pygame.time.get_ticks() - lastLetter) > (random.random()*TYPING_SPEED):
            printText(screen, s[i], 16, x, y, YELLOW)
            keyPress_sound.play()
            pygame.display.update()
            x += 16
            i += 1
            lastLetter = pygame.time.get_ticks()


def showStory():
    screen.blit(storyImg, storyImgRect)
    pygame.display.update()
    story_music.play(-1)
    slowType('GREETINGS BRAVE WARRIOR,', 20)
    slowType('YOUR GALAXY IS IN GREAT DANGER', 40)
    slowType('OF RUTHLESS ALIEN INVASION', 60)
    slowType('YOU HAVE BEEN CHOSEN', 80)
    slowType('TO FACE AGAINST THIS TYRANNY', 100)
    slowType('YOU GOT MOST ADVANCED SPACE SHIP', 120)
    slowType('YOU HAVE ASSIGNMENT TO DESTROY ENEMY ARMY', 140)
    slowType('AND DEFEAT CAPTAIN, GENERAL AND LEADER.', 160)
    slowType('IF YOU ACCOMPLISH THIS MISSION SUCCESSFULLY,', 180)
    slowType('WHOLE GALAXY WILL BE ETERNALLY GRATEFUL AND', 200)
    slowType('MAY THE FORCE ALWAYS BE ON YOUR SIDE', 220)
    slowType('PRESS ANY KEY TO CONTINUE...', 260)
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                story_music.stop()
                showGameStartScreen()


def drawHealthBar(surface, x, y, health, healthColor, maxhealth, barLength):
    if health < 0:
        health = 0
    barHeight = 25
    fill = (health / maxhealth) * barLength
    outlineRect = pygame.Rect(x, y, barLength, barHeight)
    fillRect = pygame.Rect(x, y, fill, barHeight)
    pygame.draw.rect(surface, healthColor, fillRect)
    pygame.draw.rect(surface, WHITE, outlineRect, 2)


def drawLives(surface, x, y, lives, img):
    for i in range(lives):
        imgRect = img.get_rect()
        imgRect.x = x + 35*i
        imgRect.y = y
        surface.blit(img, imgRect)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = playerImg
        self.rect = self.image.get_rect()
        self.radius = 22
        self.rect.bottom = HEIGHT - 30
        self.rect.centerx = WIDTH / 2
        self.speedx = 5
        self.speedy = 3
        self.lives = 3
        self.health = PLAYER_MAX_HEALTH
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.immune = False
        self.immune_timer = pygame.time.get_ticks()
        self.powerLvl = 1
        self.power_timer = pygame.time.get_ticks()
        self.shoot_timer = pygame.time.get_ticks()
        self.score = 0

    def update(self):
        if self.immune:
            self.image = playerImg_immune
        else:
            self.image = playerImg
        if player.lives < 1:
            pygame.mixer.music.stop()
            boss_fight_music.stop()
            pygame.mixer.music.play(-1)
            showGameOverScreen()
        if self.powerLvl > 1:
            if pygame.time.get_ticks() - self.power_timer > POWERUP_TIME:
                self.powerLvl = 1
                self.power_timer = pygame.time.get_ticks()

        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1200:
            self.hidden = False
            self.rect.bottom = HEIGHT - 30
            self.rect.centerx = WIDTH / 2
            self.immune = True
            self.immune_timer = pygame.time.get_ticks()

        if self.immune and pygame.time.get_ticks() - self.immune_timer > 1500:
            self.immune = False

        keystate = pygame.key.get_pressed()
        if keystate[K_LEFT]:
            self.rect.x -= self.speedx
        if keystate[K_RIGHT]:
            self.rect.x += self.speedx
        if keystate[K_UP]:
            self.rect.y -= self.speedy
        if keystate[K_DOWN]:
            self.rect.y += self.speedy

        if self.rect.right > WIDTH + 20:
            self.rect.right = WIDTH + 20
        if self.rect.left < -20 and self.rect.left > -200:
            self.rect.left = -20
        if self.rect.top <= 0 and self.rect.top > -200:
            self.rect.top = 0
        if self.rect.bottom >= HEIGHT - 30:
            self.rect.bottom = HEIGHT - 30


    def shoot(self):
        if not self.hidden:
            self.shoot_timer = pygame.time.get_ticks()
            if self.powerLvl == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                allSprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.powerLvl == 2:
                bullet1 = Bullet(self.rect.left+5, self.rect.centery)
                bullet2 = Bullet(self.rect.right-5, self.rect.centery)
                allSprites.add(bullet1, bullet2)
                bullets.add(bullet1, bullet2)
                shoot_sound.play()
            else:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                bullet1 = Bullet(self.rect.left + 5, self.rect.centery)
                bullet2 = Bullet(self.rect.right - 5, self.rect.centery)
                allSprites.add(bullet, bullet1, bullet2)
                bullets.add(bullet, bullet1, bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (-500, -500)

    def powerup(self):
        self.powerLvl += 1
        self.power_timer = pygame.time.get_ticks()

    def reset(self):
        self.rect.bottom = HEIGHT - 30
        self.rect.centerx = WIDTH / 2
        self.lives = 3
        self.health = PLAYER_MAX_HEALTH
        self.hidden = False
        self.powerLvl = 1
        self.score = 0


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, img1, img2, smartShoot, fly):
        pygame.sprite.Sprite.__init__(self)
        self.img1 = img1
        self.img2 = img2
        self.image = self.img1
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.x = x
        self.rect.y = y
        self.speedy = 0
        self.speedx = random.randrange(1, 3)
        self.direction = 1
        self.lastUpdate = pygame.time.get_ticks()
        self.lastBomb = pygame.time.get_ticks()
        self.smartShoot = smartShoot
        self.canFly = fly
        self.fly = False
        self.fly_timer = pygame.time.get_ticks()
        self.starty = self.rect.y
        self.hitbottom = False
        self.flyTime = random.randrange(5000, 30000)

    def move(self, direction, y = 0):
        if self.rect.y < self.starty:
            self.rect.y = self.starty
            self.fly = False
        if y == 0:
            self.rect.x += self.speedx * self.direction
        else:
            self.rect.y += 4 * direction
            if self.rect.bottom > player.rect.bottom:
                self.rect.bottom = player.rect.bottom
                self.hitbottom = True
            if self.rect.y == self.starty:
                self.fly = False

        alliens.remove(self)
        hits = pygame.sprite.spritecollide(self, alliens, False)
        if hits:
            self.direction *= -1
        alliens.add(self)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.lastUpdate > 80:
            self.lastUpdate = now
            if self.image == self.img1:
                self.image = self.img2
            else:
                self.image = self.img1
            x = self.rect.x
            y = self.rect.y
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
        if self.canFly:
            if now - self.fly_timer > self.flyTime:
                self.fly_timer = now
                self.fly = True

        if self.fly == False:
            self.hitbottom = False
            if self.rect.left <=0:
                self.rect.left = 0
                self.direction *= -1
            if self.rect.right >= WIDTH:
                self.rect.right = WIDTH
                self.direction *= -1
            self.move(self.direction)

            if now - self.lastBomb > random.randrange(800, 1000000):
                self.lastBomb = now
                if self.smartShoot:
                    if self.rect.x < player.rect.x:
                        bomba = Bomb(self.rect.centerx, self.rect.bottom, 1)
                    else:
                        bomba = Bomb(self.rect.centerx, self.rect.bottom, -1)
                else:
                    bomba = Bomb(self.rect.centerx, self.rect.bottom, random.randrange(4))
                allSprites.add(bomba)
                bombs.add(bomba)

        elif self.fly == True:
            if self.hitbottom:
                self.move(-1, 5)
            else:
                self.move(1, 5)


class Boss(pygame.sprite.Sprite):
    def __init__(self, bosstype):
        pygame.sprite.Sprite.__init__(self)
        self.image = bossImg[bosstype-1]
        self.rect = self.image.get_rect()
        self.rect.centerx = screen.get_rect().centerx
        self.rect.y = 5
        self.speedy = random.randrange(5*bosstype, 10*bosstype)
        self.speedx = random.randrange(5*bosstype, 10*bosstype)
        self.directionx = random.choice([-1, 1])
        self.directiony = random.choice([-1, 1])
        self.lastUpdate = pygame.time.get_ticks()
        self.lastDirection = pygame.time.get_ticks()
        self.lastBomb = pygame.time.get_ticks()
        self.bosstype = bosstype
        self.health = 1000 * bosstype

    def move(self):
        if self.rect.y < 5:
            self.rect.y = 5
        if self.rect.bottom > HEIGHT - 200:
            self.rect.bottom = HEIGHT - 200
        if self.rect.x >= 5 and self.rect.y <= HEIGHT - 200:
            self.rect.y += self.speedy * self.directiony

        if self.rect.x < 5:
            self.rect.x = 5
        if self.rect.right > WIDTH - 5:
            self.rect.right = WIDTH - 5
        if self.rect.x >= 5 and self.rect.x <= WIDTH - 5:
            self.rect.x += self.speedx * self.directionx

    def update(self):

        now = pygame.time.get_ticks()
        if now - self.lastDirection > random.randrange(1300,10000):
            self.lastDirection = now
            self.directionx = random.choice([-1, 1])
            self.directiony = random.choice([-1, 1])
        if now - self.lastUpdate > random.randrange(80, 200):
            self.lastUpdate = now
            self.move()

        if now - self.lastBomb > random.randrange(100, round(100000/self.bosstype)):
            self.lastBomb = now
            if self.bosstype > 1:
                if self.rect.x < player.rect.x:
                    bomba1 = Bomb(self.rect.centerx, self.rect.bottom, 1)
                    bomba2 = Bomb(self.rect.centerx - 20, self.rect.bottom, 1)
                    bomba3 = Bomb(self.rect.centerx + 20, self.rect.bottom, 1)
                    if self.bosstype == 3:
                        bomba4 = Bomb(self.rect.centerx - 40, self.rect.bottom, 1)
                        bomba5 = Bomb(self.rect.centerx + 40, self.rect.bottom, 1)
                        allSprites.add(bomba4)
                        bombs.add(bomba4)
                        allSprites.add(bomba5)
                        bombs.add(bomba5)
                else:
                    bomba1 = Bomb(self.rect.centerx, self.rect.bottom, -1)
                    bomba2 = Bomb(self.rect.centerx - 20, self.rect.bottom, -1)
                    bomba3 = Bomb(self.rect.centerx + 20, self.rect.bottom, -1)
                    if self.bosstype == 3:
                        bomba4 = Bomb(self.rect.centerx - 40, self.rect.bottom, -1)
                        bomba5 = Bomb(self.rect.centerx + 40, self.rect.bottom, -1)
                        allSprites.add(bomba4)
                        bombs.add(bomba4)
                        allSprites.add(bomba5)
                        bombs.add(bomba5)
            else:
                bomba1 = Bomb(self.rect.centerx, self.rect.bottom)
                bomba2 = Bomb(self.rect.centerx - 20, self.rect.bottom)
                bomba3 = Bomb(self.rect.centerx + 20, self.rect.bottom)

            allSprites.add(bomba1)
            bombs.add(bomba1)
            allSprites.add(bomba2)
            bombs.add(bomba2)
            allSprites.add(bomba3)
            bombs.add(bomba3)


class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, direction = random.choice([-1, 1])):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bombImg, (10, 20))
        self.rect = self.image.get_rect()
        self.rect.midtop = (x, y)
        self.speedy = random.randrange(2, 6)
        self.speedx = random.randrange(3)
        self.direction = direction
        bomb_sound.play()

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx * self.direction

        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bulletImg, (10, 25))
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -7

    def update(self):
        self.rect.y += self.speedy

        if self.rect.bottom < 0:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['health', 'fire'])
        if random.random() > 0.9:
            self.type = 'life'
        self.image = powerupImgs[self.type]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = random.randrange(3, 6)

    def update(self):
        self.rect.y += self.speedy

        if self.rect.top > HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.lastUpdate = pygame.time.get_ticks()
        self.frameRate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.lastUpdate > self.frameRate:
            self.lastUpdate = now
            self.frame += 1
            if self.frame == len(explosion[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Meteor(pygame.sprite.Sprite):
    def __init__(self, speedCap, timeCap = 0):
        pygame.sprite.Sprite.__init__(self)
        self.startImage = random.choice(meteorImg)
        self.image = self.startImage.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedCap = speedCap
        self.speedx = random.randrange(3)
        self.speedy = random.randrange(self.speedCap)
        self.direction = random.choice([-1, 1])
        self.timeCap = timeCap
        self.timeStart = pygame.time.get_ticks()
        self.rotationAngle = 0
        self.rotationSpeed = random.randrange(-9, 9)
        self.lastRotation = pygame.time.get_ticks()

    def update(self):

        if self.timeCap > 0:
            if pygame.time.get_ticks() - self.timeStart > self.timeCap:
                if self.rect.y < 0:
                    self.kill()

        now = pygame.time.get_ticks()
        if now - self.lastRotation > 50:
            self.lastRotation = now
            self.rotationAngle = (self.rotationAngle + self.rotationSpeed) % 360
            oldCenter = self.rect.center
            self.image = pygame.transform.rotate(self.startImage, self.rotationAngle)
            self.rect = self.image.get_rect()
            self.rect.center = oldCenter

        self.rect.x += self.speedx * self.direction
        self.rect.y += self.speedy

        if self.rect.y > HEIGHT or self.rect.right < 0 or self.rect.width > WIDTH:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -100)
            self.speedx = random.randrange(3)
            self.speedy = random.randrange(self.speedCap)


class Star(pygame.sprite.Sprite):
    def __init__(self, x):
        pygame.sprite.Sprite.__init__(self)
        self.startImage = pygame.transform.scale(random.choice(starImg), (random.randrange(10,20),random.randrange(10,20)))
        self.image = self.startImage.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.startx = x
        self.rect.y = -30
        self.speedx = random.randrange(2, 5)
        self.speedy = random.randrange(2, 6)
        self.direction = random.choice([-1, 1])
        self.timeStart = pygame.time.get_ticks()
        self.rotationAngle = 0
        self.rotationSpeed = random.randrange(-7, 7)
        self.lastRotation = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speedx * self.direction
        self.rect.y += self.speedy

        if self.rect.y > HEIGHT+25 or self.rect.x < 0-15 or self.rect.x > WIDTH+15:
            self.rect.y = -25
            self.rect.x = self.startx


        now = pygame.time.get_ticks()
        if now - self.lastRotation > 50:
            self.lastRotation = now
            self.rotationAngle = (self.rotationAngle + self.rotationSpeed) % 360
            oldCenter = self.rect.center
            self.image = pygame.transform.rotate(self.startImage, self.rotationAngle)
            self.rect = self.image.get_rect()
            self.rect.center = oldCenter

    def destroy(self):
        if self.rect.y > HEIGHT or  self.rect.y < 0 or self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        self.image = buttonImg
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = pygame.mouse.get_pressed()

    def update(self):
        mouse = pygame.mouse.get_pos()
        self.clicked = pygame.mouse.get_pressed()
        if mouse[0] >= self.rect.x and mouse[0] <= self.rect.right and mouse[1] >= self.rect.y and mouse[1] <= self.rect.bottom:
            self.image = buttonLitImg
            if self.clicked[0] == 1:
                self.action()
        else:
            self.image = buttonImg

        printText(screen, self.type, 42, self.rect.x + 22, self.rect.y + 55, LIGHT_GREEN, self.rect.center)

    def action(self):
        if self.type == 'PLAY':
            runGame()
        elif self.type == 'EXIT':
            pygame.quit()


playerImg = loadImage('avion.png')
playerImg_immune = loadImage('avion_immune.png')
playerLifeImg = pygame.transform.scale(loadImage('life.png'), (25, 20))
bulletImg = loadImage('raketa.png')
bombImg = loadImage('bomba.png')
allienImg = [loadImage('vanzemaljaca0.png'), loadImage('vanzemaljaca1.png'), loadImage('vanzemaljacb0.png'),
             loadImage('vanzemaljacb1.png'), loadImage('vanzemaljacc0.png'), loadImage('vanzemaljacc1.png'), ]
bossImg = [pygame.transform.scale(loadImage('boss1.png'), (200, 200)),
           pygame.transform.scale(loadImage('boss2.png'), (200, 200)),
           pygame.transform.scale(loadImage('boss3.png'), (200, 200))]
meteorImg = [pygame.transform.scale(loadImage('meteor1.png'), (100, 100)),
             pygame.transform.scale(loadImage('meteor2.png'), (70, 70)),
             pygame.transform.scale(loadImage('meteor3.png'), (50, 50)),
             pygame.transform.scale(loadImage('meteor4.png'), (30, 30)),
             pygame.transform.scale(loadImage('meteor5.png'), (20, 20))]
starImg = [loadImage('star1.png'), loadImage('star2.png'), loadImage('star3.png'), loadImage('star4.png'), loadImage('star5.png')]
buttonImg = pygame.transform.scale(loadImage('button.png'), (170, 70))
buttonLitImg = pygame.transform.scale(loadImage('buttonLit.png'), (170, 70))

backgroundImg = pygame.transform.scale(loadImage('starfield.png'), (WIDTH, HEIGHT))
backgroundRect = backgroundImg.get_rect()
startImg = pygame.transform.scale(loadImage('startscreen.png'), (WIDTH, HEIGHT))
startImgRect = startImg.get_rect()
storyImg = pygame.transform.scale(loadImage('storyImg.png'), (WIDTH, HEIGHT))
storyImgRect = storyImg.get_rect()
pauseScreen = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
pauseScreen.fill((0, 0, 0, 190))

explosion = {}
explosion['large'] = []
explosion['small'] = []

powerupImgs = {}
powerupImgs['health'] = pygame.transform.scale(loadImage('health.png'), (30, 30))
powerupImgs['fire'] = pygame.transform.scale(loadImage('fire.png'), (30, 30))
powerupImgs['life'] = pygame.transform.scale(loadImage('life.png'), (30, 30))

for i in range(10):
    file = 'explosion{}.png'.format(i)
    img = loadImage(file)
    imgLarge = pygame.transform.scale(img, (70, 70))
    explosion['large'].append(imgLarge)
    imgSmall = pygame.transform.scale(img, (30, 30))
    explosion['small'].append(imgSmall)


background_music = loadSound('RoundtableRival.ogg')
pygame.mixer.music = background_music
pygame.mixer.music.set_volume(0.2)
boss_fight_music = loadSound('DBZ_BOSS_FIGHT.ogg')
story_music = loadSound('STAR_WARS.ogg')
shoot_sound = loadSound('shoot.wav')
pygame.mixer.Sound.set_volume(shoot_sound, 0.4)
bomb_sound = loadSound('bomb.wav')
pygame.mixer.Sound.set_volume(bomb_sound, 0.3)
powerup_sound = loadSound('powerup.wav')
pygame.mixer.Sound.set_volume(powerup_sound, 0.6)
playerExplosion_sound = loadSound('playerExplosion.wav')
meteorExplosion_sound = loadSound('meteorExplosion.wav')
pygame.mixer.Sound.set_volume(meteorExplosion_sound, 0.6)
allienExplosion_sound = loadSound('allienExplosion.wav')
pygame.mixer.Sound.set_volume(allienExplosion_sound, 0.5)
keyPress_sound = loadSound('keypress.wav')
pygame.mixer.Sound.set_volume(keyPress_sound, 0.5)


# LOADING HIGH SCORE
try:
    with open(os.path.join(textfile_dir, 'highscore.txt'), 'r') as f:  # automatic file close after loop
        try:
            highscore = int(f.read())
        except:
            highscore = 0
except:
    with open(os.path.join(textfile_dir, 'highscore.txt'), 'w') as f:  # automatic file close after loop
        highscore = 0


allSprites = pygame.sprite.Group()
alliens = pygame.sprite.Group()
meteors = pygame.sprite.Group()
bullets = pygame.sprite.Group()
bombs = pygame.sprite.Group()
bosses = pygame.sprite.Group()
stars = pygame.sprite.Group()
powerups = pygame.sprite.Group()
buttons = pygame.sprite.Group()
player = Player()
allSprites.add(player)
paused = False
level = 1


def initializeGame():
    global paused
    alliens.empty()
    meteors.empty()
    bullets.empty()
    bombs.empty()
    powerups.empty()
    bosses.empty()
    stars.empty()
    player.reset()
    allSprites.empty()
    allSprites.add(player)
    paused = False


def showGameStartScreen():
    pygame.mixer.music.play(-1)
    buttons.empty()
    btn = Button(280, 300, 'PLAY')
    buttons.add(btn)
    btn = Button(600, 550, 'EXIT')
    buttons.add(btn)
    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        screen.blit(startImg, startImgRect)
        buttons.draw(screen)
        printText(screen, 'HIGH SCORE:' + str(highscore), 30, WIDTH/2 - 165, HEIGHT-30, LIGHT_GREEN)

        buttons.update()  # PRINTING TEXT ON BUTTONS

        pygame.display.update()


def showTransitionScreen(text):
    global paused, level
    running = True
    timer = pygame.time.get_ticks()

    #add stars
    for i in range(NUMSTARS):
        x = random.randrange(WIDTH)
        z = Star(x)
        stars.add(z)
        stars.update()

    while stars:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_SPACE and not paused and (pygame.time.get_ticks() - player.shoot_timer > RELOAD):
                    player.shoot()
                if event.key == K_p:
                    paused = not paused

        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            powerup_sound.play()
            if hit.type == 'health':
                player.health += 20
                if player.health > PLAYER_MAX_HEALTH:
                    player.health = PLAYER_MAX_HEALTH
            elif hit.type == 'life':
                player.lives += 1
                if player.lives > 3:
                    player.lives = 3
            else:
                player.powerup()

        if not paused:
            stars.update()
            allSprites.update()

        # DRAW
        screen.fill(BLACK)
        screen.blit(backgroundImg, backgroundRect)
        stars.draw(screen)
        printText(screen, 'Level: ' + str(level), 25, 9, HEIGHT - 29, LIGHT_GREEN)
        printText(screen, 'SCORE:' + str(player.score), 25, WIDTH - 185, HEIGHT - 3, LIGHT_GREEN)
        allSprites.draw(screen)
        now = pygame.time.get_ticks()
        if now - timer > 3000 and now - timer < 6000:
            if (pygame.time.get_ticks() - timer) % 120 <= 100:
                printText(screen, text, 70, 0, 0, LIGHT_GREEN, (WIDTH/2, 100))

        drawHealthBar(screen, 10, HEIGHT - 30, player.health, GREEN, PLAYER_MAX_HEALTH, 200)
        drawLives(screen, 15, HEIGHT - 29, player.lives, playerLifeImg)

        if paused:
            printText(screen, text, 70, 0, 0, LIGHT_GREEN, (WIDTH / 2, 100))
            screen.blit(pauseScreen, (0, 0))
            printText(screen, 'PAUSE', 100, 0, 0, LIGHT_GREEN, screen.get_rect().center)

        pygame.display.update()

        if now - timer > 5000 and not paused:
            for z in stars:
                Star.destroy(z)


def startLevel(allienRows, smartShoot, suicide):
    for k in range(allienRows):
        for i in range(11):
            tmp = random.choice([0, 2, 4])
            a = Alien(70 * i, k * 70, allienImg[tmp], allienImg[tmp + 1], smartShoot, suicide)
            allSprites.add(a)
            alliens.add(a)


def startMeteorRain(k, speedCap, time):
    for i in range(k):
        m = Meteor(speedCap, time)
        meteors.add(m)
        allSprites.add(m)


def spawnBoss(x):
    boss = Boss(x)
    bosses.add(boss)
    allSprites.add(boss)
    runLvl()
    boss_fight_music.stop()
    pygame.mixer.music.play(-1)


def checkCollision():
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        powerup_sound.play()
        if hit.type == 'health':
            player.health += 20
            if player.health > PLAYER_MAX_HEALTH:
                player.health = PLAYER_MAX_HEALTH
        elif hit.type == 'life':
            player.lives += 1
            if player.lives > 3:
                player.lives = 3
        else:
            player.powerup()

    hits = pygame.sprite.groupcollide(alliens, bullets, True, True)
    for hit in hits:
        player.score += 7 * hit.speedx
        allienExplosion_sound.play()
        expl = Explosion(hit.rect.center, 'large')
        allSprites.add(expl)
        if random.random() > 0.8:
            pow = PowerUp(hit.rect.center)
            powerups.add(pow)
            allSprites.add(pow)

    hits = pygame.sprite.groupcollide(bullets, bosses, True, False)
    for hit in hits:
        allienExplosion_sound.play()
        expl = Explosion(hit.rect.midtop, 'large')
        allSprites.add(expl)
        for boss in bosses:
            player.score += 5 * (boss.speedx + 1)
            boss.health -= 99
            if boss.health <= 0:
                bosses.remove()


    hits = pygame.sprite.spritecollide(player, bombs, True)
    for hit in hits:
        if not player.immune:
            player.health -= 13 * hit.speedy
            if player.health <= 0:
                expl = Explosion(player.rect.center, 'large')
                player.lives -= 1
                player.hide()
                allSprites.add(expl)
                playerExplosion_sound.play()
                if player.lives > 0:
                    player.health = PLAYER_MAX_HEALTH
        else:
            expl = Explosion(hit.rect.center, 'small')
            allSprites.add(expl)
            playerExplosion_sound.play()

    hits = pygame.sprite.groupcollide(meteors, bullets, True, True)
    for hit in hits:
        player.score += 60 - hit.radius
        meteorExplosion_sound.play()
        expl = Explosion(hit.rect.center, 'large')
        allSprites.add(expl)

    hits = pygame.sprite.spritecollide(player, meteors, True, pygame.sprite.collide_circle)
    for hit in hits:
        if not player.immune:
            player.health -= 2 * hit.radius
            if player.health <= 0:
                expl = Explosion(hit.rect.center, 'large')
                player.lives -= 1
                player.hide()
                allSprites.add(expl)
                expl = Explosion(player.rect.center, 'large')
                allSprites.add(expl)
                playerExplosion_sound.play()
                meteorExplosion_sound.play()

                if player.lives > 0:
                    player.health = PLAYER_MAX_HEALTH
        else:
            expl = Explosion(hit.rect.center, 'small')
            allSprites.add(expl)
            playerExplosion_sound.play()

    hits = pygame.sprite.spritecollide(player, alliens, True)
    for hit in hits:
        if not player.immune:
            player.lives -= 1
            if player.lives > 0:
                player.health = PLAYER_MAX_HEALTH

            expl = Explosion(player.rect.center, 'large')
            player.hide()
            allSprites.add(expl)
            playerExplosion_sound.play()

        expl = Explosion(hit.rect.center, 'large')
        allienExplosion_sound.play()
        allSprites.add(expl)

    hits = pygame.sprite.spritecollide(player, bosses, False)
    for hit in hits:
        if not player.immune:
            player.lives -= 1
            if player.lives > 0:
                player.health = PLAYER_MAX_HEALTH

            expl = Explosion(player.rect.center, 'large')
            player.hide()
            allSprites.add(expl)
            playerExplosion_sound.play()


def showGameOverScreen():
    global  highscore
    buttons.empty()
    btn = Button(280, 550, 'PLAY')
    buttons.add(btn)
    btn = Button(600, 550, 'EXIT')
    buttons.add(btn)
    if player.score > highscore:
        highscore = player.score
        with open(os.path.join(textfile_dir, 'highscore.txt'), 'w') as f:  # automatic file close after loop
            f.write(str(highscore))
    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        screen.fill(BLACK)
        screen.blit(backgroundImg, backgroundRect)
        if player.lives > 0:
            printText(screen, 'VICTORY', 100, 0, 0, LIGHT_GREEN, (WIDTH/2, HEIGHT/2-120))
        else:
            printText(screen, 'DEFEAT', 100, 0, 0, LIGHT_GREEN, (WIDTH/2, HEIGHT/2-120))

        if player.score == highscore:
            printText(screen, 'NEW HIGH SCORE!', 70, 0, 0, LIGHT_GREEN, (WIDTH / 2, HEIGHT / 2))
            printText(screen, str(highscore), 70, 0, 0, LIGHT_GREEN, (WIDTH / 2, HEIGHT / 2 + 90))
        else:
            printText(screen, 'SCORE: ' + str(player.score), 65, 0, 0, LIGHT_GREEN, (WIDTH/2, HEIGHT/2))
            printText(screen, 'HIGH SCORE: ' + str(highscore), 65, 0, 0, LIGHT_GREEN, (WIDTH/2, HEIGHT/2 + 90))

        buttons.draw(screen)
        buttons.update()  # PRINTING TEXT ON BUTTONS

        pygame.display.update()


def runLvl():
    global paused, player
    while alliens or meteors or bosses:
        clock.tick(FPS)

        # PROCESS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == K_SPACE and not paused and (pygame.time.get_ticks() - player.shoot_timer > RELOAD):
                    player.shoot()
                if event.key == K_p:
                    paused = not paused
        checkCollision()

        # UPDATE
        if not paused:
            allSprites.update()

        # DRAW
        screen.fill(BLACK)
        screen.blit(backgroundImg, backgroundRect)
        printText(screen, 'Level: ' + str(level), 25, 9, HEIGHT - 29, LIGHT_GREEN)
        printText(screen, 'SCORE:' + str(player.score), 25, WIDTH - 185, HEIGHT - 3, LIGHT_GREEN)
        allSprites.draw(screen)
        for boss in bosses:
            drawHealthBar(screen, 240, HEIGHT - 30, boss.health, RED, 1000*boss.bosstype, 350)
            if boss.health <= 0:
                player.score += 300*boss.bosstype
                bosses.remove(boss)
                allSprites.remove(boss)
        drawHealthBar(screen, 10, HEIGHT - 30, player.health, GREEN, PLAYER_MAX_HEALTH, 200)
        drawLives(screen, 15, HEIGHT - 29, player.lives, playerLifeImg)

        if paused:
            screen.blit(pauseScreen, (0, 0))
            printText(screen, 'PAUSE', 100, 0, 0, LIGHT_GREEN, screen.get_rect().center)

        pygame.display.update()


def runGame():
    initializeGame()
    global  level

    showTransitionScreen('ARMY ATTACKS')
    startLevel(3, False, False)
    runLvl()

    showTransitionScreen('METEOR RAIN')
    startMeteorRain(30, 6, 2500)
    runLvl()

    pygame.mixer.music.stop()
    boss_fight_music.play(-1)
    showTransitionScreen('CAPTAIN ATTACKS')
    spawnBoss(1)

    level += 1
    showTransitionScreen('ARMY ATTACKS')
    startLevel(4, True, False)
    runLvl()

    showTransitionScreen('METEOR RAIN')
    startMeteorRain(45, 8, 5000)
    runLvl()

    pygame.mixer.music.stop()
    boss_fight_music.play(-1)
    showTransitionScreen('GENERAL ATTACKS')
    spawnBoss(2)

    level += 1
    showTransitionScreen('ARMY ATTACKS')
    startLevel(5, True, True)
    runLvl()

    showTransitionScreen('METEOR RAIN')
    startMeteorRain(50, 8, 5500)
    runLvl()

    pygame.mixer.music.stop()
    boss_fight_music.play(-1)
    showTransitionScreen('LEADER ATTACKS')
    spawnBoss(3)

    if (not alliens) and (not bosses):
        showTransitionScreen('ALIENS DEFEATED')

    showGameOverScreen()

# MAIN
showStory()

pygame.quit()
