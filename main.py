import pygame
from pygame.locals import *
import random

# Inicialização geral
pygame.init()
clock = pygame.time.Clock()
# Mixer para sons
pygame.mixer.pre_init(44100, -16, 2, 512)

# Tela de jogo
screen_width = 304
screen_height = 208
screen = pygame.Surface((screen_width, screen_height))

WINDOW_SIZE = (screen_width * 3, screen_height * 3)
window = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('Platformer')

# Variáveis gerais
run = True
soundtrack = pygame.mixer.Sound("assets/soundtrack.wav") # Trilha sonora
soundtrack.play(-1, fade_ms=3000)

# Fps label
show_fps = False
fps_font = pygame.font.SysFont("freesans", 30)

# Backgrounds class
class Background(pygame.sprite.Sprite):
    def __init__(self, pos, size, color, parallax = 0):
        super().__init__()
        # Variáveis gerais do fundo
        self.pos = pos
        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
        self.parallax = parallax

    def update(self, scroll = [0, 0]):
        # Efeito parallax
        self.rect.topleft = self.pos # Reseta a posição

        # Aplica parallax
        self.rect.x -= scroll[0] * self.parallax
        self.rect.y -= scroll[1] * self.parallax

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        # Variáveis gerais do player
        self.image = image
        self.physics_rect = self.image.get_rect()
        self.physics_rect.topleft = pos
        self.rect = self.physics_rect.copy()
        self.movement = [0, 0]
        self.vertical_momentum = 0
        self.air_time = 0
        self.jump_sound = pygame.mixer.Sound("assets/jump.wav")
        self.walk_grass_sound = pygame.mixer.Sound("assets/walk_grass.wav")
        self.walk_grass_sound.set_volume(0.7)
        self.walk_dirt_sound= pygame.mixer.Sound("assets/walk_dirt.wav")
        self.walk_dirt_sound.set_volume(0.7)
        self.walk_sound_duration = 0
        # Variáveis de estado do player
        self.moving_right = False
        self.moving_left = False
        self.jumping = False
        self.jumped = False

    # Retorna toda colisão do player com a lista de tiles passada
    def collision_test(self, tile_rects):
        hit_list = []

        for tile in tile_rects:
            if self.physics_rect.colliderect(tile):
                hit_list.append(tile)

        return hit_list

    # Movimento e colisões
    def move(self, tile_rects):
        self.collisions = {'top': False, 'bottom': False, 'right': False, 'left': False}

         # Movimento e colisões horizontais
        self.physics_rect.x += self.movement[0]
        hit_list = self.collision_test(tile_rects)
        for tile in hit_list:
            if self.movement[0] > 0:
                self.physics_rect.right = tile.left
                self.collisions['right'] = True
            if self.movement[0] < 0:
                self.physics_rect.left = tile.right
                self.collisions['left'] = True

        # Movimento e colisões verticais
        self.physics_rect.y += self.movement[1]
        hit_list = self.collision_test(tile_rects)
        for tile in hit_list:
            if self.movement[1] > 0:
                self.physics_rect.bottom = tile.top
                self.collisions['bottom'] = True
            if self.movement[1] < 0:
                self.physics_rect.top = tile.bottom
                self.collisions['top'] = True

    def update(self, tiles_data, tile_rects, scroll):
        self.movement = [0, 0]

        # Movimento horizontal
        if self.moving_right:
            self.movement[0] += 2
        if self.moving_left:
            self.movement[0] -= 2

        # Pulo
        if self.jumping and self.air_time < 5 and not self.jumped:
            self.jump_sound.play()
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
            # Execute som de andar dependendo do tipo de chão que o player estiver andando
            if self.walk_sound_duration == 0 and self.movement[0] != 0:
                if not self.collisions['left'] and not self.collisions['right']:
                    if tiles_data[round(player.physics_rect.y / 16)  + 1][round(player.physics_rect.x / 16)] == '2':
                        self.walk_grass_sound.play()
                    elif tiles_data[round(player.physics_rect.y / 16)  + 1][round(player.physics_rect.x / 16)] == '1':
                        self.walk_dirt_sound.play()

                    self.walk_sound_duration += 1

            # Reseta tempo no ar e estado do pulo caso colida com o chão
            self.air_time = 0
            self.jumped = False
            self.vertical_momentum = 1
        else:
            # Tempo no ar caso esteja sem colidir com o chão, usado para o pulo e coyote time
            self.air_time += 1
            self.walk_sound_duration = 0

        # Tempo de duração do som de andar
        if self.walk_sound_duration > 0:
            self.walk_sound_duration += 1
            if self.walk_sound_duration >= 25:
                self.walk_sound_duration = 0

        # Atualiza rect para renderização adicionando o scroll
        self.rect = self.physics_rect.copy()
        self.rect.x -= scroll[0]
        self.rect.y -= scroll[1]

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
def generate_tiles(tiles_data, dirt_image, grass_image, tile_size, scroll):
    tile_rects = []

    for row_index, row in enumerate(tiles_data):
        for tile_index, tile in enumerate(row):
            if tile == '1':
                screen.blit(dirt_image, (tile_index * tile_size - scroll[0], row_index * tile_size - scroll[1]))
            if tile == '2':
                screen.blit(grass_image, (tile_index * tile_size - scroll[0], row_index * tile_size - scroll[1]))
            if row_index < 20:
                if tile != '0':
                    tile_rects.append(pygame.Rect(tile_index * tile_size, row_index * tile_size, tile_size, tile_size))

    return tile_rects

# Gerar texto e seu rect correspondente
def text(font, color, text):
    text_surface = font.render(text, 10, color)
    text_rect = text_surface.get_rect()

    return text_surface, text_rect

# Retorna scroll necessário para câmera seguir qualquer rect
def camera_follow(rect_to_follow, scroll, delay):
    scroll[1] += int((rect_to_follow.centery - scroll[1] - screen_height / 2) / delay)

    # Limites de câmera
    if rect_to_follow.centerx - screen_width / 2 <= 16:
            if scroll[0] == 15 or scroll[0] == 17:
                scroll[0] = 16
            if scroll[0] > 16:
                scroll[0] -= 2
            if scroll[0] < 16:
                scroll[0] += 2
    elif rect_to_follow.centerx + screen_width / 2 >= 592:
            if scroll[0] + screen_width == 591 or scroll[0] + screen_width == 593:
                scroll[0] = 592 - screen_width
            if scroll[0] + screen_width > 592:
                scroll[0] -= 2
            if scroll[0] + screen_width < 592:
                scroll[0] += 2
    else:
        scroll[0] += int((rect_to_follow.centerx - scroll[0] - screen_width / 2) / delay)

    return scroll

# Game Map
grass_image = pygame.image.load('assets/grass.png').convert()
dirt_image = pygame.image.load('assets/dirt.png').convert()
tile_size = 16
tiles_data = load_tiles_data('tiles_data.txt')
tile_rects = []

# Backgrounds
backgrounds = [[(140, 60), (70, 400), (9, 91, 85), 0.25],
                             [(280, 90), (50, 400), (9, 91, 85), 0.25],
                             [(100, 90), (100, 400), (14, 222,150), 0.5],
                             [(270, 130), (120, 400), (14, 222,150), 0.5]]
                             # pos, size, color, parallax, static

backgrounds_group = pygame.sprite.Group()
backgrounds_group.add(Background((0, 110), (304, 98), (7, 80, 75))) # Fundo estático
backgrounds_group.add(Background(i[0], i[1], i[2], i[3]) for i in backgrounds)

# Player
player_image = pygame.image.load('assets/player.png').convert()
player_image.set_colorkey((255, 255, 255))
player = Player(player_image, (288, 96))
player_group = pygame.sprite.GroupSingle(player)

# Camera
camera_scroll = [0, 0]
camera_delay = 10

# Loop principal
while run:

    # Controle de eventos
    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
        if event.type == KEYDOWN:
            # Altera o estado de exibição dos fps
            if event.key == K_f:
                show_fps = not show_fps
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

    # Backgrounds update e draw
    backgrounds_group.update(camera_scroll)
    backgrounds_group.draw(screen)

    # Gera o mapa
    tile_rects = generate_tiles(tiles_data, dirt_image, grass_image, tile_size, camera_scroll)

    # Player update e draw
    player_group.update(tiles_data, tile_rects, camera_scroll)
    player_group.draw(screen)

    # Scroll para a câmera seguir o player
    camera_scroll = camera_follow(player_group.sprite.physics_rect, camera_scroll, camera_delay)

    # Desenha a superfície do jogo ja redimensionada na tela
    window.blit(pygame.transform.scale(screen, WINDOW_SIZE), (0, 0))

    # Desenha os fps na tela se ativado
    if show_fps:
        fps = int(clock.get_fps())
        fps_label, fps_rect = text(fps_font, (0, 0, 0), str(fps))
        fps_rect.topright = (WINDOW_SIZE[0] - 15, 10)

        window.blit(fps_label, fps_rect)

    # Update da tela de jogo
    pygame.display.update()
    clock.tick(60)

pygame.quit() # Finalização geral
