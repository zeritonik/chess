import pygame
from values import *
from figures import *

FIELD_VARIANTS = (
[[Bishop(1), Horse(1), Rook(1), King(1), Queen(1), Rook(1), Horse(1), Bishop(1)], # 0
 [Pawn(1), Pawn(1), Pawn(1), Pawn(1), Pawn(1), Pawn(1), Pawn(1), Pawn(1)],
 [0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0],
 [Pawn(0), Pawn(0), Pawn(0), Pawn(0), Pawn(0), Pawn(0), Pawn(0), Pawn(0)],
 [Bishop(0), Horse(0), Rook(0), King(0), Queen(0), Rook(0), Horse(0), Bishop(0)]], # 0
[['x', Bishop(1), Horse(1), Rook(1), King(1), Queen(1), Rook(1), Horse(1), Bishop(1), 'x'], # 1
 [Warrior(1), Pawn(1), Pawn(1), Spearman(1), Pawn(1), Pawn(1), Spearman(1), Pawn(1), Pawn(1), Warrior(1)],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
 [Warrior(0), Pawn(0), Pawn(0), Spearman(0), Pawn(0), Pawn(0), Spearman(0), Pawn(0), Pawn(0), Warrior(0)],
 ['x', Bishop(0), Horse(0), Rook(0), King(0), Queen(0), Rook(0), Horse(0), Bishop(0), 'x']], # 1
[[King(1), 0, 0, 0, 0, 0], # 2
 [0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0],
 [King(0), Bishop(0), 0, 0, 0, 0]], # 2
)
KINGS_VARIANTS = (
((3, 7), (3, 0)), # 0
((4, 7), (4, 0)), # 1
((0, 4), (0, 0)), # 2
)


class Field:
    def __init__(self, variant=0):
        self.field = FIELD_VARIANTS[variant]
        kings = KINGS_VARIANTS[variant]
        self.kings = self.field[kings[0][1]][kings[0][0]], self.field[kings[1][1]][kings[1][0]]
        self.width, self.height = len(self.field[0]), len(self.field)

    def init_field(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.field[y][x] != 0 and self.field[y][x] != 'x':
                    self.field[y][x].set_pos(x, y)
                    self.field[y][x].set_image()

    def create_field_image(self, colors=FIELD_COLORS):
        self.image = pygame.Surface((BLOCK * self.width, BLOCK * self.height))
        self.figures = pygame.Surface((BLOCK * self.width, BLOCK * self.height)).convert_alpha()
        self.figures.fill((0, 0, 0, 0))

        cur = [0, 0]
        color = (self.height + self.width - 16) % 2 
        for y in self.field:
            for x in y:
                if x != 'x':
                    pygame.draw.rect(self.image, colors[color], (*cur, BLOCK, BLOCK))
                    if x != 0:
                        self.figures.blit(x.image, cur)
                elif x == 'x':
                    pygame.draw.rect(self.image, NO_PLACE_COLOR, (*cur, BLOCK, BLOCK))
                else:
                    pygame.draw.rect(self.image, BG, (*cur, BLOCK, BLOCK))
                cur[0] += BLOCK
                color ^= 1
            cur[0] = 0
            cur[1] += BLOCK
            if self.width % 2 == 0:
                color ^= 1

    def create_figures_image(self):
        self.figures = pygame.Surface((BLOCK * self.width, BLOCK * self.height)).convert_alpha()
        self.figures.fill((0, 0, 0, 0))
        cur = [0, 0]
        for y in self.field:
            for x in y:
                if x != 'x' and x != 0:
                    self.figures.blit(x.image, cur)
                cur[0] += BLOCK
            cur[0] = 0
            cur[1] += BLOCK

    def get_cell(self, x, y):
        x = (x - LR) // BLOCK
        y = (y - TB) // BLOCK
        if 0 <= x < self.width and 0 <= y < self.height:
            return (x, y)
        else:
            return None

    def get_enemy_figures(self, color):
        return [x for y in self.field for x in y if x != 0 and x != 'x' and x.color != color]

    def get_team_figures(self, color):
        return [x for y in self.field for x in y if x != 0 and x != 'x' and x.color == color]

    def get_atacks(self, figures):
        atacks = set()
        for figure in figures:
            for atack in figure.atacks:
                atacks.add(atack)
        return atacks

    def get_figure(self, cell):
        if self.field[cell[1]][cell[0]] != 'x' and self.field[cell[1]][cell[0]] != 0:
            return self.field[cell[1]][cell[0]]
        else:
            return None

    def set_figures_moves(self):
        for y in self.field:
            for x in y:
                if x != 0 and x != 'x' and type(x) != King:
                    x.set_moves(self)
        self.kings[0].set_moves(self)
        self.kings[1].set_moves(self)
        self.kings[0].set_moves(self)