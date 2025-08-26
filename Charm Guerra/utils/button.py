import pygame
import os

class Button:
    """Uma classe de botão simples e reutilizável para Pygame."""

    def __init__(self, x, y, width, height, text, on_click, font_size=36, font_name=None):
        """
        Inicializa o botão.

        :param font_name: Nome do arquivo da fonte (ex: 'sua_fonte.ttf') em 'assets/fonts/'.
                          Se None, usa a fonte padrão do Pygame.
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.on_click = on_click
        self.color = (100, 100, 100)  # Cinza escuro
        self.hover_color = (150, 150, 150) # Cinza claro
        self.is_hovered = False

        # --- CORREÇÃO APLICADA AQUI ---
        try:
            if font_name:
                # Constrói o caminho completo para a fonte, de forma segura
                script_dir = os.path.dirname(os.path.abspath(__file__)) # Diretório de 'utils'
                project_root = os.path.dirname(script_dir) # O diretório pai, 'Charm Guerra'
                font_path = os.path.join(project_root, 'assets', 'fonts', font_name)
                self.font = pygame.font.Font(font_path, font_size)
            else:
                # Se nenhuma fonte for especificada, usa a fonte padrão do Pygame
                self.font = pygame.font.Font(None, font_size)
        except pygame.error as e:
            print(f"AVISO: Falha ao carregar a fonte '{font_name}'. Usando fonte padrão. Erro: {e}")
            self.font = pygame.font.Font(None, font_size) # Fallback para a fonte padrão

        self.text_surface = self.font.render(self.text, True, (255, 255, 255)) # Cor do texto branca
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and event.button == 1: # Botão esquerdo do mouse
                self.on_click()

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, current_color, self.rect, border_radius=10)
        screen.blit(self.text_surface, self.text_rect)

