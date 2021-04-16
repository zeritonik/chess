from field import Field
from figures import King
from values import *
import pygame
import socket


class Game:
    def __init__(self, variant=0, color=0):
        self.field = Field(variant)
        self.field.init_field()
        self.color = color

        width = self.field.width * BLOCK + 2 * LR
        height = self.field.height * BLOCK + 2 * TB
        self.window = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()

        self.field.create_field_image()
        self.window.fill(BG)

    def game_cycle(self):
        self.choosen = None
        self.field.set_figures_moves()
        self.game = True
        while self.game:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print(f"{self.color ^ 1} - winner!")
                    self.game = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.on_click(event.pos)
            self.window.blit(self.field.image, (LR, TB))

            if self.choosen:
                self.choosen.show_moves(self.window)

            self.window.blit(self.field.figures, (LR, TB))

            pygame.display.flip()

        pygame.quit()

    def check_king(self):
        pos = self.field.kings[self.color].x, self.field.kings[self.color].y
        enemies = self.field.get_enemy_figures(FIGURE_COLORS[self.color])
        atacks = self.field.get_atacks(enemies)
        if pos in atacks:
            return True
        return False

    def check_draw(self):
        figures = self.field.get_team_figures(FIGURE_COLORS[self.color])
        for figure in figures:
            if figure.moves:
                break
        else:
            if not self.check_king():
                print("DRAW!")
                self.game = False
            else:
                king = self.field.kings[self.color]
                self.field.field[king.y][king.x] = 0

    def check_win(self):
        figures = self.field.get_team_figures(FIGURE_COLORS[self.color])
        for figure in figures:
            if type(figure) == King:
                return 
        print(f"Player {self.color ^ 1} - winner!")
        self.game = False
        
    def on_click(self, pos):
        cell = self.field.get_cell(*pos)
        if cell != None:
            if self.choosen == None:
                self.set_choosen(cell)
                return 
            res = self.choosen.move(cell, self.field)
            if res:
                self.change_turn()
        self.choosen = None

    def set_choosen(self, cell):
        figure = self.field.get_figure(cell)
        if figure and figure.color != FIGURE_COLORS[self.color]:
            self.choosen = None
        else:
            self.choosen = figure

    def change_turn(self):
        self.color ^= 1
        self.field.set_figures_moves()
        if self.check_king():
            print("King under atack!")
        self.check_draw()
        self.check_win()
        self.field.create_figures_image()


class OnlineGame(Game):
    def __init__(self, ip=None):
        self.addr = (ip, 8080)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.addr)
        variant, color = self.sock.recv(128)
        self.side_color = color
        super().__init__(variant, color)
        if self.side_color == 1:
            self.color ^= 1
        print("Connected to " + ip)

    def game_cycle(self):
        self.choosen = None
        self.field.set_figures_moves()
        self.game = True
        while self.game:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sock.send(b"disconnect")
                    self.game = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.color == self.side_color:
                        self.on_click(event.pos)
            self.window.blit(self.field.image, (LR, TB))
            if self.choosen:
                self.choosen.show_moves(self.window)
            self.window.blit(self.field.figures, (LR, TB))
            pygame.display.flip()

            if self.color != self.side_color and self.game:
                self.get_data()

        pygame.quit()
        self.sock.send(b"end")

    def get_data(self):
        data = self.sock.recv(256)
        if data.decode() == "disconnect":
            print(1)
            print("Opponent disconnected!")
            print("You are winner!")
            self.game = False
        else:
            f_cell = data[0], data[1]
            figure = self.field.get_figure(f_cell)
            m_cell = data[2], data[3]
            figure.move(m_cell, self.field)
            self.change_turn()

    def check_win(self):
        figures = self.field.get_team_figures(FIGURE_COLORS[self.color])
        for figure in figures:
            if type(figure) == King:
                return
        if self.color == self.side_color:
            print("You are loser!")
        else:
            print("You are winner!")
        self.game = False
            

    def on_click(self, pos):
        cell = self.field.get_cell(*pos)
        if cell != None:
            if self.choosen == None:
                self.set_choosen(cell)
                return 
            was = self.choosen.x, self.choosen.y
            res = self.choosen.move(cell, self.field)
            if res:
                self.sock.send(bytes([was[0], was[1], cell[0], cell[1]]))
                self.change_turn()
        self.choosen = None


print("""Choose game type:
1. On one computer
2. Online
""")
choose = input()
if choose == '1':
    color = int(input("color (0/1): "))
    variant = int(input("choose_field: "))
    game = Game(variant, color)
    game.game_cycle()
elif choose == '2':
    ip = input("connect ip: ")
    game = OnlineGame(ip=ip)
    if game.sock.recv(256).decode() == "start":
        game.game_cycle()
    del game
input()