import pygame
import math
import os
import random

class Enemy:
    def __init__(self, x, y, is_flying=False):
        self.pos = [x, y]
        self.is_flying = is_flying
        self.size = (100, 100)  # Tamanho do inimigo
        self.shots_remaining = 5  # Número de tiros antes de precisar esfriar
        self.overheat_timer = 0  # Timer para controlar o resfriamento
        self.cooldown_time = 3000  # 3 segundos em milissegundos
        self.shot_cooldown = 2000  # Tempo entre tiros (800ms)
        self.last_shot_time = 0
        self.is_overheated = False
        self.facing_right = False # Inimigo começa virado para a esquerda
        
        # Carregar imagem do inimigo
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        try:
            self.image = pygame.image.load(os.path.join(project_root, 'assets', 'images', 'enemie.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, self.size)
        except Exception as e:
            print(f"Erro ao carregar enemie.png: {e}")
            self.image = None

    def update(self, player_pos):
        # Vira o inimigo para o jogador
        if player_pos[0] > self.pos[0]:
            self.facing_right = True
        else:
            self.facing_right = False

    def can_shoot(self, current_time):
        # Verifica se a arma está superaquecida
        if self.is_overheated:
            if current_time - self.overheat_timer >= self.cooldown_time:
                self.is_overheated = False
                self.shots_remaining = 2
                return True
            return False
        
        # Verifica o cooldown entre tiros
        if current_time - self.last_shot_time < self.shot_cooldown:
            return False
            
        return True

    def shoot(self, target_pos, current_time):
        if not self.can_shoot(current_time):
            return None

        # Calcula a direção do tiro
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance == 0:
            return None
            
        direction = [dx/distance, dy/distance]
        
        # Posição inicial do tiro (centro do inimigo)
        start_pos = [self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2]
        
        # Atualiza os contadores
        self.last_shot_time = current_time
        self.shots_remaining -= 1
        
        if self.shots_remaining <= 0:
            self.is_overheated = True
            self.overheat_timer = current_time
            
        return {
            'pos': start_pos,
            'direction': direction,
            'enemy_laser': True  # Marca que é um laser inimigo
        }

    def draw(self, screen, camera_offset_x, camera_offset_y):
        if self.image:
            image_to_draw = pygame.transform.flip(self.image, not self.facing_right, False)
            screen_pos = (int(self.pos[0] + camera_offset_x), int(self.pos[1] + camera_offset_y))
            screen.blit(image_to_draw, screen_pos)
        else:
            # Fallback para um retângulo vermelho se a imagem não carregar
            pygame.draw.rect(screen, (255, 0, 0), 
                           (int(self.pos[0] + camera_offset_x), 
                            int(self.pos[1] + camera_offset_y), 
                            self.size[0], self.size[1]))