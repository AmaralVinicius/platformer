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

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        # Variáveis gerais do player
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.movement = [0, 0]
        self.vertical_momentum = 0
        self.air_time = 0
        # Variáveis de estado do player
        self.moving_right = False
        self.moving_left = False
        self.jumping = False
        self.jumped = False

    # Retorna toda colisão do player com a lista de tiles passada
    def collision_test(self, tile_rects):
        hit_list = []

        for tile in tile_rects:
            if self.rect.colliderect(tile):
                hit_list.append(tile)

        return hit_list

    # Movimento e colisões
    def move(self, tile_rects):
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}

         # Movimento e colisões horizontais
        self.rect.x += self.movement[0]
        hit_list = self.collision_test(tile_rects)
        for tile in hit_list:
            if self.movement[0] > 0:
                self.rect.right = tile.left
                self.collisions['right'] = True
            if self.movement[0] < 0:
                self.rect.left = tile.right
                self.collisions['left'] = True

        # Movimento e colisões verticais
        self.rect.y += self.movement[1]
        hit_list = self.collision_test(tile_rects)
        for tile in hit_list:
            if self.movement[1] > 0:
                self.rect.bottom = tile.top
                self.collisions['bottom'] = True
            if self.movement[1] < 0:
                self.rect.top = tile.bottom
                self.collisions['top'] = True

    def update(self, tile_rects):
        self.movement = [0, 0]

        # Movimento horizontal
        if self.moving_right:
            self.movement[0] += 2
        if self.moving_left:
            self.movement[0] -= 2

        # Pulo
        if self.jumping and self.air_time < 5 and not self.jumped:
            self.jumped = True
            self.vertical_momentum = -6

        # Movimento vertical (Gravidade)
        self.vertical_momentum += 0.3

        # Limite de velocidade de queda
        if self.vertical_momentum >= 5:
            self.vertical_momentum = 5

        # Aplica o momento vertical ao movimento do player
        self.movement[1] += self.vertical_momentum

        # Aplica o movimento e colisões
        self.move(tile_rects)

        # Corrige queda do player caso colida com teto ou chão
        if self.collisions['top']:
            self.vertical_momentum = 1

        if self.collisions['bottom']:
            self.vertical_momentum = 1
            # Reseta tempo no ar e estado do pulo caso colida com o chão
            self.air_time = 0
            self.jumped = False
        else:
            # Tempo no ar caso esteja sem colidir com o chão, usado para o pulo e coyote time
            self.air_time += 1

# Transforma os dados de um arquivo numa matriz para a função generate_tiles
def load_tiles_data(path):
    file = open(path, 'r')
    file_data = file.read()
    file.close()
    file_data = file_data.split('\n')
    tiles_data = []
    for row in file_data:
        tiles_data.append(list(row))

    return tiles_data

# Desenha os tiles do mapa e gera os rects para cada tile
def generate_tiles(tiles_data, dirt_image, grass_image, tile_size):
    tile_rects = []

    for row_index, row in enumerate(tiles_data):
        for tile_index, tile in enumerate(row):
            if tile == '1':
                screen.blit(dirt_image, (tile_index * tile_size, row_index * tile_size))
            if tile == '2':
                screen.blit(grass_image, (tile_index * tile_size, row_index * tile_size))
            if tile != '0':
                tile_rects.append(pygame.Rect(tile_index * tile_size, row_index * tile_size, tile_size, tile_size))

    return tile_rects

# Game Map
grass_image = pygame.image.load('assets/grass.png').convert()
dirt_image = pygame.image.load('assets/dirt.png').convert()
tile_size = 16

tiles_data = load_tiles_data('tiles_data.txt')

# Player
player_image = pygame.image.load('assets/player.png').convert()
player_image.set_colorkey((255, 255, 255))
player = Player(player_image, (96, 32))
player_group = pygame.sprite.GroupSingle(player)

# Loop principal
while run:

    # Controle de eventos
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            # Controle de estados do player
            if event.key == K_RIGHT:
                player_group.sprite.moving_right = True
            if event.key == K_LEFT:
                player_group.sprite.moving_left = True
            if event.key == K_UP:
                player_group.sprite.jumping = True
        if event.type == KEYUP:
            # Controle de estados do player
            if event.key == K_RIGHT:
                player_group.sprite.moving_right = False
            if event.key == K_LEFT:
                player_group.sprite.moving_left = False
            if event.key == K_UP:
                player_group.sprite.jumping = False

    # Background
    screen.fill((146, 244, 255))

    # Gera o mapa
    tile_rects = generate_tiles(tiles_data, dirt_image, grass_image, tile_size)

    # Player update e draw
    player_group.update(tile_rects)
    player_group.draw(screen)

    # Update da tela de jogo
    window.blit(pygame.transform.scale(screen, WINDOW_SIZE), (0, 0))
    pygame.display.update()
    clock.tick(60)
pygame.quit() # Finalização geral
