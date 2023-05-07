import pygame
import random
import os

pygame.font.init()


s_width = 950
s_height = 750
play_width = 300  
play_height = 600  
block_size = 30

top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

#Şekil formatları

S = [
    [".....", ".....", "..00.", ".00..", "....."],
    [".....", "..0..", "..00.", "...0.", "....."],
]

Z = [
    [".....", ".....", ".00..", "..00.", "....."],
    [".....", "..0..", ".00..", ".0...", "....."],
]

I = [
    ["..0..", "..0..", "..0..", "..0..", "....."],
    [".....", "0000.", ".....", ".....", "....."],
]

O = [[".....", ".....", ".00..", ".00..", "....."]]

J = [
    [".....", ".0...", ".000.", ".....", "....."],
    [".....", "..00.", "..0..", "..0..", "....."],
    [".....", ".....", ".000.", "...0.", "....."],
    [".....", "..0..", "..0..", ".00..", "....."],
]

L = [
    [".....", "...0.", ".000.", ".....", "....."],
    [".....", "..0..", "..0..", "..00.", "....."],
    [".....", ".....", ".000.", ".0...", "....."],
    [".....", ".00..", "..0..", "..0..", "....."],
]

T = [
    [".....", "..0..", ".000.", ".....", "....."],
    [".....", "..0..", "..00.", "..0..", "....."],
    [".....", ".....", ".000.", "..0..", "....."],
    [".....", "..0..", ".00..", "..0..", "....."],
]

#Şekil renkleri
shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255, 0),
    (255, 0, 0),
    (0, 255, 255),
    (255, 255, 0),
    (255, 165, 0),
    (0, 0, 255),
    (128, 0, 128),
]


class Piece(object):
    rows = 20  #y koordinatı
    columns = 10  #x koordinatı

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  


def pieces(current_piece,helper_piece,next_piece):
    if helper_piece is None:
        helper_piece = current_piece
        current_piece = next_piece
        next_piece = get_shape()
    else:
        helper_piece,current_piece = current_piece,helper_piece
    return current_piece, helper_piece, next_piece


def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                c = locked_positions[(j, i)]
                grid[i][j] = c
    return grid


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == "0":
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions

#Oyun alanındaki belirli konumlara uygun bir şekilde yerleştirilip yerleştirilemeyeceğini kontrol etme
def valid_space(shape, grid):
    accepted_positions = [
        [(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)
    ]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True

#Şeklin tahtadaki değerini hesapla
def space_value(shape,surface):
    last_pos = [[(i,j) for j in range(10) if surface[i][j] == (255,255,255)] for i in range(20)]
    last_pos = [j for sub in last_pos for j in sub]
    format = convert_shape_format(shape)
    for pos in format:
        if pos not in last_pos:
            if pos[1] > -1:
                return False
    return True



def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape() -> Piece:
    global shapes, shape_colors

    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(text: str, size: int, color: tuple, surface):
    font = pygame.font.SysFont("Bauhaus 93", size, bold= False)
    label = font.render(text, 1, color)

    surface.blit(
        label,
        (
            top_left_x + play_width / 2 - (label.get_width() / 2),
            top_left_y + play_height / 2 - label.get_height() / 2,
        ),
    )

#Izgara çizme
def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(
            surface, (128, 128, 128), (sx, sy + i * 30), (sx + play_width, sy + i * 30)
        )  
        for j in range(col):
            pygame.draw.line(
                surface,
                (128, 128, 128),
                (sx + j * 30, sy),
                (sx + j * 30, sy + play_height),
            )  

#Satır silme
def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc

#Seçilen şekil
def hold_block(shape, surface):
    font = pygame.font.SysFont("Bauhaus 93", 30)
    label = font.render("Seçilen Parça", 1, (255, 255, 255))
    sx = top_left_x - play_width + 50
    sy = top_left_y + play_height / 2 - 275

    if shape is not None:
        shape_format = shape.shape[shape.rotation % len(shape.shape)]

        for i, draw in enumerate(shape_format):
            row = list(draw)
            for j, column in enumerate(row):
                if column == "0":
                    pygame.draw.rect(
                        surface,
                        shape.color,
                        (
                            sx + j * block_size,
                            sy + i * block_size,
                            block_size,
                            block_size,
                        ),
                        0,
                    )

        surface.blit(label, (sx + 10, sy - 30))

#Sonraki şekli gösterme
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont("Bauhaus 93", 30)
    label = font.render("Sonraki Sekil", 1, (255, 255, 255))

    sx = top_left_x + play_width + 25
    sy = top_left_y + play_height / 2 - 74
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == "0":
                pygame.draw.rect(
                    surface, shape.color, (sx + j * 30, sy + i * 30, 30, 30), 0
                )

    surface.blit(label, (sx + 20, sy - 100))

#Pencere oluşturma ve pencerede açıklama yapma
def draw_window(surface, score=0, last_score=0):
    surface.fill((61,145,64))
    font = pygame.font.SysFont("Bauhaus 93", 60)
    label = font.render("TETRIS", 1, (255, 255, 255))
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    font2 = pygame.font.SysFont("Bauhaus 93", 20)
    label2 = font2.render("Skor: " + str(score), 1, (255, 255, 255))

    sx = top_left_x - 270
    sy = top_left_y + 40
    surface.blit(label2, (sx - 20, sy + 160))

    label3 = font2.render('Yüksek Skor: ' + highest_score(),1,(255,255,255))
    sx = top_left_x - 270
    sy = top_left_y + 60

    surface.blit(label3,(sx - 20, sy + 160))

    label4 = font2.render('Yukarı Tusu: Format degistirme',1,(255,255,255))
    sx = top_left_x - 270
    sy = top_left_y + 100

    surface.blit(label4,(sx - 20, sy + 160))

    label5 = font2.render('Asagı Tusu: Hızlı Indirme',1,(255,255,255))
    sx = top_left_x - 270
    sy = top_left_y + 120

    surface.blit(label5,(sx - 20, sy + 160))

    label6 = font2.render('Sol Tusu: Sola Hareket Ettirme',1,(255,255,255))
    sx = top_left_x - 270
    sy = top_left_y + 140

    surface.blit(label6,(sx - 20, sy + 160))

    label7 = font2.render('Sag Tusu: Saga Hareket Ettirme',1,(255,255,255))
    sx = top_left_x - 270
    sy = top_left_y + 160

    surface.blit(label7,(sx - 20, sy + 160))

    label8 = font2.render('Z Tusu: Yukarı Hareket Ettirme',1,(255,255,255))
    sx = top_left_x - 270
    sy = top_left_y + 180

    surface.blit(label8,(sx - 20, sy + 160))

    label9 = font2.render('Bosluk Tusu: Direkt Indirme',1,(255,255,255))
    sx = top_left_x - 270
    sy = top_left_y + 200

    surface.blit(label9,(sx - 20, sy + 160))

    label10 = font2.render('X Tusu: Tutma/Bırakma',1,(255,255,255))
    sx = top_left_x - 270
    sy = top_left_y + 220

    surface.blit(label10,(sx - 20, sy + 160))

    label11 = font2.render('Her x tusuna basıldıgında sekil',1,(255,255,255))
    sx = top_left_x - 270
    sy = top_left_y + 280

    surface.blit(label11,(sx - 20, sy + 160))

    label12 = font2.render('tutuldukça oyun hızlanır !!',1,(255,255,255))
    sx = top_left_x - 270
    sy = top_left_y + 300

    surface.blit(label12,(sx - 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                surface,
                grid[i][j],
                (top_left_x + j * 30, top_left_y + i * 30, 30, 30),
                0,
            )

    draw_grid(surface, 40, 10)
    pygame.draw.rect(
        surface, (0, 255, 0), (top_left_x, top_left_y, play_width, play_height), 5
    )


def main():
    global grid
    last_score = highest_score()
    locked_positions = {}  
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    helper_piece = None
    hold = False
    clock = pygame.time.Clock()
    fall_time = 0
    level_time = 0
    fall_speed = 0.27
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 4:
            level_time = 0
            if fall_speed > 0.15:
                fall_speed -= 0.005

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()
            #Tuş atamaları
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation = current_piece.rotation + 1 % len(
                        current_piece.shape
                    )
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(
                            current_piece.shape
                        )

                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    print(convert_shape_format(current_piece))

                if event.key == pygame.K_x:
                    if not hold:
                        current_piece, helper_piece, next_piece = pieces(current_piece, helper_piece, next_piece)
                        current_piece.x, current_piece.y = 5, 0
                        hold = True
                        fall_speed -= 0.020 #şekli tuttuktan sonraki hızlanması
                if event.key == pygame.K_z:
                    while space_value(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            hold = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, score)
        draw_next_shape(next_piece, win)
        hold_block(helper_piece,win)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False
            update_score(score)
    #Oyunu kaybedince gelen ekran
    draw_text_middle("!! KAYBETTIN !!", 40, (255, 255, 255), win)
    pygame.display.update()
    pygame.time.delay(3000)#Oyun bittikten 3 saniye sonra tekrar başlar

#Menü tasarımı
def main_menu():
    run = True
    while run:
        win.fill((31,31,31))
        pic = pygame.image.load(
            os.path.abspath("Tetris/static/picture/beykent_logo.png")#os kütüphanesi
        )
        lx = top_left_x - 625
        ly = top_left_y - 445
        win.blit(pic, (lx + 270, ly + 150))
        draw_text_middle("Herhangi bir tusa basın...", 50, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

#Skor güncelleme
def update_score(nscore):
    score = highest_score()
    with open("score.txt", "w") as f:
        if int(score) > nscore:
            f.write(str(score))
        else:
            f.write(str(nscore))

#Yüksek skoru txt dosyasında tutma ve txt dosyasından veriyi alma
#Yüksek skoru geçtikten sonra oyun tekrar başladığında yüksek skor güncellenir
def highest_score():
    with open(os.path.abspath("score.txt"), "r") as f:
        lines = f.readlines()
        score = lines[0].strip()
    return score


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption("Tetris Oyunu")#Açılan pencereyi adlandırma
icon = pygame.image.load(
    os.path.abspath("Tetris/static/picture/beykent_logo.png")#Açılan pencereye ikon ekleme
    )
pygame.display.set_icon(icon)

main_menu()
