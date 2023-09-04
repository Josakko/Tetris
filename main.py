import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame, sys
from copy import deepcopy
from random import choice, randrange

W, H = 10, 20
TILE = 45
GAME_RESOLUTION = W * TILE, H * TILE
RESOLUTION = 750, 940
FPS = 60
DATA_FILE ="data.txt"
FIGURES_POS = [
    [(-1, 0), (-2, 0), (0, 0), (1, 0)],
    [(0, -1), (-1, -1), (-1, 0), (0, 0)],
    [(-1, 0), (-1, 1), (0, 0), (0, -1)],
    [(0, 0), (-1, 0), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, 0)]
]


class Game:
    def __init__(self, game=pygame):
        game.init()

        screen = game.display.set_mode(RESOLUTION)
        game.display.set_caption("Tetris")
        game.display.set_icon(game.image.load("assets\JK.ico"))

        overlay = pygame.Surface((RESOLUTION), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))

        game_screen = game.Surface(GAME_RESOLUTION)
        grid = [game.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

        self.figures = [[game.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in FIGURES_POS]
        figure_rect = game.Rect(0, 0, TILE - 2, TILE - 2)
        self.field = [[0 for i in range(W)] for j in range(H)]

        anim_count, anim_speed, anim_limit = 0, 60, 2000

        bg = game.image.load("assets/bg.jpg").convert()
        game_bg = game.image.load("assets/bg2.jpg").convert()

        title_font = game.font.Font("assets/font.ttf", 63)
        font = game.font.Font("assets/font.ttf", 45)

        paused_lbl = title_font.render("Paused", True, game.Color("darkorange"))
        title = title_font.render("TETRIS", True, game.Color("darkorange"))
        score_lbl = font.render("Score:", True, game.Color("green"))
        record_lbl = font.render("Record:", True, game.Color("purple"))

        get_color = lambda: (randrange(30, 256), randrange(30, 256), randrange(30, 256))

        self.figure, self.next_figure = deepcopy(choice(self.figures)), deepcopy(choice(self.figures))
        color, next_color = get_color(), get_color()

        score, lines = 0, 0
        scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}

        self.paused = False

        while True:
            record = self.get_record()
            dx, rotate = 0, False

            screen.blit(bg, (0, 0))
            screen.blit(game_screen, (20, 20))
            game_screen.blit(game_bg, (0, 0))

            for i in range(lines):
                game.time.wait(200)

            for event in game.event.get():
                if event.type == game.QUIT:
                    sys.exit(0)
                if event.type == game.KEYDOWN:
                    if event.key == game.K_LEFT and not self.paused:
                        dx = -1
                    elif event.key == game.K_RIGHT and not self.paused:
                        dx = 1
                    elif event.key == game.K_DOWN and not self.paused:
                        anim_limit = 100
                    elif event.key == game.K_UP and not self.paused:
                        rotate = True
                    elif event.key == game.K_ESCAPE:
                        if self.paused: 
                            self.paused = not self.paused 
                            game.display.set_caption("Tetris") 
                            #title = title_font.render("TETRIS", True, game.Color("darkorange"))

                        else: 
                            self.paused = not self.paused 
                            game.display.set_caption("Paused - Tetris")
                            #title = title_font.render("Paused", True, game.Color("darkorange"))

            if self.paused:
                screen.blit(overlay, (0, 0))
                screen.blit(paused_lbl, (185, RESOLUTION[1] / 2))

            if not self.paused:
                #game.display.set_caption("Tetris")

                figure_old = deepcopy(self.figure)
                for i in range(4):
                    self.figure[i].x += dx
                    if not self.check_borders(i):
                        self.figure = deepcopy(figure_old)
                        break

                anim_count += anim_speed
                if anim_count > anim_limit:
                    anim_count = 0
                    figure_old = deepcopy(self.figure)
                    for i in range(4):
                        self.figure[i].y += 1
                        if not self.check_borders(i):
                            for i in range(4):
                                self.field[figure_old[i].y][figure_old[i].x] = color
                            self.figure, color = self.next_figure, next_color
                            self.next_figure, next_color = deepcopy(choice(self.figures)), get_color()
                            anim_limit = 2000
                            break

                center = self.figure[0]
                figure_old = deepcopy(self.figure)
                if rotate:
                    for i in range(4):
                        x = self.figure[i].y - center.y
                        y = self.figure[i].x - center.x
                        self.figure[i].x = center.x - x
                        self.figure[i].y = center.y + y
                        if not self.check_borders(i):
                            self.figure = deepcopy(figure_old)
                            break

                line, lines = H - 1, 0
                for row in range(H - 1, -1, -1):
                    count = 0
                    for column in range(W):
                        if self.field[row][column]:
                            count += 1
                        self.field[line][column] = self.field[row][column]
                    if count < W:
                        line -= 1
                    else:
                        anim_speed += 3
                        lines += 1

                score += scores[lines]
            

            [game.draw.rect(game_screen, (40, 40, 40), i_rect, 1) for i_rect in grid]

            for i in range(4):
                figure_rect.x = self.figure[i].x * TILE
                figure_rect.y = self.figure[i].y * TILE
                game.draw.rect(game_screen, color, figure_rect)

            for y, raw in enumerate(self.field):
                for x, col in enumerate(raw):
                    if col:
                        figure_rect.x, figure_rect.y = x * TILE, y * TILE
                        game.draw.rect(game_screen, col, figure_rect)

            for i in range(4):
                figure_rect.x = self.next_figure[i].x * TILE + 380
                figure_rect.y = self.next_figure[i].y * TILE + 185
                game.draw.rect(screen, next_color, figure_rect)

            screen.blit(title, (485, 0))
            screen.blit(score_lbl, (535, 780))
            screen.blit(font.render(str(score), True, game.Color("white")), (550, 840))
            screen.blit(record_lbl, (525, 650))
            screen.blit(font.render(record, True, game.Color("gold")), (550, 710))

            for i in range(W):
                if self.field[0][i]:
                    self.set_record(score)
                    self.field = [[0 for i in range(W)] for i in range(H)]
                    anim_count, anim_speed, anim_limit = 0, 60, 2000
                    score = 0
                    for i_rect in grid:
                        game.draw.rect(game_screen, get_color(), i_rect)
                        screen.blit(game_screen, (20, 20))
                        game.display.flip()
                        game.time.Clock().tick(200)

            game.display.flip()
            game.time.Clock().tick(FPS)


    def check_borders(self, i):
        if self.figure[i].x < 0 or self.figure[i].x > W - 1:
            return False
        elif self.figure[i].y > H - 1 or self.field[self.figure[i].y][self.figure[i].x]:
            return False
        return True


    def get_record(self):
        try:
            with open(DATA_FILE, "r") as f:
                return f.read()
        except:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                f.write("0")
                return "0"


    def set_record(self, score):
        if int(self.get_record()) < score:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                f.write(str(score))



Game(pygame)

