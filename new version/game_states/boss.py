import pygame
import random
import math
from .particle_system import ParticleSystem

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Atributos básicos
        self.pos = [x, y]
        self.size = (200, 200)
        self.health = 1000
        self.max_health = 1000
        self.image = pygame.Surface(self.size)
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=self.pos)
        
        # Estados e fases
        self.state = "idle"
        self.phase = 1  # Boss tem 3 fases
        self.phase_thresholds = {2: 0.6, 3: 0.3}  # Muda para fase 2 em 60% de vida, fase 3 em 30%
        
        # Timers e cooldowns
        self.last_attack_time = 0
        self.attack_cooldown = 2000
        self.dash_cooldown = 3000
        self.last_dash_time = 0
        self.pattern_start_time = 0
        self.current_pattern_duration = 0
        
        # Movimento
        self.speed = 5
        self.direction = 1
        self.velocity = [0, 0]
        self.dash_speed = 20
        self.is_dashing = False
        
        # Ataques
        self.attack_patterns = {
            1: ["projectile_spray", "ground_pound", "circle_burst"],
            2: ["projectile_wall", "dash_attack", "cross_beam"],
            3: ["bullet_hell", "rage_dash", "laser_grid"]
        }
        self.current_pattern = None
        self.bullets = []  # Lista de projéteis ativos
        
        # Efeitos visuais
        self.flash_duration = 200
        self.flash_start = 0
        self.is_flashing = False
        self.particle_system = ParticleSystem()

    def update(self, player_pos, current_time):
        # Atualiza fase baseado na vida
        health_percentage = self.health / self.max_health
        for phase, threshold in self.phase_thresholds.items():
            if health_percentage <= threshold and self.phase < phase:
                self.phase = phase
                self.start_phase_transition()

        # Atualiza estado e padrão de ataque
        if self.state == "idle":
            self._update_movement(player_pos)
            if current_time - self.last_attack_time > self.attack_cooldown:
                self._start_attack_pattern(current_time)
        elif self.state == "attacking":
            self._update_attack_pattern(current_time, player_pos)
        elif self.state == "dashing":
            self._update_dash()

        # Atualiza posição e projéteis
        self._update_position()
        self._update_bullets(player_pos)
        
        # Atualiza efeitos visuais
        if hasattr(self, 'particle_system'):
            self.particle_system.update()

    def _update_movement(self, player_pos):
        if not self.is_dashing:
            # Movimento básico em direção ao jogador com alguma aleatoriedade
            dx = player_pos[0] - self.pos[0]
            dy = player_pos[1] - self.pos[1]
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 300:  # Mantém distância mínima do jogador
                self.velocity[0] = (dx / dist) * self.speed
                self.velocity[1] = (dy / dist) * self.speed
            else:
                self.velocity[0] *= 0.95  # Desacelera suavemente
                self.velocity[1] *= 0.95

    def _update_position(self):
        # Atualiza posição com base na velocidade
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        
        # Limita à tela
        self.pos[0] = max(0, min(self.pos[0], 1280 - self.size[0]))
        self.pos[1] = max(0, min(self.pos[1], 720 - self.size[1]))
        
        self.rect.topleft = self.pos

    def _start_attack_pattern(self, current_time, player_pos=None):
        if not self.current_pattern:
            # Escolhe um padrão de ataque da fase atual
            self.current_pattern = random.choice(self.attack_patterns[self.phase])
            self.pattern_start_time = current_time
            self.state = "attacking"
            
            # Configura duração e comportamento do padrão
            if self.current_pattern == "projectile_spray":
                self.current_pattern_duration = 3000
            elif self.current_pattern == "bullet_hell":
                self.current_pattern_duration = 5000
            elif self.current_pattern == "dash_attack" and player_pos:
                self.current_pattern_duration = 2000
                self._start_dash(player_pos)

    def _update_attack_pattern(self, current_time, player_pos):
        time_in_pattern = current_time - self.pattern_start_time
        
        if time_in_pattern > self.current_pattern_duration:
            self._end_attack_pattern()
            return

        # Executa o padrão de ataque atual
        if self.current_pattern == "projectile_spray":
            if time_in_pattern % 200 == 0:  # Atira a cada 200ms
                self._fire_projectile(player_pos)
        elif self.current_pattern == "bullet_hell":
            if time_in_pattern % 100 == 0:  # Atira mais rápido
                for angle in range(0, 360, 45):  # 8 direções
                    self._fire_projectile_angle(angle)
        elif self.current_pattern == "cross_beam":
            if time_in_pattern % 500 == 0:
                self._fire_cross_beam()

    def _fire_projectile(self, target_pos):
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            start_pos = [self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2]
            bullet = {
                'pos': start_pos.copy(),
                'velocity': [(dx/dist) * 10, (dy/dist) * 10],
                'type': 'normal',
                'damage': 10
            }
            self.bullets.append(bullet)
            
            # Efeito de partículas no disparo
            self.particle_system.create_explosion(start_pos[0], start_pos[1], (255, 200, 0, 200), 10)
            # Trail do projétil
            self.particle_system.create_trail(start_pos[0], start_pos[1], (255, 100, 0, 150), 
                                           [dx/dist, dy/dist])

    def _fire_projectile_angle(self, angle):
        rad = math.radians(angle)
        bullet = {
            'pos': [self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2],
            'velocity': [math.cos(rad) * 10, math.sin(rad) * 10],
            'type': 'normal',
            'damage': 10
        }
        self.bullets.append(bullet)

    def _update_bullets(self, player_pos):
        for bullet in self.bullets[:]:
            # Adiciona trail de partículas enquanto o projétil se move
            self.particle_system.create_trail(
                bullet['pos'][0], bullet['pos'][1],
                (255, 100, 0, 100),
                [bullet['velocity'][0]/10, bullet['velocity'][1]/10],
                2
            )
            
            bullet['pos'][0] += bullet['velocity'][0]
            bullet['pos'][1] += bullet['velocity'][1]
            
            # Remove projéteis fora da tela
            if (bullet['pos'][0] < -100 or bullet['pos'][0] > 1380 or
                bullet['pos'][1] < -100 or bullet['pos'][1] > 820):
                # Efeito de desvanecimento ao remover
                self.particle_system.create_explosion(
                    bullet['pos'][0], bullet['pos'][1],
                    (255, 100, 0, 150),
                    5
                )
                self.bullets.remove(bullet)

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
        
        # Desenha os projéteis com efeito de brilho
        for bullet in self.bullets:
            bullet_pos = (int(bullet['pos'][0] + camera_offset_x), int(bullet['pos'][1] + camera_offset_y))
            # Brilho externo
            pygame.draw.circle(screen, (255, 200, 0, 128), bullet_pos, 8)
            # Núcleo do projétil
            pygame.draw.circle(screen, (255, 255, 200), bullet_pos, 5)
            pygame.draw.circle(screen, (255, 255, 255), bullet_pos, 3)
        
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

