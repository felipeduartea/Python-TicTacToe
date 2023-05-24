import copy
import sys
import pygame
import numpy as np
import random

from constants import *

#Linhas para usar o PYGAME
pygame.init
screen = pygame.display.set_mode((WIDHT,HEIGHT))
pygame.display.set_caption("Jogo da Velha com IA")
screen.fill(BG_COLOR)


class Board:

    def __init__(self):
        self.squares = np.zeros((ROWS, COLS))

        self.empty_sqrs = self.squares
        self.mark_sqrs = 0

    def final_state(self, show = False):
        '''
        @return 0 se ainda não tiver nenhum vencedor (-)
        @return 1 se o jogador 1 ganhar (X)
        @return 2 se o jogador 2 ganhar (O)
        '''

        #vitoria vertical
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQSIZE + SQSIZE//2, 20)
                    fPos = (col * SQSIZE + SQSIZE//2, HEIGHT-20)
                    pygame.draw.line(screen,color,iPos,fPos, CROSS_WIDHT)
                return self.squares[0][col]

        #vitoria horizontal
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDHT - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDHT)
                return self.squares[row][0]

        #vitoria diagonal descendente
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20,20)
                fPos = (WIDHT - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDHT)
            return self.squares[1][1]
        #vitoria diagonal ascendente
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDHT - 20,20)
                pygame.draw.line(screen, color, iPos, fPos,     CROSS_WIDHT)
            return self.squares[1][1]
        #sem vitória até o momento
        return 0

    def mark_sqr(self,row,col,player):
        self.squares[row][col] = player
        self.mark_sqrs += 1

    #fazendo com que cada quadrado só possa ser usado uma vez
    def empty_sqr(self,row,col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row,col):
                    empty_sqrs.append((row,col))

        return empty_sqrs

    def isfull(self):
        return self.mark_sqrs == 9

    def isempty(self):
        return self.mark_sqrs == 0

class AI:

    def __init__(self, level=1, player = 2):
        self.level = level
        self.player = player

    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        index = random.randrange(0, len(empty_sqrs))

        return empty_sqrs[index]


    def minimax(self,board,maximizing):
        #casos terminais
        case = board.final_state()

        #p1 ganha
        if case == 1:
            return 1, None
        #p2 ganha
        if case == 2:
            return -1, None
        #empate
        elif board.isfull():
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row,col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row,col,self.player)
                eval = self.minimax(temp_board,True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row,col)

            return min_eval, best_move

    def eval(self, main_board):
        if self.level == 0:
            #escolha aleatória
            eval = "random"
            move = self.rnd(main_board)
        else:
            #minimax (inteligente)
            eval, move = self.minimax(main_board, False)

        print(f"IA escolheu marcar o quadrado {move} com uma avalição de {eval}")
        return move #row, col
class Game:

    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1 # 1 = X e 2 = 0
        self.gamemode = "ai"
        self.running = True
        self.show_lines()

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()
    def show_lines(self):
        #verticais
        pygame.draw.line(screen,LINE_COLOR, (SQSIZE,0),(SQSIZE,HEIGHT),LINE_WIDHT)
        pygame.draw.line(screen, LINE_COLOR, (WIDHT - SQSIZE, 0), (WIDHT - SQSIZE, HEIGHT), LINE_WIDHT)

        #horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, SQSIZE), (WIDHT, SQSIZE), LINE_WIDHT)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDHT, HEIGHT - SQSIZE), LINE_WIDHT)

    #mudar o jogador da vez
    def next_turn(self):
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        self.gamemode = "ai" if self.gamemode == "pvp" else "pvp"

    def isover(self):
        return self.board.final_state(show = True) != 0 or self.board.isfull()

    def draw_fig(self,row,col):
        if self.player == 1:

            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDHT)

            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDHT)

        elif self.player == 2:
            center = (col * SQSIZE + SQSIZE//2, row * SQSIZE + SQSIZE//2)
            pygame.draw.circle(screen, CIRC_COLOR, center, RADIUS, CIRC_WIDHT)
def main():
    #criando o objeto
    game = Game()
    board = game.board
    ai = game.ai

#loop principal
    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                   # print(board.squares)

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_g:
                    game.change_gamemode()

                if event.key == pygame.K_0:
                    ai.level = 0

                if event.key == pygame.K_1:
                    ai.level = 1


            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQSIZE
                col = pos[0] // SQSIZE

                if board.empty_sqr(row,col) and game.running:
                    game.make_move(row,col)

                    if game.isover():
                        game.running = False


        if game.gamemode == "ai" and game.player == ai.player and game.running:
            #atualizar a tela
            pygame.display.update()
            #métodos da IA
            row, col = ai.eval(board)
            game.make_move(row, col)


        pygame.display.update()

main()