import os
import pygame
import random
import math
from .map_manager import MapManager
from .enemy import Enemy
from .collectible import Collectible

class GameplayState:
    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Configurações do jogador
        self.player_rect_size = (120, 220)  # Hitbox do jogador, um pouco menor para colisões mais permissivas
        self.player_visual_size = (225, 240)  # Tamanho visual do sprite (ex: 3x o tamanho original)
        self.player_speed = 0.8  # Aceleração do movimento
        self.max_speed = 12  # Velocidade máxima horizontal
        self.friction = 0.85  # Atrito para desaceleração suave
        self.gravity = 0.6  # Gravidade mais suave
        self.jump_force = -18  # Força de pulo mais suave
        self.wall_slide_speed = 2  # Velocidade de deslizamento na parede
        self.is_game_over = False
        self.player_velocity_x = 0  # Velocidade horizontal do jogador
        self.is_wall_sliding = False  # Estado de deslizamento na parede
        
        # --- Plataformas (usado para barricadas) ---
        self.platforms = []
        # # Parâmetros de geração de plataformas flutuantes (desativado)
        # self.min_platform_width = 150
        # self.max_platform_width = 300
        # self.min_gap_x = 300
        # self.max_gap_x = 500
        # self.min_gap_y = -80
        # self.max_gap_y = 80
        # self.platform_height = 20
        # self.last_platform_end_x = 0
        
        # --- NOVO: Chão Fixo ---
        self.ground_y = self.screen_height - 60
        self.ground_color = (139, 69, 19) # Cor de terra
        self.last_floating_platform_y = self.ground_y - 150 # Altura inicial para a primeira plataforma flutuante
        
        # Camera/Scrolling
        self.camera_x = 0
        self.camera_y = 0
        
        # Sistema de vida e munição
        self.max_health = 5  # Número máximo de corações
        self.hits_per_heart = 15
        self.player_hit_points = self.max_health * self.hits_per_heart
        self.current_health = self.max_health
        self.max_ammo = 60 # Munição máxima
        self.current_ammo = 60  # Munição inicial
        self.shot_cooldown = 300  # Aumentado para 300ms (era 80ms)
        self.collectibles = []  # Lista de coletáveis

        # Sistema de inimigos e trincheiras
        self.enemies = []
        self.enemy_hp = {}
        self.trenches = []  # Lista de trincheiras (cada uma é um grupo de inimigos)
        self.trench_positions = [] # Posições X das trincheiras
        self.enemy_bullets = []  # Lista de tiros dos inimigos
        self.num_trenches = 4  # Número de trincheiras antes do boss
        self.trench_width = 400  # Largura de cada trincheira
        self.trench_spacing = 6000  # Espaçamento entre trincheiras
        self.game_won = False  # Estado de vitória do jogo
        
        # Carregando texturas
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        # Carregar texturas dos corações e munição
        try:
            # Carregar corações
            self.full_heart_img = pygame.image.load(os.path.join(project_root, 'assets', 'images', 'suit_hearts.png')).convert_alpha()
            self.empty_heart_img = pygame.image.load(os.path.join(project_root, 'assets', 'images', 'suit_hearts_broken.png')).convert_alpha()
            heart_size = (30, 30)  # Tamanho dos corações na UI
            self.full_heart_img = pygame.transform.scale(self.full_heart_img, heart_size)
            self.empty_heart_img = pygame.transform.scale(self.empty_heart_img, heart_size)
            
            # Carregar símbolo de munição
            self.ammo_symbol_img = pygame.image.load(os.path.join(project_root, 'assets', 'images', 'municao_simbolo.png')).convert_alpha()
            self.ammo_symbol_img = pygame.transform.scale(self.ammo_symbol_img, (40, 40))  # Tamanho do símbolo de munição
        except Exception as e:
            print(f"Erro ao carregar imagens: {e}")
            self.full_heart_img = None
            self.empty_heart_img = None
            self.ammo_symbol_img = None
            
        # Estado inicial do jogador
        self.reset_player()
        
        # Carrega a textura do fundo
        try:
            self.background_image = pygame.image.load(os.path.join(project_root, 'assets', 'images', 'game_background.png')).convert()
            
            # Ajusta a altura para ser exatamente a altura da tela
            original_aspect = self.background_image.get_width() / self.background_image.get_height()
            new_height = screen_height
            new_width = int(new_height * original_aspect)  # Mantém a proporção original
            
            self.background_image = pygame.transform.scale(self.background_image, (new_width, new_height))
            
            # Guarda as dimensões do background para uso no scrolling
            self.background_width = new_width
            self.background_height = new_height
        except Exception as e:
            print(f"Erro ao carregar game_background.png: {e}")
            self.background_image = pygame.Surface((screen_width, screen_height))
            self.background_image.fill((135, 206, 235))  # Fallback para azul céu
            self.background_width = screen_width
            self.background_height = screen_height
            
        # Carrega a textura do player
        try:
            self.player_image = pygame.image.load(os.path.join(project_root, 'assets', 'images', 'player.png')).convert_alpha()
            self.player_image = pygame.transform.scale(self.player_image, self.player_visual_size)
        except Exception as e:
            print(f"Erro ao carregar player.png: {e}")
            self.player_image = None
        
        # --- PONTO DE MODIFICAÇÃO: Carregar som de tiro ---
        # Coloque seu arquivo de som em assets/sounds/laser_shot.wav
        self.shot_sound = None
        try:
            # Para efeitos sonoros, o formato .wav é mais recomendado por ser mais rápido de carregar.
            # Renomeie ou converta seu arquivo 'gun.mp3' para 'laser_shot.wav'.
            self.shot_sound = pygame.mixer.Sound(os.path.join(project_root, 'assets', 'sounds', 'laser_shot.wav'))
        except pygame.error as e:
            print(f"AVISO: Não foi possível carregar o som de tiro 'laser_shot.wav'. Verifique se o arquivo existe e está no formato correto. Erro: {e}")
        
        # Sistema de tiro
        self.bullets = []
        self.bullet_speed = 20  # Aumentado para tiros mais rápidos
        self.last_shot_time = 0
        self.shot_cooldown = 80  # Tempo entre tiros ainda menor
        
        # --- PONTO DE MODIFICAÇÃO: Posição da ponta da arma ---
        # Ajuste estes valores para alinhar o tiro perfeitamente com a sua arma.
        # As coordenadas (x, y) são relativas ao canto superior esquerdo do JOGADOR (player_pos).
        self.gun_barrel_offset_right = (150,128) # (x, y) quando virado para a direita
        self.gun_barrel_offset_left = (-10,128)  # (x, y) quando virado para a esquerda
        
        # Configurações visuais dos projéteis
        self.bullet_size = 4  # Tamanho base do projétil
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
        
        # Inicialização do estado atual do jogador
        self.player_pos = [100, screen_height - 100]  # Posição inicial temporária
        self.player_velocity_y = 0
        self.is_jumping = False
        self.facing_right = True
        

        
    def reset_player(self):
        """Reinicia a posição e estado do jogador e gera o mapa inicial."""
        self.platforms.clear()
        self.trench_positions.clear()
        # self._generate_initial_platforms() # Geração de plataformas flutuantes desativada
        
        # Posiciona o jogador no chão inicial
        self.player_pos = [200, self.ground_y - self.player_rect_size[1]]
        
        self.player_velocity_y = 0
        self.player_velocity_x = 0
        self.is_jumping = False
        self.is_wall_sliding = False
        self.facing_right = True
        self.is_game_over = False
        self.game_won = False
        self.camera_x = 0
        self.camera_y = 0
        
        # Resetar vida e munição
        self.player_hit_points = self.max_health * self.hits_per_heart
        self.current_health = self.max_health
        self.current_ammo = self.max_ammo
        
        # Limpar e recriar trincheiras e coletáveis
        self.enemies.clear()
        self.trenches.clear()
        self.enemy_bullets.clear()
        self.collectibles.clear()
        
        # Criar trincheiras
        for i in range(self.num_trenches):
            trench_x = 1000 + (i * self.trench_spacing)  # Primeira trincheira começa em x=1000
            self.trench_positions.append(trench_x)
            self._create_trench(trench_x)
    
    def _create_trench(self, x_pos):
        """Cria uma trincheira com inimigos em posições aleatórias."""
        num_enemies = random.randint(3, 6)  # Número aleatório de inimigos
        trench = []
        
        # Criar barricada
        barricade_height = self.player_rect_size[1] * 0.7
        barricade_width = 20
        platform = {
            'rect': pygame.Rect(x_pos, self.ground_y - barricade_height, barricade_width, barricade_height),
            'color': (100, 100, 100)  # Cor cinza para barricada
        }
        self.platforms.append(platform)
        
        # Posicionar inimigos
        for _ in range(num_enemies):
            is_flying = random.choice([True, False])
            
            if is_flying:
                # Posição aleatória no ar
                enemy_y = random.randint(100, int(self.screen_height * 0.6))
            else:
                # Posição no chão atrás da barricada
                enemy_y = self.ground_y - 140
                
            enemy_x = x_pos + random.randint(barricade_width, self.trench_width - 100)
            enemy = Enemy(enemy_x, enemy_y, is_flying)
            self.enemies.append(enemy)
            trench.append(enemy)
            self.enemy_hp[enemy] = 5  # Cada inimigo começa com 5 de vida
            
        self.trenches.append(trench)
        
    def _spawn_collectible(self, x, y):
        """Cria um coletável com 50% de chance de ser coração ou munição."""
        if random.random() < 0.5:  # 50% de chance para cada tipo
            collectible = Collectible(x, y, "heart")
        else:
            collectible = Collectible(x, y, "ammo")
        self.collectibles.append(collectible)

    # def _generate_initial_platforms(self):
    #     """Cria as plataformas flutuantes iniciais."""
    #     # Começa a gerar plataformas um pouco à frente do jogador
    #     self.last_platform_end_x = 400
    #     self.last_floating_platform_y = self.ground_y - 150

    #     # Gera algumas plataformas iniciais para preencher a tela
    #     while self.last_platform_end_x < self.screen_width * 2:
    #         self._generate_next_platform()

    # def _generate_next_platform(self):
    #     """Gera uma única plataforma nova à frente da última."""
    #     gap_x = random.randint(self.min_gap_x, self.max_gap_x)
    #     gap_y = random.randint(self.min_gap_y, self.max_gap_y)
    #     width = random.randint(self.min_platform_width, self.max_platform_width)
        
    #     new_x = self.last_platform_end_x + gap_x

    #     # Check if the new platform is too close to a trench
    #     for trench_x in self.trench_positions:
    #         safe_zone_start = trench_x - self.trench_width * 1.5
    #         safe_zone_end = trench_x + self.trench_width
    #         if (new_x < safe_zone_end) and (new_x + width > safe_zone_start):
    #             new_x = safe_zone_end
    #             break

    #     new_y = self.last_floating_platform_y + gap_y
        
    #     # Limita a altura das plataformas para não saírem muito da tela e ficarem acima do chão
    #     # --- CORREÇÃO: Força as plataformas a aparecerem mais para cima ---
    #     top_limit = self.screen_height * 0.1 # 30% do topo da tela
    #     bottom_limit = self.screen_height * 0.6 # Limite inferior para não ficarem muito baixas
    #     new_y = max(top_limit, min(new_y, bottom_limit))
        
    #     self.add_platform(new_x, new_y, width)
    #     self.last_platform_end_x = new_x + width
    #     self.last_floating_platform_y = new_y

    # def add_platform(self, x, y, width):
    #     """Adiciona uma nova plataforma à lista."""
    #     platform = {
    #         'rect': pygame.Rect(x, y, width, self.platform_height), # Altura reduzida
    #         'color': (0,0,0) # Cor Preta
    #     }
    #     self.platforms.append(platform)

    # def _manage_platforms(self):
    #     """Verifica se precisa gerar novas plataformas e remove as antigas."""
    #     # Gera novas plataformas se a última estiver entrando na tela
    #     if self.last_platform_end_x < self.camera_x + self.screen_width * 1.5:
    #         self._generate_next_platform()
            
    #     # Remove plataformas antigas que já saíram completamente da tela
    #     self.platforms = [p for p in self.platforms if p['rect'].right > self.camera_x - 200]
        
    def game_over(self):
        """Ativa o estado de game over"""
        self.is_game_over = True
        
    def enter(self):
        """Chamado quando o estado é ativado"""
        print("Entrando no estado de Gameplay!")
        self.reset_player()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.reset_player()  # Reseta o player antes de voltar ao menu
                self.game_manager.set_state('menu')
            elif event.key == pygame.K_r and self.is_game_over:
                self.reset_player()  # Reinicia o jogo quando R é pressionado no game over
            elif (event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP) and (not self.is_jumping or self.is_wall_sliding) and not self.is_game_over:
                self.player_velocity_y = self.jump_force
                self.is_jumping = True
                if self.is_wall_sliding:  # Pulo na parede
                    # Dar um pequeno impulso horizontal na direção oposta à parede
                    if self.facing_right:
                        self.player_velocity_x = -self.max_speed * 0.8
                    else:
                        self.player_velocity_x = self.max_speed * 0.8
                    self.is_wall_sliding = False
            elif event.key == pygame.K_F11:
                # Alternar entre fullscreen e windowed
                if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                    pygame.display.set_mode((1280, 720))
                else:
                    info = pygame.display.Info()
                    pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)

    def update(self):
        if self.is_game_over:
            return  # Não atualiza a gameplay se estiver em game over
            
        keys = pygame.key.get_pressed()
        
        # Movimento horizontal com WASD e setas com aceleração
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_velocity_x -= self.player_speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_velocity_x += self.player_speed
            self.facing_right = True
            
        # Limitar velocidade máxima
        self.player_velocity_x = max(-self.max_speed, min(self.max_speed, self.player_velocity_x))
        
        # Aplicar atrito
        if not (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            self.player_velocity_x *= self.friction
            
        # Atualizar posição horizontal
        self.player_pos[0] += self.player_velocity_x
            
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
        if keys[pygame.K_x] and self.current_ammo > 0:  # Verifica se X está sendo segurado e tem munição
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time > self.shot_cooldown:
                # --- PONTO DE MODIFICAÇÃO: Tocar som de tiro ---
                # Toca o som do tiro e ajusta o volume de acordo com as configurações
                if self.shot_sound:
                    self.shot_sound.set_volume(self.game_manager.volume)
                    self.shot_sound.play()

                # Criar novo projétil
                if self.facing_right:
                    offset_x, offset_y = self.gun_barrel_offset_right
                else:
                    offset_x, offset_y = self.gun_barrel_offset_left
                
                bullet_x = self.player_pos[0] + offset_x
                bullet_y = self.player_pos[1] + offset_y
                
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
                self.current_ammo -= 1  # Diminui a munição
                self.last_shot_time = current_time
            
        # Aplicar gravidade
        self.player_velocity_y += self.gravity
        self.player_pos[1] += self.player_velocity_y
        
        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], self.player_rect_size[0], self.player_rect_size[1])
        
        # 1. Verificar colisão com as plataformas flutuantes
        self.is_wall_sliding = False
        for platform in self.platforms:
            collidable_rect = platform['rect']
            if player_rect.colliderect(collidable_rect):
                overlap_left = player_rect.right - collidable_rect.left
                overlap_right = collidable_rect.right - player_rect.left
                overlap_top = player_rect.bottom - collidable_rect.top
                overlap_bottom = collidable_rect.bottom - player_rect.top
                
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                
                if min_overlap == overlap_top and self.player_velocity_y > 0:
                    player_rect.bottom = collidable_rect.top
                    self.player_pos[1] = player_rect.y
                    self.player_velocity_y = 0
                    self.is_jumping = False
                
                elif min_overlap == overlap_bottom and self.player_velocity_y < 0:
                    player_rect.top = collidable_rect.bottom
                    self.player_pos[1] = player_rect.y
                    self.player_velocity_y = 0
                
                elif min_overlap == overlap_left:
                    player_rect.right = collidable_rect.left
                    self.player_pos[0] = player_rect.x
                    if self.player_velocity_y > 0:
                        self.is_wall_sliding = True
                        self.player_velocity_y = min(self.player_velocity_y, self.wall_slide_speed)
                    self.player_velocity_x = 0
                
                elif min_overlap == overlap_right:
                    player_rect.left = collidable_rect.right
                    self.player_pos[0] = player_rect.x
                    if self.player_velocity_y > 0:
                        self.is_wall_sliding = True
                        self.player_velocity_y = min(self.player_velocity_y, self.wall_slide_speed)
                    self.player_velocity_x = 0
        
        if player_rect.bottom >= self.ground_y and self.player_velocity_y >= 0:
            player_rect.bottom = self.ground_y
            self.player_pos[1] = player_rect.y
            self.player_velocity_y = 0
            self.is_jumping = False
        
        # Atualizar projéteis do jogador e verificar colisões com inimigos
        for bullet in self.bullets[:]:
            bullet['pos'][0] += self.bullet_speed * bullet['direction_x']
            bullet['pos'][1] += self.bullet_speed * bullet['direction_y']

            bullet_collided = False
            for enemy in self.enemies[:]:
                enemy_rect = pygame.Rect(enemy.pos[0], enemy.pos[1], enemy.size[0], enemy.size[1])
                bullet_rect = pygame.Rect(bullet['pos'][0] - self.bullet_size, bullet['pos'][1] - self.bullet_size, self.bullet_size * 2, self.bullet_size * 2)
                if enemy_rect.colliderect(bullet_rect):
                    bullet_collided = True
                    self.enemy_hp[enemy] -= 1
                    if self.enemy_hp[enemy] <= 0:
                        self._spawn_collectible(enemy.pos[0], enemy.pos[1])
                        self.enemies.remove(enemy)
                        del self.enemy_hp[enemy]
                    break
            
            if bullet_collided:
                self.bullets.remove(bullet)
                continue

            margin = 200
            camera_view_left = self.camera_x - margin
            camera_view_right = self.camera_x + self.screen_width + margin

            if not (camera_view_left < bullet['pos'][0] < camera_view_right):
                self.bullets.remove(bullet)
            elif bullet['pos'][1] < -margin or bullet['pos'][1] > self.screen_height + margin:
                self.bullets.remove(bullet)

        # Atualizar inimigos
        current_time = pygame.time.get_ticks()
        for enemy in self.enemies:
            enemy.update(self.player_pos)
            bullet = enemy.shoot(self.player_pos, current_time)
            if bullet:
                self.enemy_bullets.append(bullet)

        # Atualizar projéteis inimigos
        for bullet in self.enemy_bullets[:]:
            bullet['pos'][0] += 15 * bullet['direction'][0]
            bullet['pos'][1] += 15 * bullet['direction'][1]
            
            bullet_rect = pygame.Rect(bullet['pos'][0] - 5, bullet['pos'][1] - 5, 10, 10)

            # Checar colisão com plataformas
            bullet_collided = False
            for platform in self.platforms:
                if platform['rect'].colliderect(bullet_rect):
                    self.enemy_bullets.remove(bullet)
                    bullet_collided = True
                    break
            if bullet_collided:
                continue

            if (bullet['pos'][0] < self.camera_x - 100 or 
                bullet['pos'][0] > self.camera_x + self.screen_width + 100 or
                bullet['pos'][1] < -100 or bullet['pos'][1] > self.screen_height + 100):
                self.enemy_bullets.remove(bullet)
                continue
            
            if bullet_rect.colliderect(player_rect):
                self.player_hit_points -= 1
                self.current_health = math.ceil(self.player_hit_points / self.hits_per_heart)
                self.enemy_bullets.remove(bullet)
                if self.player_hit_points <= 0:
                    self.game_over()

        # Atualizar coletáveis
        for collectible in self.collectibles[:]:
            collectible.update(self.platforms, self.ground_y)
            if collectible.rect.colliderect(player_rect):
                if collectible.type == "heart" and self.player_hit_points < self.max_health * self.hits_per_heart:
                    self.player_hit_points = min(self.player_hit_points + self.hits_per_heart, self.max_health * self.hits_per_heart)
                    self.current_health = math.ceil(self.player_hit_points / self.hits_per_heart)
                    self.collectibles.remove(collectible)
                elif collectible.type == "ammo":
                    self.current_ammo += 20
                    self.collectibles.remove(collectible)
            if collectible.pos[1] > self.screen_height * 2:
                self.collectibles.remove(collectible)

        # Lógica da câmera
        player_center_x = self.player_pos[0] + self.player_rect_size[0] / 2
        target_x = player_center_x - self.screen_width / 2
        camera_smoothness_x = 0.1
        self.camera_x += (target_x - self.camera_x) * camera_smoothness_x
        self.camera_y = 0
        
        # self._manage_platforms() # Gerenciamento de plataformas flutuantes desativado
        
        if self.player_pos[0] < 200:
            self.player_pos[0] = 200
            self.player_velocity_x = max(0, self.player_velocity_x)

        if self.camera_x > (len(self.trenches) + 1) * self.trench_spacing:
            self.game_won = True
        
        if self.player_pos[1] > self.screen_height * 1.5:
            self.game_over()


    def draw(self, screen):
        # Limpar a tela para evitar rastros
        screen.fill((0, 0, 0))
        
        # Calcular os offsets da câmera
        camera_offset_x = int(-self.camera_x)
        camera_offset_y = int(-self.camera_y)
        
        # Desenhar o fundo com parallax suave
        bg_offset_x = camera_offset_x // 2  # Movimento mais lento que a câmera (parallax)
        
        # Calcular a posição x do background considerando o tamanho total da imagem
        bg_x = bg_offset_x % self.background_width
        
        # Desenhar o background principal
        screen.blit(self.background_image, (bg_x, 0))
        
        # Se necessário, desenhar uma segunda cópia para preencher a lacuna
        if bg_x < 0:
            screen.blit(self.background_image, (bg_x + self.background_width, 0))
        elif bg_x > self.background_width - self.screen_width:
            screen.blit(self.background_image, (bg_x - self.background_width, 0))
        
        # --- NOVO: Desenhar o chão fixo ---
        # Desenha um retângulo para o chão que cobre toda a largura da tela.
        # Como a câmera não se move verticalmente, a posição Y é fixa em relação à tela.
        ground_draw_y = self.ground_y + camera_offset_y
        pygame.draw.rect(screen, self.ground_color, (0, ground_draw_y, screen.get_width(), screen.get_height() - ground_draw_y))
        
        # --- Desenhar plataformas flutuantes ---
        screen_rect = screen.get_rect()
        for platform in self.platforms:
            platform_rect_on_screen = platform['rect'].move(camera_offset_x, camera_offset_y)
            if platform_rect_on_screen.colliderect(screen_rect): # Otimização para desenhar só o visível
                pygame.draw.rect(screen, platform['color'], platform_rect_on_screen)
                
        # Desenhar coletáveis
        for collectible in self.collectibles:
            collectible.draw(screen, camera_offset_x, camera_offset_y)
            
        # Desenhar UI - Corações de vida
        heart_spacing = 35  # Espaçamento entre os corações
        for i in range(self.max_health):
            heart_x = 10 + (i * heart_spacing)
            heart_y = 10
            if i < self.current_health:
                screen.blit(self.full_heart_img, (heart_x, heart_y))
            else:
                screen.blit(self.empty_heart_img, (heart_x, heart_y))
                
        # Desenhar contador de munição no canto superior direito
        if self.ammo_symbol_img:
            # Posicionar o símbolo de munição no canto superior direito
            ammo_symbol_x = self.screen_width - 120
            ammo_symbol_y = 10
            screen.blit(self.ammo_symbol_img, (ammo_symbol_x, ammo_symbol_y))
            
            # Desenhar o número de balas ao lado do símbolo
            font = pygame.font.Font(None, 36)
            ammo_text = str(self.current_ammo)
            ammo_surface = font.render(ammo_text, True, (255, 255, 255))
            screen.blit(ammo_surface, (ammo_symbol_x + 50, ammo_symbol_y + 10))
                
        # Desenhar inimigos
        for enemy in self.enemies:
            enemy.draw(screen, camera_offset_x, camera_offset_y)
            
        # Desenhar lasers inimigos
        for bullet in self.enemy_bullets:
            # Desenhar o laser como uma linha vermelha brilhante
            start_pos = (int(bullet['pos'][0] + camera_offset_x), 
                        int(bullet['pos'][1] + camera_offset_y))
            end_pos = (int(bullet['pos'][0] - bullet['direction'][0] * 20 + camera_offset_x),
                      int(bullet['pos'][1] - bullet['direction'][1] * 20 + camera_offset_y))
            
            # Desenhar o brilho externo do laser
            pygame.draw.line(screen, (255, 100, 100), start_pos, end_pos, 4)
            # Desenhar o núcleo brilhante do laser
            pygame.draw.line(screen, (255, 255, 255), start_pos, end_pos, 2)
        
        # Desenhar projéteis
        for bullet in self.bullets:
            current_x = int(bullet['pos'][0] + camera_offset_x)
            current_y = int(bullet['pos'][1] + camera_offset_y)
            
            # Desenhar trilha do projétil
            for i in range(self.bullet_trail_length):
                trail_x = int(current_x - (bullet['direction_x'] * (i * 4)))
                trail_y = int(current_y - (bullet['direction_y'] * (i * 4)))
                trail_size = self.bullet_size - (i * 2)
                if trail_size > 0:
                    trail_color = (255, 255 - (i * 60), 0)
                    pygame.draw.circle(screen, trail_color, (trail_x, trail_y), trail_size)
            
            # Desenhar o projétil principal
            if self.bullet_image:
                screen.blit(self.bullet_image, (current_x - 8, current_y - 8))
            else:
                pygame.draw.circle(screen, (255, 255, 200), (current_x, current_y), self.bullet_size + 2)
                pygame.draw.circle(screen, (255, 255, 0), (current_x, current_y), self.bullet_size)
        
        # Desenhar o player
        player_screen_x = int(self.player_pos[0] + camera_offset_x)
        player_screen_y = int(self.player_pos[1] + camera_offset_y)
        
        if self.player_image:
            # Virar a imagem horizontalmente se necessário
            image_to_draw = pygame.transform.flip(self.player_image, not self.facing_right, False)
            
            # --- CORREÇÃO: Centraliza a textura visual em relação à hitbox ---
            # O offset X centraliza a imagem horizontalmente.
            visual_offset_x = (self.player_visual_size[0] - self.player_rect_size[0]) // 2
            # O offset Y alinha a parte de baixo da imagem com a parte de baixo da hitbox, evitando que o personagem "afunde" no chão.
            visual_offset_y = self.player_visual_size[1] - self.player_rect_size[1]
            screen.blit(image_to_draw, (player_screen_x - visual_offset_x, player_screen_y - visual_offset_y))
            
            # Desenhar hitbox para debug (comentar em produção)
            # pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(
            #     player_screen_x,
            #     player_screen_y,
            #     self.player_rect_size[0],
            #     self.player_rect_size[1]
            # ), 1)
        else:
            # Fallback: desenha um retângulo vermelho
            player_rect = pygame.Rect(
                player_screen_x,
                player_screen_y,
                self.player_rect_size[0],
                self.player_rect_size[1]
            )
            pygame.draw.rect(screen, (255, 0, 0), player_rect)

        # Desenhar HUD
        font = pygame.font.SysFont(None, 30)
        if self.is_game_over:
            # Texto de Game Over
            game_over_font = pygame.font.SysFont(None, 72)
            text_game_over = game_over_font.render("GAME OVER", True, (255, 0, 0))
            text_restart = font.render("Pressione R para reiniciar", True, (255, 255, 255))
            
            # Centralizar textos
            text_game_over_rect = text_game_over.get_rect(center=(self.screen_width//2, self.screen_height//2 - 40))
            text_restart_rect = text_restart.get_rect(center=(self.screen_width//2, self.screen_height//2 + 20))
            
            screen.blit(text_game_over, text_game_over_rect)
            screen.blit(text_restart, text_restart_rect)
        else:
            # HUD normal
            text_surface = font.render("ESPAÇO para pular, X para atirar, ESC para menu", True, (255, 255, 255))
            screen.blit(text_surface, (10, 10))