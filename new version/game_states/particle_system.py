import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color, velocity, lifetime, size, fade=True, gravity=False):
        self.x = x
        self.y = y
        self.color = color
        self.initial_color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.initial_lifetime = lifetime
        self.size = size
        self.initial_size = size
        self.fade = fade
        self.gravity = gravity
        
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        
        if self.gravity:
            self.velocity[1] += 0.1  # Aplica gravidade
            
        if self.fade:
            # Calcula a opacidade baseada no tempo de vida restante
            fade_ratio = self.lifetime / self.initial_lifetime
            if len(self.initial_color) == 4:  # Se tem alpha
                self.color = (self.initial_color[0], 
                            self.initial_color[1], 
                            self.initial_color[2], 
                            int(self.initial_color[3] * fade_ratio))
            # Reduz o tamanho gradualmente
            self.size = self.initial_size * fade_ratio

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def create_explosion(self, x, y, color, num_particles=20):
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            lifetime = random.randint(20, 40)
            size = random.uniform(2, 4)
            particle = Particle(x, y, color, velocity, lifetime, size)
            self.particles.append(particle)
    
    def create_trail(self, x, y, color, direction, num_particles=5):
        for _ in range(num_particles):
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)
            velocity = [-direction[0] * random.uniform(1, 3),
                       -direction[1] * random.uniform(1, 3)]
            lifetime = random.randint(10, 20)
            size = random.uniform(2, 4)
            particle = Particle(x + offset_x, y + offset_y, color, velocity, lifetime, size)
            self.particles.append(particle)
    
    def create_impact(self, x, y, color, direction, num_particles=15):
        angle_spread = math.pi / 4  # 45 graus para cada lado
        base_angle = math.atan2(direction[1], direction[0])
        
        for _ in range(num_particles):
            angle = base_angle + random.uniform(-angle_spread, angle_spread)
            speed = random.uniform(3, 7)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            lifetime = random.randint(15, 30)
            size = random.uniform(2, 5)
            particle = Particle(x, y, color, velocity, lifetime, size, gravity=True)
            self.particles.append(particle)
    
    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        for particle in self.particles:
            screen_x = int(particle.x + camera_offset_x)
            screen_y = int(particle.y + camera_offset_y)
            
            if len(particle.color) == 4:  # Se tem canal alpha
                surf = pygame.Surface((particle.size * 2, particle.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, particle.color, (particle.size, particle.size), particle.size)
                screen.blit(surf, (screen_x - particle.size, screen_y - particle.size))
            else:
                pygame.draw.circle(screen, particle.color, (screen_x, screen_y), particle.size)