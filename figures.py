from values import *
import pygame.draw


class Figure:
    def __init__(self, color):
        self.color = FIGURE_COLORS[color]
        self.atacks, self.moves = [], []

    def set_image(self):
        color = FIGURE_COLORS.index(self.color)
        name = type(self).name
        if color == 0:
            self.image = pygame.image.load(f"figures/white_{name}.png")
        else:
            self.image = pygame.image.load(f"figures/dark_{name}.png")

    def set_pos(self, x, y):
        self.x, self.y = x, y

    def show_moves(self, window):
        for i in self.moves:
            x, y = LR + i[0] * BLOCK, TB + i[1] * BLOCK
            pygame.draw.rect(window, MOVE_C, (x, y, BLOCK, BLOCK))

    def move(self, cell, field):
        if cell in self.moves:
            print(f"({self.x}, {self.y}) --> ({cell[0]}, {cell[1]})")
            self.move_to(cell, 0, field)
            return True
        return False

    def move_to(self, cell, figure, field):
        field.field[self.y][self.x] = figure
        self.x, self.y = cell
        field.field[self.y][self.x] = self

    def add_place(self, field, cell):
        x, y = cell
        if x not in range(0, field.width) or y not in range(0, field.height):
            return False
        if field.field[y][x] == 'x' or (field.field[y][x] != 0 and field.field[y][x].color == self.color):
            return False
        self.atacks.append(cell)
        if not self.add_move:
            return False
        self.moves.append(cell)
        if type(field.field[y][x]) == King:
            self.add_move = False
            return True
        elif field.field[y][x] == 0:
            return True
        return False


class Pawn(Figure):
    name = "pawn"

    def set_pos(self, x, y):
        self.x = x
        self.y, self.y_start = y, y

    def set_moves(self, field):
        self.moves = []
        self.atacks = []
        k = 1 if self.color == FIGURE_COLORS[1] else -1
        if field.field[self.y + k][self.x] == 0:
            self.moves.append((self.x, self.y + k))
            if self.y == self.y_start and field.field[self.y + k + k][self.x] == 0:
                self.moves.append((self.x, self.y + k + k))
        for kx in (-1, 1):
            x = self.x + kx
            if x in range(0, field.width):
                self.atacks.append((x, self.y + k))
                if field.field[self.y + k][x] != 'x' and field.field[self.y + k][x] != 0 and field.field[self.y + k][x].color != self.color:
                    self.moves.append((x, self.y + k))

    def move(self, cell, field):
        if cell in self.moves:
            print(f"({self.x}, {self.y}) --> ({cell[0]}, {cell[1]})")
            self.move_to(cell, 0, field)
            self.change_pawn(field)
            return True
        return False

    def change_pawn(self, field):
        end = field.height - 1 if self.color == FIGURE_COLORS[1] else 0
        if self.y == end:
            figures = {"Queen": Queen, "Rook": Rook, "Horse": Horse, "Bishop": Bishop}
            print(tuple(figures))
            new = input("My choice: ")
            while new not in tuple(figures):
                new = input("No such figure: ")
            figure = figures[new](FIGURE_COLORS.index(self.color))
            figure.set_pos(self.x, self.y)
            figure.set_image()
            field.field[self.y][self.x] = figure
            del self


class King(Figure):
    name = "king"

    def __init__(self, color):
        super().__init__(color)
        self.rak = []
        self.raked = False

    def add_place(self, field, cell):
        if cell[0] not in range(0, field.width) or cell[1] not in range(0, field.height):
            return False
        x, y = cell
        if field.field[y][x] == 0 or (field.field[y][x] != 'x' and field.field[y][x].color != self.color):
            self.moves.append(cell)
            return True
        return False

    def set_rak(self, field, atacks):
        self.rak = []
        x = self.x - 3
        if x in range(0, field.width) and type(field.field[self.y][x]) == Bishop and field.field[self.y][x].color == self.color:
            for i in range(x, self.x + 1):
                if (i, self.y) in atacks:
                    break
            else:
                for i in range(x + 1, self.x):
                    if type(field.field[self.y][i]) != int:
                        break
                else:
                    self.rak.append((x + 1, self.y))
        x = self.x + 4
        if x in range(0, field.width) and type(field.field[self.y][x]) == Bishop and field.field[self.y][x].color == self.color:
            for i in range(self.x, x + 1):
                if (i, self.y) in atacks:
                    break
            else:
                for i in range(self.x + 1, x):
                    if type(field.field[self.y][i]) != int:
                        break
                else:
                    self.rak.append((x - 1, self.y))

    def show_moves(self, window):
        super().show_moves(window)
        for i in self.rak:
            pygame.draw.rect(window, MOVE_C, (LR + i[0] * BLOCK, TB+ i[1] * BLOCK, BLOCK, BLOCK))

    def set_moves(self, field):
        self.moves = []
        self.atacks = []
        atacks = field.get_atacks(field.get_enemy_figures(self.color))
        for x in range(-1, 2):
            for y in range(-1, 2):
                cell = (self.x + x, self.y + y)
                self.atacks.append(cell)
                if x == y == 0 or cell in atacks:
                    continue
                else:
                    self.add_place(field, cell)
        if not self.raked:
            self.set_rak(field, atacks)

    def move(self, cell, field):
        if cell in self.moves:
            print(f"({self.x}, {self.y}) --> ({cell[0]}, {cell[1]})")
            self.move_to(cell, 0, field)
            return True
        elif cell in self.rak:
            print(f"({self.x}, {self.y}) --> ({cell[0]}, {cell[1]}) rak")
            k = -1 if self.x > cell[0] else 1
            bishop = field.field[cell[1]][cell[0] + k]
            self.move_to(cell, 0, field)
            bishop.move_to((self.x - k, self.y), 0, field)
            self.raked = True
            self.rak = []
            return True
        return False


class Horse(Figure):
    name = "horse"

    def set_moves(self, field):
        self.atacks, self.moves = [], []
        self.add_move = True
        self.add_place(field, (self.x - 1, self.y + 2))
        self.add_move = True
        self.add_place(field, (self.x + 1, self.y + 2))
        self.add_move = True
        self.add_place(field, (self.x - 1, self.y - 2))
        self.add_move = True
        self.add_place(field, (self.x + 1, self.y - 2))
        self.add_move = True
        self.add_place(field, (self.x - 2, self.y + 1))
        self.add_move = True
        self.add_place(field, (self.x + 2, self.y + 1))
        self.add_move = True
        self.add_place(field, (self.x - 2, self.y - 1))
        self.add_move = True
        self.add_place(field, (self.x + 2, self.y - 1))
        self.add_move = True


class Bishop(Figure):
    name = "bishop"

    def set_moves(self, field):
        self.atacks, self.moves = [], []
        self.add_move = True
        for x in range(self.x - 1, -1, -1):
            if not self.add_place(field, (x, self.y)):
                break
        self.add_move = True
        for x in range(self.x + 1, field.width):
            if not self.add_place(field, (x, self.y)):
                break
        self.add_move = True
        for y in range(self.y - 1, -1, -1):
            if not self.add_place(field, (self.x, y)):
                break
        self.add_move = True
        for y in range(self.y + 1, field.height):
            if not self.add_place(field, (self.x, y)):
                break


class Rook(Figure):
    name = "rook"

    def set_moves(self, field):
        self.atacks, self.moves = [], []
        self.add_move = True
        for k in range(1, min(self.x, self.y) + 1):
            if not self.add_place(field, (self.x - k, self.y - k)):
                break
        self.add_move = True
        for k in range(1, min(field.width - self.x, self.y) + 1):
            if not self.add_place(field, (self.x + k, self.y - k)):
                break
        self.add_move = True
        for k in range(1, min(field.width - self.x, field.height - self.y) + 1):
            if not self.add_place(field, (self.x + k, self.y + k)):
                break
        self.add_move = True
        for k in range(1, min(self.x, field.height - self.y) + 1):
            if not self.add_place(field, (self.x - k, self.y + k)):
                break

       
class Queen(Figure):
    name = "queen"

    def set_moves(self, field):
        self.atacks, self.moves = [], []
        self.add_move = True
        for x in range(self.x - 1, -1, -1):
            if not self.add_place(field, (x, self.y)):
                break
        self.add_move = True
        for x in range(self.x + 1, field.width):
            if not self.add_place(field, (x, self.y)):
                break
        self.add_move = True
        for y in range(self.y - 1, -1, -1):
            if not self.add_place(field, (self.x, y)):
                break
        self.add_move = True
        for y in range(self.y + 1, field.height):
            if not self.add_place(field, (self.x, y)):
                break
        self.add_move = True
        for k in range(1, min(self.x, self.y) + 1):
            if not self.add_place(field, (self.x - k, self.y - k)):
                break
        self.add_move = True
        for k in range(1, min(field.width - self.x, self.y) + 1):
            if not self.add_place(field, (self.x + k, self.y - k)):
                break
        self.add_move = True
        for k in range(1, min(field.width - self.x, field.height - self.y) + 1):
            if not self.add_place(field, (self.x + k, self.y + k)):
                break
        self.add_move = True
        for k in range(1, min(self.x, field.height - self.y) + 1):
            if not self.add_place(field, (self.x - k, self.y + k)):
                break


class Warrior(Figure):
    name = "warrior"

    def set_moves(self, field):
        self.atacks, self.moves = [], []
        for kx in (-1, 1):
            self.add_move = True
            self.add_place(field, (self.x + kx, self.y))

        k = 1 if self.color == FIGURE_COLORS[1] else -1
        self.add_move = True
        self.add_place(field, (self.x, self.y - k))
        self.add_move = True
        for ky in range(2 * k, 4 * k, k):
            if not self.add_place(field, (self.x, self.y + ky)):
                break


class Spearman(Figure):
    name = "spearman"
        
    def add_place(self, field, cell):
        if cell[0] not in range(0, field.width) or cell[1] not in range(0, field.height):
            return False
        x, y = cell
        if field.field[y][x] == 0:
            self.moves.append(cell)
            return True
        return False

    def add_atack(self, field, cell):
        if cell[0] not in range(0, field.width) or cell[1] not in range(0, field.height):
            return False
        x, y = cell
        if field.field[y][x] != 0 and field.field[y][x] != 'x' and field.field[y][x].color != self.color:
            self.atacks.append(cell)
            self.moves.append(cell)
            return True
        return False

    def set_moves(self, field):
        self.atacks, self.moves = [], []
        for kx in range(-1, 2):
            for ky in range(-1, 2):
                if kx == ky == 0:
                    pass
                else:
                    self.add_place(field, (self.x + kx, self.y + ky))
        for kx in (-2, 2):
            self.add_atack(field, (self.x + kx, self.y))
        for ky in (-2, 2):
            self.add_atack(field, (self.x, self.y + ky))