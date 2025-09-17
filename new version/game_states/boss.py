import pygame
import random
import os
import math
import sys

# Adiciona o diretório raiz do projeto ao sys.path para resolver importações
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from game_states.particle_system import ParticleSystem

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Atributos básicos
        self.pos = [x, y]
        # --- MODIFICADO: Aumentar o tamanho do chefe ---
        self.size = (350, 350)
        # --- MODIFICADO: Mais vida para o chefe ---
        self.health = 5000
        self.max_health = 5000
        self.facing_right = True

        # --- MODIFICADO: Carregar as imagens do chefe (idle e atirando) ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        try:
            # Carrega a imagem de idle (Boss.png)
            idle_image_path = os.path.join(project_root, 'assets', 'images', 'Boss.png')
            self.original_image_idle = pygame.image.load(idle_image_path).convert_alpha()
            self.original_image_idle = pygame.transform.scale(self.original_image_idle, self.size)

            # Carrega a imagem de tiro (Boss_shooting.png)
            shooting_image_path = os.path.join(project_root, 'assets', 'images', 'Boss_shooting.png')
            self.original_image_shooting = pygame.image.load(shooting_image_path).convert_alpha()
            self.original_image_shooting = pygame.transform.scale(self.original_image_shooting, self.size)
            
            self.image = self.original_image_idle # Começa com a imagem idle
        except Exception as e:
            print(f"AVISO: Não foi possível carregar as imagens do chefe ('Boss.png', 'Boss_shooting.png'). Usando quadrado vermelho. Erro: {e}")
            self.original_image_idle = None
            self.original_image_shooting = None
            self.image = pygame.Surface(self.size)
            self.image.fill((255, 0, 0))
        
        # Estados e fases
        self.state = "idle"
        self.phase = 1  # Boss tem 3 fases
        self.phase_thresholds = {2: 0.6, 3: 0.3}  # Muda para fase 2 em 60% de vida, fase 3 em 30%
        
        # Timers e cooldowns
        self.last_attack_time = 0
        # --- MODIFICADO: Ataques mais frequentes ---
        self.attack_cooldown = 1200 # Reduzido de 2s para 1.2s
        self.dash_cooldown = 3000
        self.last_dash_time = 0
        self.pattern_start_time = 0
        self.current_pattern_duration = 0
        
        # Movimento
        self.speed = 6 # --- MODIFICADO: Chefe mais rápido
        self.direction = 1
        self.velocity = [0, 0]
        self.dash_speed = 20
        self.is_dashing = False
        
        # Ataques
        # --- NOVO: Parâmetros de IA ---
        self.strafe_direction = 1
        self.last_strafe_change = 0
        self.strafe_interval = 1500 # --- MODIFICADO: Movimento mais errático
        self.optimal_distance = 400 # Distância que o chefe tenta manter

        self.attack_patterns = {
            1: ["projectile_spray", "ground_pound", "circle_burst"],
            2: ["projectile_wall", "dash_attack", "cross_beam"],
            3: ["bullet_hell", "rage_dash", "laser_grid"]
        }
        self.current_pattern = None
        self._newly_fired_bullets = [] # Lista temporária para novos projéteis
        
        # Efeitos visuais
        self.flash_duration = 200
        self.flash_start = 0
        self.is_flashing = False
        self.particle_system = ParticleSystem()

        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self, player_pos, current_time, player_velocity_x=0):
        # Atualiza fase baseado na vida
        self._newly_fired_bullets.clear() # Limpa a lista de novos tiros a cada frame

        health_percentage = self.health / self.max_health
        for phase, threshold in self.phase_thresholds.items():
            if health_percentage <= threshold and self.phase < phase:
                self.phase = phase
                self.start_phase_transition()

        # Atualiza estado e padrão de ataque
        if self.state == "idle":
            self._update_movement(player_pos, current_time)
            if current_time - self.last_attack_time > self.attack_cooldown:
                self._start_attack_pattern(current_time, player_pos)
        elif self.state == "attacking":
            self._update_attack_pattern(current_time, player_pos, player_velocity_x)
        elif self.state == "dashing":
            self._update_dash()

        # Atualiza posição e projéteis
        self._update_position()
        
        # Atualiza efeitos visuais
        if hasattr(self, 'particle_system'):
            self.particle_system.update()
        
        return self._newly_fired_bullets
            
        # --- NOVO: Lógica para virar o chefe e trocar a imagem ---
        # Determina a direção que o chefe deve encarar
        if player_pos[0] > self.pos[0] + self.size[0] / 2:
            self.facing_right = True
        else:
            self.facing_right = False
            
        # Seleciona a imagem base (idle ou atirando)
        if self.state == "attacking" and self.original_image_shooting:
            base_image = self.original_image_shooting
        else:
            base_image = self.original_image_idle
        
        # Vira a imagem se necessário e atualiza a imagem principal
        if base_image:
            self.image = pygame.transform.flip(base_image, not self.facing_right, False)

    def _update_movement(self, player_pos, current_time):
        """Movimento tático: mantém distância e se move lateralmente."""
        if not self.is_dashing:
            dx = player_pos[0] - self.pos[0]
            dy = player_pos[1] - self.pos[1]
            dist = math.sqrt(dx * dx + dy * dy)

            # Muda a direção do strafe periodicamente
            if current_time - self.last_strafe_change > self.strafe_interval:
                self.strafe_direction *= -1
                self.last_strafe_change = current_time

            # Movimento para manter a distância ótima
            if dist > self.optimal_distance + 50: # Se muito longe, aproxima
                self.velocity[0] = (dx / dist) * self.speed * 0.5
            elif dist < self.optimal_distance - 50: # Se muito perto, afasta
                self.velocity[0] = -(dx / dist) * self.speed * 0.5
            else:
                self.velocity[0] *= 0.9 # Desacelera se na distância certa

            # Adiciona o movimento lateral (strafe)
            self.velocity[0] += self.strafe_direction * self.speed * 0.5

            # Movimento vertical para seguir o jogador
            self.velocity[1] = (dy / dist) * self.speed * 0.7 if dist > 0 else 0

    def _update_position(self):
        # Atualiza posição com base na velocidade
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        
        # Limita à tela
        self.pos[0] = max(0, min(self.pos[0], 1280 - self.size[0]))
        self.pos[1] = max(0, min(self.pos[1], 720 - self.size[1]))
        
        self.rect.topleft = self.pos

    def _start_attack_pattern(self, current_time, player_pos):
        """Escolhe um ataque taticamente com base na distância do jogador."""
        if self.current_pattern: return

        dist_to_player = math.dist(self.pos, player_pos)
        available_attacks = self.attack_patterns[self.phase]
        
        # Lógica de seleção tática
        if dist_to_player < 300 and "dash_attack" in available_attacks:
            self.current_pattern = "dash_attack"
        elif dist_to_player < 400 and "cross_beam" in available_attacks:
            self.current_pattern = "cross_beam"
        else:
            # Se não se encaixa em nenhuma condição especial, escolhe um aleatório
            self.current_pattern = random.choice(available_attacks)

        self.pattern_start_time = current_time
        self.state = "attacking"
        
        # Configura duração e comportamento do padrão
        if self.current_pattern == "projectile_spray":
            self.current_pattern_duration = 3000
        elif self.current_pattern == "bullet_hell":
            self.current_pattern_duration = 5000
        elif self.current_pattern == "cross_beam":
            self.current_pattern_duration = 2000
        elif self.current_pattern == "dash_attack":
            self.current_pattern_duration = 2000
            self._start_dash(player_pos)

    def _update_attack_pattern(self, current_time, player_pos, player_velocity_x):
        time_in_pattern = current_time - self.pattern_start_time
        
        if time_in_pattern > self.current_pattern_duration:
            self._end_attack_pattern()
            return

        # --- MODIFICADO: Executa o padrão de ataque atual com tiro preditivo ---
        if self.current_pattern == "projectile_spray":
            if time_in_pattern % 150 == 0:  # --- MODIFICADO: Atira a cada 150ms
                self._fire_projectile(player_pos, player_velocity_x)
        elif self.current_pattern == "bullet_hell":
            if time_in_pattern % 120 == 0:  # --- MODIFICADO: Atira mais rápido
                for angle in range(0, 360, 30):  # --- MODIFICADO: 12 direções em vez de 8
                    self._fire_projectile_angle(angle)
        elif self.current_pattern == "cross_beam":
            if time_in_pattern % 500 == 0:
                self._fire_cross_beam()

    def _fire_projectile(self, target_pos, player_velocity_x):
        """Atira um projétil que antecipa o movimento do jogador."""
        bullet_speed = 20 # --- MODIFICADO: Projéteis ainda mais rápidos
        start_pos = [self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2]
        
        # --- NOVO: Lógica de tiro preditivo ---
        dist_to_target = math.dist(start_pos, target_pos)
        time_to_reach = dist_to_target / bullet_speed if bullet_speed > 0 else 0
        predicted_x = target_pos[0] + player_velocity_x * time_to_reach * 0.8 # 0.8 para não ser perfeito demais
        predicted_y = target_pos[1]

        dx = predicted_x - start_pos[0]
        dy = predicted_y - start_pos[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            direction = [(dx/dist), (dy/dist)]
            bullet = {
                'pos': start_pos,
                'direction': direction,
                'damage': 10,
                'visual_type': 'boss_laser' # Identificador para o visual
            }
            self._newly_fired_bullets.append(bullet)
            
            # Efeito de partículas no disparo
            self.particle_system.create_explosion(start_pos[0], start_pos[1], (255, 200, 0, 200), 10)

    def _fire_projectile_angle(self, angle):
        rad = math.radians(angle)
        direction = [math.cos(rad), math.sin(rad)]
        bullet = {
            'pos': [self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2],
            'direction': direction,
            'damage': 10,
            'visual_type': 'boss_laser'
        }
        self._newly_fired_bullets.append(bullet)

    def _fire_cross_beam(self):
        """Fires projectiles in four cardinal directions (cross shape)."""
        self._fire_projectile_angle(0)    # Right
        self._fire_projectile_angle(90)   # Down
        self._fire_projectile_angle(180)  # Left
        self._fire_projectile_angle(270)  # Up
        
        # Add some particle effects for the attack
        center_x = self.pos[0] + self.size[0] / 2
        center_y = self.pos[1] + self.size[1] / 2
        self.particle_system.create_explosion(center_x, center_y, (200, 200, 255, 200), 25)

    def _end_attack_pattern(self):
        self.current_pattern = None
        self.state = "idle"
        self.last_attack_time = pygame.time.get_ticks()

    def _start_dash(self, target_pos):
        if not self.is_dashing:
            dx = target_pos[0] - self.pos[0]
            dy = target_pos[1] - self.pos[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.velocity = [(dx/dist) * self.dash_speed, (dy/dist) * self.dash_speed]
                self.is_dashing = True
                self.last_dash_time = pygame.time.get_ticks()

    def _update_dash(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dash_time > 500:  # Dash dura 500ms
            self.is_dashing = False
            self.velocity = [0, 0]
            self.state = "idle"

    def start_phase_transition(self):
        # Efeito visual para transição de fase
        self.is_flashing = True
        self.flash_start = pygame.time.get_ticks()
        # Aumenta a velocidade e reduz cooldowns em cada fase
        self.speed *= 1.2
        self.attack_cooldown *= 0.8
        self.dash_cooldown *= 0.8

    def draw(self, screen, camera_offset_x, camera_offset_y):
        # Atualiza e desenha o sistema de partículas primeiro (para ficar atrás do boss)
        self.particle_system.update()
        self.particle_system.draw(screen, camera_offset_x, camera_offset_y)
        
        screen_pos = (int(self.pos[0] + camera_offset_x), int(self.pos[1] + camera_offset_y))
        
        # Desenha o boss com efeito de flash se necessário
        if self.is_flashing:
            current_time = pygame.time.get_ticks()
            if current_time - self.flash_start <= self.flash_duration:
                flash_surface = pygame.Surface(self.size, pygame.SRCALPHA)
                flash_surface.fill((255, 255, 255, 128))
                screen.blit(flash_surface, screen_pos)
                # Adiciona partículas de dano
                if random.random() < 0.3:  # 30% de chance por frame
                    self.particle_system.create_explosion(
                        self.pos[0] + random.randint(0, self.size[0]),
                        self.pos[1] + random.randint(0, self.size[1]),
                        (255, 255, 255, 200),
                        5
                    )
            else:
                self.is_flashing = False
        
        screen.blit(self.image, screen_pos)
        
        # Barra de vida com cores dinâmicas baseadas na fase
        health_bar_width = 200
        health_bar_height = 20
        health_percentage = self.health / self.max_health
        
        # Cores da barra de vida mudam com a fase
        if self.phase == 1:
            health_color = (0, 255, 0)
        elif self.phase == 2:
            health_color = (255, 165, 0)
        else:
            health_color = (255, 0, 0)
        
        # Background da barra de vida
        pygame.draw.rect(screen, (100, 100, 100), (screen_pos[0], screen_pos[1] - 30, health_bar_width, health_bar_height))
        # Barra de vida atual
        pygame.draw.rect(screen, health_color, (screen_pos[0], screen_pos[1] - 30, health_bar_width * health_percentage, health_bar_height))
        
        # Adiciona brilho na barra de vida
        glow_height = 2
        glow_width = max(1, int(health_bar_width * health_percentage))  # Garante largura mínima de 1 pixel
        glow_color = (health_color[0], health_color[1], health_color[2], 128)
        glow_surface = pygame.Surface((glow_width, glow_height), pygame.SRCALPHA)
        glow_surface.fill(glow_color)
        screen.blit(glow_surface, (screen_pos[0], screen_pos[1] - 30 - glow_height))
