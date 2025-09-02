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
        """Mapa básico de teste para side-scroller"""
        # Chão - alinhado exatamente com a parte inferior da tela
        ground_height = 200  # Chão mais alto para combinar com o personagem maior
        self.add_platform(0, self.screen_height - ground_height, self.screen_width * 10, ground_height)  # Chão bem mais largo
        
        # Remove todas as plataformas flutuantes já que é um side-scroller
        
        # Ponto de spawn do jogador - logo acima do chão
        spawn_height = 20  # Bem próximo ao chão
        self.spawn_points = [(400, self.screen_height - (ground_height + spawn_height))]  # Spawn mais afastado da borda
        
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
        
    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        """Desenha todos os elementos do mapa que estão visíveis na tela"""
        screen_rect = screen.get_rect()
        
        for platform in self.platforms:
            # Cria um retângulo para a plataforma com o offset da câmera
            platform_rect = pygame.Rect(
                platform['rect'].x + camera_offset_x,
                platform['rect'].y + camera_offset_y,
                platform['rect'].width,
                platform['rect'].height
            )
            
            # Só desenha a plataforma se ela estiver visível na tela
            if platform_rect.colliderect(screen_rect):
                pygame.draw.rect(screen, platform['color'], platform_rect)
