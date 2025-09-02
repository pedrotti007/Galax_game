# game_states/gameplay_state.py

import os
import pygame
from .map_manager import MapManager

class GameplayState:
    def __init__(self, game_manager, screen_width, screen_height):
        self.game_manager = game_manager
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Configurações do jogador
        self.player_rect_size = (250, 400)  # Hitbox do jogador aumentada 5x
        self.player_visual_size = (375, 400)  # Tamanho visual do sprite aumentado 5x (mantendo proporção mais larga)
        self.player_speed = 8  # Aumentado para compensar o tamanho maior
        self.gravity = 0.8
        self.jump_force = -15
        self.is_game_over = False
        
        # Sistema de mapa
        self.map_manager = MapManager(screen_width, screen_height)
        self.map_manager.load_map(1)  # Carrega o mapa de teste
        
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
            self.background_image = pygame.image.load(os.path.join(project_root, 'assets', 'images', 'ground.png')).convert()
            
            # Ajusta a altura para ser exatamente a altura da tela
            original_aspect = self.background_image.get_width() / self.background_image.get_height()
            new_height = screen_height
            new_width = int(new_height * original_aspect)  # Mantém a proporção original
            
            self.background_image = pygame.transform.scale(self.background_image, (new_width, new_height))
            
            # Guarda as dimensões do background para uso no scrolling
            self.background_width = new_width
            self.background_height = new_height
        except Exception as e:
            print(f"Erro ao carregar ground.png: {e}")
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
        
        # Inicialização do estado atual do jogador
        self.player_pos = [100, screen_height - 100]  # Posição inicial temporária
        self.player_velocity_y = 0
        self.is_jumping = False
        self.facing_right = True
        

        
    def reset_player(self):
        """Reinicia a posição e estado do jogador"""
        self.player_pos = list(self.map_manager.get_spawn_point())
        self.player_velocity_y = 0
        self.is_jumping = False
        self.facing_right = True
        self.is_game_over = False
        self.camera_x = 0
        self.camera_y = 0
        
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
        
        # Atualizar câmera (apenas scrolling horizontal)
        target_x = self.player_pos[0] - self.screen_width // 3  # 1/3 da tela para melhor visibilidade à frente
        
        # Suavização da câmera apenas no eixo X
        camera_smoothness_x = 0.12 if abs(target_x - self.camera_x) > 100 else 0.08  # Mais suave para movimentos pequenos
        
        # Adicionar pequeno offset baseado na direção do movimento
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_x += 100  # Offset para ver mais à frente quando movendo para direita
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_x -= 100  # Offset para ver mais à frente quando movendo para esquerda
        
        # Aplicar suavização apenas na câmera horizontal
        self.camera_x += (target_x - self.camera_x) * camera_smoothness_x
        self.camera_y = 0  # Mantém a câmera fixa verticalmente
        
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
        
        # Desenhar o mapa
        self.map_manager.draw(screen, camera_offset_x=camera_offset_x, camera_offset_y=camera_offset_y)
        
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
            # Centralizar a textura mais larga em relação à hitbox
            visual_offset_x = (self.player_visual_size[0] - self.player_rect_size[0]) // 2
            screen.blit(image_to_draw, (player_screen_x - visual_offset_x, player_screen_y))
            
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
