import pygame
from pygame.locals import *

# Inicialização geral
pygame.init()
clock = pygame.time.Clock()

# Tela de jogo
screen_width = 304
screen_height = 208
screen = pygame.Surface((screen_width, screen_height))

WINDOW_SIZE = (screen_width * 3, screen_height * 3)
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('Platformer')

# Variáveis gerais
run = True

# Game Map
grass_image = pygame.image.load('assets/grass.png').convert()
dirt_image = pygame.image.load('assets/dirt.png').convert()
tile_size = 16

game_map = [['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                           ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                           ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                           ['0', '0', '0', '0', '0', '0', '0', '0', '2', '2', '2', '2', '0', '0', '0', '0', '0', '0', '0'],
                           ['0', '0', '0', '0', '0', '2', '2', '2', '1', '1', '1', '1', '2', '2', '0', '0', '0', '0', '0'],
                           ['0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                           ['2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'],
                           ['1', '2', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '2', '2'],
                           ['1', '1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '2', '1', '1'],
                           ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'],
                           ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'],
                           ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1'],
                           ['1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1', '1']]

# Player
player_image = pygame.image.load('assets/player.png').convert()
player_image.set_colorkey((255, 255, 255))
player_rect = player_image.get_rect()
player_rect.topleft = (50, 50)
player_y_momentum = 0
moving_right, moving_left = False, False
player_collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}

# Retorna lista com todos rects do mapa que colidiu com o player
def collision_test(player_rect, tile_rects):
    hit_list = []
    for tile_rect in tile_rects:
        if player_rect.colliderect(tile_rect):
            hit_list.append(tile_rect)

    return hit_list

# Movimento e colisões
def move(rect, movement, tile_rects):
    collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}

    # Movimento e colisões horizontais
    rect.x += movement[0]
    hit_list = collision_test(rect, tile_rects)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collisions['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collisions['left'] = True

    # Movimento e colisões verticais
    rect.y += movement[1]
    hit_list = collision_test(rect, tile_rects)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collisions['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collisions['top'] = True

    return rect, collisions

# Loop principal
while run:

    # Controle de eventos
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP and player_collisions['bottom']:
                player_y_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    # Background
    screen .fill((146, 244, 255))

    # Desenho de todos tiles do mapa com base nas posições da matriz game_map
    tile_rects = []
    for row_index, row in enumerate(game_map):
        for tile_index, tile in enumerate(row):
            if tile == '1':
                screen.blit(dirt_image, (tile_index * tile_size, row_index * tile_size))
            if tile == '2':
                screen.blit(grass_image, (tile_index * tile_size, row_index * tile_size))
            if tile != '0':
                tile_rects.append(pygame.Rect(tile_index * tile_size, row_index * tile_size, tile_size, tile_size))

    # Movimentação do player
    player_movement = [0, 0]

    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2

    # Gravidade do player
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    # Limite da velocidade de queda do player
    if player_y_momentum >= 3:
        player_y_momentum = 3

    # Aplicar movimentação e colisões
    player_rect, player_collisions = move(player_rect, player_movement, tile_rects)

    # Corrige queda do player caso colida com teto ou chão
    if player_collisions['bottom'] or player_collisions['top']:
        player_y_momentum = 1

    # Desenha player
    screen.blit(player_image, player_rect)

    # Update da tela de jogo
    window.blit(pygame.transform.scale(screen, WINDOW_SIZE), (0, 0))
    pygame.display.update()
    clock.tick(60)

pygame.quit() # Finalização geral
