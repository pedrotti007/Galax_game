import pygame

class MapManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.platforms = []
        self.decorations = []
        self.spawn_points = []
        self.collectibles = []
        
    def load_map(self, map_id):
        """Carrega um mapa predefinido baseado no ID"""
        self.platforms.clear()  # Limpa plataformas existentes
        if map_id == 1:
            self._create_test_map()
        elif map_id == 2:
            self._create_platform_test()
            
    def _create_test_map(self):
        """Mapa básico de teste com algumas plataformas"""
        # Chão
        self.add_platform(0, self.screen_height - 40, self.screen_width, 40)
        
        # Plataformas (altura reduzida entre elas)
        self.add_platform(300, self.screen_height - 160, 200, 20)  # Reduzido de 200 para 160
        self.add_platform(600, self.screen_height - 240, 200, 20)  # Reduzido de 300 para 240
        self.add_platform(100, self.screen_height - 320, 200, 20)  # Reduzido de 400 para 320
        
        # Ponto de spawn do jogador
        self.spawn_points = [(100, self.screen_height - 100)]
        
    def _create_platform_test(self):
        """Mapa para testar diferentes tipos de plataformas"""
        # Chão
        self.add_platform(0, self.screen_height - 40, self.screen_width, 40)
        
        # Escada de plataformas (altura entre plataformas reduzida)
        for i in range(5):
            x = 100 + (i * 200)
            y = self.screen_height - 100 - (i * 80)  # Reduzido de 100 para 80 de altura entre plataformas
            self.add_platform(x, y, 150, 20)
            
    def add_platform(self, x, y, width, height, platform_type="normal"):
        """Adiciona uma nova plataforma ao mapa"""
        platform = {
            'rect': pygame.Rect(x, y, width, height),
            'type': platform_type,
            'color': (100, 70, 40)  # Cor padrão marrom
        }
        self.platforms.append(platform)
        
    def get_spawn_point(self):
        """Retorna o ponto de spawn inicial"""
        return self.spawn_points[0] if self.spawn_points else (100, self.screen_height - 100)
        
    def draw(self, screen, camera_offset=0):
        """Desenha todos os elementos do mapa"""
        for platform in self.platforms:
            pygame.draw.rect(screen, platform['color'],
                           pygame.Rect(platform['rect'].x + camera_offset,
                                     platform['rect'].y,
                                     platform['rect'].width,
                                     platform['rect'].height))
