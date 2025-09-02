# game_states/gameplay_state.py

import pygame
from .map_manager import MapManager

class GameplayState:
    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height

        # --- NOVO: Superfície de gameplay para a escala ---
        self.gameplay_surface = pygame.Surface((self.screen_width, self.screen_height))
        
        # Configurações do jogador
        self.player_rect_size = (50, 80) # Tamanho LÓGICO do jogador
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
        self.player_image_original = None # Imagem base em alta resolução
        self.player_image_hires = None # Versão reescalada para a tela final
        try:
            self.player_image_original = pygame.image.load('assets/images/player.png').convert_alpha()
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
                bullet_x = self.player_pos[0] + (self.player_rect_size[0] if self.facing_right else 0)
                bullet_y = self.player_pos[1] + (self.player_rect_size[1] / 2)
                
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
        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], self.player_rect_size[0], self.player_rect_size[1])
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
        self.player_pos[0] = max(0, min(self.screen_width - self.player_rect_size[0], self.player_pos[0]))


    def draw(self, screen):
        # --- LÓGICA DE DESENHO ESCALADO ---
        # 1. Desenha todos os elementos do jogo na superfície pequena (gameplay_surface)
        
        # Fundo da gameplay
        self.gameplay_surface.fill((135, 206, 235))  # Céu azul claro
        
        # Aplicar offset da câmera em todos os elementos
        camera_offset = int(-self.camera_x)
        
        # Desenhar o mapa
        self.map_manager.draw(self.gameplay_surface, camera_offset=camera_offset)
        
        # Desenhar projéteis com efeitos
        for bullet in self.bullets:
            # Posição atual do projétil
            current_x = int(bullet['pos'][0] + camera_offset) # A posição já é relativa à câmera
            current_y = int(bullet['pos'][1])
            
            # Desenhar trilha do projétil
            for i in range(self.bullet_trail_length):
                trail_x = int(current_x - (bullet['direction_x'] * (i * 4))) # O offset da câmera já está em current_x
                trail_y = int(current_y - (bullet['direction_y'] * (i * 4))) # O eixo Y não tem câmera
                trail_size = self.bullet_size - (i * 2)
                if trail_size > 0:
                    # Cor da trilha (amarelo para laranja)
                    trail_color = (255, 255 - (i * 60), 0)
                    pygame.draw.circle(self.gameplay_surface, trail_color, (trail_x, trail_y), trail_size)
            
            # Desenhar o projétil principal
            if self.bullet_image:
                # Quando tivermos uma imagem para o projétil
                self.gameplay_surface.blit(self.bullet_image, (current_x - 8, current_y - 8))
            else:
                # Efeito de brilho (círculos sobrepostos)
                pygame.draw.circle(self.gameplay_surface, (255, 255, 200), (current_x, current_y), self.bullet_size + 2)  # Brilho externo
                pygame.draw.circle(self.gameplay_surface, (255, 255, 0), (current_x, current_y), self.bullet_size)  # Projétil principal
        
        # 2. Escala a superfície pequena para a tela final. `transform.scale` cria o efeito pixelado.
        final_screen_size = screen.get_size()
        scaled_surface = pygame.transform.scale(self.gameplay_surface, final_screen_size)
        screen.blit(scaled_surface, (0, 0))

        # 3. DESENHA O JOGADOR EM ALTA RESOLUÇÃO (por cima da tela escalada)
        # Calcula os fatores de escala
        scale_x = final_screen_size[0] / self.screen_width
        scale_y = final_screen_size[1] / self.screen_height

        # Prepara a imagem de alta resolução do jogador na primeira vez
        if self.player_image_original and self.player_image_hires is None:
            hires_size = (int(self.player_rect_size[0] * scale_x), int(self.player_rect_size[1] * scale_y))
            self.player_image_hires = pygame.transform.scale(self.player_image_original, hires_size)

        # Calcula a posição final do jogador na tela
        player_screen_x_float = (self.player_pos[0] + camera_offset) * scale_x
        player_screen_y_float = self.player_pos[1] * scale_y

        if self.player_image_hires:
            image_to_draw = pygame.transform.flip(self.player_image_hires, not self.facing_right, False)
            # Arredonda a posição final para o pixel mais próximo para evitar o tremor
            screen.blit(image_to_draw, (round(player_screen_x_float), round(player_screen_y_float)))
        else:
            # Fallback: desenha um retângulo em alta resolução
            player_screen_rect = pygame.Rect(round(player_screen_x_float), round(player_screen_y_float), self.player_rect_size[0] * scale_x, self.player_rect_size[1] * scale_y)
            pygame.draw.rect(screen, (255, 0, 0), player_screen_rect)


        # 4. Desenha o HUD diretamente na tela final para que o texto fique nítido.
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render("ESPAÇO para pular, X para atirar, ESC para menu", True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
