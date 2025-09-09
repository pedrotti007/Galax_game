import pygame
import os

class Collectible:
    def __init__(self, x, y, type_="heart"):
        self.pos = [x, y]
        self.type = type_  # "heart" ou "ammo"
        self.size = (30, 30)
        self.rect = pygame.Rect(x, y, self.size[0], self.size[1])
        
        # Carregar texturas
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        try:
            if type_ == "heart":
                self.image = pygame.image.load(os.path.join(project_root, 'assets', 'images', 'heart_drop.png')).convert_alpha()
            else:  # ammo
                self.image = pygame.image.load(os.path.join(project_root, 'assets', 'images', 'caixa_de_balas.png')).convert_alpha()
            self.image = pygame.transform.scale(self.image, self.size)
        except Exception as e:
            print(f"Erro ao carregar imagem do coletável: {e}")
            self.image = None

    def update(self):
        # Coletáveis agora ficam parados onde aparecem.
        pass

    def draw(self, screen, camera_offset_x, camera_offset_y):
        if self.image:
            screen_pos = (int(self.pos[0] + camera_offset_x), int(self.pos[1] + camera_offset_y))
            screen.blit(self.image, screen_pos)
        else:
            # Fallback: desenhar um retângulo colorido
            color = (255, 0, 0) if self.type == "heart" else (255, 255, 0)
            pygame.draw.rect(screen, color,
                           pygame.Rect(int(self.pos[0] + camera_offset_x),
                                     int(self.pos[1] + camera_offset_y),
                                     self.size[0], self.size[1]))
