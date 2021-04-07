import json
import math
import os
import random
import time
import pygame

true = True
false = False # so i can be lazy XD

pygame.mixer.pre_init(48000, -16, 1, 1024)
pygame.init()

screen_dimensions = (800, 600)


class SceneBase:
    def __init__(self):
        self.next = self

    def ProcessInput(self, events, pressed_keys):
        print("uh-oh, you didn't override this in the child class")

    def Update(self, *args):
        print("uh-oh, you didn't override this in the child class")

    def Render(self, screen):
        print("uh-oh, you didn't override this in the child class")

    def SwitchToScene(self, next_scene):
        self.next = next_scene

    def Terminate(self):
        self.SwitchToScene(None)


def calculateDistance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


"""
-------------------Running the game----------------------
"""


def run_game(width, height, fps, starting_scene):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Beat Malfunction")
    pygame.display.set_icon(pygame.image.load("images/icon.png"))
    clock = pygame.time.Clock()
    glitch_sfx = pygame.mixer.Sound("sfx/sound_effects/impact-glitch.mp3")

    active_scene = starting_scene

    try:
        active_scene.music.set_volume(0.9)
        active_scene.music.play(-1)
    except AttributeError:
        pass  # stop yelling at me pycharm
    except Exception as E:
        print(E)

    while active_scene is not None:
        pressed_keys = pygame.key.get_pressed()

        # Event filtering
        filtered_events = []
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                              pressed_keys[pygame.K_RALT]
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True

            if quit_attempt:
                glitch_sfx.play()
                screen.blit(pygame.image.load("images/scenery/animated/glitched_overlay/glitch_overlay0045.png"),
                            (0, 0))
                pygame.time.wait(500)
                active_scene.Terminate()
            else:
                filtered_events.append(event)

        active_scene.ProcessInput(filtered_events, pressed_keys)
        active_scene.Update()
        active_scene.Render(screen)

        active_scene = active_scene.next

        pygame.display.flip()
        clock.tick(fps)


"""
---------- classes and game shit --------------
"""


class Button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, win, outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('Arial', 25)
            text = font.render(self.text, True, (200, 200, 200))
            win.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2),
                self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        if self.x < pos[0] < self.x + self.width:
            if self.y < pos[1] < self.y + self.height:
                return True

        return False


class TitleScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.music = pygame.mixer.Sound("sfx/music/titlescreen.mp3")
        self.music.set_volume(0.8)
        self.clickSound = pygame.mixer.Sound("sfx/sound_effects/laser_1.mp3")

        self.hud_circle_images = []
        for r, d, f in os.walk("images/scenery/animated/hud-circle"):
            for file in f:
                if file.startswith("hud-circle"):
                    self.hud_circle_images.append(pygame.image.load("images/scenery/animated/hud-circle/" + file))
        self.hud_circle_cycle = len(self.hud_circle_images)
        self.hud_circle_image = self.hud_circle_images[0]

        self.glitch_images = []
        for r, d, f in os.walk("images/scenery/animated/glitched_overlay"):
            for file in f:
                self.glitch_images.append(
                    pygame.image.load("images/scenery/animated/glitched_overlay/" + file))
        self.glitch_image_cycle = len(self.glitch_images)
        self.glitch_image = self.glitch_images[0]

    def ProcessInput(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.music.stop()
                self.clickSound.play(1, 500, 200)
                self.SwitchToScene(MenuScene())

    def Update(self):
        if self.hud_circle_cycle + 1 >= len(self.hud_circle_images):
            self.hud_circle_cycle = 0
        self.hud_circle_image = self.hud_circle_images[self.hud_circle_cycle]
        self.hud_circle_cycle += 1

        if self.glitch_image_cycle + 1 >= len(self.glitch_images):
            self.glitch_image_cycle = 0
        self.glitch_image = self.glitch_images[self.glitch_image_cycle]
        self.glitch_image_cycle += 1

    def Render(self, screen):
        font = pygame.font.SysFont("Arial", 50)
        title_text = font.render("BEAT MALFUNCTION", True,
                                 (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)))
        font = pygame.font.SysFont("Arial", 25)
        sub_text = font.render("Press ENTER to begin...",
                               True,
                               (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)))

        mouse = pygame.mouse.get_pos()
        pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))

        screen.blit(self.hud_circle_image, (0, 0))

        screen.blit(title_text, (screen.get_width() - title_text.get_rect().width - 150, 100))

        screen.blit(sub_text, (screen.get_width() - sub_text.get_rect()
                               .width + random.randint(1, 3) - 250, 500))

        screen.blit(self.glitch_image, (0, 0))

        pygame.draw.circle(screen, (random.randint(1, 55), random.randint(1, 255), random.randint(1, 255)),
                           (mouse[0] + random.randint(1, 10), mouse[1] + random.randint(1, 10)), 10)


"""
---------- songs / beatmaps --------------
"""


class BeatMap(SceneBase):
    def __init__(self, directory):
        SceneBase.__init__(self)

        # load song
        pygame.mixer.stop()
        self.title = "Error"
        self.json_file = ""
        self.json = None
        self.beats = []
        self.movements = []
        self.score = 0
        self.health = 100
        self.directory = directory

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".mp3"):
                    self.music = pygame.mixer.Sound(f"{directory}/{file}")
                    self.music_length = self.music.get_length()
                    self.title = file.replace(".mp3", "")
                elif ".json" in file:
                    self.json_file = file # if multiple json files last one will be selected


        # create list of movement_timings from json files
        with open(f"{directory}/{self.json_file}", "r") as beats_file:
            self.json = json.load(beats_file)

        self.movements = self.json[self.title.lower()]["movement_timings"]

        self.current_movements = []
        self.start_time = time.time()

        # the hud overlay
        self.hud_overlay_images = []
        for r, d, f in os.walk("images/scenery/animated/basic-hud"):
            for file in f:
                if file.startswith("basic-hud"):
                    self.hud_overlay_images.append(pygame.image.load("images/scenery/animated/basic-hud/" + file))
        self.hud_overlay_cycle = len(self.hud_overlay_images)
        self.hud_overlay_image = self.hud_overlay_images[0]

        # clicker ball shit
        self.ball_images = []
        for r, d, f in os.walk("images/circles/magic-ball-purple"):
            for file in f:
                if file.startswith("magic-ball-purple"):
                    self.ball_images.append(pygame.image.load("images/circles/magic-ball-purple/" + file))
        self.ball_images_cycle = len(self.ball_images)
        self.ball_image = self.ball_images[0]

        # steps and positions
        self.ball_x, self.ball_y = (400, 300)
        self.stepx, self.stepy = (0, 0)

        self.time_since_start = time.time() - self.start_time

        self.music_length = 30 + random.randint(1, 15)

        self.ball_x, self.ball_y = (400, 300)

        self.hitbox = (self.ball_x + 17, self.ball_y + 11, 75, 75)

    def GetScores(self):
        scores = dict()
        with open(self.directory + "/highscore.txt", "r") as score_file:
            for line in score_file.readlines():
                if line == "/n":
                    continue
                x = line.split()
                date = x[0]
                score = x[2]
                scores[date] = score

        return scores

    def Fail(self):
        self.next = MenuScene()

    def Update(self):
        self.hitbox = (self.ball_x, self.ball_y, 75, 75)

        self.time_since_start = time.time() - self.start_time

        if self.hud_overlay_cycle + 1 >= len(self.hud_overlay_images):
            self.hud_overlay_cycle = 0
        self.hud_overlay_image = self.hud_overlay_images[self.hud_overlay_cycle]
        self.hud_overlay_cycle += 1

        if self.ball_images_cycle + 1 >= len(self.ball_images):
            self.ball_images_cycle = 0
        self.ball_image = self.ball_images[self.ball_images_cycle]
        self.ball_images_cycle += 1

        # beat timings
        for beat in self.movements:
            if beat["time"] == round(time.time() - self.start_time):
                self.current_movements.append(beat)

        for beat in self.current_movements:
            beat_x = beat['x']
            beat_y = beat['y']
            dx, dy = (beat_x - self.ball_x, beat_y - self.ball_y)
            self.stepx, self.stepy = (dx / 50., dy / 50.)

        mouse = pygame.mouse.get_pos()
        if mouse[1] - 75 < self.hitbox[1] + self.hitbox[3] and mouse[1] + 75 > self.hitbox[1]:
            if mouse[1] + 75 > self.hitbox[0] and mouse[0] - 75 < self.hitbox[0] + self.hitbox[2]:
                self.score += 15
        else:
            self.health -= 1

        self.ball_x += self.stepx
        self.ball_y += self.stepy

        if self.health <= 0:
            self.Fail()

        if round(time.time() - self.start_time, 2) >= self.music_length:
            pygame.mixer.stop()
            self.SwitchToScene(MenuScene())

    def ProcessInput(self, events, pressed_keys):
        if pressed_keys[pygame.K_r]:
            pygame.mixer.stop()
            self.SwitchToScene(MenuScene())

    def Render(self, screen):
        mouse = pygame.mouse.get_pos()
        screen.blit(self.hud_overlay_image, (0, 0))

        screen.blit(self.ball_image, (self.ball_x, self.ball_y))

        screen.blit(
            pygame.font.SysFont("Arial", 25).render(f"Score: {self.score}", True, (100, 200, 100)),
            (10, 300))
        screen.blit(
            pygame.font.SysFont("Arial", 25).render(f"Health: {self.health}", True, (100, 200, 100)),
            (10, 250))

        pygame.draw.circle(screen, (random.randint(1, 55), random.randint(1, 255), random.randint(1, 255)),
                           (mouse[0] + random.randint(1, 10), mouse[1] + random.randint(1, 10)),
                           10)

    def SwitchToScene(self, next_scene):
        from datetime import date
        today = date.today()
        with open(f"{self.directory}/highscore.txt", "a") as file:
            file.write("\n{} - {}".format(today.strftime("%b-%d-%Y-%M"), self.score))
        self.next = next_scene


"""
---------- main menu --------------
"""

beatmaps = []
for root, dirs, files in os.walk("songs"):
    for dir in dirs:
        beatmaps.append(BeatMap(f"songs/{dir}"))

class ScoreDisplay(SceneBase):
    def __init__(self):
        super().__init__()
        self.beatMaps = beatmaps
        pygame.mixer.stop()

        b_x, b_y = (100, 200)
        self.space = 165 + 265
        self.buttons = []
        for bm in self.beatMaps:
            self.buttons.append(Button((random.randint(20, 50), random.randint(20, 50), random.randint(20, 50)),
                       b_x, b_y, 165, 30, bm.title))
            b_x += self.space

    def ProcessInput(self, events, pressed_keys):
        if pressed_keys[pygame.K_r]:
            pygame.mixer.stop()
            self.SwitchToScene(MenuScene())
    def Update(self):
        pass
    def Render(self,screen):
        screen.fill((44, 44, 44))
        title_font = pygame.font.SysFont("Arial", 30)
        small_font = pygame.font.SysFont("Arial", 20)
        title = title_font.render("High Scores", True,
                                  (random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)))
        screen.blit(title, (screen.get_width() / 2 - title.get_rect().width + 75, 50))

        for b in self.buttons:
            b.draw(screen)

        y = 300
        x = screen.get_width() / 2 - 200
        for bm in self.beatMaps:
            for date, score in bm.GetScores().items():
                text = small_font.render("{} - {}pts @ {}".format(bm.title, score, date), True, (202, 220, 222))
                screen.blit(text, (x, y))
                y += 20



class MenuScene(SceneBase):

    def __init__(self):
        SceneBase.__init__(self)
        self.nonunicode = "\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac" \
                          "\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9" \
                          "\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5" \
                          "\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1" \
                          "\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd" \
                          "\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9" \
                          "\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5" \
                          "\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff\u0100" \
                          "\u0101\u0102\u0103\u0104\u0105\u0106\u0107\u0108" \
                          "\u0109\u010a\u010b\u010c\u010d\u010e\u010f\u0110" \
                          "\u0111\u0112\u0113\u0114\u0115\u0116\u0117\u0118" \
                          "\u0119\u011a\u011b\u011c\u011d\u011e\u011f\u0120" \
                          "\u0121\u0122\u0123\u0124\u0125\u0126\u0127\u0128" \
                          "\u0129\u012a\u012b\u012c\u012d\u012e\u012f\u0130" \
                          "\u0131\u0132\u0133\u0134\u0135\u0136\u0137\u0138" \
                          "\u0139\u013a\u013b\u013c\u013d\u013e\u013f\u0140" \
                          "\u0141\u0142\u0143\u0144\u0145\u0146\u0147\u0148" \
                          "\u0149\u014a\u014b\u014c\u014d\u014e\u014f\u0150" \
                          "\u0151\u0152\u0153\u0154\u0155\u0156\u0157\u0158" \
                          "\u0159\u015a\u015b\u015c\u015d\u015e\u015f\u0160" \
                          "\u0161\u0162\u0163\u0164\u0165\u0166\u0167\u0168" \
                          "\u0169\u016a\u016b\u016c\u016d\u016e\u016f\u0170" \
                          "\u0171\u0172\u0173\u0174\u0175\u0176\u0177\u0178" \
                          "\u0179\u017a\u017b\u017c\u017d\u017e" # list of "glitched" characters

        self.songs = [map for map in beatmaps]
        self.maps = []
        song_y = 100
        for song in self.songs:
            title = []
            for x in range(len(song.title)):
                title.append(random.choice(self.nonunicode))
            self.maps.append(
                Button((random.randint(20, 50), random.randint(20, 50), random.randint(20, 50)),
                       600, song_y, 165, 30, str("".join(title))))
            song_y += 50

        self.score_button = Button((random.randint(20, 50), random.randint(20, 50), random.randint(20, 50)),
                       600, 500, 165, 30, "SCORES")



        # hud overlay
        self.hud_overlay_images = []
        for r, d, f in os.walk("images/scenery/animated/basic-hud"):
            for file in f:
                if file.startswith("basic-hud"):
                    self.hud_overlay_images.append(pygame.image.load("images/scenery/animated/basic-hud/" + file))
        self.hud_overlay_cycle = len(self.hud_overlay_images)
        self.hud_overlay_image = self.hud_overlay_images[0]

        # audio shits
        self.music = pygame.mixer.Sound("sfx/sound_effects/background-hum.wav")
        self.glitch_sound = pygame.mixer.Sound("sfx/sound_effects/laser_1.mp3")
        self.background_glitch = pygame.mixer.Sound("sfx/sound_effects/long-glitch-background.mp3")
        self.background_glitch.play(-1)
        self.playing_glitch_sound = False

    def ProcessInput(self, events, pressed_keys):
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for map in self.maps:
                    if map.isOver(mouse_pos):
                        map.color = (
                            random.randint(0, 20),
                            random.randint(0, 20),
                            random.randint(0, 255)
                        )
                    pygame.mixer.stop()
                    scene = random.choice(self.songs)
                    scene.music.play(-1)
                    self.SwitchToScene(scene)

                if self.score_button.isOver(pygame.mouse.get_pos()):
                    self.SwitchToScene(ScoreDisplay())

    def Update(self):
        for map in self.maps:
            if map.isOver(pygame.mouse.get_pos()):
                if not self.playing_glitch_sound:
                    self.glitch_sound.play()
                    self.playing_glitch_sound = True
                map.color = (random.randint(200, 255),
                             random.randint(0, 20),
                             random.randint(0, 20))
            else:
                map.color = (random.randint(20, 50), random.randint(20, 50), random.randint(20, 50))
                self.playing_glitch_sound = False

        if self.hud_overlay_cycle + 1 >= len(self.hud_overlay_images):
            self.hud_overlay_cycle = 0
        self.hud_overlay_image = self.hud_overlay_images[self.hud_overlay_cycle]
        self.hud_overlay_cycle += 1

    def Render(self, screen):
        mouse = pygame.mouse.get_pos()
        # screen.fill((random.randint(1, 10), random.randint(1, 10), random.randint(1, 10)))
        screen.blit(self.hud_overlay_image, (0, 0))
        pygame.mouse.set_cursor((8, 8), (0, 0), (0, 0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0, 0))

        font = pygame.font.SysFont("Arial", 20)
        title_text = font.render("BEAT MALFUNCTION", True,
                                 (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255)))
        screen.blit(title_text, (300, 10))

        for map in self.maps:
            newText = ""
            for i in range(len(map.text)):
                newText+=random.choice(self.nonunicode)
            map.text = newText
            map.draw(screen)

        self.score_button.draw(screen)

        # draw mouse circle cursor (goes last!)
        pygame.draw.circle(screen, (random.randint(1, 55), random.randint(1, 255), random.randint(1, 255)),
                           (mouse[0] + random.randint(1, 10), mouse[1] + random.randint(1, 10)),
                           10)


run_game(800, 600, 60, TitleScene())
