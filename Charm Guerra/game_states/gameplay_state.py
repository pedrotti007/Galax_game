# game_states/gameplay_state.py

import pygame
from .map_manager import MapManager

class GameplayState:
    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Configurações do jogador
        self.player_pos = [100, screen_height - 100]  # Posição inicial mais adequada para side-scrolling
        self.player_speed = 5
        self.player_velocity_y = 0
        self.gravity = 0.8
        self.jump_force = -15
        self.is_jumping = False
        self.facing_right = True
        
        # Sistema de tiro
        self.bullets = []
        self.bullet_speed = 20  # Aumentado para tiros mais rápidos
        self.last_shot_time = 0
        self.shot_cooldown = 80  # Tempo entre tiros ainda menor
        
        # Configurações visuais dos projéteis
        self.bullet_size = 8  # Tamanho base do projétil
        self.bullet_trail_length = 3  # Quantidade de partículas de trail
        self.bullet_image = None
        try:
        # Você pode adicionar uma imagem para os tiros aqui
            # self.bullet_image = pygame.image.load('assets/images/bullet.png').convert_alpha()
            # self.bullet_image = pygame.transform.scale(self.bullet_image, (16, 16))
            pass
        except Exception:
            print("Usando visual padrão para os projéteis")
        self.aim_direction = [1, 0]  # [x, y] direção padrão (para frente)
        
        # Sistema de mapa
        self.map_manager = MapManager(screen_width, screen_height)
        self.map_manager.load_map(1)  # Carrega o mapa de teste
        
        # Camera/Scrolling
        self.camera_x = 0
        
        # Ajustar posição inicial do jogador para o ponto de spawn
        self.player_pos = list(self.map_manager.get_spawn_point())
        
        # Carregamento de assets
        self.player_image = None
        try:
            self.player_image = pygame.image.load('assets/images/player.png').convert_alpha()
            self.player_image = pygame.transform.scale(self.player_image, (50, 80))  # Ajustado para proporção mais adequada
        except Exception:
            print("Aviso: 'assets/images/player.png' não encontrado. Usando fallback de retângulo para o jogador.")
        
    def enter(self):
        print("Entrando no estado de Gameplay!")
        # Inicie a música do jogo aqui, se houver
        # pygame.mixer.music.load('assets/audio/game_music.mp3')
        # pygame.mixer.music.play(-1) # -1 para loop infinito

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game_manager.set_state('menu')
            elif (event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP) and not self.is_jumping:
                self.player_velocity_y = self.jump_force
                self.is_jumping = True

    def update(self):
        keys = pygame.key.get_pressed()
        
        # Movimento horizontal com WASD e setas
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_pos[0] -= self.player_speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_pos[0] += self.player_speed
            self.facing_right = True
            
        # Atualizar direção da mira
        self.aim_direction = [0, 0]
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.aim_direction[0] = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.aim_direction[0] = 1
            
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.aim_direction[1] = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.aim_direction[1] = 1
            
        # Se nenhuma tecla de direção está pressionada, manter tiro na horizontal
        if self.aim_direction == [0, 0]:
            self.aim_direction = [1 if self.facing_right else -1, 0]
            
        # Sistema de tiro automático
        if keys[pygame.K_x]:  # Verifica se X está sendo segurado
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time > self.shot_cooldown:
                # Criar novo projétil
                bullet_x = self.player_pos[0] + (50 if self.facing_right else 0)
                bullet_y = self.player_pos[1] + 40
                
                # Normalizar a direção do tiro
                magnitude = (self.aim_direction[0]**2 + self.aim_direction[1]**2)**0.5
                if magnitude == 0:
                    normalized_dir = [1 if self.facing_right else -1, 0]
                else:
                    normalized_dir = [
                        self.aim_direction[0] / magnitude,
                        self.aim_direction[1] / magnitude
                    ]
                
                self.bullets.append({
                    'pos': [bullet_x, bullet_y],
                    'direction_x': normalized_dir[0],
                    'direction_y': normalized_dir[1]
                })
                self.last_shot_time = current_time
            
        # Aplicar gravidade
        self.player_velocity_y += self.gravity
        self.player_pos[1] += self.player_velocity_y
        
        # Verificar colisão com plataformas
        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], 50, 80)
        for platform in self.map_manager.platforms:
            if player_rect.colliderect(platform['rect']):
                # Colisão por cima da plataforma
                if self.player_velocity_y > 0:
                    player_rect.bottom = platform['rect'].top
                    self.player_pos[1] = player_rect.y
                    self.player_velocity_y = 0
                    self.is_jumping = False
                # Colisão por baixo da plataforma
                elif self.player_velocity_y < 0:
                    player_rect.top = platform['rect'].bottom
                    self.player_pos[1] = player_rect.y
                    self.player_velocity_y = 0
        
        # Atualizar projéteis
        for bullet in self.bullets[:]:
            bullet['pos'][0] += self.bullet_speed * bullet['direction_x']
            bullet['pos'][1] += self.bullet_speed * bullet['direction_y']
            # Remover projéteis que saíram da tela
            if (bullet['pos'][0] < 0 or bullet['pos'][0] > self.screen_width or
                bullet['pos'][1] < 0 or bullet['pos'][1] > self.screen_height):
                self.bullets.remove(bullet)
        
        # Atualizar câmera (scrolling simples)
        target_x = self.player_pos[0] - self.screen_width // 3
        self.camera_x += (target_x - self.camera_x) * 0.1
        
        # Limitar o jogador à tela
        self.player_pos[0] = max(0, min(self.screen_width - 50, self.player_pos[0]))


    def draw(self, screen):
        # Fundo
        screen.fill((135, 206, 235))  # Céu azul claro
        
        # Aplicar offset da câmera em todos os elementos
        camera_offset = int(-self.camera_x)
        
        # Desenhar o mapa
        self.map_manager.draw(screen, camera_offset=camera_offset)
        
        # Desenhar projéteis com efeitos
        for bullet in self.bullets:
            # Posição atual do projétil
            current_x = int(bullet['pos'][0] + camera_offset)
            current_y = int(bullet['pos'][1])
            
            # Desenhar trilha do projétil
            for i in range(self.bullet_trail_length):
                trail_x = int(current_x - (bullet['direction_x'] * (i * 4)))
                trail_y = int(current_y - (bullet['direction_y'] * (i * 4)))
                trail_size = self.bullet_size - (i * 2)
                if trail_size > 0:
                    # Cor da trilha (amarelo para laranja)
                    trail_color = (255, 255 - (i * 60), 0)
                    pygame.draw.circle(screen, trail_color, (trail_x, trail_y), trail_size)
            
            # Desenhar o projétil principal
            if self.bullet_image:
                # Quando tivermos uma imagem para o projétil
                screen.blit(self.bullet_image, (current_x - 8, current_y - 8))
            else:
                # Efeito de brilho (círculos sobrepostos)
                pygame.draw.circle(screen, (255, 255, 200), (current_x, current_y), self.bullet_size + 2)  # Brilho externo
                pygame.draw.circle(screen, (255, 255, 0), (current_x, current_y), self.bullet_size)  # Projétil principal
        
        # Desenhar jogador
        if self.player_image:
            # Virar a imagem se necessário
            image = pygame.transform.flip(self.player_image, not self.facing_right, False)
            screen.blit(image, (self.player_pos[0] + camera_offset, self.player_pos[1]))
        else:
            pygame.draw.rect(screen, (255, 0, 0), 
                           (self.player_pos[0] + camera_offset, self.player_pos[1], 50, 80))
        
        # HUD
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render("ESPAÇO para pular, X para atirar, ESC para menu", True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
