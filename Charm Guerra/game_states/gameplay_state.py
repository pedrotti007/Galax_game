# game_states/gameplay_state.py

import os
import pygame
import random
from .map_manager import MapManager

class GameplayState:
    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Configurações do jogador
        self.player_rect_size = (120, 220)  # Hitbox do jogador, um pouco menor para colisões mais permissivas
        self.player_visual_size = (225, 240)  # Tamanho visual do sprite (ex: 3x o tamanho original)
        self.player_speed = 8  # Aumentado para compensar o tamanho maior
        self.gravity = 0.8
        self.jump_force = -23
        self.is_game_over = False
        
        # --- Sistema de Geração de Plataformas Flutuantes ---
        self.platforms = []
        # Parâmetros de geração (ajuste para mudar a dificuldade)
        self.min_platform_width = 190
        self.max_platform_width = 450
        self.min_gap_x = 1000 # Aumentado AINDA MAIS para gerar MENOS plataformas
        self.max_gap_x = 1300  # Aumentado AINDA MAIS para gerar MENOS plataformas
        self.min_gap_y = -100 # Aumentado para posições verticais MAIS aleatórias
        self.max_gap_y = 250  # Aumentado para posições verticais MAIS aleatórias
        self.last_platform_end_x = 0
        
        # --- NOVO: Chão Fixo ---
        self.ground_y = self.screen_height - 60
        self.ground_color = (139, 69, 19) # Cor de terra
        self.last_floating_platform_y = self.ground_y - 150 # Altura inicial para a primeira plataforma flutuante
        
        # Camera/Scrolling
        self.camera_x = 0
        self.camera_y = 0
        
        # Estado inicial do jogador
        self.reset_player()
        
        # Carregando texturas
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
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
        self._generate_initial_platforms()
        
        # Posiciona o jogador no chão inicial
        self.player_pos = [200, self.ground_y - self.player_rect_size[1]]
        
        self.player_velocity_y = 0
        self.is_jumping = False
        self.facing_right = True
        self.is_game_over = False
        self.camera_x = 0
        self.camera_y = 0

    def _generate_initial_platforms(self):
        """Cria as plataformas flutuantes iniciais."""
        # Começa a gerar plataformas um pouco à frente do jogador
        self.last_platform_end_x = 400
        self.last_floating_platform_y = self.ground_y - 150

        # Gera algumas plataformas iniciais para preencher a tela
        while self.last_platform_end_x < self.screen_width * 2:
            self._generate_next_platform()

    def _generate_next_platform(self):
        """Gera uma única plataforma nova à frente da última."""
        gap_x = random.randint(self.min_gap_x, self.max_gap_x)
        gap_y = random.randint(self.min_gap_y, self.max_gap_y)
        width = random.randint(self.min_platform_width, self.max_platform_width)
        
        new_x = self.last_platform_end_x + gap_x
        new_y = self.last_floating_platform_y + gap_y
        
        # Limita a altura das plataformas para não saírem muito da tela e ficarem acima do chão
        # --- CORREÇÃO: Força as plataformas a aparecerem mais para cima ---
        top_limit = self.screen_height * 0.1 # 30% do topo da tela
        bottom_limit = self.screen_height * 0.6 # Limite inferior para não ficarem muito baixas
        new_y = max(top_limit, min(new_y, bottom_limit))
        
        self.add_platform(new_x, new_y, width)
        self.last_platform_end_x = new_x + width
        self.last_floating_platform_y = new_y

    def add_platform(self, x, y, width):
        """Adiciona uma nova plataforma à lista."""
        platform = {
            'rect': pygame.Rect(x, y, width, 40), # Altura fixa de 40
            'color': (0,0,0) # Cor Preta
        }
        self.platforms.append(platform)

    def _manage_platforms(self):
        """Verifica se precisa gerar novas plataformas e remove as antigas."""
        # Gera novas plataformas se a última estiver entrando na tela
        if self.last_platform_end_x < self.camera_x + self.screen_width * 1.5:
            self._generate_next_platform()
            
        # Remove plataformas antigas que já saíram completamente da tela
        self.platforms = [p for p in self.platforms if p['rect'].right > self.camera_x - 200]
        
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
            elif (event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP) and not self.is_jumping and not self.is_game_over:
                self.player_velocity_y = self.jump_force
                self.is_jumping = True
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
                # --- CORREÇÃO: Posição da bala alinhada com a arma ---
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
                self.last_shot_time = current_time
            
        # Aplicar gravidade
        self.player_velocity_y += self.gravity
        self.player_pos[1] += self.player_velocity_y
        
        # --- CORREÇÃO: Lógica de colisão separada para chão infinito e plataformas ---
        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], self.player_rect_size[0], self.player_rect_size[1])
        
        # 1. Verificar colisão com as plataformas flutuantes
        for platform in self.platforms:
            collidable_rect = platform['rect']
            if player_rect.colliderect(collidable_rect):
                # Colisão por cima (pousando)
                if self.player_velocity_y > 0 and player_rect.bottom > collidable_rect.top:
                    player_rect.bottom = collidable_rect.top
                    self.player_pos[1] = player_rect.y
                    self.player_velocity_y = 0
                    self.is_jumping = False
                # Colisão por baixo (batendo a cabeça)
                elif self.player_velocity_y < 0 and player_rect.top < collidable_rect.bottom:
                    player_rect.top = collidable_rect.bottom
                    self.player_pos[1] = player_rect.y
                    self.player_velocity_y = 0
        
        # 2. Verificar colisão com o chão (que agora é infinito)
        # A condição `self.player_velocity_y >= 0` previne que o jogador seja "puxado" para o chão se ele pulou de uma plataforma baixa.
        if player_rect.bottom >= self.ground_y and self.player_velocity_y >= 0:
            player_rect.bottom = self.ground_y
            self.player_pos[1] = player_rect.y
            self.player_velocity_y = 0
            self.is_jumping = False
        
        # Atualizar projéteis
        for bullet in self.bullets[:]:
            bullet['pos'][0] += self.bullet_speed * bullet['direction_x']
            bullet['pos'][1] += self.bullet_speed * bullet['direction_y']

            # --- CORREÇÃO: Remover projéteis que saíram da VISTA DA CÂMERA ---
            # A posição do projétil está em coordenadas do mundo. O código antigo comparava
            # com o tamanho da tela (ex: 1920), fazendo com que os tiros desaparecessem
            # assim que o jogador passasse dessa coordenada no mapa.
            # A forma correta é comparar com os limites da câmera no mundo do jogo.
            margin = 200 # Margem para garantir que o projétil suma bem fora da tela
            camera_view_left = self.camera_x - margin
            camera_view_right = self.camera_x + self.screen_width + margin

            if not (camera_view_left < bullet['pos'][0] < camera_view_right):
                self.bullets.remove(bullet)
            elif bullet['pos'][1] < -margin or bullet['pos'][1] > self.screen_height + margin:
                self.bullets.remove(bullet)

        # --- LÓGICA DA CÂMERA ATUALIZADA ---
        # O alvo da câmera é calculado para que o centro do jogador fique no centro da tela.
        player_center_x = self.player_pos[0] + self.player_rect_size[0] / 2
        target_x = player_center_x - self.screen_width / 2

        # A suavização da câmera torna o movimento mais fluido.
        camera_smoothness_x = 0.1
        self.camera_x += (target_x - self.camera_x) * camera_smoothness_x
        self.camera_y = 0  # Mantém a câmera fixa verticalmente
        
        # --- NOVO: Gerenciamento de plataformas ---
        self._manage_platforms()
        
        # Verificar game over (caiu do mapa)
        if self.player_pos[1] > self.screen_height * 1.5:  # Margem para queda
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
